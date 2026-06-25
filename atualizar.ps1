# =============================================================================
# CORTEX OS — atualizador (Windows PowerShell)
# Troca SO a camada de produto; preserva o dado do usuario (memoria, voz, nicho).
# Uso:
#   .\atualizar.ps1 -Novo "C:\caminho\do\CORTEX-novo-descompactado" [-Instalado "C:\CORTEX"] [-Aplicar]
# Sem -Aplicar = dry-run (so mostra o plano). Confira e rode de novo com -Aplicar.
# =============================================================================

param(
    [Parameter(Mandatory = $true)][string]$Novo,
    [string]$Instalado = "",
    [switch]$Aplicar
)

function Ok   { param($Msg) Write-Host "[OK] $Msg" -ForegroundColor Green }
function Info { param($Msg) Write-Host "[..] $Msg" -ForegroundColor Yellow }
function Erro { param($Msg) Write-Host "[ERRO] $Msg" -ForegroundColor Red }

# A versao NOVA traz o script motor; usamos ele (logica mais recente).
$Motor = Join-Path $Novo "_claude_global\skills\atualizar\scripts\atualizar.py"
if (-not (Test-Path $Motor)) {
    Erro "Nao achei o motor de atualizacao em: $Motor"
    Erro "Confirme que -Novo aponta pra raiz do CORTEX novo (descompactado)."
    exit 1
}

# Se nao informaram o instalado, tenta a pasta de trabalho padrao do CORTEX
if ($Instalado -eq "") {
    $Instalado = "C:\CORTEX"
    Info "Instalado nao informado; assumindo: $Instalado"
}
if (-not (Test-Path $Instalado)) {
    Erro "Pasta instalada nao encontrada: $Instalado. Use -Instalado pra apontar a raiz."
    exit 1
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " CORTEX OS - atualizacao" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

if ($Aplicar) {
    Info "Aplicando (com backup automatico antes)..."
    python "$Motor" --instalado "$Instalado" --novo "$Novo" --yes
} else {
    Info "DRY-RUN (nada sera escrito). Rode com -Aplicar depois de conferir."
    python "$Motor" --instalado "$Instalado" --novo "$Novo" --dry-run
}
