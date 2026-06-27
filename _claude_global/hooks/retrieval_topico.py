#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Hook UserPromptSubmit: retrieval por topico em modo ponteiro.

A memoria do CORTEX depende do modelo LEMBRAR de abrir o guia/regra certo entre
dezenas de arquivos. Quando ele esquece, entrega abaixo do piso de qualidade.

Este hook detecta o TEMA do prompt por um mapa keyword->arquivo curado e injeta
somente o caminho + resumo curto. O modelo le o arquivo se precisar.

Disciplina anti-dumbzone:
- cap de TETO_ARQUIVOS por turno (1): so o match mais forte entra;
- match por palavra inteira, sem acento (o operador digita com acento);
- nao injeta nada se nenhuma keyword casar.

Estende a doutrina do roteia_cliente (mesmo formato de hook UserPromptSubmit).

CONFIG: {{PASTA_CORTEX}} e resolvido na instalacao pro caminho absoluto da PASTA
CORTEX (a pasta de trabalho FLAT onde mora o conteudo de memoria/, incluindo
references/). NAO confundir com {{CAMINHO_MEMORIA}} (memoria pessoal por-projeto
em ~/.claude/projects) nem com {{PASTA_REFERENCIAS}} (pasta de ingestao).
"""
import os, re, sys, unicodedata

# stdout em UTF-8: no Windows o default e cp1252 e quebra em seta/emoji/acento.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# resolvido na instalacao. Ex: C:\CORTEX  ou  /home/voce/CORTEX (a pasta de trabalho).
CORTEX_BASE = r"{{PASTA_CORTEX}}"
if CORTEX_BASE.startswith("{{"):
    CORTEX_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "memoria"))
REF = os.path.join(CORTEX_BASE, "references")

TETO_ARQUIVOS = 1          # no maximo 1 ponteiro por turno
MAX_CHARS_ARQUIVO = 6000   # fallback para resumo curto

# Mapa curado tema -> arquivo. Cada entrada:
#   "arquivo.md": {modo, keywords}
#   modo "secao"   -> injeta do marcador '## Regras extras' ao fim (guia de nicho)
#   modo "inteiro" -> injeta o arquivo todo (regra de sistema curta)
# keyword casa por palavra inteira, minuscula, sem acento, sensivel ao limite \w.
MAPA = {
    # --- guias de nicho (injeta a secao acionavel) ---
    "nichos/nicho-design.md": {"modo": "secao", "keywords": [
        "design grafico", "tipografia", "hierarquia visual", "grid", "layout da peca",
        "peca visual", "ui", "ux", "interface", "wireframe", "branding", "identidade visual"]},
    "nichos/nicho-dev.md": {"modo": "secao", "keywords": [
        "programacao", "refatorar", "teste unitario", "arquitetura de codigo",
        "clean code", "codigo fonte", "bug", "deploy", "api"]},
    "nichos/nicho-escrita.md": {"modo": "secao", "keywords": [
        "copywriting", "headline", "texto de venda", "escrever copy", "revisar copy",
        "redacao", "artigo", "roteiro", "newsletter"]},
    "nichos/nicho-marketing.md": {"modo": "secao", "keywords": [
        "marketing digital", "posicionamento", "funil", "aquisicao", "campanha",
        "cac", "ltv", "growth", "conversao", "publico alvo", "conteudo"]},
    "nichos/nicho-operacoes.md": {"modo": "secao", "keywords": [
        "gestao", "processo", "operacao", "fluxo de trabalho", "automacao",
        "produtividade", "rotina", "checklist operacional"]},
    "nichos/nicho-vendas.md": {"modo": "secao", "keywords": [
        "vendas", "prospeccao", "comercial", "lead", "proposta", "fechamento",
        "objecao", "follow-up", "negociacao", "pipeline de vendas"]},
    # --- regras de sistema (injeta o arquivo inteiro) ---
    "voz.md": {"modo": "inteiro", "keywords": [
        "voz do operador", "tom de voz", "escrever como ele", "voz dele"]},
    "tiers-de-modelo.md": {"modo": "inteiro", "keywords": [
        "tier de modelo", "qual modelo", "delegar subagente", "orquestrar",
        "fan-out", "haiku ou sonnet"]},
    "principios-aios.md": {"modo": "inteiro", "keywords": [
        "principios do aios", "6 principios", "regua do sistema", "audit do cortex"]},
    "politica-contexto-memoria-compactacao.md": {"modo": "inteiro", "keywords": [
        "contexto pesado", "memoria grande", "tamanho da memoria", "link sem gatilho",
        "gatilho nao funcionou", "complexo pra acionar", "complexo para acionar",
        "dificil de acionar", "jeito que eu falo", "jeito que o usuario fala",
        "compactando automatico", "compactacao automatica", "auto compact",
        "auto compactacao", "perder contexto", "alucinar por contexto"]},
    "guardrails-autoevolucao-cortex.md": {"modo": "inteiro", "keywords": [
        "vibecoding do cortex", "auto evolucao do cortex", "melhorar o cortex sozinho",
        "mudanca no cortex", "risco do cortex", "editar memoria sozinho",
        "spam no terminal", "codigo spammando", "terminal quiet"]},
    "protocolo-auto-melhoria-continua-cortex.md": {"modo": "inteiro", "keywords": [
        "ja pedi isso varias vezes", "melhorar a cada dia", "cada dia de uso",
        "menos atrito na proxima sessao", "proximas sessoes ter menos atrito",
        "nao quero falar de cortex todo dia", "perder horas falando do cortex",
        "atrito que o usuario gera", "melhorar sozinho baseado nas interacoes",
        "como pedir para melhorar o cortex", "quando eu falar puxe"]},
    "context-engineering-cortex.md": {"modo": "inteiro", "keywords": [
        "context engineering", "context-engineering", "engenharia de contexto",
        "regras globais", "regra global", "prioridade n1", "prioridade numero 1",
        "indice global", "md global como indice", "como carregar contexto"]},
    "criterio-acesso-contexto-cortex.md": {"modo": "inteiro", "keywords": [
        "quando acessar contexto", "custo de token pra abrir arquivo",
        "custo de token para abrir arquivo", "custo de token pra abrir contexto",
        "custo de token para abrir contexto", "pasta cortex como biblioteca",
        "cortex como biblioteca", "biblioteca roteavel", "biblioteca roteável",
        "mandei @arquivo", "arquivo apontado com @", "menor contexto que muda",
        "texto e codigo por padrao", "midia pesada sob demanda"]},
    "protocolo-execucao.md": {"modo": "inteiro", "keywords": [
        "level-up", "automacao semanal", "automatizar rotina", "alavanca de automacao"]},
}


def sem_acento(s):
    """remove acento pra casar 'programacao' com 'programação' (operador digita com acento)."""
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def casa(prompt_norm, alias_norm):
    """match por palavra inteira, ambos ja sem acento e minusculos."""
    return re.search(r"(?<!\w)" + re.escape(alias_norm) + r"(?!\w)", prompt_norm) is not None


def extrai_secao(texto):
    """recorta do '## Regras extras' ate o fim (parte acionavel do nicho).
    fallback: o arquivo todo cortado no teto."""
    m = re.search(r"^##\s+Regras extras.*", texto, re.MULTILINE | re.IGNORECASE)
    if m:
        return texto[m.start():].strip()
    return texto[:MAX_CHARS_ARQUIVO].strip()


def carrega(arquivo, modo):
    caminho = os.path.join(REF, arquivo)
    if not os.path.isfile(caminho):
        return None
    try:
        with open(caminho, encoding="utf-8") as f:
            texto = f.read()
    except Exception:
        return None
    if modo == "secao":
        return extrai_secao(texto)
    return texto[:MAX_CHARS_ARQUIVO].strip()


def resumo_ponteiro(arquivo, modo):
    caminho = os.path.join(REF, arquivo)
    if not os.path.isfile(caminho):
        return None
    try:
        with open(caminho, encoding="utf-8") as f:
            cabeca = f.read(600)
    except Exception:
        cabeca = ""
    linhas = [l.strip() for l in cabeca.splitlines() if l.strip() and not l.startswith("<!--")]
    titulo = next((l.lstrip("#").strip() for l in linhas if l.startswith("#")), None)
    frase = next((l for l in linhas if not l.startswith("#") and len(l) > 20), None)
    hint = "guia: leia a secao acionavel" if modo == "secao" else "referencia: leia se necessario"
    partes = [p for p in [titulo, frase] if p]
    resumo = " | ".join(partes[:2])
    return f"- {caminho}" + (f"  # {resumo} ({hint})" if resumo else f"  # {hint}")


def main():
    # le o stdin como UTF-8 explicito: o harness manda JSON UTF-8, mas o default do
    # Python no Windows e cp1252 e quebraria acento ('conversão' -> 'conversÃ£o').
    try:
        raw = sys.stdin.buffer.read().decode("utf-8")
    except Exception:
        raw = sys.stdin.read()
    try:
        import json
        data = json.loads(raw)
    except Exception:
        return
    prompt = (data.get("prompt") or "").strip()
    if not prompt:
        return
    prompt_norm = sem_acento(prompt.lower())

    # score por arquivo = comprimento da maior keyword batida (keyword longa = sinal forte)
    candidatos = []  # (score, arquivo, modo)
    for arquivo, cfg in MAPA.items():
        hits = [k for k in cfg["keywords"] if casa(prompt_norm, sem_acento(k))]
        if hits:
            candidatos.append((max(len(k) for k in hits), arquivo, cfg["modo"]))

    if not candidatos:
        return

    candidatos.sort(key=lambda c: c[0], reverse=True)
    escolhidos = candidatos[:TETO_ARQUIVOS]

    ponteiros = []
    for _, arquivo, modo in escolhidos:
        linha = resumo_ponteiro(arquivo, modo)
        if not linha:
            continue
        ponteiros.append(linha)

    if not ponteiros:
        return

    cabeca = (
        "[RETRIEVAL POR TOPICO] O prompt casou com material do CORTEX. "
        "Leia o ponteiro se necessario, sem carregar contexto por garantia. "
        "Precedencia: bloqueio global > cliente > preferencia/skill > guia > generico."
    )
    print(cabeca + "\n" + "\n".join(ponteiros))


if __name__ == "__main__":
    main()
