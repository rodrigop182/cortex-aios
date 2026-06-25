#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
detectar_handoff.py — chamado pelo hook SessionStart do Claude Code.

Verifica se ha algum briefing de handoff em handoff-session/. Se houver, injeta no
contexto da sessao nova um aviso curto apontando os arquivos disponiveis, pra o Claude
saber DE PRIMEIRA que existe handoff — sem tropecar procurando _sessions-pendentes.log
(isso e da skill fecha-sessao, outra coisa).

IMPORTANTE: o aviso NAO manda retomar a tarefa. Retomar e so sob pedido do operador
("continua de onde paramos", "le o handoff"). O hook so garante que, quando ele pedir,
o Claude va direto ao arquivo certo em vez de adivinhar — e que a retomada seja
SILENCIOSA (nao narrar a conferencia de estado; entregar so o resultado).

Imprime JSON em stdout no formato que o SessionStart espera (additionalContext).
Falha em silencio (nunca trava o inicio da sessao).
"""
import sys, json, pathlib

# pasta de handoffs, relativa a este script: handoff/scripts/ -> handoff/handoff-session/
HANDOFF_DIR = pathlib.Path(__file__).resolve().parent.parent / "handoff-session"

def main():
    try:
        mds = [p for p in HANDOFF_DIR.glob("handoff-*.md")] if HANDOFF_DIR.is_dir() else []
    except Exception:
        mds = []

    if not mds:
        return  # nada a injetar; sessao limpa

    # ordena do mais recente pro mais antigo (nome handoff-AAAA-MM-DD-... + mtime de desempate)
    mds_ord = sorted(mds, key=lambda p: (p.name, p.stat().st_mtime), reverse=True)

    if len(mds_ord) == 1:
        contexto = (
            f"HANDOFF DISPONIVEL: existe 1 briefing de sessao anterior em "
            f"'{mds_ord[0].as_posix()}'. Se o operador pedir para continuar de onde paramos "
            "(ou citar a tarefa anterior), leia ESTE arquivo PRIMEIRO e retome do 'proximo "
            "passo', respeitando decisoes e armadilhas. RETOMADA E SILENCIOSA: nao anuncie que "
            "vai conferir o estado/bater com o handoff; se precisar checar o disco, faca em "
            "SEGUNDO PLANO e entregue so o resultado (onde paramos + proxima acao), sem despejar "
            "comandos nem diagnostico longo. Se ele abrir assunto novo, ignore o handoff e nao o "
            "mencione. NAO confundir com _sessions-pendentes.log (isso e da skill fecha-sessao)."
        )
    else:
        lista = "; ".join(p.as_posix() for p in mds_ord)
        contexto = (
            f"HANDOFFS DISPONIVEIS ({len(mds_ord)}), do mais recente ao mais antigo: {lista}. "
            "Se o operador pedir para continuar de onde paramos, roteie pela skill continuar-sessao: "
            "por ASSUNTO (handoff que casa com o que ele disse) ou por RECENCIA (o de maior mtime "
            "que seja TRABALHO dele, pulando os de infra/manutencao). Va DIRETO; nao leia o 'Foco' "
            "de todos nem pergunte, EXCETO em empate real (2+ no mesmo minuto) ou se a pista nao "
            "casar com nenhum. RETOMADA E SILENCIOSA: nao anuncie que vai conferir o estado/bater "
            "com o handoff; se precisar checar o disco (divergencia ao ler), faca em SEGUNDO PLANO "
            "e entregue so o resultado consolidado (2-4 linhas), sem despejar comandos nem "
            "diagnostico longo no chat. Se ele abrir assunto novo, ignore todos e nao mencione. "
            "Handoff cuja tarefa voce sabe que ja foi resolvida nao deve estar aqui: ver a skill "
            "handoff (limpeza). NAO confundir com _sessions-pendentes.log (isso e da skill fecha-sessao)."
        )

    out = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": contexto,
        }
    }
    sys.stdout.write(json.dumps(out, ensure_ascii=False))

if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # nunca travar o inicio da sessao
