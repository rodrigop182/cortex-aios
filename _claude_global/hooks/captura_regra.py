#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
captura_regra.py — chamado pelo hook UserPromptSubmit do Claude Code.

Fecha o furo "pedi uma regra e passou batido". A destilacao (fecha-sessao) e
RETROATIVA: so pega o aprendizado depois, no fim da sessao, e so se a sessao
for marcada. Quando o operador da uma regra ou preferencia DURAVEL no meio da
conversa ("sempre faz X", "nunca Y", "de agora em diante Z"), gravar na hora
nao pode depender so do modelo lembrar — e o que falha.

Este hook NAO raciocina (hook = shell, nao pensa). Ele so detecta SINAIS de que
o prompt CARREGA uma regra/preferencia duravel e injeta um lembrete pro Claude
AVALIAR se vale gravar AGORA. Mesma filosofia do nudge_destilacao e do
detectar_handoff: cutuca, nao executa. A decisao de gravar (e o discernimento
"isso e regra duravel ou so um pedido pontual?") fica com o Claude, que tem o
contexto. O hook so garante que a chance de gravar nao passe despercebida.

Falso-positivo e barato (o Claude le, conclui "isso nao e regra" e ignora numa
linha). Falso-negativo e caro (a regra some). Por isso o gatilho e generoso mas
o lembrete deixa claro que e pra AVALIAR, nao gravar cego.

DETECTOR DE REPETICAO: quando o mesmo tipo de pedido ja apareceu antes (>=2x),
o aviso e REFORCADO — candidato de ALTA prioridade a virar regra AGORA.
O historico vive no _regras-detectadas.log da pasta de memoria (ultimas 200 linhas).

Imprime JSON em stdout (additionalContext). Falha em silencio (nunca trava o turno).
"""
import sys, json, re, os, hashlib

# Sinais de que o prompt pode conter uma REGRA / PREFERENCIA DURAVEL (nao um
# pedido pontual). Sao gatilhos de linguagem, casados sem acento e case-insensitive
# (o operador pode ditar por voz e a transcricao varia). Generoso de proposito:
# melhor cutucar a mais do que perder a regra.
GATILHOS = [
    r"\bsempre\b",
    r"\bnunca\b",
    r"\bde agora em diante\b",
    r"\bde hoje em diante\b",
    r"\ba partir de agora\b",
    r"\ba partir de hoje\b",
    r"\bdaqui (pra|para) frente\b",
    r"\bdaqui (pra|para) (a )?frente\b",
    r"\bdaqui em diante\b",
    r"\bnao faz assim\b",
    r"\bnao faca assim\b",
    r"\bnao faca mais\b",
    r"\bnao faz mais\b",
    r"\bpara de (fazer|faze|usar|usa|por|botar|colocar|me)\b",
    r"\bpara com (isso|essa|esse)\b",
    r"\bnao e (pra|para) (voce )?faz",
    r"\bpode (sempre|gravar|lembrar)\b",
    r"\bpode faz(er)? (direto|sozinho|sem)\b",
    r"\bpode (ir|seguir) direto\b",
    r"\bnao precisa (perguntar|pedir|me avisar|confirmar)\b",
    r"\bnao precisa (mais )?(ficar )?(perguntando|pedindo)\b",
    r"\b(grava|guarda|lembra|memoriza|anota) (essa|isso|esse|essa regra|isso ai)\b",
    r"\bquero que (voce )?(sempre|nunca|de agora)\b",
    r"\bprefiro que\b",
    r"\bda proxima vez\b",
    r"\btoda vez que\b",
    r"\bnao quero que (voce )?(faca|faz|fique|use)\b",
    r"\bregra\b.*\b(nova|criar|cria|adiciona)\b",
    r"\bna proxima\b.*\bfaz\b",
    # SINAL LINGUISTICO DE REPETICAO (o operador denuncia que JA pediu) — alta prioridade
    r"\bja (te )?(falei|disse|pedi|avisei|mandei)\b",
    r"\bde novo\b",
    r"\bmais uma vez\b",
    r"\boutra vez\b",
    r"\bquantas vezes\b",
    r"\bsempre (que|faco|tenho) que (falar|pedir|repetir|lembrar)\b",
    r"\btoda (vez|hora) (eu )?(tenho que|preciso)\b",
    # PREFERENCIA NEGATIVA forte (sinaliza regra de evitar)
    r"\bodeio\b",
    r"\bdetesto\b",
    r"\bnao suporto\b",
    r"\bnao aguento\b",
    r"\bnao gosto (quando|de)\b",
    r"\bme irrita\b",
]

# CONFIGURE: troque {{CAMINHO_MEMORIA}} pelo caminho ABSOLUTO da sua pasta de memoria
# (a mesma que o fecha-sessao usa), ex: C:\Users\voce\.claude\projects\<id>\memory
# O instalador resolve esse placeholder automaticamente; so ajuste a mao se rodar manual.
# Caminho do log de repeticao (placeholder substituido por caminho real no fork vivo)
_LOG_PATH = os.path.join(r"{{CAMINHO_MEMORIA}}", "_regras-detectadas.log")
_MAX_LINHAS = 200

def _normaliza(txt):
    # baixa caixa, remove acentos e pontuacao — pra "sempre faz X" e "Sempre faz x!" casarem
    try:
        import unicodedata
        txt = "".join(
            c for c in unicodedata.normalize("NFD", txt)
            if unicodedata.category(c) != "Mn"
        )
    except Exception:
        pass
    txt = txt.lower()
    txt = re.sub(r"[^\w\s]", "", txt)  # remove pontuacao
    return txt

def _hash_trecho(alvo_normalizado):
    # Extrai palavras de conteudo (sem stopwords curtas) e gera hash curto
    stopwords = {"a", "o", "e", "de", "da", "do", "em", "pra", "para",
                 "que", "nao", "se", "com", "um", "uma", "eu", "vc",
                 "voce", "me", "meu", "minha", "ao"}
    palavras = [w for w in alvo_normalizado.split() if len(w) > 2 and w not in stopwords]
    # Usa as primeiras 8 palavras de conteudo como chave de identidade
    chave = " ".join(sorted(palavras[:8]))
    return hashlib.md5(chave.encode("utf-8")).hexdigest()[:12]

def _ler_log():
    try:
        if not os.path.exists(_LOG_PATH):
            return []
        with open(_LOG_PATH, "r", encoding="utf-8") as f:
            return [l.rstrip("\n") for l in f.readlines()]
    except Exception:
        return []

def _gravar_log(linhas_existentes, nova_linha):
    try:
        os.makedirs(os.path.dirname(_LOG_PATH), exist_ok=True)
        # Append atomico: duas janelas simultaneas nao se sobrescrevem.
        # O OS garante atomicidade pra linhas curtas em modo "a".
        with open(_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(nova_linha + "\n")
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

def _contar_ocorrencias(linhas, hash_alvo):
    count = 0
    for linha in linhas:
        # formato de linha: "HASH:palavras-chave"
        partes = linha.split(":", 1)
        if partes and partes[0].strip() == hash_alvo:
            count += 1
    return count

def main():
    raw = sys.stdin.read()
    if not raw.strip():
        return
    try:
        data = json.loads(raw)
        prompt = data.get("prompt", "") or ""
    except Exception:
        # se nao for JSON, trata o stdin inteiro como o texto do prompt
        prompt = raw

    if not prompt.strip():
        return

    # Ignora ENVELOPES DE SISTEMA (task-notification, system-reminder, local-command,
    # command-name, ide_selection, etc.): chegam via UserPromptSubmit mas NAO sao pedido
    # do usuario. Comecam todos com '<tag>'; humano em PT-BR nao abre mensagem com '<'.
    # Sem este guard o log enche de 'tasknotification...' como se fosse regra.
    if prompt.lstrip().startswith("<"):
        return

    alvo = _normaliza(prompt)
    bateu = any(re.search(p, alvo) for p in GATILHOS)
    if not bateu:
        return

    # Detector de repeticao
    hash_atual = _hash_trecho(alvo)
    linhas = _ler_log()
    ocorrencias = _contar_ocorrencias(linhas, hash_atual)

    # Palavras-chave curtas pra auditoria humana do log
    palavras_chave = " ".join(alvo.split()[:6])
    nova_linha = f"{hash_atual}:{palavras_chave}"
    _gravar_log(linhas, nova_linha)

    vez = ocorrencias + 1  # esta e a vez atual (ja gravada acima)

    # BACKSTAGE POR PADRAO: a captura e SILENCIOSA durante o trabalho do usuario. O log
    # acima (`_regras-detectadas.log`) e a fonte da verdade e sera destilado no fechamento
    # / passe automatico (vigia de inatividade / catch-up), entao NADA se perde mesmo se o
    # usuario nunca fechar a sessao. Ver references/manutencao-backstage-arquitetura.md.
    #
    # UNICA excecao que fala no contexto: REPETICAO FORTE (>=3a vez). Ai esquecer custa caro
    # e o sinal e raro (nao vira spam) — vale cutucar pra gravar JA. 1a/2a vez ficam so no log.
    if vez < 3:
        return  # silencioso: so o log, zero ruido no chat de trabalho

    aviso = (
        f"[backstage] Este pedido/correcao JA APARECEU {vez}x — repeticao forte. Se ainda "
        "nao virou regra na memoria, grave AGORA (arquivo + 1 linha no indice), em silencio, "
        "sem narrar pro operador. Nao e assunto do chat; so registre."
    )
    out = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": aviso,
        }
    }
    sys.stdout.write(json.dumps(out, ensure_ascii=False))

if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # nunca travar o turno
