#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
snapshot_memoria.py — trava anti-sobrescrita da memoria (PreToolUse em Write/Edit).

O auto-memory em ~/.claude/projects/<proj>/memory/ nao tem git nem backup: um Write
por cima apaga o antigo pra sempre. Este hook intercepta Write/Edit ANTES de gravar
e, se o alvo e um arquivo de memoria que JA EXISTE, copia a versao atual pra uma
pasta de snapshots datada. Nunca bloqueia (exit 0 sempre); so preserva.

Snapshots vivem em <memory>/.historico/<arquivo>/<timestamp>.md — fora do indice,
invisivel, recuperavel. Mantem os ultimos N por arquivo (poda o excesso pra nao inchar).

Retorno: exit 0 SEMPRE (rede de protecao, nunca atrapalha o trabalho).
"""
import json
import sys
import shutil
import time
import pathlib

# Quantas versoes antigas guardar por arquivo (alem da atual). Poda o resto.
MANTER = 15

# So protege arquivos cujo caminho passa por uma destas pastas (memoria de verdade).
MARCADORES = ("/memory/", "\\memory\\", "/memoria/", "\\memoria\\")


def _e_memoria(path: str) -> bool:
    p = path.replace("\\", "/").lower()
    if not p.endswith(".md"):
        return False
    if "/.historico/" in p:           # nao snapshotar o proprio snapshot
        return False
    return any(m.replace("\\", "/") in p for m in MARCADORES)


def _snapshot(alvo: pathlib.Path):
    """Copia a versao ATUAL de alvo pra <memory>/.historico/<nome>/<ts>.md antes de ser sobrescrita."""
    if not alvo.is_file():
        return  # arquivo novo: nada a preservar
    hist = alvo.parent / ".historico" / alvo.stem
    hist.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    destino = hist / f"{ts}.md"
    # nao duplicar se o conteudo e identico ao snapshot mais recente
    try:
        atuais = sorted(hist.glob("*.md"))
        if atuais and atuais[-1].read_bytes() == alvo.read_bytes():
            return
    except Exception:
        pass
    try:
        shutil.copy2(alvo, destino)
    except Exception:
        return
    # poda: mantem so os MANTER mais recentes
    try:
        snaps = sorted(hist.glob("*.md"))
        for velho in snaps[:-MANTER]:
            velho.unlink()
    except Exception:
        pass


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool = payload.get("tool_name", "")
    if tool not in ("Write", "Edit"):
        sys.exit(0)

    ti = payload.get("tool_input", {}) or {}
    fpath = ti.get("file_path") or ti.get("path") or ""
    if not fpath or not _e_memoria(fpath):
        sys.exit(0)

    try:
        _snapshot(pathlib.Path(fpath))
    except Exception:
        pass  # rede de protecao: erro aqui jamais trava o Write
    sys.exit(0)


if __name__ == "__main__":
    main()
