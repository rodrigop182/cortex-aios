#!/usr/bin/env python3
"""
extrai.py — pre-filtro mecanico (tier-3) dos transcripts brutos.

Le os .jsonl de sessao do Claude Code e cospe, por sessao util, um .txt enxuto
so com a VOZ do operador (mensagens humanas) + os textos do assistant, ordenados
no tempo. Descarta tool_result volumoso, thinking, imagem e injecao de sistema.
Pula sessao sem fala humana real (sessao de subagente / vazia).

Por que existe: jogar transcript bruto no contexto incha (proibido). Este script
roda como passo barato e deixa so o que importa pros extratores (subagentes leves).

Uso:
  python extrai.py --src DIR [--out DIR] [--days N] [--since AAAA-MM-DD]

  --src    pasta dos .jsonl (OBRIGATORIO: caminho da pasta de projetos do Claude Code,
           ex: ~/.claude/projects/c--MeuProjeto)
  --out    pasta de saida dos .txt enxutos (default: <cwd>/_catchup/enxutos)
  --days   janela: so sessoes iniciadas nos ultimos N dias (default: 7)
  --since  janela alternativa: so sessoes a partir desta data (vence --days)

Saida: um .txt por sessao + _manifest.txt (ts | arquivo | turnos_user | bytes).
"""
import json, os, glob, sys, re, argparse
from datetime import datetime, timedelta, timezone

DEFAULT_SRC = None  # detectado automaticamente via --src obrigatorio

# ruido a marcar/pular nas mensagens de user (comando, injecao de sistema, selecao de IDE)
NOISE = re.compile(r'<command-name>|<command-message>|<local-command|system-reminder|caveman|<ide_selection')

def textof(content):
    """extrai blocos de texto; ignora tool_use/tool_result/thinking/imagem."""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for b in content:
            if isinstance(b, dict) and b.get("type") == "text":
                t = b.get("text", "").strip()
                if t:
                    parts.append(t)
        return "\n".join(parts).strip()
    return ""

def parse_ts(ts):
    """ISO -> datetime aware; tolera Z e ausencia de tz."""
    if not ts:
        return None
    try:
        s = ts.replace("Z", "+00:00")
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None

MARKER_FILE = "_ultimo-processado.txt"

def ler_marker(out_dir):
    """Retorna datetime do ultimo processamento, ou None."""
    path = os.path.join(out_dir, MARKER_FILE)
    if not os.path.exists(path):
        return None
    try:
        ts = open(path, encoding="utf-8").read().strip()
        return parse_ts(ts)
    except Exception:
        return None

def gravar_marker(out_dir, ts_str):
    """Grava o timestamp ISO da sessao mais recente processada."""
    path = os.path.join(out_dir, MARKER_FILE)
    with open(path, "w", encoding="utf-8") as f:
        f.write(ts_str + "\n")

def main():
    ap = argparse.ArgumentParser(
        description="Pre-filtro mecanico dos transcripts do Claude Code."
    )
    ap.add_argument(
        "--src",
        required=True,
        help=(
            "Pasta dos .jsonl de sessao do Claude Code. "
            "Ex: ~/.claude/projects/c--MeuProjeto  "
            "(encontre em ~/.claude/projects/ — escolha a pasta do seu projeto)"
        ),
    )
    ap.add_argument("--out", default=os.path.join(os.getcwd(), "_catchup", "enxutos"))
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--since", default=None)
    ap.add_argument("--force", action="store_true", help="ignora o marcador e reprocessa tudo na janela")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)

    if args.since:
        cutoff = parse_ts(args.since + "T00:00:00")
    else:
        cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)

    # marker = limite de "ja processado" — pula sessoes mais antigas que isso
    marker = None if args.force else ler_marker(args.out)
    if marker:
        print(f"marcador encontrado: ja processado ate {marker.isoformat()}")
        print(f"processando so sessoes MAIS RECENTES que o marcador")

    files = glob.glob(os.path.join(args.src, "*.jsonl"))
    if not files:
        print(f"Nenhum .jsonl encontrado em: {args.src}")
        print("Verifique o caminho passado em --src.")
        sys.exit(1)

    manifest = []
    skipped_old = 0
    skipped_empty = 0

    for fp in files:
        sid = os.path.splitext(os.path.basename(fp))[0]
        first_ts = None
        user_msgs = []   # (ts, texto, eh_ruido)
        asst_msgs = []
        try:
            with open(fp, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        o = json.loads(line)
                    except Exception:
                        continue
                    ts = o.get("timestamp")
                    if ts and first_ts is None:
                        first_ts = ts
                    msg = o.get("message")
                    if not isinstance(msg, dict):
                        continue
                    role = msg.get("role")
                    txt = textof(msg.get("content"))
                    if not txt:
                        continue
                    if role == "user":
                        user_msgs.append((ts, txt, bool(NOISE.search(txt))))
                    elif role == "assistant":
                        asst_msgs.append((ts, txt))
        except Exception:
            continue

        # janela temporal
        fdt = parse_ts(first_ts)
        if cutoff and fdt and fdt < cutoff:
            skipped_old += 1
            continue

        # ja processada em execucao anterior
        if marker and fdt and fdt <= marker:
            skipped_old += 1
            continue

        # pula sessoes sem fala humana real
        real_user = [u for u in user_msgs if not u[2] and len(u[1]) > 1]
        if not real_user and not asst_msgs:
            skipped_empty += 1
            continue
        if not real_user:
            skipped_empty += 1
            continue

        safe_ts = re.sub(r'[^0-9]', '', first_ts or "")[:14] or "00000000000000"
        outname = f"{safe_ts}__{sid}.txt"
        outpath = os.path.join(args.out, outname)

        events = []
        for ts, txt, noise in user_msgs:
            events.append((ts or "", "USER(cmd/sys)" if noise else "USER", txt))
        for ts, txt in asst_msgs:
            if len(txt) > 1200:
                txt = txt[:1200] + " [...cortado]"
            events.append((ts or "", "ASST", txt))
        events.sort(key=lambda e: e[0])

        with open(outpath, "w", encoding="utf-8") as out:
            out.write(f"# SESSAO {sid}  | inicio {first_ts}\n")
            out.write(f"# turnos user reais: {len(real_user)} | total user: {len(user_msgs)} | asst: {len(asst_msgs)}\n\n")
            for ts, tag, txt in events:
                out.write(f"[{tag}] {txt}\n\n")

        manifest.append((safe_ts, outname, len(real_user), os.path.getsize(outpath)))

    manifest.sort()
    with open(os.path.join(args.out, "_manifest.txt"), "w", encoding="utf-8") as m:
        m.write("ts_key | arquivo | turnos_user_reais | bytes\n")
        for safe_ts, name, nu, sz in manifest:
            m.write(f"{safe_ts} | {name} | {nu} | {sz}\n")

    # grava marcador com o timestamp da sessao mais recente processada
    if manifest:
        ts_mais_recente = max(x[0] for x in manifest)
        t = ts_mais_recente
        if len(t) >= 14:
            iso = f"{t[0:4]}-{t[4:6]}-{t[6:8]}T{t[8:10]}:{t[10:12]}:{t[12:14]}+00:00"
        else:
            iso = t
        gravar_marker(args.out, iso)
        print(f"marcador gravado: {iso}")

    total_bytes = sum(x[3] for x in manifest)
    print(f"janela: {'desde ' + args.since if args.since else 'ultimos ' + str(args.days) + ' dias'}")
    print(f"sessoes uteis: {len(manifest)}  (puladas: {skipped_old} fora da janela/ja-processadas, {skipped_empty} sem fala humana)")
    print(f"bytes enxutos: {total_bytes} (~{total_bytes//1024} KB)")
    print(f"turnos user reais somados: {sum(x[2] for x in manifest)}")
    if manifest:
        print("primeiras 3:", [x[1] for x in manifest[:3]])
        print("ultimas 3:", [x[1] for x in manifest[-3:]])

if __name__ == "__main__":
    main()
