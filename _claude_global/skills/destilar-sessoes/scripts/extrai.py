#!/usr/bin/env python3
"""
extrai.py — pre-filtro mecanico (tier-3) dos transcripts brutos.

Le os .jsonl de sessao e cospe, por sessao util, um .txt enxuto so com a VOZ
do operador (mensagens humanas) + os textos do assistant, ordenados no tempo.
Descarta tool_result volumoso, thinking, imagem e injecao de sistema.
Pula sessao sem fala humana real (sessao de subagente / vazia).

Por que existe: jogar transcript bruto no contexto incha (proibido). Este script
roda como passo barato e deixa so o que importa pros extratores (subagentes leves).

Uso:
  python extrai.py [--src DIR] [--out DIR] [--days N] [--since AAAA-MM-DD]

  --src    pasta dos .jsonl do Claude Code (default: ~/.claude/projects)
  --out    pasta de saida dos .txt enxutos (default: <cwd>/_catchup/enxutos)
  --days   janela: so sessoes iniciadas nos ultimos N dias (default: 7)
  --since  janela alternativa: so sessoes a partir desta data (vence --days)

Saida: um .txt por sessao + _manifest.txt (ts | arquivo | turnos_user | bytes).
"""
import json, os, glob, sys, re, argparse
from datetime import datetime, timedelta, timezone

DEFAULT_SRC = os.path.expanduser("~/.claude/projects")
DEFAULT_SRC_CODEX = os.path.expanduser("~/.codex/sessions")
DEFAULT_HANDOFF_SRC = os.path.expanduser("~/.claude/skills/handoff/handoff-session")

# ruido a marcar/pular nas mensagens de user (comando, injecao de sistema, selecao de IDE)
NOISE = re.compile(r'<command-name>|<command-message>|<local-command|system-reminder|caveman|<ide_selection')
# boilerplate do Codex — injections de sistema que não são fala real
NOISE_CODEX = re.compile(r'AGENTS\.md|permissions instructions|environment_context|filesystem|<INSTRUCTIONS|workspace_roots|sandbox_policy|approval_policy')

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

def textof_codex(content):
    """extrai texto de content no formato Codex (input_text / output_text)."""
    if isinstance(content, list):
        parts = []
        for b in content:
            if isinstance(b, dict) and b.get("type") in ("input_text", "output_text"):
                t = b.get("text", "").strip()
                if t:
                    parts.append(t)
        return "\n".join(parts).strip()
    return ""

def is_codex_format(first_obj):
    """Detecta se o jsonl é formato Codex (tem campo 'type' e 'payload')."""
    return "type" in first_obj and "payload" in first_obj

def parse_codex_file(fp, cutoff, marker):
    """Parse de rollout Codex. Retorna (sid, first_ts, user_msgs, asst_msgs) ou None se pular."""
    # sid = nome do arquivo sem .jsonl
    sid = os.path.splitext(os.path.basename(fp))[0]
    first_ts = None
    user_msgs = []
    asst_msgs = []
    session_id = None
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
                # extrair session_id do session_meta
                if o.get("type") == "session_meta":
                    session_id = o.get("payload", {}).get("session_id", sid)
                    continue
                if o.get("type") != "response_item":
                    continue
                payload = o.get("payload", {})
                role = payload.get("role", "")
                txt = textof_codex(payload.get("content", []))
                if not txt:
                    continue
                # filtrar boilerplate de injeção do sistema
                if NOISE_CODEX.search(txt[:300]):
                    continue
                if role == "user":
                    is_noise = bool(NOISE.search(txt))
                    user_msgs.append((ts, txt, is_noise))
                elif role == "assistant":
                    asst_msgs.append((ts, txt))
    except Exception:
        return None
    return (session_id or sid, first_ts, user_msgs, asst_msgs)

def codex_files_in_window(codex_src, cutoff):
    """Lista rollout-*.jsonl do Codex dentro da janela de cutoff."""
    import pathlib
    result = []
    base = pathlib.Path(codex_src)
    if not base.exists():
        return result
    for fp in base.rglob("rollout-*.jsonl"):
        result.append(str(fp))
    return result

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
HANDOFF_CONTEXT_FILE = "_handoff-context.txt"

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

def extrair_bloco_handoff(texto, titulo):
    """Extrai um resumo curto de um handoff para dedup da destilacao."""
    linhas = [l.rstrip() for l in texto.splitlines()]
    blocos = []
    capturar = False
    nomes = (
        "## Foco da proxima sessao",
        "## Foco da próxima sessão",
        "## Onde paramos",
        "## O que falta / proximo passo",
        "## O que falta / próximo passo",
        "## Proximos passos",
        "## Próximos passos",
    )
    for linha in linhas:
        if linha.startswith("## "):
            capturar = any(linha.startswith(n) for n in nomes)
            if capturar:
                blocos.append(linha)
            continue
        if capturar and linha.strip():
            blocos.append(linha)
        if sum(len(x) for x in blocos) > 1800:
            break
    resumo = "\n".join(blocos).strip()
    if not resumo:
        resumo = "\n".join(linhas[:25]).strip()
    return f"## {titulo}\n{resumo[:2200]}"

def escrever_contexto_handoffs(handoff_src, out_dir, cutoff, max_files=12):
    """Escreve contexto de handoffs ativos para evitar memoria/wiki duplicada."""
    import pathlib
    base = pathlib.Path(handoff_src)
    if not base.exists():
        return 0
    candidatos = []
    for fp in base.glob("*.md"):
        try:
            mtime = datetime.fromtimestamp(fp.stat().st_mtime, timezone.utc)
        except Exception:
            continue
        if cutoff and mtime < cutoff:
            continue
        candidatos.append((mtime, fp))
    candidatos.sort(key=lambda item: item[0], reverse=True)
    partes = []
    for _, fp in candidatos[:max_files]:
        try:
            texto = fp.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        partes.append(extrair_bloco_handoff(texto, fp.name))
    path = os.path.join(out_dir, HANDOFF_CONTEXT_FILE)
    if not partes:
        if os.path.exists(path):
            os.remove(path)
        return 0
    with open(path, "w", encoding="utf-8") as f:
        f.write("# Contexto de handoffs ativos\n\n")
        f.write("Uso: contexto de exclusao para destilar-sessoes. Estado de projeto e proximo passo aqui NAO viram wiki/memoria duplicada.\n\n")
        f.write("\n\n---\n\n".join(partes))
        f.write("\n")
    return len(partes)

def processar_sessao(sid, first_ts, user_msgs, asst_msgs, out_dir, cutoff, marker, manifest, skipped_old, skipped_empty, prefix=""):
    """Processa uma sessao (Claude ou Codex) e grava enxuto se valida. Retorna (skipped_old, skipped_empty)."""
    fdt = parse_ts(first_ts)
    if cutoff and fdt and fdt < cutoff:
        return skipped_old + 1, skipped_empty
    if marker and fdt and fdt <= marker:
        return skipped_old + 1, skipped_empty

    real_user = [u for u in user_msgs if not u[2] and len(u[1]) > 1]
    if not real_user:
        return skipped_old, skipped_empty + 1

    safe_ts = re.sub(r'[^0-9]', '', first_ts or "")[:14] or "00000000000000"
    outname = f"{safe_ts}__{prefix}{sid}.txt"
    outpath = os.path.join(out_dir, outname)

    events = []
    for ts, txt, noise in user_msgs:
        events.append((ts or "", "USER(cmd/sys)" if noise else "USER", txt))
    for ts, txt in asst_msgs:
        if len(txt) > 1200:
            txt = txt[:1200] + " [...cortado]"
        events.append((ts or "", "ASST", txt))
    events.sort(key=lambda e: e[0])

    with open(outpath, "w", encoding="utf-8") as out:
        fonte = "CODEX" if prefix else "CLAUDE"
        out.write(f"# SESSAO {sid}  | inicio {first_ts} | fonte {fonte}\n")
        out.write(f"# turnos user reais: {len(real_user)} | total user: {len(user_msgs)} | asst: {len(asst_msgs)}\n\n")
        for ts, tag, txt in events:
            out.write(f"[{tag}] {txt}\n\n")

    manifest.append((safe_ts, outname, len(real_user), os.path.getsize(outpath)))
    return skipped_old, skipped_empty


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=DEFAULT_SRC)
    ap.add_argument("--codex-src", default=DEFAULT_SRC_CODEX, help="pasta raiz dos rollouts Codex (default: ~/.codex/sessions)")
    ap.add_argument("--no-codex", action="store_true", help="nao processar sessoes do Codex")
    ap.add_argument("--handoff-src", default=DEFAULT_HANDOFF_SRC, help="pasta de handoffs ativos (default: ~/.claude/skills/handoff/handoff-session)")
    ap.add_argument("--no-handoff", action="store_true", help="nao gerar contexto de handoffs para dedup")
    ap.add_argument("--out", default=os.path.join(os.getcwd(), "_catchup", "enxutos"))
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--since", default=None)
    ap.add_argument("--force", action="store_true", help="ignora o marcador e reprocessa tudo na janela")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)

    # cutoff = limite minimo de antiguidade (janela de dias ou --since)
    if args.since:
        cutoff = parse_ts(args.since + "T00:00:00")
    else:
        cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)

    # marker = limite de "ja processado" — pula sessoes mais antigas que isso
    marker = None if args.force else ler_marker(args.out)
    if marker:
        print(f"marcador encontrado: ja processado ate {marker.isoformat()}")
        print(f"processando so sessoes MAIS RECENTES que o marcador")

    if not args.no_handoff:
        n_handoffs = escrever_contexto_handoffs(args.handoff_src, args.out, cutoff)
        if n_handoffs:
            print(f"handoffs: {n_handoffs} contexto(s) ativos para dedup")

    manifest = []
    skipped_old = 0
    skipped_empty = 0

    # --- Sessoes Claude Code ---
    files = glob.glob(os.path.join(args.src, "*.jsonl"))
    if not files:
        files = glob.glob(os.path.join(args.src, "*", "*.jsonl"))
    for fp in files:
        sid = os.path.splitext(os.path.basename(fp))[0]
        first_ts = None
        user_msgs = []
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

        skipped_old, skipped_empty = processar_sessao(
            sid, first_ts, user_msgs, asst_msgs,
            args.out, cutoff, marker, manifest, skipped_old, skipped_empty
        )

    # --- Sessoes Codex ---
    if not args.no_codex:
        codex_files = codex_files_in_window(args.codex_src, cutoff)
        codex_found = 0
        for fp in codex_files:
            resultado = parse_codex_file(fp, cutoff, marker)
            if resultado is None:
                continue
            sid, first_ts, user_msgs, asst_msgs = resultado
            skipped_old, skipped_empty = processar_sessao(
                sid, first_ts, user_msgs, asst_msgs,
                args.out, cutoff, marker, manifest, skipped_old, skipped_empty,
                prefix="codex__"
            )
            codex_found += 1
        if codex_found:
            print(f"codex: {codex_found} rollouts encontrados")

    manifest.sort()
    with open(os.path.join(args.out, "_manifest.txt"), "w", encoding="utf-8") as m:
        m.write("ts_key | arquivo | turnos_user_reais | bytes\n")
        for safe_ts, name, nu, sz in manifest:
            m.write(f"{safe_ts} | {name} | {nu} | {sz}\n")

    # grava marcador com o timestamp da sessao mais recente processada
    if manifest:
        ts_mais_recente = max(x[0] for x in manifest)
        # converte safe_ts (14 digits AAAAMMDDHHMMSS) de volta pra ISO
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
