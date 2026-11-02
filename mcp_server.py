#!/usr/bin/env python3
"""
mcp_server.py - servidor MCP (stdio) que deixa um assistente de IA consultar a base
de boletins de urna. Somente leitura. Usa apenas a biblioteca padrao do Python.

Ferramentas expostas:
  guia           - devolve o AGENTS.md (definicoes e regras de analise)
  esquema        - tabelas, colunas, candidatos e arquivos de origem
  consultar_sql  - roda um SELECT na base e devolve o resultado + a propria consulta

Configuracao no Claude Desktop (claude_desktop_config.json):
  {
    "mcpServers": {
      "boletins-urna": {
        "command": "python",
        "args": ["C:/caminho/para/urna-perguntas/mcp_server.py"]
      }
    }
  }
"""
import json
import os
import sqlite3
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import consultar  # noqa: E402

VERSAO_PROTOCOLO = "2025-06-18"
MAX_LINHAS = 500

FERRAMENTAS = [
    {
        "name": "guia",
        "description": "Leia ANTES de responder qualquer pergunta: definicoes (o que e 'aumento', 'perda', 'urna'), "
                       "armadilhas conhecidas e exemplos de SQL validados para os boletins de urna.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "esquema",
        "description": "Lista as tabelas e colunas da base de boletins de urna, os candidatos e os arquivos de origem (com sha256).",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "consultar_sql",
        "description": "Executa uma consulta SQL (dialeto SQLite, somente leitura) na base de boletins de urna. "
                       "Sempre mostre ao usuario a consulta usada junto com a resposta.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sql": {"type": "string", "description": "consulta SELECT/WITH em SQLite"},
                "max_linhas": {"type": "integer", "description": f"linhas a devolver (padrao 100, max {MAX_LINHAS})"},
            },
            "required": ["sql"],
        },
    },
]


def texto(t, erro=False):
    return {"content": [{"type": "text", "text": t}], "isError": erro}


def chamar(nome, args):
    if nome == "guia":
        with open(os.path.join(AQUI, "AGENTS.md"), encoding="utf-8") as f:
            return texto(f.read())
    con = consultar.conectar()
    try:
        if nome == "esquema":
            return texto(consultar.esquema(con))
        if nome == "consultar_sql":
            sql = args.get("sql", "")
            maximo = max(1, min(int(args.get("max_linhas", 100)), MAX_LINHAS))
            try:
                cab, linhas, cortado = consultar.executar(con, sql, maximo)
            except sqlite3.Error as e:
                return texto(f"Erro SQL: {e}\n\nConsulta:\n{sql}", erro=True)
            aviso = f"\n(resultado cortado em {maximo} linhas)" if cortado else ""
            return texto(f"Consulta:\n```sql\n{sql.strip()}\n```\n\n{consultar.tabela(cab, linhas)}\n"
                         f"({len(linhas)} linha(s)){aviso}")
        return texto(f"Ferramenta desconhecida: {nome}", erro=True)
    finally:
        con.close()


def responder(msg):
    metodo = msg.get("method")
    if metodo == "initialize":
        pedida = msg.get("params", {}).get("protocolVersion", VERSAO_PROTOCOLO)
        return {
            "protocolVersion": pedida,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "boletins-urna", "version": "0.1.0"},
            "instructions": "Base de boletins de urna do TSE. Chame 'guia' antes de responder e mostre sempre a SQL usada.",
        }
    if metodo == "ping":
        return {}
    if metodo == "tools/list":
        return {"tools": FERRAMENTAS}
    if metodo == "tools/call":
        p = msg.get("params", {})
        return chamar(p.get("name"), p.get("arguments") or {})
    raise KeyError(metodo)


def main():
    # no Windows o padrao do console nao e UTF-8; o protocolo MCP exige UTF-8
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    for linha in sys.stdin:
        linha = linha.strip()
        if not linha:
            continue
        try:
            msg = json.loads(linha)
        except json.JSONDecodeError:
            continue
        if "id" not in msg:  # notificacao (ex.: notifications/initialized)
            continue
        try:
            resp = {"jsonrpc": "2.0", "id": msg["id"], "result": responder(msg)}
        except KeyError:
            resp = {"jsonrpc": "2.0", "id": msg["id"], "error": {"code": -32601, "message": "metodo nao suportado"}}
        except SystemExit as e:
            resp = {"jsonrpc": "2.0", "id": msg["id"], "result": texto(str(e), erro=True)}
        except Exception as e:  # nunca derrubar o servidor
            resp = {"jsonrpc": "2.0", "id": msg["id"], "result": texto(f"Erro: {e}", erro=True)}
        sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
