#!/usr/bin/env bash
# =============================================================================
# CORTEX OS — atualizador (macOS / Linux)
# Troca SO a camada de produto; preserva o dado do usuario (memoria, voz, nicho).
# Uso:
#   ./atualizar.sh --novo /caminho/do/CORTEX-novo [--instalado ~/CORTEX] [--aplicar]
# Sem --aplicar = dry-run (so mostra o plano). Confira e rode de novo com --aplicar.
# =============================================================================
set -euo pipefail

NOVO=""
INSTALADO=""
APLICAR=0

while [ $# -gt 0 ]; do
    case "$1" in
        --novo)       NOVO="$2"; shift 2 ;;
        --instalado)  INSTALADO="$2"; shift 2 ;;
        --aplicar)    APLICAR=1; shift ;;
        *) echo "[ERRO] argumento desconhecido: $1"; exit 1 ;;
    esac
done

if [ -z "$NOVO" ]; then
    echo "[ERRO] --novo e obrigatorio (raiz do CORTEX novo, descompactado)."
    exit 1
fi

MOTOR="$NOVO/_claude_global/skills/atualizar/scripts/atualizar.py"
if [ ! -f "$MOTOR" ]; then
    echo "[ERRO] Nao achei o motor em: $MOTOR"
    echo "[ERRO] Confirme que --novo aponta pra raiz do CORTEX novo."
    exit 1
fi

if [ -z "$INSTALADO" ]; then
    INSTALADO="$HOME/CORTEX"
    echo "[..] instalado nao informado; assumindo: $INSTALADO"
fi
if [ ! -d "$INSTALADO" ]; then
    echo "[ERRO] pasta instalada nao encontrada: $INSTALADO"
    exit 1
fi

PY="$(command -v python3 || command -v python)"

echo ""
echo "============================================"
echo " CORTEX OS - atualizacao"
echo "============================================"
echo ""

if [ "$APLICAR" -eq 1 ]; then
    echo "[..] Aplicando (com backup automatico antes)..."
    "$PY" "$MOTOR" --instalado "$INSTALADO" --novo "$NOVO" --yes
else
    echo "[..] DRY-RUN (nada sera escrito). Rode com --aplicar depois de conferir."
    "$PY" "$MOTOR" --instalado "$INSTALADO" --novo "$NOVO" --dry-run
fi
