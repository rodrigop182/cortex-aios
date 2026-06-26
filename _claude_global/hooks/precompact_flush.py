#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
precompact_flush.py — chamado pelo hook PreCompact do Claude Code.

Quando o contexto vai ser compactado NO MEIO de uma sessão longa, o aprendizado daquele trecho
sumiria sem deixar rastro. O hook SessionEnd só dispara ao FECHAR a janela; a
compactação acontece antes. Esta é a brecha que este flush fecha.

Um hook roda shell, NÃO raciocina. Então ele NÃO destila — só deixa o RASTRO,
marcando que foi por COMPACTAÇÃO. Na sessão seguinte, a skill fecha-sessao lê
o rastro e destila com julgamento.

Reutiliza o MESMO log de pendências do registrar_sessao.py, para a fecha-sessao
achar tudo num lugar só. Marca trigger=compact para ela saber que é meio-de-sessão.

Recebe o JSON do hook no stdin (session_id, transcript_path, cwd,
compaction_trigger=auto|manual). Falha em silêncio (nunca bloqueia a compactação).
"""
import sys, json, datetime, pathlib

# CONFIGURE: ajuste este caminho na instalação.
# Aponte para a pasta memory/ do seu projeto (onde _sessions-pendentes.log ficará).
# Exemplo: r"C:\Users\SEU_USUARIO\.claude\projects\c--CORTEX\memory\_sessions-pendentes.log"
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
        trigger = data.get("compaction_trigger", "?")
        linha = (f"{agora} | FLUSH-PRECOMPACT ({trigger}) "
                 f"| sessão {data.get('session_id','?')} "
                 f"| cwd {data.get('cwd','?')} "
                 f"| transcript {data.get('transcript_path','?')}\n")
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(linha)
    except Exception:
        pass  # nunca bloquear a compactação
    # exit 0 implícito: deixa a compactação prosseguir

if __name__ == "__main__":
    main()
