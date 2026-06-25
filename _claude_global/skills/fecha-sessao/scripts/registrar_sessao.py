#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
registrar_sessao.py — chamado pelo hook SessionEnd do Claude Code.

NAO destila nada (um hook roda shell, nao raciocina). Ele so deixa um RASTRO:
anexa uma linha em memory/_sessions-pendentes.log com data + caminho do transcript
da sessao que acabou. Na sessao seguinte, o Claude le esse arquivo e destila as
regras do dia (ver SKILL.md de fecha-sessao).

Recebe o JSON do hook no stdin (session_id, transcript_path, cwd, reason...).
Falha em silencio (nunca trava o fim da sessao).

CONFIGURACAO: ajuste LOG abaixo para o caminho real do seu memory/_sessions-pendentes.log.
Padrao: ~/.claude/projects/<id-do-projeto>/memory/_sessions-pendentes.log
"""
import sys, json, datetime, pathlib

# CONFIGURE: troque {{CAMINHO_MEMORIA}} pelo caminho ABSOLUTO da sua pasta de memoria
# (a mesma do captura_regra), ex: C:\Users\voce\.claude\projects\<id>\memory
# O instalador resolve esse placeholder; sem isso o loop de aprendizado quebra silencioso.
LOG = pathlib.Path(
    r"{{CAMINHO_MEMORIA}}\_sessions-pendentes.log"
)

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        linha = (f"{agora} | sessao {data.get('session_id','?')} "
                 f"| cwd {data.get('cwd','?')} "
                 f"| transcript {data.get('transcript_path','?')}\n")
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(linha)
    except Exception:
        pass  # nunca travar o encerramento

if __name__ == "__main__":
    main()
