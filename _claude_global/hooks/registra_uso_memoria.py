#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
registra_uso_memoria.py — chamado pelo hook PostToolUse (matcher Read) do Claude Code.

INSTRUMENTACAO DE USO (FASE 5, mecanismo 1 — a fundacao da poda por evidencia).
Sem medir uso, podar regra e CHUTE. Este hook registra, 100% silencioso, toda vez que
um arquivo de memoria individual e ABERTO (Read) — sinal de que aquela regra foi
realmente consultada nesta sessao. A poda_por_evidencia.py le este log pra saber o
ULTIMO uso de cada regra e propor candidatas mortas (com gate humano, nunca sozinha).

Filtra rapido: so registra .md DENTRO da pasta de memoria, ignorando o proprio
MEMORY.md (indice, lido todo turno — uso nao significa nada) e os _*.log/_*.txt.
Append atomico (duas janelas nao se sobrescrevem). Backstage total: ZERO saida no chat.

Falha em silencio (nunca trava o turno). Ver references/auto-manutencao-memoria.md.
"""
import sys, json, os, datetime, pathlib

# CONFIGURE: troque {{CAMINHO_MEMORIA}} pelo caminho ABSOLUTO da pasta de memoria.
# O instalador resolve esse placeholder. E a MESMA pasta do MEMORY.md / captura_regra.
MEMORY_DIR = pathlib.Path(r"{{CAMINHO_MEMORIA}}")
_LOG_PATH = MEMORY_DIR / "_uso-memoria.log"
_MAX_LINHAS = 4000  # ~meses de uso; poda quando passar de 2x


def _eh_memoria_individual(fp):
    """True se fp e um arquivo .md de regra dentro da pasta de memoria (nao o indice
    nem log/baseline). Compara por pasta resolvida pra aceitar caminho abs ou relativo."""
    try:
        p = pathlib.Path(fp).resolve()
    except Exception:
        return None
    if p.suffix.lower() != ".md":
        return None
    nome = p.name
    if nome == "MEMORY.md" or nome.startswith("_"):
        return None
    try:
        if p.parent.resolve() != MEMORY_DIR.resolve():
            return None
    except Exception:
        return None
    return nome


def _gravar(slug):
    try:
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        os.makedirs(str(MEMORY_DIR), exist_ok=True)
        with open(_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"{ts}\t{slug}\n")
        _podar_se_preciso()
    except Exception:
        pass


def _podar_se_preciso():
    """Mantem as ultimas _MAX_LINHAS; so reescreve quando passar de 2x (minimiza
    janela de colisao entre processos). A poda olha o ULTIMO uso, entao cortar as
    linhas mais antigas nao perde o sinal recente."""
    try:
        if not _LOG_PATH.exists():
            return
        linhas = _LOG_PATH.read_text(encoding="utf-8").splitlines()
        if len(linhas) <= 2 * _MAX_LINHAS:
            return
        tmp = _LOG_PATH.with_suffix(".log.tmp")
        tmp.write_text("\n".join(linhas[-_MAX_LINHAS:]) + "\n", encoding="utf-8")
        os.replace(str(tmp), str(_LOG_PATH))  # atomico: nunca deixa o log corrompido
    except Exception:
        pass


def main():
    raw = sys.stdin.read()
    if not raw.strip():
        return
    try:
        raw = raw.encode("utf-8").decode("utf-8-sig")  # remove BOM se algum ambiente mandar
        data = json.loads(raw)
    except Exception:
        return
    ti = data.get("tool_input", {}) or {}
    fp = ti.get("file_path") or ti.get("path") or ""
    if not fp:
        return
    slug = _eh_memoria_individual(fp)
    if slug:
        _gravar(slug)
    # NUNCA injeta additionalContext: instrumentacao e 100% silenciosa (backstage).


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
