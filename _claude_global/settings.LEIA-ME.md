# settings.json — instruções de instalação

O arquivo `settings.json` nesta pasta é um TEMPLATE. Antes de usar, você precisa substituir
os placeholders e mesclar o conteúdo no seu settings.json real do Claude Code.

## O que substituir

Localize todas as ocorrências de `{{CAMINHO_CLAUDE}}` e troque pelo caminho absoluto da
pasta `.claude` do seu usuário. Exemplos por sistema operacional:

- Windows: `C:/Users/SEU_USUARIO/.claude`
- macOS/Linux: `/home/SEU_USUARIO/.claude` ou `/Users/SEU_USUARIO/.claude`

Use barras normais `/` mesmo no Windows (o Claude Code aceita ambas, mas `/` é mais seguro
em JSON).

## Hooks registrados no settings.json

Lista completa dos hooks que este template registra, por evento. Cada entrada mostra o evento,
o matcher e se o script tem placeholder próprio além do `{{CAMINHO_CLAUDE}}`.

**PreToolUse — matcher `Bash|PowerShell`:**

- `guarda_seguranca.py` — bloqueia comandos destrutivos óbvios antes de executar.
  Placeholder: nenhum além do `{{CAMINHO_CLAUDE}}` do settings.

**PreToolUse — matcher `Write|Edit`:**

- `snapshot_memoria.py` — salva snapshot da versão anterior antes de sobrescrever qualquer
  arquivo dentro de `/memory/` ou `/memoria/` (anti-perda; mantém as últimas 15 versões em
  `.historico/`). Placeholder: nenhum além do `{{CAMINHO_CLAUDE}}`.
- `guardiao_escrita.py` — detecta se outra sessão tocou o mesmo arquivo nos últimos 15 min
  e avisa no stderr, além de salvar snapshot (anti-colisão entre janelas paralelas).
  Placeholder: nenhum além do `{{CAMINHO_CLAUDE}}`.

**UserPromptSubmit:**

- `captura_regra.py` — detecta sinais de regra/preferência durável no prompt e alerta o
  Claude para avaliar se deve gravar na memória. Na 3ª repetição do mesmo pedido, injeta
  aviso no contexto. Placeholder: **`{{CAMINHO_MEMORIA}}`** (log de repetições).
- `captura_feedback.py` — captura silenciosamente elogio, crítica, erro ou acerto no prompt
  e grava em `_feedback.log` para destilação posterior. Nunca injeta nada no contexto.
  Placeholder: **`{{CAMINHO_MEMORIA}}`** (caminho do log).

**SessionStart:**

- `nudge_destilacao.py` — verifica se há sessões pendentes de destilação e injeta aviso
  discreto. Placeholder: **`{{CAMINHO_MEMORIA}}`**.
- `sync_pull.py` — puxa o que outra máquina enviou via git pull. Placeholder:
  **`{{REPO_SYNC}}`**. Opcional: só se usa mais de um dispositivo.

Hooks como handoff, referências e tamanho de memória ficam fora do boot por padrão. Rode sob
demanda ou com `--emit` quando precisar auditar, sem gastar contexto em toda sessão.

**PreCompact — matcher `auto`:**

- `precompact_flush.py` — registra rastro da sessão antes de compactar, para não perder
  contexto no loop de aprendizado. Placeholder: **`{{CAMINHO_MEMORIA}}`**.

**SessionEnd:**

- `registrar_sessao.py` — registra a sessão no log de pendentes (pertence à skill
  fecha-sessao). Placeholder: **`{{CAMINHO_MEMORIA}}`**.
- `sync_push.py` — aplica trava anti-segredo e envia o que mudou via git push. Placeholder:
  **`{{REPO_SYNC}}`**. Opcional: só se usa mais de um dispositivo.

---

Se você NÃO usa sync entre dispositivos, remova do `settings.json` as entradas de
`sync_pull.py` e `sync_push.py`. Se usa, rode a skill `/sync` pra configurar o repo PRIVADO
primeiro e ajuste o `{{REPO_SYNC}}` dentro dos dois scripts.

NÃO estão incluídos hooks de roteamento de cliente, statusline e monitor de contexto: dependem
de configuração pessoal e ficam fora do template.

## Como mesclar

Se você ainda não tem um `settings.json` no seu `~/.claude/`, copie este arquivo direto
(depois de substituir os placeholders).

Se já tem um `settings.json`, mescle a seção `"hooks"` manualmente: copie cada entrada
de hook para dentro do seu arquivo existente, sem sobrescrever o que já está lá.

## Placeholders nos scripts dos hooks

Além do `{{CAMINHO_CLAUDE}}` no settings.json (que aponta onde os hooks estão instalados),
os scripts têm placeholders próprios que precisam ser trocados diretamente nos arquivos `.py`.
Cada arquivo tem um comentário `# CONFIGURE:` marcando o lugar exato.

**`{{CAMINHO_MEMORIA}}`** — pasta `memory/` do seu projeto CORTEX OS. Exemplo:

```text
C:\Users\SEU_USUARIO\.claude\projects\c--MeuProjeto\memory
```

O caminho deve bater com onde o Claude Code armazena a memória do projeto (pasta
`.claude/projects/` dentro do `~/.claude`, com o nome da pasta do projeto).

Deve ser trocado em todos os arquivos abaixo:

- `hooks/precompact_flush.py`
- `hooks/nudge_destilacao.py`
- `hooks/guarda_tamanho_memoria.py`
- `hooks/captura_regra.py`
- `hooks/captura_feedback.py`
- `skills/fecha-sessao/scripts/registrar_sessao.py`

(`sync_push.py`/`sync_pull.py` usam `{{REPO_SYNC}}`, não `{{CAMINHO_MEMORIA}}` — veja abaixo.)

**`{{PASTA_REFERENCIAS}}`** — pasta onde você joga material de referência pra ingerir. Exemplo:
`C:\CORTEX\referencias`. Deve ser trocado em: `hooks/nudge_referencias.py`, caso voce
ative auditoria de referencias sob demanda.
