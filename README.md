# Perguntas aos boletins de urna

Faça perguntas em português sobre os boletins de urna do TSE a uma IA (Claude ou ChatGPT) e receba a resposta
**junto com a consulta que a produziu**, para qualquer pessoa conferir.

> *"Quantos % de aumento de votos cada candidato teve nas urnas que encerraram entre 17:00 e 18:00?"*
> *"Qual seção teve a maior perda de votos de um candidato entre o 1º e o 2º turno?"*
> *"Os totais batem com o resultado oficial?"*

Você não precisa saber programar. São quatro passos:

1. [Baixe este projeto](#1-baixe-este-projeto)
2. [Baixe os boletins de urna](#2-baixe-os-boletins-de-urna) e coloque na pasta `boletins/`
3. [Abra a pasta no Claude ou no ChatGPT](#3-abra-a-pasta-no-claude-ou-no-chatgpt)
4. [Pergunte](#4-pergunte)

---

## 1. Baixe este projeto

Nesta página do GitHub, clique no botão verde **Code** → **Download ZIP**. Extraia o ZIP numa pasta do seu
computador (por exemplo, `Documentos\urna-perguntas`).

## 2. Baixe os boletins de urna

Os boletins são publicados pelo TSE no
[Portal de Dados Abertos — Resultados 2026 — Boletim de Urna](https://dadosabertos.tse.jus.br/dataset/resultados-2026-boletim-de-urna).
Baixe o **1º e o 2º turno** do estado que quer analisar e **coloque os arquivos na pasta `boletins/`** do
projeto. Não precisa extrair o ZIP.

| UF | Estado | 1º turno (4/out/2026) | 2º turno (25/out/2026) |
|---|---|---|---|
| AC | Acre | [bweb_1t_AC_051020261403.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_1t_AC_051020261403.zip) | [bweb_2t_AC_261020260742.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_2t_AC_261020260742.zip) |
| AL | Alagoas | [bweb_1t_AL_051020261403.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_1t_AL_051020261403.zip) | [bweb_2t_AL_261020260742.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_2t_AL_261020260742.zip) |
| AM | Amazonas | [bweb_1t_AM_051020261403.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_1t_AM_051020261403.zip) | [bweb_2t_AM_261020260742.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_2t_AM_261020260742.zip) |
| AP | Amapá | [bweb_1t_AP_051020261403.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_1t_AP_051020261403.zip) | [bweb_2t_AP_261020260742.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_2t_AP_261020260742.zip) |
| BA | Bahia | [bweb_1t_BA_051020261403.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_1t_BA_051020261403.zip) | [bweb_2t_BA_261020260742.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_2t_BA_261020260742.zip) |
| CE | Ceará | [bweb_1t_CE_051020261403.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_1t_CE_051020261403.zip) | [bweb_2t_CE_261020260742.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_2t_CE_261020260742.zip) |
| DF | Distrito Federal | [bweb_1t_DF_051020261403.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_1t_DF_051020261403.zip) | [bweb_2t_DF_261020260742.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_2t_DF_261020260742.zip) |
| ES | Espírito Santo | [bweb_1t_ES_051020261403.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_1t_ES_051020261403.zip) | [bweb_2t_ES_261020260742.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_2t_ES_261020260742.zip) |
| GO | Goiás | [bweb_1t_GO_051020261403.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_1t_GO_051020261403.zip) | [bweb_2t_GO_261020260742.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_2t_GO_261020260742.zip) |
| MA | Maranhão | [bweb_1t_MA_051020261403.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_1t_MA_051020261403.zip) | [bweb_2t_MA_261020260742.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_2t_MA_261020260742.zip) |
| MG | Minas Gerais | [bweb_1t_MG_051020261403.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_1t_MG_051020261403.zip) | [bweb_2t_MG_261020260742.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_2t_MG_261020260742.zip) |
| MS | Mato Grosso do Sul | [bweb_1t_MS_051020261403.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_1t_MS_051020261403.zip) | [bweb_2t_MS_261020260742.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_2t_MS_261020260742.zip) |
| MT | Mato Grosso | [bweb_1t_MT_051020261403.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_1t_MT_051020261403.zip) | [bweb_2t_MT_261020260742.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_2t_MT_261020260742.zip) |
| PA | Pará | [bweb_1t_PA_051020261403.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_1t_PA_051020261403.zip) | [bweb_2t_PA_261020260742.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_2t_PA_261020260742.zip) |
| PB | Paraíba | [bweb_1t_PB_051020261403.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_1t_PB_051020261403.zip) | [bweb_2t_PB_261020260742.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_2t_PB_261020260742.zip) |
| PE | Pernambuco | [bweb_1t_PE_051020261403.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_1t_PE_051020261403.zip) | [bweb_2t_PE_261020260742.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_2t_PE_261020260742.zip) |
| PI | Piauí | [bweb_1t_PI_051020261403.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_1t_PI_051020261403.zip) | [bweb_2t_PI_261020260742.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_2t_PI_261020260742.zip) |
| PR | Paraná | [bweb_1t_PR_051020261403.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_1t_PR_051020261403.zip) | [bweb_2t_PR_261020260742.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_2t_PR_261020260742.zip) |
| RJ | Rio de Janeiro | [bweb_1t_RJ_051020261403.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_1t_RJ_051020261403.zip) | [bweb_2t_RJ_261020260742.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_2t_RJ_261020260742.zip) |
| RN | Rio Grande do Norte | [bweb_1t_RN_051020261403.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_1t_RN_051020261403.zip) | [bweb_2t_RN_261020260742.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_2t_RN_261020260742.zip) |
| RO | Rondônia | [bweb_1t_RO_051020261403.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_1t_RO_051020261403.zip) | [bweb_2t_RO_261020260742.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_2t_RO_261020260742.zip) |
| RR | Roraima | [bweb_1t_RR_051020261403.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_1t_RR_051020261403.zip) | [bweb_2t_RR_261020260742.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_2t_RR_261020260742.zip) |
| RS | Rio Grande do Sul | [bweb_1t_RS_051020261403.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_1t_RS_051020261403.zip) | [bweb_2t_RS_261020260742.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_2t_RS_261020260742.zip) |
| SC | Santa Catarina | [bweb_1t_SC_051020261403.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_1t_SC_051020261403.zip) | [bweb_2t_SC_261020260742.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_2t_SC_261020260742.zip) |
| SE | Sergipe | [bweb_1t_SE_051020261403.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_1t_SE_051020261403.zip) | [bweb_2t_SE_261020260742.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_2t_SE_261020260742.zip) |
| SP | São Paulo | [bweb_1t_SP_051020261403.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_1t_SP_051020261403.zip) | [bweb_2t_SP_261020260742.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_2t_SP_261020260742.zip) |
| TO | Tocantins | [bweb_1t_TO_051020261403.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_1t_TO_051020261403.zip) | [bweb_2t_TO_261020260742.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_2t_TO_261020260742.zip) |
| ZZ | Exterior | [bweb_1t_ZZ_051020261403.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_1t_ZZ_051020261403.zip) | [bweb_2t_ZZ_261020260742.zip](https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_2t_ZZ_261020260742.zip) |

- Os arquivos do 1º turno são grandes porque trazem todos os cargos (SP extraído tem cerca de 8 GB). O projeto
  usa só as linhas de Presidente.
- Pode colocar vários estados ao mesmo tempo. Não misture eleições de anos diferentes na mesma pasta.
- Se algum link não abrir, procure o arquivo na [página do conjunto de dados](https://dadosabertos.tse.jus.br/dataset/resultados-2026-boletim-de-urna).
  Outras eleições: [2022](https://dadosabertos.tse.jus.br/dataset/resultados-2022-boletim-de-urna),
  [2024 (municipal)](https://dadosabertos.tse.jus.br/dataset/resultados-2024-boletim-de-urna).
- O TSE publica, ao lado de cada `.zip`, um arquivo `.zip.sha512` com o resumo criptográfico (hash) do
  arquivo, para conferir que o download não foi alterado. No Windows o hash do seu arquivo sai com
  `certutil -hashfile bweb_1t_SP_051020261403.zip SHA512`.

A pasta fica assim:

```
urna-perguntas/
├── boletins/
│   ├── bweb_1t_SP_051020261403.zip
│   └── bweb_2t_SP_261020260742.zip
├── AGENTS.md
├── README.md
└── ...
```

## 3. Abra a pasta no Claude ou no ChatGPT

**Claude:** no aplicativo do Claude para computador, inicie uma conversa e **associe a pasta `urna-perguntas`**
(o botão de adicionar pasta na caixa de mensagem). O Claude roda os comandos sozinho, num ambiente próprio que
já tem Python; no nosso teste não foi preciso instalar nada.

**ChatGPT:** no aplicativo do ChatGPT para computador (Codex), escolha a pasta `urna-perguntas` como projeto,
no modo **Local**. Nesse caso os comandos rodam no seu computador, então é preciso ter o
[Python](https://www.python.org/downloads/) instalado (no Windows, marque *"Add Python to PATH"* na instalação).

**Outros assistentes que trabalham numa pasta** (Claude Code, Codex CLI, Cursor, Gemini CLI) funcionam do
mesmo jeito: eles leem o arquivo `AGENTS.md`, que explica tudo o que precisam saber.

## 4. Pergunte

Na primeira mensagem, peça:

> **Leia o AGENTS.md, prepare os dados dos boletins e me mostre o resumo.**

A IA vai processar os boletins (cerca de 1 minuto para SP) e mostrar os totais por candidato.
**Compare esses totais com o resultado oficial do TSE** antes de seguir. Depois é só perguntar, por exemplo:

- Quantos % de aumento de votos cada candidato teve nas urnas que encerraram entre 17:00 e 18:00?
- Qual seção teve a maior perda de votos de cada candidato entre os turnos? E em pontos percentuais?
- Como votou a cidade de Campinas no 2º turno, comparado ao 1º?
- Em quais seções a urna foi trocada entre os turnos, e o resultado delas é diferente das outras?
- Os boletins são consistentes por dentro (comparecimento, soma de votos, horários)?
- Faça um gráfico do percentual de cada candidato pela hora em que o boletim chegou ao TSE.

Toda resposta deve trazer a consulta SQL usada. Se não trouxer, peça: *"mostre a SQL"*.

---

## Painel visual (sem IA)

Depois que a IA preparar os dados, abra o arquivo `painel/index.html` com duplo clique. Ele funciona no
navegador, sem internet, e mostra:
- o percentual de cada candidato e a variação entre turnos;
- o aumento de votos por faixa de horário de encerramento ou de chegada do boletim;
- a curva da apuração acumulada;
- a distribuição da variação por seção e as seções com maior perda.

Tudo pode ser filtrado por município.

## Como conferir que os números são confiáveis

- **Os boletins são os oficiais:** confira o hash do `.zip` baixado com o `.zip.sha512` do TSE (passo 2).
- **A importação não perdeu nada:** o resumo impresso pelo `preparar.py` deve bater com o resultado oficial.
  Ele também grava o sha256 de cada CSV lido (pergunte à IA: *"de quais arquivos vieram os dados?"*).
- **Cada boletim é consistente por dentro:** pergunte à IA *"os boletins batem por dentro?"*. Ela roda a checagem descrita no `AGENTS.md`.
- **A IA não inventou:** toda resposta traz a SQL. Outra pessoa pode rodar a mesma consulta e chegar ao mesmo número.

## Limitações e cuidados

- A base tem o que está no boletim de urna: votos por seção, horários, número da urna. Não tem dados de
  eleitores individuais nem os logs internos das urnas.
- "Urna" aqui é a seção eleitoral. Seções agregadas (várias seções numa urna) e urnas substituídas
  aparecem nas colunas `tem_agregacao` e `urna_trocada`.
- Diferenças entre grupos de seções (por horário, por região) costumam refletir o perfil dos locais de
  votação. Elas não indicam irregularidade por si só. Compare sempre com os outros grupos.
- A IA pode errar a consulta. Por isso a SQL aparece junto da resposta: confira ou peça para outra pessoa conferir.

---

## Para quem quer usar sem IA ou integrar em outras ferramentas

Tudo funciona com Python 3.8+ e nada mais (só a biblioteca padrão):

```bash
python preparar.py                      # lê boletins/ e cria dados/eleicao.sqlite + painel/dados.js
python preparar.py --cargo Governador   # outro cargo
python consultar.py --esquema           # tabelas e colunas
python consultar.py "SELECT nm_municipio, COUNT(*) AS secoes FROM secao_turnos GROUP BY 1 ORDER BY 2 DESC LIMIT 10"
python consultar.py --arquivo minha_consulta.sql
```

**Claude Desktop via MCP:** o `mcp_server.py` expõe as ferramentas `guia`, `esquema` e `consultar_sql`.
Adicione ao `claude_desktop_config.json` (no Windows: `%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "boletins-urna": {
      "command": "python",
      "args": ["C:/caminho/para/urna-perguntas/mcp_server.py"]
    }
  }
}
```

### Estrutura

```
boletins/          coloque aqui os .zip/.csv do TSE (não vão para o GitHub)
preparar.py        boletins → dados/eleicao.sqlite + painel/dados.js
consultar.py       roda SQL somente-leitura e imprime uma tabela (ou salva CSV)
mcp_server.py      servidor MCP (Claude Desktop e outros clientes MCP)
AGENTS.md          manual para a IA: primeiros passos, tabelas, definições, armadilhas, exemplos
CLAUDE.md          aponta para o AGENTS.md
painel/index.html  painel visual offline
```

## Licença

Código sob licença MIT. Os dados são públicos, publicados pelo TSE.
