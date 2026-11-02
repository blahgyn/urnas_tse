# Guia para assistentes de IA: perguntas sobre boletins de urna

Este repositório transforma os boletins de urna publicados pelo TSE (`bweb_*.csv` / `bweb_*.zip`) numa base
SQLite (`dados/eleicao.sqlite`). O usuário faz perguntas em linguagem natural e você responde
consultando essa base. Leia este guia inteiro antes da primeira consulta.

## Primeiros passos (faça você mesmo, sem pedir ao usuário)

O usuário normalmente **não sabe programar**. Ele só baixou este repositório, colocou os boletins na pasta
`boletins/` e associou a pasta a você. Rode os comandos você mesmo; não peça para ele abrir terminal.

1. Prepare a base (rápido se já estiver pronta):
   ```bash
   python3 preparar.py --se-necessario      # no Windows/PowerShell: python preparar.py --se-necessario
   ```
   - Lê tudo o que estiver em `boletins/` (`.zip` ou `.csv`). O 1º turno de SP (8 GB) leva cerca de 1 minuto.
     Se o seu ambiente limita o tempo dos comandos, rode-o sozinho, sem encadear outros comandos.
   - Se disser "Nenhum boletim encontrado": explique ao usuário que ele precisa baixar os arquivos do TSE e
     colocá-los em `boletins/`, e aponte a seção "Baixe os boletins de urna" do `README.md`.
   - Se `python3` não existir, tente `python` ou `py`. Não há nada para instalar com pip.
   - No fim, o script imprime os totais por candidato. Mostre-os ao usuário e lembre que ele pode
     compará-los com o resultado oficial do TSE.
2. Confira o esquema: `python3 consultar.py --esquema`.
3. Responda às perguntas com `python3 consultar.py "SELECT ..."`.

Os dados de uma só eleição devem estar em `boletins/` (pode haver vários estados). Se encontrar arquivos de
anos diferentes, avise o usuário antes de preparar.

## Regras

1. **Toda resposta numérica vem com a SQL que a produziu**, num bloco ```sql```, e com uma frase dizendo
   como você interpretou a pergunta (qual turno, qual horário, qual denominador). Quem lê precisa
   conseguir reproduzir e contestar o número.
2. **Nunca invente números.** Se a base não tem o dado, diga isso.
3. **Se a pergunta for ambígua, escolha a leitura mais natural, diga qual foi e mostre a alternativa**
   quando ela mudar o resultado (ex.: horário de encerramento do 1º ou do 2º turno).
4. **Descreva, não acuse.** Mostre o que os dados mostram. Diferenças entre grupos de urnas têm causas
   comuns (perfil do bairro, tamanho da seção, filas, comparecimento). Quando relevante, compare o grupo
   pedido com os demais (ex.: a faixa 17h contra 18h e 19h) para dar contexto.
5. Antes da primeira consulta, rode o esquema para confirmar nomes de colunas e candidatos:
   `python3 consultar.py --esquema` (ou a ferramenta `esquema` do servidor MCP).

## Como consultar

```bash
python3 consultar.py "SELECT ... FROM secao_turnos ..."      # mostra até 50 linhas
python3 consultar.py "SELECT ..." --max 200
python3 consultar.py "SELECT ..." --csv saida.csv            # resultado completo
python3 consultar.py --arquivo minha_consulta.sql
```

Dialeto: **SQLite**. A conexão é somente leitura. Use `python3` ou `python`, o que existir no ambiente. Pelo servidor MCP (`mcp_server.py`) as ferramentas são
`guia`, `esquema` e `consultar_sql`.

## Tabelas

### `secao_turnos` (use esta para quase tudo)
Uma linha por seção eleitoral, com o 1º e o 2º turno lado a lado. Chave: `uf, cd_municipio, nr_zona, nr_secao`.
Os sufixos `_t1` e `_t2` indicam o turno.

| coluna | significado |
|---|---|
| `nm_municipio`, `nr_zona`, `nr_secao`, `nr_local_votacao` | identificação da seção |
| `aptos_tN`, `comparecimento_tN`, `abstencoes_tN` | eleitores aptos, que votaram e que faltaram |
| `<candidato>_tN` | votos do candidato na seção (ex.: `fulano_de_tal_t1`; os nomes reais estão em `metadados`). 0 quando não teve voto |
| `validos_tN` | votos nominais (+ legenda, quando houver). Não inclui brancos e nulos |
| `brancos_tN`, `nulos_tN`, `total_votos_tN` | brancos, nulos e soma de tudo |
| `pct_<candidato>_tN` | % dos votos válidos da seção |
| `abertura_tN`, `encerramento_tN` | data e hora de abertura/encerramento da votação na urna |
| `hora_encerramento_tN` | só a hora do encerramento, texto `'HH:MM'` |
| `emissao_bu_tN` | quando a urna imprimiu o boletim |
| `bu_recebido_tN`, `hora_bu_recebido_tN` | quando o boletim chegou ao TSE (`'HH:MM'`) |
| `urna_tN` | número da urna efetivamente usada |
| `tipo_urna_tN` | Apurada / Não apurada / Anulada… |
| `secoes_agregadas_tN` | outras seções que votaram nesta urna (ex.: `'10 / 114'`) |
| `biom_sem_habilitacao_tN` | eleitores com biometria liberados sem ela |
| `dif_<candidato>` | votos no 2º turno − votos no 1º turno, na mesma seção |
| `dif_pp_<candidato>` | variação em pontos percentuais dos votos válidos (2º − 1º) |
| `dif_comparecimento` | comparecimento 2º − 1º |
| `urna_trocada` | 1 se o número da urna mudou entre os turnos |
| `tem_agregacao` | 1 se a seção teve seções agregadas em algum turno |

Os candidatos que viram colunas são os do 2º turno. A lista exata (nome → coluna) está em
`SELECT valor FROM metadados WHERE chave='candidatos_secao_turnos'`.

### `votos` (formato longo, todos os candidatos)
Uma linha por seção × votável: `turno, uf, cd_municipio, nr_zona, nr_secao, cd_cargo, ds_cargo,
ds_tipo_votavel ('Nominal'|'Branco'|'Nulo'|'Legenda'), nr_votavel, nm_votavel, sg_partido, qt_votos`.
Use para candidatos do 1º turno que não foram ao 2º (filtre por `nm_votavel`).
**Se um candidato não teve voto numa seção, não existe linha**: trate como 0 (use `LEFT JOIN` + `COALESCE`).

### `secoes`
Uma linha por turno × seção com todos os dados do boletim (inclui `cd_carga_1`, `cd_carga_2`,
`cd_flashcard`, `dt_carga_urna`, `nr_junta_apuradora`). Datas em texto ISO `'AAAA-MM-DD HH:MM:SS'`.

### `fontes` e `metadados`
Arquivos de origem (nome, data de geração pelo TSE, **sha256**) e informações da importação.
Cite o arquivo/sha256 quando a pessoa quiser comprovar de onde veio o número.

## Como traduzir a pergunta

| o usuário diz | use |
|---|---|
| "urna" | uma seção (`secao_turnos`). Cada seção tem um boletim; com seções agregadas, uma urna atende várias |
| "fechou / encerrou às X" | `hora_encerramento_t2` (ou `_t1` se a pergunta for do 1º turno) |
| "chegou / foi transmitida / entrou na apuração às X" | `hora_bu_recebido_tN` |
| "entre 17:00 e 18:00" | `hora >= '17:00' AND hora < '18:00'` (texto, comparação funciona) |
| "aumento de votos do X" | `(SUM(x_t2) - SUM(x_t1)) / SUM(x_t1)` sobre as mesmas seções |
| "perda de votos" | `dif_x < 0`; a maior perda é `ORDER BY dif_x ASC` |
| "percentual / proporção" | por padrão % dos **votos válidos**. Diga se usou outro denominador |
| "em São Paulo" | a base inteira, se só tem SP (confira `SELECT DISTINCT uf FROM secao_turnos`); "cidade de São Paulo" é `nm_municipio = 'SÃO PAULO'` |

Nomes de município estão em MAIÚSCULAS com acento (`'SÃO PAULO'`, `'RIBEIRÃO PRETO'`). Na dúvida,
use `nm_municipio LIKE '%RIBEIR%PRETO%'`.

## Armadilhas

- **Some antes de dividir.** O % de um grupo é `SUM(a)/SUM(b)`, não `AVG(a/b)` (a média das seções dá
  o mesmo peso a seções de 30 e de 400 eleitores). Use `AVG` só quando a pergunta for sobre a seção típica.
- **Variação absoluta depende do comparecimento.** Se a seção teve menos eleitores no 2º turno, todos podem
  "perder" votos. Para comparar preferência, mostre também `dif_pp_<candidato>`.
- **Seções pequenas geram percentuais extremos.** Para rankings em %, filtre (ex.: `validos_t1 >= 50`) e diga que filtrou.
- **Seções agregadas e urnas trocadas** (`tem_agregacao`, `urna_trocada`) podem explicar diferenças entre
  turnos. Mostre essas colunas quando listar seções individuais.
- **Divisão por zero**: use `NULLIF(denominador, 0)`.
- Na base de SP, quase todas as seções encerram às 17h; faixas como 18h e 19h têm poucas seções. Sempre
  informe o número de seções do grupo.

## Exemplos validados

Nos exemplos, `<c>` é a coluna de um candidato (ex.: `<c>_t1`, `dif_<c>`). Troque pelo nome real que aparece
em `SELECT valor FROM metadados WHERE chave='candidatos_secao_turnos'`. Trate todos os candidatos do mesmo
jeito: quando fizer uma conta para um, ofereça a mesma conta para os outros.

**"Quantos % de aumento de votos o candidato X teve nas urnas fechadas entre 17:00 e 18:00?"**
```sql
SELECT COUNT(*) AS secoes, SUM(<c>_t1) AS votos_1o, SUM(<c>_t2) AS votos_2o,
       ROUND(100.0 * (SUM(<c>_t2) - SUM(<c>_t1)) / SUM(<c>_t1), 2) AS aumento_pct
FROM secao_turnos
WHERE hora_encerramento_t2 >= '17:00' AND hora_encerramento_t2 < '18:00';
```
Interpretação: mesmas seções nos dois turnos, horário de encerramento do 2º turno. Para dar contexto, mostre a
mesma conta para todas as faixas de horário (`GROUP BY substr(hora_encerramento_t2, 1, 2)`) e para os outros
candidatos.

**"Qual a urna com mais perda de votos do candidato X?"**
```sql
SELECT nm_municipio, nr_zona, nr_secao, <c>_t1, <c>_t2, dif_<c>,
       ROUND(dif_pp_<c>, 2) AS dif_pontos_percentuais,
       comparecimento_t1, comparecimento_t2, urna_trocada, tem_agregacao
FROM secao_turnos ORDER BY dif_<c> ASC LIMIT 10;
```
Mostre também o ranking em pontos percentuais (`ORDER BY dif_pp_<c>`, com `validos_t1 >= 50 AND validos_t2 >= 50`).

**"Quantos votos um candidato que não foi ao 2º turno teve numa cidade?"**
```sql
SELECT SUM(v.qt_votos) AS votos
FROM votos v JOIN secoes s USING (turno, uf, cd_municipio, nr_zona, nr_secao)
WHERE v.turno = 1 AND v.nm_votavel = '<NOME COMO NA BASE>' AND s.nm_municipio = 'SÃO PAULO';
```
Confira a grafia com `SELECT DISTINCT nm_votavel FROM votos WHERE turno = 1`.

**"Os boletins batem por dentro?"** (o esperado é zero em todas as colunas)
```sql
SELECT turno, COUNT(*) AS secoes,
       SUM(qt_comparecimento > qt_aptos)                  AS comparecimento_maior_que_aptos,
       SUM(qt_comparecimento + qt_abstencoes <> qt_aptos) AS aptos_nao_fecha,
       SUM(qt_comparecimento <> (SELECT SUM(v.qt_votos) FROM votos v
                                 WHERE v.turno = s.turno AND v.cd_municipio = s.cd_municipio
                                   AND v.nr_zona = s.nr_zona AND v.nr_secao = s.nr_secao
                                   AND v.ds_cargo = (SELECT valor FROM metadados WHERE chave = 'cargo_secao_turnos')))
                                                          AS votos_diferente_comparecimento,
       SUM(dt_encerramento < dt_abertura)                 AS encerrou_antes_de_abrir,
       SUM(dt_emissao_bu < dt_encerramento)               AS bu_antes_do_encerramento
FROM secoes s GROUP BY turno;
```

**"Os totais conferem com o TSE?"**
```sql
SELECT turno, ds_tipo_votavel, nm_votavel, SUM(qt_votos) AS votos,
       CASE WHEN ds_tipo_votavel = 'Nominal' THEN
         ROUND(100.0 * SUM(qt_votos) / SUM(SUM(CASE WHEN ds_tipo_votavel IN ('Nominal','Legenda')
               THEN qt_votos ELSE 0 END)) OVER (PARTITION BY turno), 2) END AS pct_validos
FROM votos
WHERE ds_cargo = (SELECT valor FROM metadados WHERE chave = 'cargo_secao_turnos')
GROUP BY turno, ds_tipo_votavel, nm_votavel
ORDER BY turno, votos DESC;
```

## Gráficos

Se o usuário pedir um gráfico e você puder gerar arquivos, exporte com `--csv` e gere o gráfico a partir do
CSV. Para uma visão pronta, indique o painel: abrir `painel/index.html` no navegador.
