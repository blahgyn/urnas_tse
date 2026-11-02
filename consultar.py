#!/usr/bin/env python3
"""
consultar.py - roda uma consulta SQL (somente leitura) na base criada pelo preparar.py.

Uso:
    python consultar.py "SELECT nm_municipio, COUNT(*) FROM secao_turnos GROUP BY 1 ORDER BY 2 DESC LIMIT 10"
    python consultar.py --arquivo minha_consulta.sql
    python consultar.py --esquema
    python consultar.py "SELECT ..." --csv resultado.csv     (salva tudo em CSV)

Usa apenas a biblioteca padrao do Python.
"""
import argparse
import csv
import os
import sqlite3
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE_PADRAO = os.path.join(AQUI, "dados", "eleicao.sqlite")


def conectar(caminho=BASE_PADRAO, limite_segundos=120):
    if not os.path.exists(caminho):
        sys.exit(f"Base nao encontrada em {caminho}. Coloque os boletins do TSE na pasta boletins/ e rode primeiro: python preparar.py")
    con = sqlite3.connect(f"file:{caminho}?mode=ro", uri=True)
    inicio = time.time()
    con.set_progress_handler(lambda: 1 if time.time() - inicio > limite_segundos else 0, 100000)
    return con


def esquema(con):
    linhas = []
    for nome, tipo in con.execute("SELECT name, type FROM sqlite_master WHERE type IN ('table','view') ORDER BY name"):
        cols = [r[1] for r in con.execute(f"PRAGMA table_info('{nome}')")]
        n = con.execute(f"SELECT COUNT(*) FROM \"{nome}\"").fetchone()[0]
        linhas.append(f"{nome} ({n:,} linhas): " + ", ".join(cols))
    linhas.append("")
    for chave, valor in con.execute("SELECT chave, valor FROM metadados"):
        linhas.append(f"metadados.{chave} = {valor}")
    for r in con.execute("SELECT arquivo, dt_geracao, hh_geracao, sha256 FROM fontes"):
        linhas.append(f"fonte: {r[0]} gerado {r[1]} {r[2]} sha256={r[3]}")
    return "\n".join(linhas)


IDENTIFICADORES = ("nr_", "cd_", "urna", "turno", "ano")


def formatar(v, coluna=""):
    if v is None:
        return ""
    if isinstance(v, float):
        return f"{v:,.4f}".rstrip("0").rstrip(".") if abs(v) < 1e15 else str(v)
    if isinstance(v, int):
        # numeros de secao, zona, urna etc. ficam sem separador de milhar
        return str(v) if coluna.lower().startswith(IDENTIFICADORES) else f"{v:,}"
    return str(v)


def tabela(cabecalho, linhas):
    texto = [[formatar(v, cabecalho[i]) for i, v in enumerate(r)] for r in linhas]
    larg = [max([len(c)] + [len(r[i]) for r in texto]) for i, c in enumerate(cabecalho)]
    out = [" | ".join(c.ljust(larg[i]) for i, c in enumerate(cabecalho)),
           "-+-".join("-" * w for w in larg)]
    for r in texto:
        out.append(" | ".join(v.rjust(larg[i]) if linhas and isinstance(linhas[0][i], (int, float)) else v.ljust(larg[i])
                              for i, v in enumerate(r)))
    return "\n".join(out)


def executar(con, sql, maximo=50):
    cur = con.execute(sql)
    if cur.description is None:
        return [], [], False
    cab = [d[0] for d in cur.description]
    linhas = cur.fetchmany(maximo + 1)
    cortado = len(linhas) > maximo
    return cab, linhas[:maximo], cortado


def main():
    ap = argparse.ArgumentParser(description="Consulta SQL somente-leitura na base de boletins de urna.")
    ap.add_argument("sql", nargs="?", help="consulta SQL (SQLite)")
    ap.add_argument("--arquivo", help="ler a consulta de um arquivo .sql")
    ap.add_argument("--esquema", action="store_true", help="mostra tabelas, colunas e fontes")
    ap.add_argument("--max", type=int, default=50, help="maximo de linhas exibidas (padrao 50)")
    ap.add_argument("--csv", help="salva o resultado completo neste arquivo CSV")
    ap.add_argument("--base", default=BASE_PADRAO)
    args = ap.parse_args()
    sys.stdout.reconfigure(errors="replace")  # consoles do Windows sem UTF-8

    con = conectar(args.base)
    if args.esquema:
        print(esquema(con))
        return
    sql = open(args.arquivo, encoding="utf-8").read() if args.arquivo else args.sql
    if not sql:
        ap.error("informe uma consulta SQL, --arquivo ou --esquema")
    try:
        if args.csv:
            cur = con.execute(sql)
            with open(args.csv, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow([d[0] for d in cur.description])
                n = 0
                for r in cur:
                    w.writerow(r)
                    n += 1
            print(f"{n:,} linhas salvas em {args.csv}")
            return
        cab, linhas, cortado = executar(con, sql, args.max)
    except sqlite3.Error as e:
        sys.exit(f"Erro na consulta: {e}")
    print(tabela(cab, linhas))
    print(f"\n({len(linhas)} linha(s){'; resultado cortado, use --max ou --csv' if cortado else ''})")


if __name__ == "__main__":
    main()
