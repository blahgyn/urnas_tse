#!/usr/bin/env python3
"""
preparar.py - converte os boletins de urna do TSE (bweb_*.csv ou .zip) numa
base SQLite pronta para perguntas, e gera os dados do painel.

Uso mais simples: coloque os arquivos do TSE na pasta boletins/ e rode
    python preparar.py

Outras formas:
    python preparar.py --se-necessario          (so refaz se os boletins mudaram)
    python preparar.py bweb_1t_SP_....csv bweb_2t_SP_....zip
    python preparar.py --pasta C:/Downloads/tse --cargo Governador
    python preparar.py --todos-cargos

Usa apenas a biblioteca padrao do Python (3.8+). Nada para instalar.
"""
import argparse
import csv
import glob
import hashlib
import json
import os
import re
import sqlite3
import sys
import time
import unicodedata
import zipfile

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA_PADRAO = os.path.join(AQUI, "dados", "eleicao.sqlite")
PAINEL_PADRAO = os.path.join(AQUI, "painel", "dados.js")

# coluna do CSV -> (coluna na base, tipo)
COLS_SECAO = [
    ("NR_TURNO", "turno", int),
    ("SG_UF", "uf", str),
    ("CD_MUNICIPIO", "cd_municipio", int),
    ("NM_MUNICIPIO", "nm_municipio", str),
    ("NR_ZONA", "nr_zona", int),
    ("NR_SECAO", "nr_secao", int),
    ("NR_LOCAL_VOTACAO", "nr_local_votacao", int),
    ("QT_APTOS", "qt_aptos", int),
    ("QT_COMPARECIMENTO", "qt_comparecimento", int),
    ("QT_ABSTENCOES", "qt_abstencoes", int),
    ("DS_TIPO_URNA", "ds_tipo_urna", str),
    ("NR_URNA_EFETIVADA", "nr_urna_efetivada", int),
    ("CD_CARGA_1_URNA_EFETIVADA", "cd_carga_1", str),
    ("CD_CARGA_2_URNA_EFETIVADA", "cd_carga_2", str),
    ("CD_FLASHCARD_URNA_EFETIVADA", "cd_flashcard", str),
    ("DT_CARGA_URNA_EFETIVADA", "dt_carga_urna", str),
    ("DS_CARGO_PERGUNTA_SECAO", "ds_cargo_pergunta_secao", str),
    ("DS_SECOES_AGREGADAS", "ds_secoes_agregadas", str),
    ("DT_ABERTURA", "dt_abertura", str),
    ("DT_ENCERRAMENTO", "dt_encerramento", str),
    ("DT_EMISSAO_BU", "dt_emissao_bu", str),
    ("DT_BU_RECEBIDO", "dt_bu_recebido", str),
    ("QT_ELEI_BIOM_SEM_HABILITACAO", "qt_biom_sem_habilitacao", int),
    ("NR_JUNTA_APURADORA", "nr_junta_apuradora", int),
    ("NR_TURMA_APURADORA", "nr_turma_apuradora", int),
]
COLS_VOTO = [
    ("NR_TURNO", "turno", int),
    ("SG_UF", "uf", str),
    ("CD_MUNICIPIO", "cd_municipio", int),
    ("NR_ZONA", "nr_zona", int),
    ("NR_SECAO", "nr_secao", int),
    ("CD_CARGO_PERGUNTA", "cd_cargo", int),
    ("DS_CARGO_PERGUNTA", "ds_cargo", str),
    ("DS_TIPO_VOTAVEL", "ds_tipo_votavel", str),
    ("NR_VOTAVEL", "nr_votavel", int),
    ("NM_VOTAVEL", "nm_votavel", str),
    ("SG_PARTIDO", "sg_partido", str),
    ("QT_VOTOS", "qt_votos", int),
]

ESQUEMA = """
CREATE TABLE secoes (
    turno INTEGER, uf TEXT, cd_municipio INTEGER, nm_municipio TEXT,
    nr_zona INTEGER, nr_secao INTEGER, nr_local_votacao INTEGER,
    qt_aptos INTEGER, qt_comparecimento INTEGER, qt_abstencoes INTEGER,
    ds_tipo_urna TEXT, nr_urna_efetivada INTEGER, cd_carga_1 TEXT, cd_carga_2 TEXT,
    cd_flashcard TEXT, dt_carga_urna TEXT, ds_cargo_pergunta_secao TEXT,
    ds_secoes_agregadas TEXT, dt_abertura TEXT, dt_encerramento TEXT,
    dt_emissao_bu TEXT, dt_bu_recebido TEXT, qt_biom_sem_habilitacao INTEGER,
    nr_junta_apuradora INTEGER, nr_turma_apuradora INTEGER,
    PRIMARY KEY (turno, uf, cd_municipio, nr_zona, nr_secao)
);
CREATE TABLE votos (
    turno INTEGER, uf TEXT, cd_municipio INTEGER, nr_zona INTEGER, nr_secao INTEGER,
    cd_cargo INTEGER, ds_cargo TEXT, ds_tipo_votavel TEXT, nr_votavel INTEGER,
    nm_votavel TEXT, sg_partido TEXT, qt_votos INTEGER
);
CREATE TABLE fontes (
    arquivo TEXT, bytes INTEGER, sha256 TEXT, dt_geracao TEXT, hh_geracao TEXT,
    linhas_lidas INTEGER, linhas_importadas INTEGER
);
CREATE TABLE metadados (chave TEXT PRIMARY KEY, valor TEXT);
"""


def conv(valor, tipo):
    # Leiame do TSE: "#NULO"/"#NE" = sem informacao; nos campos numericos o equivalente e -1/-3
    if valor == "" or valor.startswith("#NULO") or valor == "#NE":
        return None
    if tipo is int:
        try:
            n = int(valor)
        except ValueError:
            return None
        return None if n in (-1, -3) else n
    return valor


def slug(nome):
    s = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")
    return s if s and not s[0].isdigit() else "c_" + s


PADRAO_BOLETIM = re.compile(r"^bweb_.*\.(csv|zip)$", re.IGNORECASE)


def descobrir_boletins(pastas):
    """Procura bweb_*.csv / bweb_*.zip nas pastas (sem subpastas). Se houver o .zip e o .csv
    extraido do mesmo boletim, usa so o .csv para nao importar duas vezes."""
    achados = {}
    for pasta in pastas:
        if not os.path.isdir(pasta):
            continue
        for nome in sorted(os.listdir(pasta)):
            if not PADRAO_BOLETIM.match(nome):
                continue
            base, ext = os.path.splitext(nome)
            atual = achados.get(base.lower())
            if atual is None or (ext.lower() == ".csv" and atual.lower().endswith(".zip")):
                achados[base.lower()] = os.path.join(pasta, nome)
    return [achados[k] for k in sorted(achados)]


def expandir(caminhos):
    lista = []
    for padrao in caminhos:
        encontrados = sorted(glob.glob(padrao)) or [padrao]
        for c in encontrados:
            if os.path.isdir(c):
                lista += descobrir_boletins([c])
            elif not os.path.exists(c):
                sys.exit(f"Arquivo nao encontrado: {c}")
            else:
                lista.append(c)
    return lista


def assinatura_entradas(arquivos, cargos):
    """Identifica o conjunto de entrada (nomes + tamanhos + cargo) para saber se a base esta atualizada."""
    return json.dumps({"arquivos": sorted([os.path.basename(a), os.path.getsize(a)] for a in arquivos),
                       "cargos": cargos}, ensure_ascii=False)


def fontes_de(arquivos):
    """Gera (nome, tamanho, arquivo_binario) para cada CSV, inclusive dentro de .zip."""
    for caminho in arquivos:
        if caminho.lower().endswith(".zip"):
            with zipfile.ZipFile(caminho) as z:
                for info in z.infolist():
                    if info.filename.lower().endswith(".csv"):
                        with z.open(info) as fh:
                            yield f"{os.path.basename(caminho)}:{info.filename}", info.file_size, fh
        else:
            with open(caminho, "rb") as fh:
                yield os.path.basename(caminho), os.path.getsize(caminho), fh


def abrir_base_vazia(caminho):
    """Abre a base zerada. Se o arquivo ja existe e nao pode ser apagado (algumas IAs trabalham
    em pastas onde apagar e proibido), reaproveita o arquivo removendo as tabelas."""
    os.makedirs(os.path.dirname(os.path.abspath(caminho)), exist_ok=True)
    if os.path.exists(caminho):
        try:
            os.remove(caminho)
        except OSError:
            con = sqlite3.connect(caminho)
            con.execute("PRAGMA journal_mode=OFF")
            for (nome, tipo) in con.execute(
                    "SELECT name, type FROM sqlite_master WHERE type IN ('table','view') "
                    "AND name NOT LIKE 'sqlite_%'").fetchall():
                con.execute(f'DROP {"VIEW" if tipo == "view" else "TABLE"} IF EXISTS "{nome}"')
            con.commit()
            con.execute("VACUUM")
            con.close()
    con = sqlite3.connect(caminho)
    con.execute("PRAGMA journal_mode=OFF")
    con.execute("PRAGMA synchronous=OFF")
    return con


def importar(con, nome, tamanho, fh, cargos):
    """Le um CSV do TSE linha a linha. Filtra pelo cargo antes de interpretar o CSV (rapido)."""
    sha = hashlib.sha256()
    cab_bytes = fh.readline()
    sha.update(cab_bytes)
    cab = next(csv.reader([cab_bytes.decode("latin-1").lstrip("﻿").strip()], delimiter=";"))
    pos = {c: i for i, c in enumerate(cab)}
    faltando = [c for c, _, _ in COLS_SECAO + COLS_VOTO if c not in pos]
    if faltando:
        sys.exit(f"{nome}: nao parece um boletim de urna do TSE (faltam colunas {faltando})")
    i_cargo = pos["DS_CARGO_PERGUNTA"]
    filtros = [f';"{c}";'.encode("latin-1") for c in cargos] if cargos else None
    cargos_set = set(cargos) if cargos else None

    lidas = 0
    importadas = 0
    geracao = None
    lote_s, lote_v = [], []
    inicio = time.time()
    lido_bytes = len(cab_bytes)
    ultimo_aviso = 0.0

    def gerar():
        nonlocal lidas, lido_bytes, ultimo_aviso
        for linha in fh:
            sha.update(linha)
            lidas += 1
            lido_bytes += len(linha)
            if lidas % 200000 == 0:
                agora = time.time()
                if agora - ultimo_aviso > 10:
                    ultimo_aviso = agora
                    pct = 100.0 * lido_bytes / tamanho if tamanho else 0
                    print(f"  {nome}: {pct:5.1f}%  ({lidas:,} linhas lidas)", flush=True)
            if filtros and not any(f in linha for f in filtros):
                continue
            yield linha.decode("latin-1")

    sql_s = "INSERT OR IGNORE INTO secoes VALUES (%s)" % ",".join("?" * len(COLS_SECAO))
    sql_v = "INSERT INTO votos VALUES (%s)" % ",".join("?" * len(COLS_VOTO))
    idx_s = [(pos[c], t) for c, _, t in COLS_SECAO]
    idx_v = [(pos[c], t) for c, _, t in COLS_VOTO]
    for row in csv.reader(gerar(), delimiter=";"):
        if cargos_set and row[i_cargo] not in cargos_set:
            continue
        if geracao is None:
            geracao = (row[pos["DT_GERACAO"]], row[pos["HH_GERACAO"]])
        lote_s.append([conv(row[i], t) for i, t in idx_s])
        lote_v.append([conv(row[i], t) for i, t in idx_v])
        importadas += 1
        if len(lote_v) >= 50000:
            con.executemany(sql_s, lote_s)
            con.executemany(sql_v, lote_v)
            lote_s, lote_v = [], []
    # consome o resto do arquivo para o hash ficar completo
    for linha in fh:
        sha.update(linha)
    con.executemany(sql_s, lote_s)
    con.executemany(sql_v, lote_v)
    con.execute(
        "INSERT INTO fontes VALUES (?,?,?,?,?,?,?)",
        (nome, tamanho, sha.hexdigest(), *(geracao or (None, None)), lidas, importadas),
    )
    print(f"  {nome}: {lidas:,} linhas lidas, {importadas:,} importadas em {time.time()-inicio:.0f}s")


def candidatos_principais(con, cargo):
    """Candidatos que viram colunas em secao_turnos: os do 2o turno, ou os 5 mais votados do 1o."""
    for turno, limite in ((2, 99), (1, 5)):
        rows = con.execute(
            """SELECT nr_votavel, nm_votavel, SUM(qt_votos) FROM votos
               WHERE turno=? AND ds_cargo=? AND ds_tipo_votavel='Nominal'
               GROUP BY 1,2 ORDER BY 3 DESC LIMIT ?""",
            (turno, cargo, limite),
        ).fetchall()
        if rows:
            return [(nr, nm, slug(nm)) for nr, nm, _ in rows]
    return []


def criar_secao_turnos(con, cargo):
    """Tabela larga: uma linha por secao, com 1o e 2o turno lado a lado."""
    cands = candidatos_principais(con, cargo)
    turnos = [t for (t,) in con.execute("SELECT DISTINCT turno FROM votos WHERE ds_cargo=? ORDER BY 1", (cargo,))]

    def bloco(t):
        piv = ",\n".join(
            f"SUM(CASE WHEN nr_votavel={nr} THEN qt_votos ELSE 0 END) AS {sl}" for nr, _, sl in cands
        )
        return f"""
        SELECT v.uf, v.cd_municipio, v.nr_zona, v.nr_secao,
            {piv},
            SUM(CASE WHEN ds_tipo_votavel IN ('Nominal','Legenda') THEN qt_votos ELSE 0 END) AS validos,
            SUM(CASE WHEN ds_tipo_votavel='Branco' THEN qt_votos ELSE 0 END) AS brancos,
            SUM(CASE WHEN ds_tipo_votavel='Nulo' THEN qt_votos ELSE 0 END) AS nulos,
            SUM(qt_votos) AS total_votos
        FROM votos v WHERE v.turno={t} AND v.ds_cargo=?
        GROUP BY 1,2,3,4"""

    con.execute("DROP TABLE IF EXISTS secao_turnos")
    chaves = " UNION ".join(
        f"SELECT uf, cd_municipio, nr_zona, nr_secao FROM votos WHERE turno={t} AND ds_cargo=?" for t in turnos
    )
    sel = ["k.uf", "k.cd_municipio", "COALESCE(s1.nm_municipio, s2.nm_municipio) AS nm_municipio",
           "k.nr_zona", "k.nr_secao", "COALESCE(s1.nr_local_votacao, s2.nr_local_votacao) AS nr_local_votacao"]
    joins = []
    for t in turnos:
        a = f"t{t}"
        joins.append(f"LEFT JOIN ({bloco(t)}) v{t} ON v{t}.uf=k.uf AND v{t}.cd_municipio=k.cd_municipio "
                     f"AND v{t}.nr_zona=k.nr_zona AND v{t}.nr_secao=k.nr_secao")
        joins.append(f"LEFT JOIN secoes s{t} ON s{t}.turno={t} AND s{t}.uf=k.uf AND s{t}.cd_municipio=k.cd_municipio "
                     f"AND s{t}.nr_zona=k.nr_zona AND s{t}.nr_secao=k.nr_secao")
        sel += [
            f"s{t}.qt_aptos AS aptos_{a}", f"s{t}.qt_comparecimento AS comparecimento_{a}",
            f"s{t}.qt_abstencoes AS abstencoes_{a}",
        ]
        sel += [f"v{t}.{sl} AS {sl}_{a}" for _, _, sl in cands]
        sel += [f"v{t}.validos AS validos_{a}", f"v{t}.brancos AS brancos_{a}",
                f"v{t}.nulos AS nulos_{a}", f"v{t}.total_votos AS total_votos_{a}"]
        sel += [f"ROUND(100.0*v{t}.{sl}/NULLIF(v{t}.validos,0), 4) AS pct_{sl}_{a}" for _, _, sl in cands]
        sel += [
            f"s{t}.dt_abertura AS abertura_{a}", f"s{t}.dt_encerramento AS encerramento_{a}",
            f"substr(s{t}.dt_encerramento, 12, 5) AS hora_encerramento_{a}",
            f"s{t}.dt_emissao_bu AS emissao_bu_{a}", f"s{t}.dt_bu_recebido AS bu_recebido_{a}",
            f"substr(s{t}.dt_bu_recebido, 12, 5) AS hora_bu_recebido_{a}",
            f"s{t}.ds_tipo_urna AS tipo_urna_{a}", f"s{t}.nr_urna_efetivada AS urna_{a}",
            f"s{t}.ds_secoes_agregadas AS secoes_agregadas_{a}",
            f"s{t}.qt_biom_sem_habilitacao AS biom_sem_habilitacao_{a}",
        ]
    if 1 in turnos and 2 in turnos:
        sel += [f"(v2.{sl} - v1.{sl}) AS dif_{sl}" for _, _, sl in cands]
        sel += [f"ROUND(100.0*v2.{sl}/NULLIF(v2.validos,0) - 100.0*v1.{sl}/NULLIF(v1.validos,0), 4) AS dif_pp_{sl}"
                for _, _, sl in cands]
        sel += ["(s2.qt_comparecimento - s1.qt_comparecimento) AS dif_comparecimento",
                "(s1.nr_urna_efetivada IS NOT s2.nr_urna_efetivada) AS urna_trocada",
                "(s1.ds_secoes_agregadas IS NOT NULL OR s2.ds_secoes_agregadas IS NOT NULL) AS tem_agregacao"]
    sql = (f"CREATE TABLE secao_turnos AS SELECT\n  " + ",\n  ".join(sel)
           + f"\nFROM ({chaves}) k\n" + "\n".join(joins))
    # os parametros seguem a ordem em que os "?" aparecem: chaves primeiro, depois cada bloco
    params = [cargo] * len(turnos) + [cargo] * len(turnos)
    con.execute(sql, params)
    con.execute("CREATE INDEX ix_st_mun ON secao_turnos(cd_municipio)")
    con.execute("INSERT OR REPLACE INTO metadados VALUES ('cargo_secao_turnos', ?)", (cargo,))
    con.execute("INSERT OR REPLACE INTO metadados VALUES ('candidatos_secao_turnos', ?)",
                (json.dumps([{"numero": nr, "nome": nm, "coluna": sl} for nr, nm, sl in cands], ensure_ascii=False),))
    con.execute("INSERT OR REPLACE INTO metadados VALUES ('turnos', ?)", (json.dumps(turnos),))
    return cands, turnos


def exportar_painel(con, caminho, cands, turnos):
    """Escreve painel/dados.js (window.DADOS = {...}) para o painel abrir sem servidor."""
    cols = ["uf", "cd_municipio", "nm_municipio", "nr_zona", "nr_secao"]
    for t in turnos:
        a = f"t{t}"
        cols += [f"aptos_{a}", f"comparecimento_{a}", f"validos_{a}", f"brancos_{a}", f"nulos_{a}"]
        cols += [f"{sl}_{a}" for _, _, sl in cands]
        cols += [f"hora_encerramento_{a}", f"hora_bu_recebido_{a}", f"urna_{a}"]
    rows = con.execute(f"SELECT {', '.join(cols)} FROM secao_turnos").fetchall()
    dados = {
        "candidatos": [{"numero": nr, "nome": nm, "coluna": sl} for nr, nm, sl in cands],
        "turnos": turnos,
        "fontes": [dict(zip(["arquivo", "dt_geracao", "hh_geracao", "sha256"], r))
                   for r in con.execute("SELECT arquivo, dt_geracao, hh_geracao, sha256 FROM fontes")],
        "colunas": {c: [r[i] for r in rows] for i, c in enumerate(cols)},
    }
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write("window.DADOS = ")
        json.dump(dados, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")
    print(f"Painel: {caminho} ({os.path.getsize(caminho)/1e6:.1f} MB)")


def resumo(con, cands, turnos):
    print("\nResumo (confira com os totais oficiais do TSE):")
    for t in turnos:
        n, = con.execute("SELECT COUNT(*) FROM secoes WHERE turno=?", (t,)).fetchone()
        print(f"  {t}o turno - {n:,} secoes")
        for nm, v in con.execute(
            """SELECT nm_votavel, SUM(qt_votos) FROM votos WHERE turno=? AND ds_cargo=
               (SELECT valor FROM metadados WHERE chave='cargo_secao_turnos')
               GROUP BY nm_votavel ORDER BY 2 DESC LIMIT 6""", (t,)):
            print(f"      {nm:<30} {v:>12,}")


def base_atualizada(caminho, assinatura):
    if not os.path.exists(caminho):
        return False
    try:
        con = sqlite3.connect(f"file:{caminho}?mode=ro", uri=True)
        r = con.execute("SELECT valor FROM metadados WHERE chave='entradas'").fetchone()
        ok = con.execute("SELECT COUNT(*) FROM secao_turnos").fetchone()[0] > 0
        con.close()
        return bool(r) and r[0] == assinatura and ok
    except sqlite3.Error:
        return False


def main():
    ap = argparse.ArgumentParser(description="Importa boletins de urna (bweb_*.csv/.zip do TSE) para SQLite.")
    ap.add_argument("arquivos", nargs="*",
                    help="CSVs ou ZIPs do boletim de urna. Se omitido, usa tudo o que estiver em boletins/")
    ap.add_argument("--pasta", action="append", help="pasta onde procurar os boletins (pode repetir)")
    ap.add_argument("--cargo", default="Presidente", help="cargo a importar (padrao: Presidente)")
    ap.add_argument("--todos-cargos", action="store_true", help="importa todos os cargos (base bem maior)")
    ap.add_argument("--se-necessario", action="store_true",
                    help="nao faz nada se a base ja foi gerada com estes mesmos boletins")
    ap.add_argument("--saida", default=SAIDA_PADRAO, help=f"arquivo SQLite (padrao: {os.path.relpath(SAIDA_PADRAO)})")
    ap.add_argument("--painel", default=PAINEL_PADRAO, help="onde escrever os dados do painel")
    ap.add_argument("--sem-painel", action="store_true", help="nao gera os dados do painel")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(errors="replace")
    except AttributeError:
        pass

    if args.arquivos:
        arquivos = expandir(args.arquivos)
    else:
        pastas = args.pasta or [os.path.join(AQUI, "boletins"), AQUI]
        arquivos = descobrir_boletins(pastas)
    if not arquivos:
        sys.exit("Nenhum boletim encontrado. Baixe os arquivos bweb_1t_<UF>_....zip e bweb_2t_<UF>_....zip do TSE "
                 "(links no README.md) e coloque-os na pasta boletins/.")
    print("Boletins encontrados:")
    for a in arquivos:
        print(f"  {a}  ({os.path.getsize(a)/1e6:,.0f} MB)")

    cargos = None if args.todos_cargos else [args.cargo]
    assinatura = assinatura_entradas(arquivos, cargos)
    if args.se_necessario and base_atualizada(args.saida, assinatura):
        print(f"A base ja esta atualizada com estes boletins: {args.saida}")
        return

    con = abrir_base_vazia(args.saida)
    con.executescript(ESQUEMA)

    inicio = time.time()
    for nome, tamanho, fh in fontes_de(arquivos):
        print(f"Lendo {nome} ({tamanho/1e6:,.0f} MB)...")
        importar(con, nome, tamanho, fh, cargos)
        con.commit()

    if not con.execute("SELECT 1 FROM votos LIMIT 1").fetchone():
        sys.exit(f"Nenhuma linha do cargo '{args.cargo}' encontrada. Confira o nome do cargo (ex.: Presidente, Governador).")

    print("Criando indices e a tabela secao_turnos...")
    con.executescript("""
        CREATE INDEX ix_votos_secao ON votos(turno, cd_municipio, nr_zona, nr_secao);
        CREATE INDEX ix_votos_votavel ON votos(turno, ds_cargo, nr_votavel);
        CREATE INDEX ix_secoes_mun ON secoes(cd_municipio);
    """)
    cargo_principal = args.cargo
    if args.todos_cargos and not con.execute("SELECT 1 FROM votos WHERE ds_cargo=? LIMIT 1", (cargo_principal,)).fetchone():
        cargo_principal = con.execute("SELECT ds_cargo FROM votos LIMIT 1").fetchone()[0]
    cands, turnos = criar_secao_turnos(con, cargo_principal)
    con.execute("INSERT OR REPLACE INTO metadados VALUES ('criado_em', datetime('now'))")
    con.execute("INSERT OR REPLACE INTO metadados VALUES ('entradas', ?)", (assinatura,))
    con.commit()

    if not args.sem_painel:
        exportar_painel(con, args.painel, cands, turnos)
    resumo(con, cands, turnos)
    con.execute("ANALYZE")
    con.commit()
    con.close()
    print(f"\nPronto em {time.time()-inicio:.0f}s. Base: {args.saida} ({os.path.getsize(args.saida)/1e6:.0f} MB)")


if __name__ == "__main__":
    main()
