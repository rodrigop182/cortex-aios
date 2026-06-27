#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mede_1shot.py - extrai metricas de 1-shot a partir dos transcripts enxutos.

Le os .txt gerados por extrai.py em _catchup/enxutos, chama Haiku para
identificar tarefas de producao e anexa linhas em:
  <PASTA_CORTEX>/memoria/metricas/1shot-log.csv

Regra de seguranca: se estiver em duvida, omite a linha. A metrica aceita ruido,
mas nao aceita inventar tarefa.
"""
import argparse
import csv
import glob
import json
import os
import re
import sys
from pathlib import Path


DEFAULT_ENXUTOS = os.path.join(os.getcwd(), "_catchup", "enxutos")
DEFAULT_LOG = r"{{PASTA_CORTEX}}/memoria/metricas/1shot-log.csv"
LOTE_BYTES = 45_000
MAX_FILE_BYTES = 30_000
FIELDNAMES = ["data", "sessao", "tarefa", "nicho", "iteracoes", "oneshot", "obs"]
NICHOS = {"landing", "video", "cortex", "copy", "infra", "design", "outro"}


PROMPT = """Voce e o medidor de 1-shot do CORTEX.

Leia as sessoes enxutas abaixo e extraia linhas de metrica por TAREFA DE PRODUCAO.

Definicoes:
- Tarefa de producao = pedido que gera entregavel: codigo, landing, copy, design, video, script, infra, memoria ou decisao de arquitetura.
- Conversa, pergunta trivial, brainstorm sem entregavel e decisao solta sem artefato NAO contam.
- iteracoes = numero de mensagens do operador que corrigem ou redirecionam o MESMO entregavel antes do aceite.
- oneshot = "sim" se iteracoes == 0; "nao" se iteracoes >= 1.
- Refinamento depois de aceite nao conta como correcao da entrega anterior.
- Se a sessao nao permite saber se houve entrega ou correcao, omita.
- Nunca invente tarefa, nicho, data ou resultado. Use so evidencia do texto.

Nicho permitido: landing, video, cortex, copy, infra, design, outro.

Formato de saida: JSON puro, sem markdown:
{{
  "linhas": [
    {{
      "data": "YYYY-MM-DD",
      "sessao": "id-curto-da-sessao",
      "tarefa": "descricao curta do entregavel",
      "nicho": "landing|video|cortex|copy|infra|design|outro",
      "iteracoes": 0,
      "obs": "nota curta, opcional"
    }}
  ]
}}

Se nada for medivel: {{"linhas": []}}

SESSOES:
{sessoes}
"""


def ler_truncado(path):
    raw = Path(path).read_bytes()
    if len(raw) > MAX_FILE_BYTES:
        raw = raw[:MAX_FILE_BYTES]
    return raw.decode("utf-8", errors="replace")


def arquivos_enxutos(enxutos_dir):
    files = sorted(glob.glob(os.path.join(enxutos_dir, "*.txt")))
    return [f for f in files if not os.path.basename(f).startswith("_")]


def lotes(enxutos_dir):
    lote, tamanho = [], 0
    for f in arquivos_enxutos(enxutos_dir):
        fsz = min(os.path.getsize(f), MAX_FILE_BYTES)
        if lote and tamanho + fsz > LOTE_BYTES:
            yield lote
            lote, tamanho = [], 0
        lote.append(f)
        tamanho += fsz
    if lote:
        yield lote


def _get_client():
    import anthropic

    if os.environ.get("ANTHROPIC_API_KEY"):
        return anthropic.Anthropic()
    creds_path = Path.home() / ".claude" / ".credentials.json"
    if creds_path.exists():
        data = json.loads(creds_path.read_text(encoding="utf-8"))
        token = data.get("claudeAiOauth", {}).get("accessToken")
        if token:
            return anthropic.Anthropic(auth_token=token)
    raise RuntimeError("Nenhuma credencial Anthropic encontrada.")


def chamar_haiku(prompt):
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
    if not texto:
        return None
    m = re.search(r"\{[\s\S]*\}", texto)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


def limpar_campo(valor, limite):
    texto = str(valor or "").replace("\n", " ").replace("\r", " ").strip()
    texto = re.sub(r"\s+", " ", texto)
    return texto[:limite]


def normalizar_linha(row):
    data = limpar_campo(row.get("data"), 10)
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", data):
        return None

    sessao = limpar_campo(row.get("sessao"), 80)
    tarefa = limpar_campo(row.get("tarefa"), 120)
    if not sessao or not tarefa:
        return None

    nicho = limpar_campo(row.get("nicho"), 20).lower()
    if nicho not in NICHOS:
        nicho = "outro"

    try:
        iteracoes = int(row.get("iteracoes", 0))
    except Exception:
        return None
    if iteracoes < 0:
        return None

    return {
        "data": data,
        "sessao": sessao,
        "tarefa": tarefa,
        "nicho": nicho,
        "iteracoes": str(iteracoes),
        "oneshot": "sim" if iteracoes == 0 else "nao",
        "obs": limpar_campo(row.get("obs"), 160),
    }


def chave(row):
    return (
        row.get("data", ""),
        row.get("sessao", ""),
        row.get("tarefa", "").strip().lower(),
    )


def ler_existentes(log_path):
    existentes = set()
    path = Path(log_path)
    if not path.exists():
        return existentes
    try:
        with path.open("r", encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                existentes.add(chave(row))
    except Exception:
        pass
    return existentes


def anexar_linhas(log_path, linhas, dry_run=False):
    path = Path(log_path)
    existentes = ler_existentes(path)
    novas = [l for l in linhas if chave(l) not in existentes]
    if dry_run:
        print(f"  [dry-run] anexaria {len(novas)} linha(s)")
        for l in novas[:10]:
            print(f"    {l}")
        return len(novas)
    if not novas:
        return 0
    path.parent.mkdir(parents=True, exist_ok=True)
    precisa_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if precisa_header:
            writer.writeheader()
        writer.writerows(novas)
    return len(novas)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--enxutos", default=DEFAULT_ENXUTOS)
    ap.add_argument("--log", default=DEFAULT_LOG)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not os.path.isdir(args.enxutos):
        print(f"Pasta de enxutos nao encontrada: {args.enxutos}")
        return 1

    todos = []
    total_lotes = 0
    for lote_files in lotes(args.enxutos):
        total_lotes += 1
        sessoes_txt = ""
        for fp in lote_files:
            sessoes_txt += ler_truncado(fp) + "\n\n---\n\n"
        prompt = PROMPT.format(sessoes=sessoes_txt[:45_000])
        print(f"1shot lote {total_lotes}: {len(lote_files)} sessao(oes), {len(sessoes_txt)//1024}KB -> Haiku...")
        saida = chamar_haiku(prompt)
        dados = extrair_json(saida)
        if not dados:
            print("  Sem JSON valido neste lote")
            continue
        linhas = []
        for row in dados.get("linhas", []):
            normalizada = normalizar_linha(row)
            if normalizada:
                linhas.append(normalizada)
        print(f"  {len(linhas)} linha(s) de metrica")
        todos.extend(linhas)

    adicionadas = anexar_linhas(args.log, todos, dry_run=args.dry_run)
    print(f"Total: {total_lotes} lote(s), {adicionadas} linha(s) nova(s) em {args.log}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
