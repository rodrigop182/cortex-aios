#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
nudge_destilacao.py — chamado pelo hook SessionStart do Claude Code.

Fecha o loop de aprendizado sem depender do `claude` CLI headless. Em vez de
um subagente headless, o nudge vira CONTEXTO injetado no
início da sessão: se há sessões acumuladas na fila de pendentes, o Claude é
avisado DE PRIMEIRA e sugere destilar.

Mesma filosofia do detectar_handoff.py (hook injeta nudge, não raciocina) e
do princípio 6 (transparente, não muta no escuro): NÃO destila sozinho, só
cutuca. A destilação em si continua sendo a skill fecha-sessao, rodada com
julgamento.

Só cutuca a partir de um PISO (LIMIAR linhas) para não incomodar a cada
sessão por 1 pendência. Conta tanto sessões normais quanto marcadores
FLUSH-PRECOMPACT.

Imprime JSON em stdout (additionalContext). Falha em silêncio (nunca trava o início).
"""
import sys, json, pathlib

# CONFIGURE: ajuste estes caminhos na instalação.
# Aponte para a pasta memory/ do seu projeto CORTEX OS.
# Exemplo: r"C:\Users\SEU_USUARIO\.claude\projects\c--CORTEX\memory\_sessions-pendentes.log"
LOG = pathlib.Path(
    r"{{CAMINHO_MEMORIA}}\_sessions-pendentes.log"
)

# CONFIGURE: ajuste este caminho se o log de conflito de sync também for relevante.
# Exemplo: r"C:\Users\SEU_USUARIO\.claude\projects\c--CORTEX\memory\_sync-conflito.log"
CONFLITO = pathlib.Path(
    r"{{CAMINHO_MEMORIA}}\_sync-conflito.log"
)

# Só cutuca quando o backlog passa disto (evita spam por 1-2 pendências triviais).
# 3 = boa calibragem: destilação roda em subagente fora do contexto, custa pouco;
# segurar até 5 represa o aprendizado.
LIMIAR = 3

def _bloco_conflito():
    """Se o sync deixou um conflito sem mesclar, devolve aviso para resolver. Senão, ''."""
    try:
        if not CONFLITO.is_file():
            return ""
        linhas = [l for l in CONFLITO.read_text(encoding="utf-8").splitlines() if l.strip()]
        if not linhas:
            return ""
    except Exception:
        return ""
    return (
        f"[backstage] CONFLITO DE SYNC PENDENTE ({len(linhas)}): duas janelas editaram a mesma "
        "regra e o auto-sync nao mesclou. Resolver antes do trabalho novo (git fetch + diff + merge + push; "
        "depois esvaziar memory/_sync-conflito.log)."
    )

def _bloco_destilacao():
    """Aviso de destilação pendente, se o backlog passou do limiar. Senão, ''."""
    try:
        if not LOG.is_file():
            return ""
        # Filtra comentarios (#) e linhas vazias: senao um cabecalho de bootstrap no log
        # faz o nudge contar comentario como sessao e disparar pra sempre (bug do vivo 21/06).
        linhas = [
            l for l in LOG.read_text(encoding="utf-8").splitlines()
            if l.strip() and not l.lstrip().startswith("#")
        ]
    except Exception:
        return ""
    n = len(linhas)
    if n < LIMIAR:
        return ""  # backlog pequeno; não incomodar
    flushes = sum(1 for l in linhas if "FLUSH-PRECOMPACT" in l)
    detalhe = f" ({flushes} por compactação no meio de sessão)" if flushes else ""
    return (
        f"[backstage] {n} sessao(es) na fila de destilacao{detalhe}. "
        "Destilar em folga via subagente (skill fecha-sessao), nao agora no meio do trabalho."
    )

def main():
    # conflito primeiro (mais urgente: dado em risco), destilação depois
    partes = [b for b in (_bloco_conflito(), _bloco_destilacao()) if b]
    if not partes:
        return
    out = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": "\n\n".join(partes),
        }
    }
    sys.stdout.write(json.dumps(out, ensure_ascii=False))

if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # nunca travar o início da sessão
