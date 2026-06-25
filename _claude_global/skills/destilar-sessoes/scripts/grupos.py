#!/usr/bin/env python3
"""
grupos.py — agrupa os .txt enxutos em N lotes balanceados por tamanho.

Cada lote vira a "ordem de servico" de um subagente extrator (tier leve), que le
o lote inteiro e devolve o achado estruturado. Balancear por bytes (nao por
contagem) evita lote gigante que estoura a janela do subagente.

Mantem ordem CRONOLOGICA dentro e entre os lotes: e o que deixa enxergar a curva
inexperiente -> maduro (sessao antiga vs recente). Nao embaralhar.

Uso:
  python grupos.py [--enxutos DIR] [--out FILE] [--n N] [--bytes-por-lote B]

  --n              numero de lotes (default: auto, mira ~60 KB por lote)
  --bytes-por-lote alvo de bytes por lote quando --n nao e dado (default: 60000)

Saida: grupos.json = lista de lotes; cada lote = lista de caminhos de .txt.
"""
import json, os, argparse, math

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--enxutos", default=os.path.join(os.getcwd(), "_catchup", "enxutos"))
    ap.add_argument("--out", default=os.path.join(os.getcwd(), "_catchup", "grupos.json"))
    ap.add_argument("--n", type=int, default=0)
    ap.add_argument("--bytes-por-lote", type=int, default=60000)
    args = ap.parse_args()

    manifest_path = os.path.join(args.enxutos, "_manifest.txt")
    rows = []
    with open(manifest_path, encoding="utf-8") as f:
        next(f)  # header
        for line in f:
            p = line.strip().split(" | ")
            if len(p) == 4:
                rows.append((p[0], p[1], int(p[2]), int(p[3])))
    rows.sort()  # cronologico ascendente

    if not rows:
        print("nada a agrupar: _manifest.txt vazio")
        json.dump([], open(args.out, "w"))
        return

    total = sum(r[3] for r in rows)
    N = args.n if args.n > 0 else max(1, math.ceil(total / args.bytes_por_lote))
    target = total / N

    groups, cur, acc = [], [], 0
    for r in rows:
        path = os.path.join(args.enxutos, r[1]).replace("\\", "/")
        cur.append(path)
        acc += r[3]
        if acc >= target and len(groups) < N - 1:
            groups.append(cur)
            cur, acc = [], 0
    if cur:
        groups.append(cur)

    json.dump(groups, open(args.out, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"total {total//1024} KB em {len(rows)} sessoes -> {len(groups)} lotes (alvo ~{int(target)//1024} KB/lote)")
    for i, g in enumerate(groups):
        kb = sum(os.path.getsize(p) for p in g) // 1024
        print(f"  lote {i}: {len(g)} sessoes, ~{kb} KB")
    print("salvo:", args.out)

if __name__ == "__main__":
    main()
