# Atualizar com Codex - CORTEX OS

Use este guia quando o Codex for ajudar a aplicar uma versão nova do CORTEX.

Codex é bom para inspecionar arquivos, rodar comandos e conferir diffs. Como ele não usa os hooks do
Claude Code do mesmo jeito, trate a atualização como procedimento manual assistido.

## Regra de ouro

Dry-run primeiro. Aplicar só depois de conferir o plano.

## Três caminhos que não podem ser confundidos

- **CORTEX novo:** pasta extraída da nova versão.
- **Pasta-fonte antiga:** pasta do pacote antigo que você guardou depois de instalar. Ela tem
  `_claude_global/`, `memoria/`, `MANIFESTO-UPDATE.md` e `VERSION`.
- **Pasta CORTEX viva:** pasta que você abre no VSCode, normalmente `C:\CORTEX` ou `~/CORTEX`.

O update troca produto na pasta-fonte e, quando informado, faz deploy seguro para os lugares vivos:

- `~/.claude`;
- pasta CORTEX viva.

## Prompt para Codex

Cole isto no Codex, ajustando os caminhos:

```text
Atualize meu CORTEX preservando meus dados.

Versão nova: [CAMINHO-DO-CORTEX-NOVO].
Pasta-fonte antiga: [CAMINHO-DO-CORTEX-FONTE-ANTIGO].
Pasta CORTEX viva: [CAMINHO-DA-PASTA-CORTEX].
Pasta Claude: [CAMINHO-DA-PASTA-.CLAUDE].

Faça nesta ordem:
1. Leia MANIFESTO-UPDATE.md da versão nova.
2. Rode o atualizador em dry-run com --claude-dir e --cortex-dir.
3. Compare a versão nova com a antiga e explique TUDO que a antiga não tinha e a nova passa a ter.
4. Resuma o que será escrito, removido e preservado.
5. Mostre separadamente: (a) produto novo, (b) produto alterado, (c) dado preservado.
6. Só aplique se eu confirmar.
7. Depois confira VERSION, context/, memory/ e projects/.
```

## Comandos que o Codex deve usar

Windows:

```powershell
python "C:\caminho\do\CORTEX-novo\_claude_global\skills\atualizar\scripts\atualizar.py" --instalado "C:\caminho\do\CORTEX-fonte-antigo" --novo "C:\caminho\do\CORTEX-novo" --claude-dir "$env:USERPROFILE\.claude" --cortex-dir "C:\CORTEX" --dry-run
```

Aplicar:

```powershell
python "C:\caminho\do\CORTEX-novo\_claude_global\skills\atualizar\scripts\atualizar.py" --instalado "C:\caminho\do\CORTEX-fonte-antigo" --novo "C:\caminho\do\CORTEX-novo" --claude-dir "$env:USERPROFILE\.claude" --cortex-dir "C:\CORTEX" --yes
```

Mac/Linux/Git Bash:

```bash
python3 "/caminho/do/CORTEX-novo/_claude_global/skills/atualizar/scripts/atualizar.py" --instalado "/caminho/do/CORTEX-fonte-antigo" --novo "/caminho/do/CORTEX-novo" --claude-dir "$HOME/.claude" --cortex-dir "$HOME/CORTEX" --dry-run
```

Aplicar:

```bash
python3 "/caminho/do/CORTEX-novo/_claude_global/skills/atualizar/scripts/atualizar.py" --instalado "/caminho/do/CORTEX-fonte-antigo" --novo "/caminho/do/CORTEX-novo" --claude-dir "$HOME/.claude" --cortex-dir "$HOME/CORTEX" --yes
```

## O que o Codex deve conferir depois

- `VERSION` da pasta instalada.
- `~/.claude/CLAUDE.md` atualizado quando o dry-run indicou deploy.
- `AGENTS.md` existente na pasta CORTEX viva.
- Arquivos novos de produto que deveriam existir.
- `context/sobre-mim.md` preservado.
- `context/sobre-operacao.md` preservado.
- `context/prioridades.md` preservado.
- `memory/MEMORY.md` preservado.
- `projects/` preservado.
- backup `_backup-update-*` criado.

## O que o Codex deve EXPLICAR no dry-run

Antes de aplicar, o Codex deve entregar um resumo em linguagem simples com estas três partes:

### 1. O que o CORTEX antigo não tinha e agora passa a ter

Listar capacidade por capacidade, não só arquivo por arquivo.

Exemplo de formato:

- **Léxico operacional:** o sistema agora traduz melhor fala leiga do operador para termo técnico e sabe quando subir um problema local para capacidade sistêmica.
- **Padrão de Markdown para agente:** os `.md` agora têm critério explícito para gastar menos tokens e facilitar retrieval.
- **Filtro de generalização:** pedidos que nascem locais passam a ser avaliados por valor sistêmico antes de virarem remendo nichado.
- **Bootstrap mais enxuto no Codex:** `AGENTS.md` passa a carregar menos contexto e apontar mais para referências sob demanda.

### 2. O que mudou no comportamento do sistema

Explicar o efeito prático:

- o que o agente vai entender melhor;
- o que vai carregar menos;
- o que vai ser encontrado mais rápido;
- o que agora vira regra sistêmica em vez de ajuste local.

### 3. O que NÃO muda

Explicar explicitamente o que fica preservado:

- contexto;
- memória;
- projetos;
- decisões;
- voz;
- qualquer dado do usuário.

## Regra de qualidade da explicação

Não basta dizer "foram adicionados arquivos X e Y".

O Codex deve explicar:

- qual capacidade nova apareceu;
- qual gap antigo ela fecha;
- qual comportamento do sistema muda por causa disso;
- quais arquivos do usuário continuam intocados.

## O que o Codex não deve fazer

- Não usar `git add .`.
- Não apagar backup.
- Não sobrescrever `context/`, `memory/`, `projects/` ou `decisions/`.
- Não colocar token no comando versionado.
- Não aplicar update sem dry-run.

## Quando usar GitHub token

Se o pacote estiver em repo privado, o motor aceita `--github-repo` e `--github-token`.

Preferência segura:

- passar token por variável de ambiente;
- nunca salvar token em arquivo;
- nunca colar token em doc ou commit.
