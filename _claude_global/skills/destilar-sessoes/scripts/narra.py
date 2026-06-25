#!/usr/bin/env python3
"""
narra.py — gera narrativa cronologica por projeto a partir dos enxutos.

Le os .txt de _catchup/enxutos/, classifica por projeto por palavra-chave,
agrupa TODAS as sessoes de cada projeto e pede pro Haiku escrever uma narrativa
em linguagem natural: o que foi feito, o que foi descartado, o que ficou.

Diferente do sintetiza.py (que extrai regras abstratas), este script produz
a HISTORIA do projeto — cronologica, navegavel, com decisoes e descartados.

Saida: {{CAMINHO_MEMORIA}}/projects/<projeto>-narrativa.md por projeto.

Uso:
  python narra.py [--enxutos DIR] [--out DIR] [--dry-run] [--projeto SLUG]

  --enxutos  pasta com os .txt do extrai.py (default: ./_catchup/enxutos)
  --out      pasta de saida (default: {{CAMINHO_MEMORIA}}/projects)
  --dry-run  mostra o que faria sem chamar o modelo
  --projeto  processa so um projeto especifico (ex: projeto-a)
"""
import os, sys, glob, argparse
from pathlib import Path
import anthropic

DEFAULT_ENXUTOS = os.path.join(os.getcwd(), "_catchup", "enxutos")
DEFAULT_OUT     = r"{{CAMINHO_MEMORIA}}/projects"
MAX_FILE_BYTES  = 40_000   # trunca sessao individual antes de concatenar
LOTE_BYTES      = 60_000   # sessoes por lote de refinamento (rolling summary)

# Projetos rastreados — PERSONALIZAR com seus projetos. Ordem importa: primeiro match vence.
# Formato: ("slug", ["palavra-chave-1", "palavra-chave-2", ...])
# O slug vira nome do arquivo de saida (<slug>-narrativa.md).
# Sessoes que nao casam com nenhum projeto sao ignoradas (retornam None).
PROJETOS = [
    ("projeto-a",   ["nome-do-projeto-a", "apelido-a"]),
    ("projeto-b",   ["nome-do-projeto-b", "cliente-b"]),
    ("cortex",      ["cortex", "catch-up", "catchup", "destilacao", "fecha-sessao", "sintetiza", "extrai.py"]),
]

# Nome de exibicao de cada projeto nas narrativas geradas.
# Adicione uma entrada aqui para cada slug em PROJETOS.
NOMES_DISPLAY = {
    "projeto-a":  "Projeto A",
    "projeto-b":  "Projeto B",
    "cortex":     "CORTEX (sistema AIOS)",
}

PROMPT_INICIAL = """Voce e o CORTEX do {{NOME_OPERADOR}}, {{DESCRICAO_OPERADOR}}.

Leia o PRIMEIRO LOTE de sessoes do projeto "{projeto}" e escreva um RASCUNHO de narrativa markdown.

Estrutura obrigatoria:

# Narrativa — {projeto_display}

_Gerado em: {data}_

## O que foi construido
[cronologia — o que foi feito, quando]

## O que tentamos e descartamos
[tentativas com motivo do descarte]

## Metodologia atual
[o jeito que funciona hoje]

## Estado atual
[o que esta pronto / o que falta]

## Aprendizados-chave
- [max 5 bullets — so o que nao e obvio]

REGRAS: PT-BR direto. Max 6 linhas por secao. Nao inventar. Dado financeiro: ignorar. Sem registro = escrever "Sem registro suficiente."

SESSOES (lote {lote_num}/{lote_total}):
{sessoes}
"""

PROMPT_REFINAR = """Voce e o CORTEX do {{NOME_OPERADOR}}.

Abaixo esta a NARRATIVA ATUAL do projeto "{projeto}" (ja condensada) e um NOVO LOTE de sessoes.
Atualize a narrativa incorporando o que o novo lote acrescenta.

NARRATIVA ATUAL (max 4000 chars):
{narrativa_atual}

NOVO LOTE (lote {lote_num}/{lote_total}):
{sessoes}

Retorne a narrativa COMPLETA e ATUALIZADA no mesmo formato markdown. Mantenha cada secao em max 8 linhas — seja seletivo, priorize o que e novo ou contradiz o anterior.
"""

def ler_truncado(path):
    raw = Path(path).read_bytes()
    if len(raw) > MAX_FILE_BYTES:
        raw = raw[:MAX_FILE_BYTES]
    return raw.decode("utf-8", errors="replace")

def classificar_projeto(conteudo):
    """Retorna slug do projeto baseado em palavras-chave no conteudo, ou None se nao casar."""
    lower = conteudo.lower()
    for slug, keywords in PROJETOS:
        if any(k in lower for k in keywords):
            return slug
    return None  # ignora sessoes que nao casam com projeto conhecido

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

def nome_display(slug):
    """Retorna nome de exibicao do projeto, ou o proprio slug se nao configurado."""
    return NOMES_DISPLAY.get(slug, slug)

def main():
    from datetime import date

    ap = argparse.ArgumentParser()
    ap.add_argument("--enxutos", default=DEFAULT_ENXUTOS)
    ap.add_argument("--out", default=DEFAULT_OUT,
                    help="Pasta de saida (default: {{CAMINHO_MEMORIA}}/projects)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--projeto", default=None, help="Processar so este projeto (slug)")
    args = ap.parse_args()

    if not os.path.isdir(args.enxutos):
        print(f"Pasta de enxutos nao encontrada: {args.enxutos}")
        sys.exit(1)

    os.makedirs(args.out, exist_ok=True)

    # 1. Classificar todos os arquivos por projeto
    files = sorted(glob.glob(os.path.join(args.enxutos, "*.txt")))
    files = [f for f in files if not os.path.basename(f).startswith("_")]

    por_projeto = {}
    for f in files:
        conteudo = ler_truncado(f)
        proj = classificar_projeto(conteudo)
        if proj:
            por_projeto.setdefault(proj, []).append(f)

    if args.projeto:
        if args.projeto not in por_projeto:
            print(f"Projeto '{args.projeto}' nao encontrado. Disponiveis: {list(por_projeto.keys())}")
            sys.exit(1)
        por_projeto = {args.projeto: por_projeto[args.projeto]}

    hoje = str(date.today())

    # 2. Por projeto: rolling summary lote a lote
    for proj, arquivos in por_projeto.items():
        print(f"\n=== {proj} ({len(arquivos)} sessoes) ===")

        # Montar lotes de LOTE_BYTES
        lotes = []
        lote_atual, lote_sz = [], 0
        for f in arquivos:
            fsz = min(os.path.getsize(f), MAX_FILE_BYTES)
            if lote_atual and lote_sz + fsz > LOTE_BYTES:
                lotes.append(lote_atual)
                lote_atual, lote_sz = [], 0
            lote_atual.append(f)
            lote_sz += fsz
        if lote_atual:
            lotes.append(lote_atual)

        print(f"  {len(lotes)} lotes de ~{LOTE_BYTES//1024}KB cada")

        narrativa_atual = None
        for i, lote_files in enumerate(lotes):
            sessoes_txt = "".join(ler_truncado(f) + "\n\n---\n\n" for f in lote_files)
            print(f"  Lote {i+1}/{len(lotes)}: {len(lote_files)} sessoes, {len(sessoes_txt)//1024}KB -> Haiku...")

            if args.dry_run:
                print("  [dry-run] pulando chamada ao modelo")
                continue

            if narrativa_atual is None:
                prompt = PROMPT_INICIAL.format(
                    projeto=proj,
                    projeto_display=nome_display(proj),
                    data=hoje,
                    lote_num=i+1,
                    lote_total=len(lotes),
                    sessoes=sessoes_txt
                )
            else:
                # Cap da narrativa acumulada: evita prompt gigante nas iteracoes tardias
                narrativa_cap = narrativa_atual[:4000]
                prompt = PROMPT_REFINAR.format(
                    projeto=proj,
                    narrativa_atual=narrativa_cap,
                    lote_num=i+1,
                    lote_total=len(lotes),
                    sessoes=sessoes_txt
                )

            narrativa_atual = chamar_haiku(prompt)
            if not narrativa_atual:
                print(f"  FALHOU no lote {i+1} — abortando {proj}")
                break

        if args.dry_run or not narrativa_atual:
            continue

        out_path = os.path.join(args.out, f"{proj}-narrativa.md")
        Path(out_path).write_text(narrativa_atual, encoding="utf-8")
        print(f"  Salvo: {out_path}")

    print("\nPronto.")

if __name__ == "__main__":
    main()
