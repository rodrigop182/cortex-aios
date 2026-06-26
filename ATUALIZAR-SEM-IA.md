# Atualizar sem IA - CORTEX OS

Use este guia quando você recebeu uma versão nova do CORTEX e quer atualizar sem pedir para um
agente fazer por você.

O update troca só a camada de produto e preserva seus dados.

## O que fica preservado

- `context/`;
- `memory/`;
- `projects/`;
- `decisions/`;
- sua voz;
- seus nichos;
- handoffs;
- qualquer arquivo sensível.

## Antes de começar

Você precisa ter:

- pasta-fonte antiga do CORTEX, ou seja, a pasta do pacote guardada depois da instalação;
- CORTEX novo extraído em outra pasta;
- Python instalado;
- alguns minutos para ler o dry-run.

Nunca aplique direto. Rode o plano primeiro.

Importante: `C:\CORTEX` ou `~/CORTEX` é a pasta viva de trabalho. Ela guarda sua memória. A
atualização de produto é mais segura quando você aponta também a pasta-fonte antiga do pacote.

Se você não guardou a pasta-fonte antiga, peça ajuda com `ATUALIZAR-COM-CODEX.md` para conferir a
melhor rota antes de aplicar.

## Windows

Na pasta do CORTEX novo:

```powershell
.\atualizar.ps1 -Novo "C:\caminho\do\CORTEX-novo" -Instalado "C:\caminho\do\CORTEX-fonte-antigo"
```

Leia o plano.

Se estiver certo:

```powershell
.\atualizar.ps1 -Novo "C:\caminho\do\CORTEX-novo" -Instalado "C:\caminho\do\CORTEX-fonte-antigo" -Aplicar
```

## Mac, Linux ou Git Bash

Na pasta do CORTEX novo:

```bash
bash atualizar.sh --novo "/caminho/do/CORTEX-novo" --instalado "/caminho/do/CORTEX-fonte-antigo"
```

Leia o plano.

Se estiver certo:

```bash
bash atualizar.sh --novo "/caminho/do/CORTEX-novo" --instalado "/caminho/do/CORTEX-fonte-antigo" --aplicar
```

## Depois de aplicar

Confira:

- o terminal mostrou backup criado;
- `VERSION` mudou para a versão nova;
- seus arquivos em `context/` continuam preenchidos na pasta CORTEX viva;
- seus projetos continuam em `projects/`;
- `memory/MEMORY.md` continua com seu perfil compacto.

Para atualizar também os lugares vivos (`~/.claude` e a pasta CORTEX), use a rota com agente ou com
Codex em `ATUALIZAR-COM-CODEX.md`, porque ela chama o motor com `--claude-dir` e `--cortex-dir`.

## Se algo der errado

Restaure a pasta `_backup-update-...` criada pelo atualizador.

Se você não tiver certeza, pare depois do dry-run e peça ajuda.
