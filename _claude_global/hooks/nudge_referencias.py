#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
nudge_referencias.py — hook SessionStart do Claude Code.

Mesmo padrão do nudge_destilacao.py: o hook NÃO processa, só CUTUCA. Varre a pasta de
referências configurada (PASTA, abaixo), compara com o manifesto _ingeridos.md, e se houver arquivo
que ainda não foi destilado, injeta um aviso discreto no início da sessão pedindo
para DELEGAR a ingestão a um subagente (skill ingerir-referencia), fora do contexto
principal.

Filosofia (transparente: não muta no escuro): só avisa que há referência nova;
a ingestão em si roda com julgamento, e regra de trabalho NUNCA é gravada sozinha
(só referência consultável; regra vira proposta ao operador).

Link colado no CHAT não passa por aqui (não é arquivo na pasta): esse é tratado na hora.

Imprime JSON em stdout (additionalContext). Falha em silêncio (nunca trava o início).
"""
import sys, json, pathlib

# CONFIGURE: substitua pelo caminho real da pasta onde o operador joga material de referência.
# Exemplo: r"C:\CORTEX\referencias" ou r"/home/usuario/cortex/referencias"
PASTA = pathlib.Path(r"{{PASTA_REFERENCIAS}}")

MANIFESTO = PASTA / "_ingeridos.md"

# Nomes que NUNCA contam como referência a ingerir (infra da pasta).
IGNORAR_NOMES = {"README.md", "_ingeridos.md"}


def _novos():
    """Lista os nomes de arquivo na pasta que ainda não aparecem no manifesto."""
    if not PASTA.is_dir():
        return []
    try:
        txt = MANIFESTO.read_text(encoding="utf-8") if MANIFESTO.is_file() else ""
    except Exception:
        txt = ""
    novos = []
    for p in PASTA.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(PASTA)
        # ignora infra: nomes fixos e qualquer arquivo/pasta com prefixo _ ou .
        if p.name in IGNORAR_NOMES:
            continue
        if any(part.startswith(("_", ".")) for part in rel.parts):
            continue
        # já conhecido se o nome do arquivo aparece em qualquer lugar do manifesto
        if p.name in txt:
            continue
        novos.append(p.name)
    return novos


def main():
    novos = _novos()
    if not novos:
        return
    n = len(novos)
    lista = ", ".join(novos[:8]) + (" ..." if n > 8 else "")
    msg = (
        f"[backstage] {n} referencia(s) nova(s) na pasta de referencias: {lista}. "
        "Processar em folga via subagente (skill ingerir-referencia), nao narrar."
    )
    out = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": msg,
        }
    }
    sys.stdout.write(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # nunca travar o início da sessão
