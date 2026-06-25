#!/usr/bin/env bash
# =============================================================================
# CORTEX OS — instalador (Mac/Linux/Git-Bash)
# Uso: bash instalar.sh [--lite] [--hooks] [--destino /caminho/da/memoria]
# =============================================================================

set -euo pipefail

# -----------------------------------------------------------------------------
# Cores e helpers
# -----------------------------------------------------------------------------
VERDE="\033[0;32m"
AMARELO="\033[1;33m"
VERMELHO="\033[0;31m"
RESET="\033[0m"

ok()   { echo -e "${VERDE}[OK]${RESET} $*"; }
info() { echo -e "${AMARELO}[..] $*${RESET}"; }
erro() { echo -e "${VERMELHO}[ERRO] $*${RESET}" >&2; }

# Carimbo de data pro nome da pasta de backup (uma vez por execução)
CARIMBO="$(date +%Y%m%d-%H%M%S)"

# -----------------------------------------------------------------------------
# Copia origem -> destino preservando o que já existe no destino.
# Antes de sobrescrever um arquivo, move a versão do usuário pra um backup.
# Nunca apagamos uma skill/agent/hook próprio do usuário sem cópia.
# -----------------------------------------------------------------------------
copiar_com_backup() {
  local origem="$1"   # pasta fonte
  local destino="$2"  # pasta destino
  local rotulo="$3"   # "skills" | "agents" | "hooks" (nome do backup)

  mkdir -p "$destino"
  local pasta_backup="$HOME/.claude/_backup-cortex-$CARIMBO/$rotulo"
  local houve_backup=0

  # percorre arquivos da origem, ignorando lixo de compilação Python
  while IFS= read -r -d '' item; do
    local rel="${item#"$origem"/}"
    local alvo="$destino/$rel"

    # se já existe no destino, faz backup antes de sobrescrever
    if [ -f "$alvo" ]; then
      mkdir -p "$(dirname "$pasta_backup/$rel")"
      cp "$alvo" "$pasta_backup/$rel"
      houve_backup=1
    fi

    mkdir -p "$(dirname "$alvo")"
    cp "$item" "$alvo"
  done < <(find "$origem" -type f ! -path '*/__pycache__/*' ! -name '*.pyc' -print0)

  if [ "$houve_backup" -eq 1 ]; then
    info "Backup dos arquivos sobrescritos em: $pasta_backup"
  fi
}

# -----------------------------------------------------------------------------
# Backup de um arquivo único (ex: CLAUDE.md) antes de sobrescrever.
# Salva a versão do usuário em ~/.claude/_backup-cortex-<data>/<rótulo>.
# -----------------------------------------------------------------------------
backup_arquivo() {
  local caminho="$1"  # arquivo que será sobrescrito
  local rotulo="$2"   # nome com que guardar no backup (ex: CLAUDE.md)
  [ -f "$caminho" ] || return 0
  local pasta_backup="$HOME/.claude/_backup-cortex-$CARIMBO"
  mkdir -p "$pasta_backup"
  cp "$caminho" "$pasta_backup/$rotulo"
  info "Backup do anterior em: $pasta_backup/$rotulo"
}

# -----------------------------------------------------------------------------
# Valores padrão
# -----------------------------------------------------------------------------
MODO="full"          # --lite troca pra lite
INSTALAR_HOOKS=0     # --hooks ativa
PASTA_MEMORIA=""     # --destino <caminho> define; default: ~/CORTEX

# -----------------------------------------------------------------------------
# Parse de argumentos
# -----------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --lite)
      MODO="lite"
      shift
      ;;
    --hooks)
      INSTALAR_HOOKS=1
      shift
      ;;
    --destino)
      PASTA_MEMORIA="$2"
      shift 2
      ;;
    -h|--help)
      echo "Uso: bash instalar.sh [--lite] [--hooks] [--destino /caminho]"
      echo ""
      echo "  --lite        Instala o modo LITE (cérebro menor, ~40 linhas/turno)"
      echo "  --hooks       Instala os hooks de automação (fecha-sessao, nudge, segurança)"
      echo "  --destino     Pasta de trabalho fixa do CORTEX (padrão: ~/CORTEX)"
      exit 0
      ;;
    *)
      erro "Argumento desconhecido: $1. Use --help pra ver as opções."
      exit 1
      ;;
  esac
done

# Pasta de trabalho fixa do CORTEX (você ABRE SEMPRE esta pasta no VSCode).
# Cravar um caminho fixo é o que faz a memória e as skills te seguirem: o
# Claude Code indexa memória e skills POR PASTA.
PASTA_MEMORIA="${PASTA_MEMORIA:-$HOME/CORTEX}"

# Pasta onde este script está (raiz do CORTEX OS clonado)
CORTEX_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# -----------------------------------------------------------------------------
# Cabeçalho
# -----------------------------------------------------------------------------
echo ""
echo "============================================"
echo " CORTEX OS — instalação"
echo "============================================"
echo " Modo     : $MODO"
echo -e " Pasta    : $PASTA_MEMORIA  ${AMARELO}(abra SEMPRE esta pasta no VSCode)${RESET}"
echo " Hooks    : $([ $INSTALAR_HOOKS -eq 1 ] && echo 'sim' || echo 'não')"
echo "============================================"
echo ""

# -----------------------------------------------------------------------------
# Verifica pré-requisitos
# -----------------------------------------------------------------------------
info "Verificando pré-requisitos..."

if [ ! -d "$CORTEX_DIR/_claude_global" ]; then
  erro "Pasta _claude_global não encontrada em $CORTEX_DIR."
  erro "Execute este script a partir da raiz do repositório CORTEX OS clonado."
  exit 1
fi

if [ ! -d "$HOME/.claude" ]; then
  info "Pasta ~/.claude não encontrada. Criando..."
  mkdir -p "$HOME/.claude"
  ok "~/.claude criada."
fi

# -----------------------------------------------------------------------------
# 1. Cérebro global (CLAUDE.md)
# -----------------------------------------------------------------------------
info "Instalando cérebro global (modo $MODO)..."

if [ "$MODO" = "lite" ]; then
  FONTE_CEREBRO="$CORTEX_DIR/lite/CLAUDE-LITE.md"
else
  FONTE_CEREBRO="$CORTEX_DIR/_claude_global/CLAUDE.md"
fi

if [ ! -f "$FONTE_CEREBRO" ]; then
  erro "Arquivo $FONTE_CEREBRO não encontrado. Verifique o repositório."
  exit 1
fi

# Pede confirmação se já existe
DESTINO_CEREBRO="$HOME/.claude/CLAUDE.md"
if [ -f "$DESTINO_CEREBRO" ]; then
  echo ""
  echo -e "${AMARELO}ATENÇÃO:${RESET} Já existe um arquivo em $DESTINO_CEREBRO."
  echo "Sobrescrever vai substituir seu CLAUDE.md atual pelo do CORTEX OS."
  printf "Deseja sobrescrever? (s/N) "
  read -r RESPOSTA
  if [[ ! "$RESPOSTA" =~ ^[sS]$ ]]; then
    info "Pulando instalação do CLAUDE.md. O existente foi mantido."
  else
    backup_arquivo "$DESTINO_CEREBRO" "CLAUDE.md"
    cp "$FONTE_CEREBRO" "$DESTINO_CEREBRO"
    ok "~/.claude/CLAUDE.md instalado (modo $MODO)."
  fi
else
  cp "$FONTE_CEREBRO" "$DESTINO_CEREBRO"
  ok "~/.claude/CLAUDE.md instalado (modo $MODO)."
fi

# -----------------------------------------------------------------------------
# 2. Skills globais
# -----------------------------------------------------------------------------
info "Instalando skills globais..."

if [ -d "$CORTEX_DIR/_claude_global/skills" ]; then
  copiar_com_backup "$CORTEX_DIR/_claude_global/skills" "$HOME/.claude/skills" "skills"
  ok "Skills copiadas para ~/.claude/skills/"
else
  info "Pasta _claude_global/skills não encontrada. Pulando."
fi

# -----------------------------------------------------------------------------
# 3. Agents globais
# -----------------------------------------------------------------------------
info "Instalando agents globais..."

if [ -d "$CORTEX_DIR/_claude_global/agents" ]; then
  copiar_com_backup "$CORTEX_DIR/_claude_global/agents" "$HOME/.claude/agents" "agents"
  ok "Agents copiados para ~/.claude/agents/"
else
  info "Pasta _claude_global/agents não encontrada. Pulando."
fi

# -----------------------------------------------------------------------------
# 4. Hooks (opcional, --hooks)
# -----------------------------------------------------------------------------
if [ $INSTALAR_HOOKS -eq 1 ]; then
  info "Instalando hooks..."
  if [ -d "$CORTEX_DIR/_claude_global/hooks" ]; then
    copiar_com_backup "$CORTEX_DIR/_claude_global/hooks" "$HOME/.claude/hooks" "hooks"
    ok "Hooks copiados para ~/.claude/hooks/"
    echo ""
    echo -e "${AMARELO}Lembrete de hooks:${RESET} ajuste os caminhos marcados com"
    echo "  # CONFIGURE:  dentro dos arquivos em ~/.claude/hooks/"
    echo "  Aponte PASTA_MEMORIA para: $PASTA_MEMORIA"
  else
    info "Pasta _claude_global/hooks não encontrada. Pulando."
  fi
else
  info "Hooks ignorados (passe --hooks pra instalá-los)."
fi

# -----------------------------------------------------------------------------
# 5. Memória + pasta de trabalho (instalada FLAT na raiz do CORTEX)
# -----------------------------------------------------------------------------
info "Instalando o CORTEX em $PASTA_MEMORIA (sua pasta de trabalho fixa)..."

if [ -d "$PASTA_MEMORIA" ] && [ "$(ls -A "$PASTA_MEMORIA" 2>/dev/null)" ]; then
  echo ""
  echo -e "${AMARELO}ATENÇÃO:${RESET} A pasta $PASTA_MEMORIA já existe e não está vazia."
  printf "Copiar o conteúdo por cima? Arquivos com mesmo nome serão sobrescritos (os seus vão pro backup). (s/N) "
  read -r RESPOSTA_MEM
  if [[ ! "$RESPOSTA_MEM" =~ ^[sS]$ ]]; then
    info "Memória não instalada. O diretório existente foi mantido."
  else
    copiar_com_backup "$CORTEX_DIR/memoria" "$PASTA_MEMORIA" "memoria"
    ok "Memória copiada para $PASTA_MEMORIA"
  fi
else
  mkdir -p "$PASTA_MEMORIA"
  # "/." copia o conteúdo INCLUSIVE os ocultos (.claude/skills, .gitignore).
  # Sem o "/.", o "*" do bash pula dotfiles e as skills do motor não vão junto.
  cp -r "$CORTEX_DIR/memoria/." "$PASTA_MEMORIA/"
  ok "Memória instalada em $PASTA_MEMORIA"
fi

# -----------------------------------------------------------------------------
# 6. Aviso na raiz: ABRA SEMPRE ESTA PASTA
# Cravar a pasta de trabalho e gritar isso na raiz é o que evita o problema
# da "memória que não segue": o Claude Code indexa memória/skills POR PASTA.
# -----------------------------------------------------------------------------
if [ -d "$PASTA_MEMORIA" ]; then
  cat > "$PASTA_MEMORIA/_ABRA-ESTA-PASTA-NO-VSCODE.md" <<EOF
# ABRA SEMPRE ESTA PASTA NO VSCODE

> **Esta é a pasta-cérebro do seu CORTEX:** \`$PASTA_MEMORIA\`

Toda vez que for trabalhar com o Claude Code, abra **esta pasta** no VSCode
(menu **Arquivo > Abrir Pasta...** e escolha \`$PASTA_MEMORIA\`).

## Por que sempre a mesma pasta

O Claude Code guarda sua memória e suas skills **por pasta**. Se você abrir
uma pasta diferente a cada dia, ele perde o fio: a memória do que aprendeu e
as skills (/onboard, /regras, /audit...) **não aparecem**. Abrindo SEMPRE
\`$PASTA_MEMORIA\`, seu CORTEX te conhece e funciona em cheio toda vez.

## Dica

No VSCode, fixe esta pasta: **Arquivo > Adicionar Pasta ao Espaço de Trabalho**
e salve o workspace. Assim ela abre sozinha.
EOF
  ok "Aviso criado: $PASTA_MEMORIA/_ABRA-ESTA-PASTA-NO-VSCODE.md"
fi

# -----------------------------------------------------------------------------
# Instruções finais
# -----------------------------------------------------------------------------
echo ""
echo "============================================"
echo " CORTEX OS instalado."
echo "============================================"
echo ""
echo "Próximos passos:"
echo ""
echo "  1. Abra o VSCode SEMPRE nesta pasta (Arquivo > Abrir Pasta):"
echo "     $PASTA_MEMORIA"
echo "     (leia o _ABRA-ESTA-PASTA-NO-VSCODE.md lá dentro)"
echo ""
if [ $INSTALAR_HOOKS -eq 1 ]; then
echo "  2. Ajuste os hooks em ~/.claude/hooks/ (procure # CONFIGURE:)."
echo "     Aponte o caminho da memória para: $PASTA_MEMORIA"
echo ""
echo "  3. Com o Claude Code aberto NESSA pasta, rode:"
else
echo "  2. Com o Claude Code aberto NESSA pasta, rode:"
fi
echo "     /onboard"
echo ""
echo "     A entrevista leva ~5 minutos e preenche seus dados."
echo ""
echo "  Dúvidas: veja INSTALAR.md e lite/MODO-LITE.md no repositório."
echo ""
