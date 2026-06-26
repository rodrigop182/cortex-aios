#!/usr/bin/env python3
"""
sintetiza.py — converte sessoes enxutas em artigos de conceito.

Le os .txt de _catchup/enxutos/, agrupa em lotes, chama o Claude SDK
pra extrair conhecimento por CONCEITO (nao por sessao), salva artigos em
<wiki>/ e regenera o index.md.

Por que por conceito e nao por sessao: sessao e efemera; conceito acumula.
"como trabalhar com o operador" cresce em cada sessao nova que toca no tema,
em vez de criar N arquivos redundantes.

Uso:
  python sintetiza.py [--enxutos DIR] [--wiki DIR] [--dry-run]

  --enxutos  pasta com os .txt do extrai.py (default: ./_catchup/enxutos)
  --wiki     pasta de saida dos artigos (OBRIGATORIO ou passar como arg)
  --dry-run  mostra o que faria sem gravar nada

Custo estimado: ~1-3k tokens por lote de sessoes (Haiku lendo texto ja enxuto).
"""
import os, sys, glob, json, re, argparse, textwrap
from pathlib import Path
import anthropic

DEFAULT_ENXUTOS  = os.path.join(os.getcwd(), "_catchup", "enxutos")
INDEX_PATH       = None  # definido por args.wiki
TEMPLATE_FILA    = None  # sem caderno de template no kit do amigo
LOTE_BYTES      = 50_000   # ~50KB por lote = cabido no contexto do Haiku
MAX_FILE_BYTES  = 40_000   # trunca arquivo individual acima disso antes de lote
MAX_ARTIGO_LINHAS = 40     # artigo curto: 1 conceito, sem encheção

# Conceitos que o CORTEX rastreia — o extrator classifica cada achado num desses
CONCEITOS = [
    "como-trabalhar-com-operador",   # jeito de conduzir, tom, autonomia
    "design-regras-duras",           # regras visuais inegociaveis
    "execucao-e-delegacao",          # planejar, subagente, tier, custo
    "ferramentas-e-armadilhas",      # SVG, Chrome headless, PowerShell, etc
    "projetos-clientes",             # estado de clientes/projetos
    "cortex-e-sistema",              # melhorias no proprio CORTEX, skills, hooks
]

PROMPT_DEDUP = """Você é um editor sênior de conhecimento do CORTEX do operador.
Seu trabalho: manter o wiki DENSO e ENXUTO — cada linha deve ganhar seu lugar, nenhuma sobrevive por inércia.

ARTIGO EXISTENTE:
{existente}

NOVOS ACHADOS (extraídos de sessões recentes):
{achados}

REGRAS DE INTEGRAÇÃO (aplique nesta ordem):

1. VARIANTE / PARÁFRASE — mesmo conceito, palavras diferentes:
   → NÃO adicione. Se o achado novo tem evidência mais forte ou mais recente, atualize só a evidência da linha existente.

2. CONTRADIÇÃO — achado novo inverte ou refina a regra existente:
   → Substitua pela versão mais recente/madura. A curva de maturidade existe pra isso.

3. FRAGMENTO — achado novo cobre só parte de uma regra existente:
   → Descarte o fragmento. Regra existente já é mais completa.

4. GENUINAMENTE NOVO — ideia que não existe no artigo:
   → Adicione ao final. Mas aplique o teste: "essa regra mudaria meu comportamento numa sessão real?" Se não, descarte.

PODA OBRIGATÓRIA — ao reescrever, remova também:
- Regras que contradizem o CLAUDE.md atual (o CLAUDE.md vence)
- Regras redundantes entre si dentro do artigo (fusionar em 1)
- Regras vagas demais pra serem acionáveis ("ser proativo", "ter cuidado")
- Artigo com mais de 35 regras: consolidar as mais fracas até caber

TETO: máximo 35 linhas de regra por artigo. Se já está no teto, só entra nova regra se remover uma existente mais fraca.

FORMATO de saída — cada linha:
- <regra acionável em 1 frase>  *(evidencia: <o que gerou isso>)*

Retorne APENAS o artigo resultante completo, sem explicação, sem cabeçalhos extras.
"""

PROMPT_EXTRATOR = """Você é um extrator de conhecimento do CORTEX do operador.

Leia as sessoes abaixo e extraia SO o que vale pro futuro.

Sinais de CORREÇÃO EXPLÍCITA (gravar regra):
- "uê"/"ué" + descrição do erro
- "pq vc fez X" / "como assim" / "como é que"
- "comportamento mt estranho" / "isso é regra crítica"
- Repetição da mesma correção em 2+ turnos

Sinais de APROVAÇÃO (confirmar que acertou):
- Aprovação monossilábica + emenda com próximo pedido
- Ausência de objeção + próximo pedido direto = aprovação tácita

Sinais de EXPLORAÇÃO (quer pensar junto, NÃO executar ainda):
- "né?" / "faz sentido?" / "voce acha?" / "aqui comigo"
- "tipo" no meio da frase
- "sei lá" como marcador de incerteza

CRITÉRIO DE ENTRADA (todos devem passar):
1. RECORRÊNCIA: apareceu 2+ vezes nas sessões OU foi correção explícita
2. ACIONÁVEL: gera comportamento diferente numa sessão futura — se não muda nada, não entra
3. DURÁVEL: ainda será verdade daqui a 3 meses — estado temporário de projeto não entra

IGNORAR sempre:
- Correção pontual de 1x sem sinal de frustração → vai pro handoff, não pra wiki
- Dado financeiro (renda, valor, saldo, proposta) → nunca
- Conteúdo em <private> → zona morta
- Gatilhos manuais ("problema:", "qual seria?", "regra:", "(regra)") → são convenções de uso, não regras
- Estado de projeto (o que foi feito hoje, o que falta) → é handoff, não wiki
- Preferência mencionada uma vez sem confirmação → muito fraca

QUALIDADE DA REGRA:
- Escreva como instrução direta: "Ao fazer X, sempre Y" ou "Nunca Z quando W"
- Sem hedging ("talvez", "quando possível", "em geral")
- Sem redundância com o que já existe nos conceitos — se já é CLAUDE.md, não é wiki

Para cada achado, classifique em UM dos conceitos:
{conceitos}

Classifique também o ESCOPO:
- "pessoal": específico do operador (cliente, voz, marca, caminho, nicho, preferência pessoal)
- "cortex-geral": útil pra QUALQUER usuário do Claude Code sem contexto do operador

Na dúvida: "pessoal". Só marca "cortex-geral" se outro usuário sem contexto do operador se beneficiaria identicamente.

FORMATO de saída (JSON puro, sem markdown):
{{
  "achados": [
    {{
      "conceito": "<slug>",
      "regra": "<instrução direta, 1 frase>",
      "evidencia": "<o que nas sessões gerou isso>",
      "recorrencia": <número>,
      "escopo": "pessoal|cortex-geral"
    }}
  ]
}}

Se nada passar no critério: {{"achados": []}}

SESSOES:
{sessoes}
"""

def ler_truncado(path):
    """Lê arquivo .txt truncando em MAX_FILE_BYTES (evita prompt gigante)."""
    raw = Path(path).read_bytes()
    if len(raw) > MAX_FILE_BYTES:
        raw = raw[:MAX_FILE_BYTES]
    return raw.decode("utf-8", errors="replace")

# Projetos/temas rastreados — ordem importa: primeiro match vence
PROJETOS = [
    ("cortex",  ["cortex", "catch-up", "catchup", "destilacao", "fecha-sessao", "handoff", "skill"]),
    ("geral",   []),  # fallback — o operador vai ter projetos diferentes
]

def classificar_projeto(conteudo):
    """Retorna slug do projeto baseado em palavras-chave no conteúdo."""
    lower = conteudo.lower()
    for slug, keywords in PROJETOS:
        if not keywords:
            continue
        if any(k in lower for k in keywords):
            return slug
    return "geral"

def lotes(enxutos_dir):
    """Agrupa arquivos .txt por projeto, depois em lotes de ~LOTE_BYTES bytes."""
    files = sorted(glob.glob(os.path.join(enxutos_dir, "*.txt")))
    files = [f for f in files if not os.path.basename(f).startswith("_")]

    # Classificar cada arquivo por projeto
    por_projeto = {}
    for f in files:
        conteudo = ler_truncado(f)
        proj = classificar_projeto(conteudo)
        por_projeto.setdefault(proj, []).append((f, min(os.path.getsize(f), MAX_FILE_BYTES)))

    # Lotejar dentro de cada projeto por tamanho
    for proj, arquivos in por_projeto.items():
        lote, sz = [], 0
        for f, fsz in arquivos:
            if lote and sz + fsz > LOTE_BYTES:
                yield proj, lote
                lote, sz = [], 0
            lote.append(f)
            sz += fsz
        if lote:
            yield proj, lote

def _get_client():
    """Cria cliente Anthropic: API key do env, ou OAuth token do credentials.json."""
    import json as _json
    if os.environ.get("ANTHROPIC_API_KEY"):
        return anthropic.Anthropic()
    creds_path = Path.home() / ".claude" / ".credentials.json"
    if creds_path.exists():
        data = _json.loads(creds_path.read_text(encoding="utf-8"))
        token = data.get("claudeAiOauth", {}).get("accessToken")
        if token:
            return anthropic.Anthropic(auth_token=token)
    raise RuntimeError("Nenhuma credencial encontrada. Defina ANTHROPIC_API_KEY ou logue no Claude Code.")

def chamar_haiku(prompt):
    """Chama claude-haiku via SDK Python. Retorna texto da resposta."""
    client = _get_client()
    try:
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text.strip()
    except Exception as e:
        print(f"  ERRO Haiku SDK: {e}", file=sys.stderr)
        return None

def extrair_json(texto):
    """Extrai JSON do output do modelo (ignora markdown ao redor)."""
    if not texto:
        return None
    m = re.search(r'\{[\s\S]*\}', texto)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None

def carregar_artigo(wiki_dir, conceito):
    """Le artigo existente ou retorna string vazia."""
    path = os.path.join(wiki_dir, f"{conceito}.md")
    if os.path.exists(path):
        return open(path, encoding="utf-8").read()
    return ""

def salvar_artigo(wiki_dir, conceito, conteudo, dry_run=False):
    path = os.path.join(wiki_dir, f"{conceito}.md")
    if dry_run:
        print(f"  [dry-run] salvaria {path} ({len(conteudo)} chars)")
        return
    os.makedirs(wiki_dir, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(conteudo)

def atualizar_artigo(existente, novos_achados, dry_run=False):
    """Mescla achados novos no artigo existente via Haiku (dedup semântico)."""
    if not novos_achados:
        return existente, 0

    achados_txt = "\n".join(
        f"- {a['regra']}  *(evidencia: {a.get('evidencia','?')})*"
        for a in novos_achados
        if a.get("regra", "").strip()
    )
    if not achados_txt.strip():
        return existente, 0

    # Sem artigo existente: só formata os achados
    if not existente.strip():
        return achados_txt + "\n", len(novos_achados)

    if dry_run:
        return existente, len(novos_achados)

    prompt = PROMPT_DEDUP.format(existente=existente.strip(), achados=achados_txt)
    resultado = chamar_haiku(prompt)
    if not resultado:
        # fallback: append simples se Haiku falhar
        return existente.rstrip() + "\n\n" + achados_txt + "\n", len(novos_achados)

    linhas_antes = len([l for l in existente.splitlines() if l.strip().startswith("-")])
    linhas_depois = len([l for l in resultado.splitlines() if l.strip().startswith("-")])
    delta = linhas_depois - linhas_antes
    return resultado.strip() + "\n", max(delta, 0)

def enfileirar_template(achados, dry_run=False):
    """Enfileira achados cortex-geral num caderno de melhorias — sem destino no kit generico."""
    if TEMPLATE_FILA is None:
        return 0
    import datetime as _dt
    gerais = [a for a in achados if a.get("escopo") == "cortex-geral" and a.get("regra","").strip()]
    if not gerais:
        return 0
    hoje = _dt.date.today().isoformat()
    linhas = []
    for a in gerais:
        conceito = a.get("conceito", "geral")
        regra = a.get("regra", "").strip()
        linhas.append(f"- [ ] {hoje} — regra — {regra} — fonte: wiki/{conceito}.md\n")
    if dry_run:
        print(f"  [dry-run] enfileiraria {len(linhas)} item(ns) cortex-geral no template")
        return len(linhas)
    try:
        with open(TEMPLATE_FILA, "a", encoding="utf-8") as f:
            f.writelines(linhas)
        print(f"  MELHORIAS-PRO-TEMPLATE: +{len(linhas)} item(ns) cortex-geral enfileirado(s)")
    except Exception as e:
        print(f"  AVISO: nao conseguiu enfileirar no template: {e}", file=sys.stderr)
    return len(linhas)

RETRIEVAL_MAPA_PATH = None
RETRIEVAL_RUIDO_PATH = None
FREQ_THRESHOLD = 3   # palavra aparece em 3+ sessoes do lote = candidata a ruido

def detectar_keywords_ruido(enxutos_dir):
    """
    Varre os enxutos e gera lista de candidatas a ruido — requer RETRIEVAL_MAPA_PATH
    e RETRIEVAL_RUIDO_PATH configurados. No kit generico esses caminhos sao None,
    entao a funcao retorna cedo sem fazer nada.
    """
    if RETRIEVAL_MAPA_PATH is None or RETRIEVAL_RUIDO_PATH is None:
        return

    import re as _re, collections, unicodedata as _ud

    def sem_acento(s):
        return "".join(c for c in _ud.normalize("NFKD", s) if not _ud.combining(c))

    stopwords = {
        "que", "nao", "sim", "pra", "pro", "com", "para", "uma", "uns",
        "isso", "esse", "esta", "este", "ele", "ela", "eles", "elas",
        "tem", "ter", "ser", "foi", "vai", "vou", "fazer", "feito",
        "mais", "mas", "como", "quando", "onde", "porque", "qual",
        "voce", "meu", "minha", "seu", "sua", "nos", "mas", "por",
        "sem", "aqui", "ali", "agora", "depois", "antes", "sempre",
        "ainda", "tambem", "entao", "assim", "ate", "mesmo", "muito",
        "bem", "mal", "das", "dos", "num", "numa", "sobre", "outro",
    }

    files = sorted(glob.glob(os.path.join(enxutos_dir, "*.txt")))
    files = [f for f in files if not os.path.basename(f).startswith("_")]
    if not files:
        return

    doc_freq = collections.Counter()
    for f in files:
        txt = sem_acento(Path(f).read_text(encoding="utf-8", errors="replace").lower())
        palavras = set(_re.findall(r'\b[a-z]{3,}\b', txt))
        palavras -= stopwords
        for p in palavras:
            doc_freq[p] += 1

    try:
        src = Path(RETRIEVAL_MAPA_PATH).read_text(encoding="utf-8")
        kws_no_mapa = set(_re.findall(r'"([^"]{3,})"', src))
        kws_no_mapa = {k for k in kws_no_mapa if not any(c in k for c in r'/\.')}
    except Exception:
        kws_no_mapa = set()

    n_sessoes = len(files)
    candidatas = []
    for kw in kws_no_mapa:
        kw_norm = sem_acento(kw.lower())
        palavras_kw = [p for p in kw_norm.split() if len(p) >= 3 and p not in stopwords]
        if not palavras_kw:
            continue
        freq_max = max(doc_freq.get(p, 0) for p in palavras_kw)
        if freq_max >= FREQ_THRESHOLD and n_sessoes > 0:
            pct = int(100 * freq_max / n_sessoes)
            if pct >= 50:
                candidatas.append((pct, freq_max, kw))

    if not candidatas:
        return

    candidatas.sort(reverse=True)
    hoje = __import__("datetime").date.today().isoformat()
    linhas = [
        f"# Keywords candidatas a ruido no retrieval — {hoje}\n\n",
        f"Sessoes analisadas: {n_sessoes}. Threshold: aparece em 50%+ das sessoes.\n\n",
        "Revisar manualmente: se a keyword dispara em contextos que nao pedem o arquivo,\n",
        "remover ou tornar mais especifica em `retrieval_topico.py`.\n\n",
        "| Keyword | Sessoes | % |\n",
        "|---------|---------|---|\n",
    ]
    for pct, freq, kw in candidatas[:20]:
        linhas.append(f"| `{kw}` | {freq}/{n_sessoes} | {pct}% |\n")

    try:
        Path(RETRIEVAL_RUIDO_PATH).write_text("".join(linhas), encoding="utf-8")
        print(f"  retrieval-ruido: {len(candidatas)} candidata(s) salvas em _retrieval-ruido.md")
    except Exception as e:
        print(f"  AVISO: nao conseguiu salvar ruido: {e}", file=sys.stderr)


def gerar_index(wiki_dir):
    """Regenera index.md — 1 linha por artigo, ~2k tokens."""
    artigos = sorted(glob.glob(os.path.join(wiki_dir, "*.md")))
    artigos = [a for a in artigos if os.path.basename(a) != "index.md"]
    linhas = ["# Wiki CORTEX — índice\n",
              "_Ler só o índice na sessão; seguir links sob demanda._\n\n"]
    for a in artigos:
        slug = os.path.splitext(os.path.basename(a))[0]
        conteudo = open(a, encoding="utf-8").read()
        n = len([l for l in conteudo.splitlines() if l.strip().startswith("-")])
        linhas.append(f"- [{slug}]({slug}.md) — {n} regra(s)\n")
    return "".join(linhas)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--enxutos", default=DEFAULT_ENXUTOS)
    ap.add_argument("--wiki", required=True,
                    help="Pasta de saida dos artigos wiki (ex: ~/meu-projeto/memoria/wiki)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    index_path = os.path.join(args.wiki, "index.md")

    if not os.path.isdir(args.enxutos):
        print(f"Pasta de enxutos nao encontrada: {args.enxutos}")
        sys.exit(1)

    os.makedirs(args.wiki, exist_ok=True)

    # acumulador por conceito
    por_conceito = {c: [] for c in CONCEITOS}
    total_lotes = 0

    for proj, lote_files in lotes(args.enxutos):
        total_lotes += 1
        sessoes_txt = ""
        for fp in lote_files:
            sessoes_txt += ler_truncado(fp) + "\n\n---\n\n"

        prompt = PROMPT_EXTRATOR.format(
            conceitos="\n".join(f"  - {c}" for c in CONCEITOS),
            sessoes=sessoes_txt[:45000]
        )

        print(f"Lote {total_lotes} [{proj}]: {len(lote_files)} sessoes, {len(sessoes_txt)//1024}KB -> Haiku...")
        if args.dry_run:
            print("  [dry-run] pulando chamada ao modelo")
            continue

        saida = chamar_haiku(prompt)
        dados = extrair_json(saida)
        if not dados:
            print(f"  Sem JSON valido neste lote")
            continue

        achados = dados.get("achados", [])
        gerais = sum(1 for a in achados if a.get("escopo") == "cortex-geral")
        print(f"  {len(achados)} achados ({gerais} cortex-geral)")
        enfileirar_template(achados, dry_run=args.dry_run)
        for a in achados:
            c = a.get("conceito", "")
            if c in por_conceito:
                por_conceito[c].append(a)

    # merge nos artigos
    total_adicionados = 0
    for conceito, achados in por_conceito.items():
        if not achados:
            continue
        existente = carregar_artigo(args.wiki, conceito)
        novo, n = atualizar_artigo(existente, achados, dry_run=args.dry_run)
        if n > 0:
            salvar_artigo(args.wiki, conceito, novo, args.dry_run)
            print(f"  {conceito}: +{n} regra(s)")
            total_adicionados += n

    # detecta keywords de ruido (no-op no kit generico)
    detectar_keywords_ruido(args.enxutos)

    # regenera index
    if not args.dry_run:
        index = gerar_index(args.wiki)
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(index)
        print(f"\nindex.md regenerado ({len(index)} chars, ~{len(index)//4} tokens)")

    # limpa enxutos processados (preserva marcador e manifest)
    if not args.dry_run and total_lotes > 0:
        removidos = 0
        for f in glob.glob(os.path.join(args.enxutos, "*.txt")):
            if os.path.basename(f).startswith("_"):
                continue  # preserva _manifest.txt, _ultimo-processado.txt
            os.remove(f)
            removidos += 1
        if removidos:
            print(f"enxutos removidos: {removidos} arquivos .txt (marcador preservado)")

    print(f"\nTotal: {total_lotes} lotes processados, {total_adicionados} regras adicionadas")

if __name__ == "__main__":
    main()
