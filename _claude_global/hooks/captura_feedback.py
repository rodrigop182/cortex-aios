#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
captura_feedback.py — chamado pelo hook UserPromptSubmit do Claude Code.

Captura SILENCIOSA do feedback que o operador da conversando: acerto, erro, critica,
elogio. O ponto do CORTEX e melhorar com cada sessao sem o usuario precisar fazer
nada — e sem POLUIR o chat de trabalho dele. Este hook NAO injeta nada no contexto:
so ESCREVE no log `_feedback.log`, que e destilado DEPOIS (no fechamento ou no passe
automatico do vigia de inatividade / catch-up). Assim, mesmo que o operador nunca de
/fecha-sessao, o sinal nao se perde — o log e a fonte da verdade.

Mecanica e filosofia (backstage total): references/manutencao-backstage-arquitetura.md.

NUNCA imprime additionalContext (diferente do captura_regra, que fala so na repeticao
forte). Feedback e sempre 100% silencioso. Falha em silencio (nunca trava o turno).
"""
import sys, json, re, os, datetime

# CONFIGURE: troque {{CAMINHO_MEMORIA}} pelo caminho ABSOLUTO da pasta de memoria.
# No fork vivo ja vem resolvido.
_LOG_PATH = os.path.join(r"{{CAMINHO_MEMORIA}}", "_feedback.log")
_MAX_LINHAS = 300

# Sinais de FEEDBACK, casados sem acento e case-insensitive. Cada grupo mapeia um TIPO.
# Generoso mas tipado: a destilacao posterior decide o que vira regra/ajuste.
SINAIS = {
    "elogio": [
        r"\bgostei\b", r"\bficou (otimo|bom|massa|foda|top|perfeito|lindo|show)\b",
        r"\bperfeito\b", r"\bexatamente (isso|assim)\b", r"\bera isso\b",
        r"\bmandou bem\b", r"\bagora sim\b", r"\bisso (ai|mesmo)\b", r"\bcurti\b",
        r"\bficou (muito )?bom\b", r"\bta (otimo|perfeito|massa)\b",
    ],
    "critica": [
        r"\bnao gostei\b", r"\bta (fraco|ruim|estranho|feio|generico)\b",
        r"\bficou (fraco|ruim|estranho|feio|generico|esquisito)\b",
        r"\bnao (era|e) (isso|bem isso)\b", r"\bsem graca\b", r"\bcara de (ia|template|canva)\b",
        r"\bnao curti\b", r"\bpodia (ser|estar) melhor\b", r"\bdecepc",
    ],
    "erro": [
        r"\b(voce )?errou\b", r"\bta errado\b", r"\bnao e assim\b", r"\bquebrou\b",
        r"\bnao funciona\b", r"\bbugou\b", r"\bisso (ta|esta) errado\b",
        r"\bnao era (pra|para)\b", r"\bde novo (o |a )?mesmo erro\b", r"\brefaz\b",
    ],
    "acerto": [
        r"\bfunciona(ndo|u)?\b.*\bagora\b", r"\bresolveu\b", r"\bdeu certo\b",
        r"\bagora (foi|funcionou|vai)\b", r"\bisso resolveu\b",
    ],
}

def _normaliza(txt):
    try:
        import unicodedata
        txt = "".join(c for c in unicodedata.normalize("NFD", txt)
                      if unicodedata.category(c) != "Mn")
    except Exception:
        pass
    return txt.lower()

def _gravar(tipo, trecho):
    try:
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        # trecho curto, sem quebra de linha, pra 1 linha por evento
        trecho = re.sub(r"\s+", " ", trecho).strip()[:160]
        linha = f"{ts}\t{tipo}\t{trecho}"
        os.makedirs(os.path.dirname(_LOG_PATH), exist_ok=True)
        # Append atomico: duas janelas simultaneas nao se sobrescrevem.
        # O OS garante atomicidade pra linhas curtas em modo "a".
        with open(_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(linha + "\n")
        _podar_se_preciso(_LOG_PATH, _MAX_LINHAS)
    except Exception:
        pass

def _podar_se_preciso(path, max_linhas):
    """Reescreve o log mantendo as ultimas max_linhas — so roda quando o arquivo
    passar de 2x o limite, pra minimizar a janela de colisao entre processos."""
    try:
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as f:
            linhas = [l.rstrip("\n") for l in f.readlines()]
        if len(linhas) <= 2 * max_linhas:
            return
        linhas = linhas[-max_linhas:]
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(linhas) + "\n")
    except Exception:
        pass

def main():
    raw = sys.stdin.read()
    if not raw.strip():
        return
    try:
        prompt = json.loads(raw).get("prompt", "") or ""
    except Exception:
        prompt = raw
    if not prompt.strip():
        return

    # Ignora ENVELOPES DE SISTEMA (task-notification, system-reminder, local-command,
    # command-name, ide_selection, etc.): chegam via UserPromptSubmit mas NAO sao feedback
    # do usuario. Comecam todos com '<tag>'; humano em PT-BR nao abre mensagem com '<'.
    # Sem este guard o log enche de '<task-notification>' classificado como 'elogio'.
    if prompt.lstrip().startswith("<"):
        return

    alvo = _normaliza(prompt)
    # registra o PRIMEIRO tipo que casar (um evento por prompt; ordem: erro/critica
    # tem prioridade sobre elogio/acerto se ambos aparecerem, pra nao perder o negativo)
    for tipo in ("erro", "critica", "acerto", "elogio"):
        if any(re.search(p, alvo) for p in SINAIS[tipo]):
            _gravar(tipo, prompt)
            break
    # NUNCA injeta additionalContext: feedback e 100% silencioso (backstage).

if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
