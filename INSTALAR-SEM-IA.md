# Instalar sem IA - CORTEX OS

Use este caminho se você quer instalar o CORTEX sozinho, sem pedir para um agente fazer por você.

O instalador copia os arquivos, cria backup antes de sobrescrever e deixa uma pasta fixa para você
abrir sempre no VSCode.

## Antes de começar

Você precisa ter:

- VSCode instalado;
- Claude Code instalado e logado;
- o arquivo `CORTEX-OS.zip` baixado;
- 5 a 10 minutos para instalar e conferir.

Se você só quer testar com o menor risco possível, use o destino padrão:

- Windows: `C:\CORTEX`;
- Mac/Linux: `~/CORTEX`.

## Windows

1. Clique com o botão direito no `CORTEX-OS.zip` e escolha extrair tudo.
2. Abra a pasta extraída.
3. Clique com o botão direito em uma área vazia da pasta e escolha abrir no Terminal ou PowerShell.
4. Rode:

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force
.\instalar.ps1
```

Se quiser instalar em outra pasta:

```powershell
.\instalar.ps1 -Destino "D:\CORTEX"
```

Se aparecer pergunta sobre sobrescrever arquivo existente, leia com calma. O instalador cria backup
antes de substituir.

## Mac, Linux ou Git Bash

1. Extraia o `CORTEX-OS.zip`.
2. Abra o terminal dentro da pasta extraída.
3. Rode:

```bash
bash instalar.sh
```

Se quiser instalar em outra pasta:

```bash
bash instalar.sh --destino "$HOME/CORTEX"
```

## Depois da instalação

Abra o VSCode sempre na pasta CORTEX:

- Windows: `C:\CORTEX`;
- Mac/Linux: `~/CORTEX`;
- ou a pasta que você escolheu com `-Destino` ou `--destino`.

Dentro dessa pasta deve existir:

- `_ABRA-ESTA-PASTA-NO-VSCODE.md`;
- `intake.md`;
- `context/`;
- `.claude/skills/onboard/SKILL.md`.

## Configuração do perfil

Você tem dois caminhos.

### Caminho recomendado

Com o Claude Code aberto na pasta CORTEX, rode:

```text
/onboard
```

Ele faz a entrevista e preenche os arquivos de contexto.

### Caminho manual

Se preferir preencher sem IA, use:

- `CONFIGURAR-SEM-IA.md`;
- `intake.md`;
- `context/sobre-mim.md`;
- `context/sobre-operacao.md`;
- `context/prioridades.md`.

## Hooks avançados

Os hooks ativam automações de fechamento de sessão, segurança e destilação.

Para a primeira instalação, mantenha sem hooks. O CORTEX funciona com perfil, memória e skills locais
mesmo sem essa camada automática.

Instale hooks só depois que o básico estiver funcionando:

```powershell
.\instalar.ps1 -Hooks
```

```bash
bash instalar.sh --hooks
```

Se instalar hooks, leia `INSTALAR.md`, porque alguns caminhos precisam ser ajustados.

## Teste final

Depois de configurar, abra o Claude Code na pasta CORTEX e pergunte:

```text
no que eu devo focar esta semana?
```

Resposta boa:

- usa seu contexto;
- recomenda uma ação principal;
- explica o risco;
- pergunta só o necessário.

Se algo falhar, abra `TROUBLESHOOTING.md`.
