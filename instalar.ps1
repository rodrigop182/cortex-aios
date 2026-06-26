# =============================================================================
# CORTEX OS - instalador (Windows PowerShell)
# Uso: .\instalar.ps1 [-Lite] [-Hooks] [-Destino "C:\caminho\da\memoria"]
# =============================================================================

param(
    [switch]$Lite,
    [switch]$Hooks,
    [string]$Destino = ""
)

# -----------------------------------------------------------------------------
# Helpers de saída colorida
# -----------------------------------------------------------------------------
function Ok   { param($Msg) Write-Host "[OK] $Msg" -ForegroundColor Green }
function Info { param($Msg) Write-Host "[..] $Msg" -ForegroundColor Yellow }
function Erro { param($Msg) Write-Host "[ERRO] $Msg" -ForegroundColor Red }

# Carimbo de data pro nome da pasta de backup (uma vez por execucao)
$Carimbo = Get-Date -Format "yyyyMMdd-HHmmss"

# -----------------------------------------------------------------------------
# Copia de origem -> destino preservando o que ja existe no destino.
# Antes de sobrescrever um arquivo, move a versao do usuario pra um backup.
# Assim nunca apagamos uma skill/agent/hook proprio do usuario sem copia.
# -----------------------------------------------------------------------------
function Copiar-ComBackup {
    param(
        [string]$Origem,   # pasta fonte (ex: ...\_claude_global\skills)
        [string]$Destino,  # pasta destino (ex: ~\.claude\skills)
        [string]$Rotulo    # "skills" | "agents" | "hooks" (so pro nome do backup)
    )

    if (-not (Test-Path $Destino)) {
        New-Item -ItemType Directory -Path $Destino -Force | Out-Null
    }

    $PastaBackup = Join-Path $ClaudeDir "_backup-cortex-$Carimbo\$Rotulo"
    # Pula __pycache__/.pyc e a pasta-placeholder {{CAMINHO_MEMORIA}} (seeds de log que
    # viajam dentro de hooks/ mas NAO devem ser copiados literal pros hooks vivos: o lugar
    # deles e a pasta de memoria resolvida, nao ~/.claude/hooks).
    $Itens = Get-ChildItem -Path $Origem -Recurse -File |
        Where-Object {
            $_.FullName -notmatch '\\__pycache__\\' -and
            $_.Extension -ne '.pyc' -and
            $_.FullName -notmatch '\\\{\{CAMINHO_MEMORIA\}\}\\'
        }

    foreach ($Item in $Itens) {
        # caminho relativo a partir da pasta de origem
        $Rel = $Item.FullName.Substring($Origem.Length).TrimStart('\')
        $Alvo = Join-Path $Destino $Rel

        # se ja existe no destino, faz backup antes de sobrescrever
        if (Test-Path $Alvo) {
            $AlvoBackup = Join-Path $PastaBackup $Rel
            $DirBackup = Split-Path $AlvoBackup -Parent
            if (-not (Test-Path $DirBackup)) {
                New-Item -ItemType Directory -Path $DirBackup -Force | Out-Null
            }
            Copy-Item -Path $Alvo -Destination $AlvoBackup -Force
        }

        # garante a subpasta no destino e copia
        $DirAlvo = Split-Path $Alvo -Parent
        if (-not (Test-Path $DirAlvo)) {
            New-Item -ItemType Directory -Path $DirAlvo -Force | Out-Null
        }
        Copy-Item -Path $Item.FullName -Destination $Alvo -Force
    }

    if (Test-Path $PastaBackup) {
        Info "Backup dos arquivos sobrescritos em: $PastaBackup"
    }
}

# -----------------------------------------------------------------------------
# Backup de um arquivo unico (ex: CLAUDE.md) antes de sobrescrever.
# Salva a versao do usuario em ~/.claude/_backup-cortex-<data>/<rotulo>.
# -----------------------------------------------------------------------------
function Backup-Arquivo {
    param(
        [string]$Caminho,  # arquivo que sera sobrescrito
        [string]$Rotulo    # nome com que guardar no backup (ex: "CLAUDE.md")
    )
    if (-not (Test-Path $Caminho)) { return }
    $PastaBackup = Join-Path $ClaudeDir "_backup-cortex-$Carimbo"
    if (-not (Test-Path $PastaBackup)) {
        New-Item -ItemType Directory -Path $PastaBackup -Force | Out-Null
    }
    $AlvoBackup = Join-Path $PastaBackup $Rotulo
    Copy-Item -Path $Caminho -Destination $AlvoBackup -Force
    Info "Backup do anterior em: $AlvoBackup"
}

# -----------------------------------------------------------------------------
# Resolve {{CAMINHO_CLAUDE}} num arquivo, preservando UTF-8 SEM BOM.
# (PS 5.1 Set-Content -Encoding UTF8 mete BOM e Get/Set corrompe acento PT-BR; por
# isso usa-se [IO.File] com UTF8Encoding($false).) Idempotente: so toca se achar o token.
# -----------------------------------------------------------------------------
function Resolve-CaminhoClaude {
    param(
        [string]$Arquivo,      # arquivo a tratar
        [string]$ValorClaude   # caminho real de ~/.claude, com barras "/"
    )
    if (-not (Test-Path $Arquivo)) { return }
    $enc = New-Object System.Text.UTF8Encoding($false)
    $txt = [System.IO.File]::ReadAllText($Arquivo, $enc)
    if ($txt -like '*{{CAMINHO_CLAUDE}}*') {
        $txt = $txt.Replace('{{CAMINHO_CLAUDE}}', $ValorClaude)
        [System.IO.File]::WriteAllText($Arquivo, $txt, $enc)
    }
}

# -----------------------------------------------------------------------------
# Valores padrão
# -----------------------------------------------------------------------------
$Modo = if ($Lite) { "lite" } else { "full" }

# Pasta CORTEX (sua pasta de trabalho fixa): se não informado, usa C:\CORTEX.
# É a pasta que você ABRE SEMPRE no VSCode. Cravar um caminho fixo é o que faz a
# memória e as skills te seguirem: o Claude Code indexa memória e skills POR PASTA.
if ($Destino -eq "") {
    $Destino = "C:\CORTEX"
}

# Pasta raiz do CORTEX OS clonado (onde este script está)
$CortexDir = $PSScriptRoot

# Pasta global do Claude Code
$ClaudeDir = Join-Path $env:USERPROFILE ".claude"

# -----------------------------------------------------------------------------
# Cabeçalho
# -----------------------------------------------------------------------------
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " CORTEX OS - instalacao" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " Modo     : $Modo"
Write-Host " Pasta    : $Destino" -NoNewline
Write-Host "  (abra SEMPRE esta pasta no VSCode)" -ForegroundColor Yellow
Write-Host " Hooks    : $(if ($Hooks) { 'sim' } else { 'nao' })"
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# -----------------------------------------------------------------------------
# Verifica pré-requisitos
# -----------------------------------------------------------------------------
Info "Verificando pre-requisitos..."

$PastaGlobal = Join-Path $CortexDir "_claude_global"
if (-not (Test-Path $PastaGlobal)) {
    Erro "Pasta _claude_global nao encontrada em $CortexDir."
    Erro "Execute este script a partir da raiz do repositorio CORTEX OS clonado."
    exit 1
}

if (-not (Test-Path $ClaudeDir)) {
    Info "Pasta ~/.claude nao encontrada. Criando..."
    New-Item -ItemType Directory -Path $ClaudeDir -Force | Out-Null
    Ok "$ClaudeDir criada."
}

# -----------------------------------------------------------------------------
# 1. Cerebro global (CLAUDE.md)
# -----------------------------------------------------------------------------
Info "Instalando cerebro global (modo $Modo)..."

$ArquivoCerebro = if ($Modo -eq "lite") {
    Join-Path $CortexDir "lite\CLAUDE-LITE.md"
} else {
    Join-Path $CortexDir "_claude_global\CLAUDE.md"
}

if (-not (Test-Path $ArquivoCerebro)) {
    Erro "Arquivo $ArquivoCerebro nao encontrado. Verifique o repositorio."
    exit 1
}

$DestinoCerebro = Join-Path $ClaudeDir "CLAUDE.md"

if (Test-Path $DestinoCerebro) {
    Write-Host ""
    Write-Host "ATENCAO:" -ForegroundColor Yellow -NoNewline
    Write-Host " Ja existe um arquivo em $DestinoCerebro."
    Write-Host "Sobrescrever vai substituir seu CLAUDE.md atual pelo do CORTEX OS."
    $Resposta = Read-Host "Deseja sobrescrever? (s/N)"
    if ($Resposta -match "^[sS]$") {
        Backup-Arquivo -Caminho $DestinoCerebro -Rotulo "CLAUDE.md"
        Copy-Item -Path $ArquivoCerebro -Destination $DestinoCerebro -Force
        Ok "CLAUDE.md instalado (modo $Modo)."
    } else {
        Info "Pulando instalacao do CLAUDE.md. O existente foi mantido."
    }
} else {
    Copy-Item -Path $ArquivoCerebro -Destination $DestinoCerebro -Force
    Ok "CLAUDE.md instalado (modo $Modo)."
}

# -----------------------------------------------------------------------------
# 2. Skills globais
# -----------------------------------------------------------------------------
Info "Instalando skills globais..."

$PastaSkills = Join-Path $CortexDir "_claude_global\skills"
if (Test-Path $PastaSkills) {
    $DestinoSkills = Join-Path $ClaudeDir "skills"
    Copiar-ComBackup -Origem $PastaSkills -Destino $DestinoSkills -Rotulo "skills"
    Ok "Skills copiadas para $DestinoSkills"
} else {
    Info "Pasta _claude_global\skills nao encontrada. Pulando."
}

# -----------------------------------------------------------------------------
# 3. Agents globais
# -----------------------------------------------------------------------------
Info "Instalando agents globais..."

$PastaAgents = Join-Path $CortexDir "_claude_global\agents"
if (Test-Path $PastaAgents) {
    $DestinoAgents = Join-Path $ClaudeDir "agents"
    Copiar-ComBackup -Origem $PastaAgents -Destino $DestinoAgents -Rotulo "agents"
    Ok "Agents copiados para $DestinoAgents"
} else {
    Info "Pasta _claude_global\agents nao encontrada. Pulando."
}

# -----------------------------------------------------------------------------
# 4. Hooks (opcional, -Hooks)
# -----------------------------------------------------------------------------
if ($Hooks) {
    Info "Instalando hooks..."
    $PastaHooks = Join-Path $CortexDir "_claude_global\hooks"
    if (Test-Path $PastaHooks) {
        $DestinoHooks = Join-Path $ClaudeDir "hooks"
        Copiar-ComBackup -Origem $PastaHooks -Destino $DestinoHooks -Rotulo "hooks"
        Ok "Hooks copiados para $DestinoHooks"

        # settings.json REGISTRA os hooks. Sem ele, nenhum hook roda (era o furo do
        # fallback manual). NUNCA sobrescreve um settings.json existente (pode ter sua
        # config): nesse caso, instrui o merge manual da secao "hooks".
        $ClaudeSlash = $ClaudeDir.Replace('\', '/')
        $SettingsFonte = Join-Path $CortexDir "_claude_global\settings.json"
        $SettingsDestino = Join-Path $ClaudeDir "settings.json"
        if (Test-Path $SettingsFonte) {
            if (Test-Path $SettingsDestino) {
                Info "Ja existe um settings.json - NAO vou sobrescrever (pode ter sua config)."
                Write-Host "  Para ATIVAR os hooks, mescle a secao 'hooks' de:" -ForegroundColor Yellow
                Write-Host "    $SettingsFonte" -ForegroundColor Cyan
                Write-Host "  no seu $SettingsDestino (troque {{CAMINHO_CLAUDE}} por $ClaudeSlash)."
            } else {
                Copy-Item $SettingsFonte $SettingsDestino -Force
                Resolve-CaminhoClaude -Arquivo $SettingsDestino -ValorClaude $ClaudeSlash
                Ok "settings.json instalado (hooks registrados; {{CAMINHO_CLAUDE}} resolvido)."
            }
        } else {
            Info "settings.json nao encontrado no pacote - hooks nao serao registrados."
        }

        # Resolve {{CAMINHO_CLAUDE}} nos .py copiados (hooks + skills), preservando UTF-8.
        Get-ChildItem -Path $DestinoHooks -Recurse -Filter *.py -ErrorAction SilentlyContinue |
            ForEach-Object { Resolve-CaminhoClaude -Arquivo $_.FullName -ValorClaude $ClaudeSlash }
        $DestinoSkills = Join-Path $ClaudeDir "skills"
        if (Test-Path $DestinoSkills) {
            Get-ChildItem -Path $DestinoSkills -Recurse -Filter *.py -ErrorAction SilentlyContinue |
                ForEach-Object { Resolve-CaminhoClaude -Arquivo $_.FullName -ValorClaude $ClaudeSlash }
        }

        Write-Host ""
        Write-Host "Falta 1 ajuste manual (caminho da auto-memoria):" -ForegroundColor Yellow
        Write-Host "  Troque {{CAMINHO_MEMORIA}} pelo caminho da sua pasta de memoria"
        Write-Host "  (~/.claude/projects/<id-da-pasta>/memory) nos hooks de aprendizado e em"
        Write-Host "  skills/fecha-sessao/scripts/registrar_sessao.py. Detalhe no INSTALAR.md."
        Write-Host "  Sem isso, captura de regra e fila de sessoes ficam inativas (o resto roda)."
    } else {
        Info "Pasta _claude_global\hooks nao encontrada. Pulando."
    }
} else {
    Info "Hooks ignorados (passe -Hooks para instala-los)."
}

# -----------------------------------------------------------------------------
# 5. Memoria + pasta de trabalho (instalada FLAT na raiz do CORTEX)
# -----------------------------------------------------------------------------
Info "Instalando o CORTEX em $Destino (sua pasta de trabalho fixa)..."

$PastaMemoriaFonte = Join-Path $CortexDir "memoria"
if (-not (Test-Path $PastaMemoriaFonte)) {
    Info "Pasta memoria nao encontrada no repositorio. Pulando."
} else {
    # Verifica se o destino existe e tem conteudo
    $DestinoExiste = Test-Path $Destino
    $DestinoTemConteudo = $DestinoExiste -and ((Get-ChildItem -Path $Destino -ErrorAction SilentlyContinue | Measure-Object).Count -gt 0)

    if ($DestinoTemConteudo) {
        Write-Host ""
        Write-Host "ATENCAO:" -ForegroundColor Yellow -NoNewline
        Write-Host " A pasta $Destino ja existe e nao esta vazia."
        $RespostaMem = Read-Host "Copiar o conteudo por cima? Arquivos com mesmo nome serao sobrescritos (os seus vao pro backup). (s/N)"
        if ($RespostaMem -match "^[sS]$") {
            Copiar-ComBackup -Origem $PastaMemoriaFonte -Destino $Destino -Rotulo "memoria"
            Ok "Memoria copiada para $Destino"
        } else {
            Info "Memoria nao instalada. O diretorio existente foi mantido."
        }
    } else {
        if (-not $DestinoExiste) {
            New-Item -ItemType Directory -Path $Destino -Force | Out-Null
        }
        Copy-Item -Path "$PastaMemoriaFonte\*" -Destination $Destino -Recurse -Force
        Ok "Memoria instalada em $Destino"
    }
}

# -----------------------------------------------------------------------------
# 6. Aviso na raiz: ABRA SEMPRE ESTA PASTA
# Cravar a pasta de trabalho e gritar isso na raiz e o que evita o problema
# da "memoria que nao segue": o Claude Code indexa memoria/skills POR PASTA.
# -----------------------------------------------------------------------------
if (Test-Path $Destino) {
    $Aviso = @"
# ABRA SEMPRE ESTA PASTA NO VSCODE

> **Esta e a pasta-cerebro do seu CORTEX:** ``$Destino``

Toda vez que for trabalhar com o Claude Code, abra **esta pasta** no VSCode
(menu **Arquivo > Abrir Pasta...** e escolha ``$Destino``).

## Por que sempre a mesma pasta

O Claude Code guarda sua memoria e suas skills **por pasta**. Se voce abrir
uma pasta diferente a cada dia, ele perde o fio: a memoria do que aprendeu e
as skills (/onboard, /regras, /audit...) **nao aparecem**. Abrindo SEMPRE
``$Destino``, seu CORTEX te conhece e funciona em cheio toda vez.

## Dica

No VSCode, fixe esta pasta: **Arquivo > Adicionar Pasta ao Espaco de Trabalho**
e salve o workspace. Assim ela abre sozinha.
"@
    $CaminhoAviso = Join-Path $Destino "_ABRA-ESTA-PASTA-NO-VSCODE.md"
    [System.IO.File]::WriteAllText($CaminhoAviso, $Aviso, (New-Object System.Text.UTF8Encoding($false)))
    Ok "Aviso criado: $CaminhoAviso"
}

# -----------------------------------------------------------------------------
# Instrucoes finais
# -----------------------------------------------------------------------------
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " CORTEX OS instalado." -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Proximos passos:"
Write-Host ""
Write-Host "  1. Abra o VSCode SEMPRE nesta pasta (Arquivo > Abrir Pasta):"
Write-Host "     $Destino" -ForegroundColor Cyan
Write-Host "     (leia o _ABRA-ESTA-PASTA-NO-VSCODE.md la dentro)"
Write-Host ""
if ($Hooks) {
    Write-Host "  2. Ajuste os hooks (procure '# CONFIGURE:' nos arquivos em ~/.claude/hooks/)."
    Write-Host "     Aponte o caminho da memoria para: $Destino" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  3. Com o Claude Code aberto NESSA pasta, rode:"
} else {
    Write-Host "  2. Com o Claude Code aberto NESSA pasta, rode:"
}
Write-Host "     /onboard" -ForegroundColor Green
Write-Host ""
Write-Host "     A entrevista leva ~5 minutos e preenche seus dados."
Write-Host ""
Write-Host "  Duvidas: veja INSTALAR.md e lite/MODO-LITE.md no repositorio."
Write-Host ""
