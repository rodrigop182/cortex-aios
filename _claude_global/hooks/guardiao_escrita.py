#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
guardiao_escrita.py — trava anti-colisao entre chats (PreToolUse em Write/Edit).

Roda com varios chats em paralelo; dois agentes editando o mesmo arquivo corrompe
trabalho em silencio. Este hook, ANTES de cada Write/Edit:

  1. Consulta um indice leve (arquivo -> ultimo {session, hora} que escreveu nele).
  2. Se OUTRA sessao tocou esse mesmo arquivo nos ultimos JANELA_MIN minutos -> AVISA FORTE
     (stderr, exit 0; deixa gravar) e salva um SNAPSHOT do estado atual (recuperavel).
  3. Registra a propria escrita no indice (pra o proximo chat ver).

Decisao: AVISAR + snapshot, NAO bloquear (nao travar o fluxo; nada se perde porque
ha backup). Exit 0 sempre, com a mensagem de aviso no stderr quando ha colisao.

Sem dependencia externa (stdlib). Indice e snapshots vivem em ~/.claude/.atividade/.
"""
import json
import sys
import time
import shutil
import pathlib

BASE = pathlib.Path.home() / ".claude" / ".atividade"
INDICE = BASE / "_atividade-arquivos.json"
SNAP_DIR = BASE / "snapshots"
JANELA_MIN = 15          # outra sessao tocou nos ultimos N min = colisao
GC_HORAS = 48            # entradas do indice mais velhas que isto sao descartadas


def _carregar():
    try:
        return json.loads(INDICE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _salvar(idx: dict):
    try:
        BASE.mkdir(parents=True, exist_ok=True)
        INDICE.write_text(json.dumps(idx, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


def _norm(p: str) -> str:
    return str(pathlib.Path(p.replace("\\", "/"))).lower()


def _snapshot(alvo: pathlib.Path):
    """Backup do estado atual do arquivo antes de uma escrita em colisao (recuperavel)."""
    if not alvo.is_file():
        return None
    try:
        SNAP_DIR.mkdir(parents=True, exist_ok=True)
        ts = time.strftime("%Y%m%d-%H%M%S")
        destino = SNAP_DIR / f"{alvo.stem}__{ts}{alvo.suffix}"
        shutil.copy2(alvo, destino)
        return destino
    except Exception:
        return None


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if payload.get("tool_name", "") not in ("Write", "Edit"):
        sys.exit(0)

    ti = payload.get("tool_input", {}) or {}
    fpath = ti.get("file_path") or ti.get("path") or ""
    if not fpath:
        sys.exit(0)

    sessao = payload.get("session_id", "?")
    agora = time.time()
    chave = _norm(fpath)

    idx = _carregar()
    # GC: remove entradas velhas (nao deixa o indice crescer pra sempre)
    idx = {k: v for k, v in idx.items()
           if isinstance(v, dict) and (agora - v.get("hora", 0)) < GC_HORAS * 3600}

    anterior = idx.get(chave)
    colisao = (
        anterior
        and anterior.get("sessao") != sessao
        and (agora - anterior.get("hora", 0)) < JANELA_MIN * 60
    )

    if colisao:
        mins = int((agora - anterior["hora"]) / 60)
        snap = _snapshot(pathlib.Path(fpath))
        msg = (
            "AVISO DE COLISAO ENTRE CHATS (CORTEX OS).\n"
            f"Outro chat (sessao {anterior['sessao'][:8]}) escreveu neste MESMO arquivo ha {mins} min:\n"
            f"  {fpath}\n"
            "Voce pode estar sobrescrevendo trabalho de outra janela aberta. "
            "A escrita VAI prosseguir e um backup do estado atual foi salvo"
            + (f" em {snap}" if snap else "")
            + ".\nSe nao era pra mexer aqui, PARE e confirme qual chat e o dono deste arquivo."
        )
        print(msg, file=sys.stderr)

    # registra a propria escrita (sempre)
    idx[chave] = {"sessao": sessao, "hora": agora, "path": fpath}
    _salvar(idx)

    # exit 0: nunca bloqueia (avisar, nao travar). O aviso ja foi pro stderr.
    sys.exit(0)


if __name__ == "__main__":
    main()
