#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
guarda_tamanho_memoria.py — chamado pelo hook SessionStart do Claude Code.

FREIO ESTRUTURAL do indice fino. O MEMORY.md (auto-memoria) e lido todo turno, mas
o Claude Code so carrega ~24.4KB dele: o que passa disso fica INVISIVEL ao modelo —
inclusive regras gravadas recentemente. Sem um freio, o arquivo reestoura em semanas
e volta a truncar silencioso, quebrando a promessa de "nunca explicar 2x" no elo da
RECUPERACAO.

Faz DUAS medicoes (FASE 5 — auto-manutencao):
  1) BYTES: se passar do limiar, avisa pra enxugar.
  2) FAMILIA INCHADA: conta as linhas-item ("- [") por secao "##". Familia com muitas
     entradas INDIVIDUAIS (nao consolidadas) e o sinal de que cresceu LINEAR e pede
     consolidacao num bloco tematico (varios ponteiros por linha) — e o mecanismo que
     mantem o indice crescendo com o nº de TEMAS (finito), nao de REGRAS (infinito).
     Ver references/auto-manutencao-memoria.md.

Este hook NAO poda nem consolida sozinho (principio 6: transparente, nao muta no escuro).
So MEDE e, no limiar, injeta um aviso curto pro Claude agir com julgamento. Mesma
filosofia do nudge_destilacao: cutuca, nao executa.

Imprime JSON em stdout (additionalContext). Falha em silencio (nunca trava o inicio).
"""
import sys, json, re, os, pathlib

# CONFIGURE: troque {{CAMINHO_MEMORIA}} pelo caminho ABSOLUTO da pasta de memoria
# (a mesma do captura_regra / fecha-sessao). O instalador resolve esse placeholder.
MEMORY = pathlib.Path(os.path.join(r"{{CAMINHO_MEMORIA}}", "MEMORY.md"))

# Teto REAL de carregamento do Claude Code (~24.4KB). O que passa disso nao e lido.
TETO = 24400
# Limiar de alerta: avisa ANTES de estourar, com margem pra agir sem perder nada.
LIMIAR_ALERTA = 23000
# Limiar de familia inchada: nº de linhas-item INDIVIDUAIS numa mesma secao "##".
# Acima disso, a familia pede consolidacao em bloco tematico. Calibrado ACIMA do
# nucleo de conducao ja consolidado (~19 regras heterogeneas, sem sub-tema extraivel):
# nao alarma o estado saudavel, avisa so quando uma familia volta a inflar.
LIMIAR_FAMILIA = 22


def _familia_mais_inchada(texto):
    """Conta linhas-item ('- [') por secao '## '. Retorna (nome, n) da maior, ou None.
    Linhas de bloco condensado ('- **Tema:**' com varios links) contam como 1 — e o
    objetivo: familia ja consolidada nao dispara; familia com muitos itens soltos sim."""
    secao, n = None, 0
    pior_nome, pior_n = None, 0
    for linha in texto.splitlines():
        m = re.match(r"^##\s+(.+)", linha)
        if m:
            if secao and n > pior_n:
                pior_nome, pior_n = secao, n
            secao, n = m.group(1).strip(), 0
        elif secao and re.match(r"^-\s*\[", linha):  # so item de topo, nao sub-bullet indentado
            n += 1
    if secao and n > pior_n:
        pior_nome, pior_n = secao, n
    return (pior_nome, pior_n) if pior_nome else None


def main():
    try:
        if not MEMORY.exists():
            return
        texto = MEMORY.read_text(encoding="utf-8")
        bytes_atuais = len(texto.encode("utf-8"))
    except Exception:
        return

    avisos = []
    kb = bytes_atuais / 1024.0

    # 1) BYTES
    if bytes_atuais >= TETO:
        avisos.append(
            f"CRITICO: MEMORY.md em {kb:.1f}KB, passou do teto (~24.4KB) — fim do "
            "indice invisivel. Enxugar (consolidar familia em bloco tematico) antes de confiar no indice."
        )
    elif bytes_atuais >= LIMIAR_ALERTA:
        avisos.append(
            f"MEMORY.md em {kb:.1f}KB, perto do teto (~24.4KB). Vale consolidar uma familia logo."
        )

    # 2) FAMILIA INCHADA (independe do tamanho total — pega o crescimento linear cedo)
    inchada = _familia_mais_inchada(texto)
    if inchada and inchada[1] > LIMIAR_FAMILIA:
        avisos.append(
            f"familia '{inchada[0]}' com {inchada[1]} entradas soltas (> {LIMIAR_FAMILIA}) — "
            "candidata a consolidar num bloco tematico (varios ponteiros por linha)."
        )

    if not avisos:
        return  # dentro do saudavel, nao incomoda

    out = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": "[backstage] " + " | ".join(avisos),
        }
    }
    sys.stdout.write(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # nunca travar o inicio
