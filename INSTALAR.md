# CORTEX OS - instalação

Seu cérebro de IA pessoal. Lembra quem você é, como você trabalha, e aprende a cada sessão pra
não te reexplicar nada duas vezes. Roda no Claude Code (e adaptável a outros agentes de CLI).

Tem três caminhos:

- **guiado pelo agente:** o próprio Claude Code instala pra você;
- **sem IA:** você roda `instalar.ps1` ou `instalar.sh`;
- **manual de emergência:** você copia os arquivos à mão.

Para a rota sem IA, veja [INSTALAR-SEM-IA.md](INSTALAR-SEM-IA.md). Para preencher o perfil sem
rodar `/onboard`, veja [CONFIGURAR-SEM-IA.md](CONFIGURAR-SEM-IA.md).

---

## A forma fácil (recomendada): deixe o Claude Code instalar

Você não precisa mexer em pasta nem rodar comando no terminal. Quem instala é o seu próprio
Claude Code, que você já tem.

1. Deixe o `CORTEX-OS.zip` na sua pasta de **Downloads** (não precisa descompactar).
2. Abra o Claude Code (VSCode) em qualquer pasta.
3. Cole esta mensagem e mande:

   > Instale o CORTEX OS pra mim. O arquivo CORTEX-OS.zip está na minha pasta de Downloads (se
   > não estiver, me pergunte onde está). Descompacte num lugar temporário, abra o
   > `INSTALAR-AGENTE.md` de dentro dele e siga à risca, com segurança (faça backup antes de
   > sobrescrever qualquer coisa minha) e me guiando em português a cada passo. No fim, me diga
   > exatamente o que fazer pra começar.

4. Aprove as permissões que ele pedir. Ele copia tudo pros lugares certos, ajusta o que precisa,
   e te diz o próximo passo (abrir a pasta CORTEX e rodar `/onboard`).

O que faz isso funcionar: o roteiro `INSTALAR-AGENTE.md` (dentro do pacote) guia o agente passo a
passo, com backup antes de tocar em qualquer coisa sua. O resto deste arquivo é a **instalação
manual**, caso você prefira fazer à mão ou o caminho fácil não rolar.

---

## 0. Pré-requisito

- **Claude Code** instalado (ou outro agente que leia `~/.claude/CLAUDE.md` e skills em
  `SKILL.md`). Python 3 pra os hooks (opcional, mas recomendado: é o que fecha o loop de
  aprendizado sozinho).
- **Uma pasta de trabalho FIXA, que você abre SEMPRE no VSCode.** O instalador crava
  `C:\CORTEX` (Windows) ou `~/CORTEX` (Mac/Linux). Abrir sempre a mesma pasta é o que faz a
  memória e as skills te seguirem: o Claude Code indexa as duas **por pasta**. Abriu outra pasta,
  o CORTEX não te conhece e as skills somem.

## 0.1. Rota sem IA por instalador

Essa é a rota recomendada para quem quer instalar sozinho:

- Windows: extraia o zip e rode `.\instalar.ps1` no PowerShell.
- Mac/Linux/Git Bash: extraia o zip e rode `bash instalar.sh`.

O instalador copia a memória para a pasta CORTEX, instala o cérebro global, cria backup antes de
sobrescrever e deixa um aviso na pasta que você deve abrir no VSCode.

Na primeira instalação, rode sem hooks. Os hooks são avançados e podem ser ativados depois com
`-Hooks` ou `--hooks`.

Guia completo: [INSTALAR-SEM-IA.md](INSTALAR-SEM-IA.md).

## 1. Copie os arquivos pros lugares certos

O pacote tem duas partes: o **global** (vai pro seu `~/.claude/`) e a **memória** (vai FLAT pra
sua pasta CORTEX, a que você abre sempre). Recomendado usar o instalador (`instalar.sh` /
`instalar.ps1`), que faz tudo isto e ainda cria o aviso `_ABRA-ESTA-PASTA-NO-VSCODE.md`. Manual:

```bash
# 1a. A memória + as skills do motor vão FLAT pra sua pasta CORTEX (a que você abre sempre).
#     O "/." no fim leva também os ocultos (.claude/skills). Sem ele, as skills ficam de fora:
cp -r memoria/.   ~/CORTEX/

# 1b. O cérebro global (modo FULL):
cp _claude_global/CLAUDE.md   ~/.claude/CLAUDE.md

# 1c. Skills e agents globais (skill-creator, fecha-sessao, handoff, executor-mecanico):
cp -r _claude_global/skills/*   ~/.claude/skills/
cp -r _claude_global/agents/*   ~/.claude/agents/

# 1d. Hooks, o loop que fecha sozinho, opcional mas recomendado:
cp -r _claude_global/hooks/*   ~/.claude/hooks/
```

No Windows (PowerShell): a pasta CORTEX é `C:\CORTEX`. Troque `cp -r` por `Copy-Item -Recurse` e
as barras por `\`. Pra memória flat: `Copy-Item -Path "memoria\*" -Destination "C:\CORTEX" -Recurse -Force`.

## 2. Ajuste os caminhos

Alguns arquivos têm placeholders de caminho pra você trocar. **Placeholder não trocado = hook que
falha silenciosamente**, sem aviso.

### `{{CAMINHO_CLAUDE}}`

No `settings.json` (todas as entradas de `command`): troque pelo caminho absoluto da pasta
`.claude` do seu usuário. Exemplos: `C:/Users/SEU_USUARIO/.claude` (Windows),
`/home/SEU_USUARIO/.claude` (Linux/macOS). Use barras `/` mesmo no Windows.

### `{{CAMINHO_MEMORIA}}`

Aponta para a pasta `memory/` do seu projeto CORTEX (onde o Claude Code armazena a memória
automática). **Use barras `/`** mesmo no Windows (evita que o `\U` de `\Users` vire escape inválido
do Python nos hooks). Exemplo: `C:/Users/SEU_USUARIO/.claude/projects/c--<nome-da-sua-pasta>/memory`.

Troque este placeholder **em todos os arquivos abaixo** (cada um tem um comentário `# CONFIGURE:`
marcando o lugar exato):

- `hooks/precompact_flush.py`
- `hooks/nudge_destilacao.py`
- `hooks/guarda_tamanho_memoria.py`
- `hooks/captura_regra.py`
- `hooks/captura_feedback.py`
- `hooks/registra_uso_memoria.py`
- `hooks/poda_por_evidencia.py`
- `skills/fecha-sessao/scripts/registrar_sessao.py`

(`sync_push.py` e `sync_pull.py` NÃO entram aqui: eles usam `{{REPO_SYNC}}`, não
`{{CAMINHO_MEMORIA}}`; veja a seção `{{REPO_SYNC}}` abaixo.)

Sem isso, o loop de aprendizado (captura de regra na hora, fila de sessões, monitoramento de
tamanho da memória e log de feedback) quebra em silêncio.

### `{{PASTA_REFERENCIAS}}`

Usado pelo `hooks/nudge_referencias.py` quando voce ativar auditoria/ingestao de referencias sob
demanda. Troque pelo caminho absoluto da pasta onde você
joga material de referência pra ingerir, por exemplo: `C:\CORTEX\referencias`.

**Se você não usa ingestão de referências** (skill `ingerir-referencia`), pode simplesmente
ignorar este placeholder. O restante do sistema funciona normalmente sem ela.

### `{{REPO_SYNC}}`

Usado por `hooks/sync_push.py` e `hooks/sync_pull.py`. Troque pelo caminho do repositório git
de sincronização entre máquinas (a pasta que contém o `.git/`). Esse caminho é diferente do
`{{CAMINHO_MEMORIA}}` acima.

**Se você usa só uma máquina**, pode remover as entradas de `sync_pull.py` e `sync_push.py` do
`settings.json`. O restante funciona sem elas.

### `~/.claude/CLAUDE.md`

O `/onboard` preenche os `{{...}}` de identidade por você no passo 3. Não há caminho de memória
pra ajustar: o cérebro usa caminhos relativos (`memory/`, `references/`), que resolvem sozinhos
porque você abre o editor sempre na mesma pasta CORTEX.

---

> **Verificação antes de seguir:** rode o comando abaixo pra garantir que não sobrou nenhum
> placeholder `{{...}}` sem trocar. Qualquer arquivo listado ainda tem placeholder pendente.
>
> ```bash
> # macOS/Linux:
> grep -rl "{{" ~/.claude/hooks/ ~/.claude/skills/ ~/.claude/settings.json ~/.claude/CLAUDE.md
>
> # Windows (PowerShell):
> Get-ChildItem -Recurse -Path "$env:USERPROFILE\.claude\hooks","$env:USERPROFILE\.claude\skills" |
>   Select-String -Pattern "\{\{" | Select-Object -ExpandProperty Path -Unique
> Select-String -Pattern "\{\{" -Path "$env:USERPROFILE\.claude\settings.json","$env:USERPROFILE\.claude\CLAUDE.md" |
>   Select-Object -ExpandProperty Path -Unique
> ```
>
> Se ainda listar algum arquivo, ajuste antes do `/onboard`, senão o hook falha em silêncio.
> Se o instalador encontrou skills/hooks seus com o mesmo nome, ele guardou os originais em
> `~/.claude/_backup-cortex-<data>/` antes de sobrescrever. Confira lá se algo seu sumiu.

## 3. Rode o onboarding

Abra o VSCode **SEMPRE na sua pasta do CORTEX** (ex: `C:\CORTEX` no Windows, `~/cortex` no Mac/Linux,
use o nome que você escolheu na instalação). É a pasta-cérebro, tem o aviso
`_ABRA-ESTA-PASTA-NO-VSCODE.md` dentro. Com o Claude Code aberto
nela, diga:

```
/onboard
```

Ele te entrevista (7 perguntas, ~5 min), pergunta seu nicho, monta seu
contexto e verifica que tudo ficou de pé. No fim, teste:

```
no que eu devo focar essa semana?
```

Se ele responder te conhecendo, está funcionando.

## 4. Primeiros passos

- `/como-funciona`: a visão geral do sistema, a qualquer momento.
- `/regras`: veja e ajuste as regras que ele segue. Desligue o que não te servir.
- `/audit`: daqui a uns dias, tire a nota do seu setup.
- `/level-up`: toda semana, ache 1 tarefa pra automatizar.

---

## O que tem dentro

Para uma visão de produto, instalação, update e dado do usuário, veja também
[MAPA-DO-PACOTE.md](MAPA-DO-PACOTE.md).

```
CORTEX OS/
├── INSTALAR.md            (este arquivo)
├── lite/                  (modo LITE, cérebro mínimo pra plano básico)
├── _claude_global/        (vai pro ~/.claude)
│   ├── CLAUDE.md          (cérebro FULL)
│   ├── settings.json      (hooks; veja settings.LEIA-ME.md)
│   ├── skills/            (skill-creator, fecha-sessao, handoff, atualizar)
│   ├── agents/            (executor-mecanico)
│   └── hooks/             (guarda_seguranca, snapshot_memoria,
│                           guardiao_escrita, guarda_tamanho_memoria,
│                           nudge_destilacao, nudge_referencias,
│                           captura_regra, captura_feedback,
│                           registra_uso_memoria, poda_por_evidencia,
│                           precompact_flush, sync_push, sync_pull)
└── memoria/               (conteúdo vai FLAT pra C:\CORTEX, a pasta que você abre sempre)
    ├── _ABRA-ESTA-PASTA-NO-VSCODE.md  (o aviso na raiz)
    ├── README.md          (como a memória funciona)
    ├── intake.md          (as 7 perguntas)
    ├── regras-base.md     (referência das regras)
    ├── connections.md     (o que o sistema alcança)
    ├── context/           (sobre você, /onboard preenche)
    ├── references/        (frameworks, voz, nichos, doutrinas)
    ├── projects/          (clientes/projetos isolados)
    ├── decisions/log.md   (decisões e porquês)
    └── .claude/skills/    (onboard, regras, como-funciona, audit,
                            level-up, plan, grill-me)
```

## As skills primordiais (o que faz o CORTEX andar sozinho)

- **skill-creator** (oficial Anthropic): ensina o CORTEX a criar skills novas. É o que mantém
  o sistema crescendo com você.
- **onboard / como-funciona / regras**: se configura, se explica, se governa.
- **audit / level-up**: se avalia e se evolui (1 automação por semana).
- **fecha-sessao + hooks**: o loop de aprendizado que fecha sozinho, destila o dia em regras
  sem você pedir.
- **plan / grill-me / handoff**: planejar, pressionar, dar continuidade.

## Rodando em outra IA (Gemini, GLM, Cursor, modelo local)

O CORTEX é otimizado pro **Claude Code**, que entende nativamente `~/.claude/CLAUDE.md`, skills
em `SKILL.md`, hooks e subagentes. Pra adaptar a outro agente:

- **O cérebro (`CLAUDE.md`)** funciona em qualquer agente que aceite um arquivo de instruções
  de sistema: cole o conteúdo no campo de "system prompt"/"custom instructions" da sua IA.
- **As skills** são markdown legível: se sua IA não tem o conceito de skill, você pode colar o
  conteúdo da skill no chat quando precisar dela (ex: cole o `onboard/SKILL.md` e peça pra
  seguir).
- **Os hooks** (loop automático) são específicos do Claude Code. Sem eles, rode `/fecha-sessao`
  manualmente no fim do dia, e `/handoff` antes de trocar de conversa. Perde o "automático",
  mantém o método.
- **Modo LITE** ajuda bastante em IAs com janela de contexto menor. Veja `lite/MODO-LITE.md`.

Resumo: a alma do CORTEX (cérebro fino + memória + método) é portável; o que é exclusivo do
Claude Code é a automação por hooks. Em outra plataforma, você roda o mesmo método à mão.

---
> CORTEX OS. Arquitetura: cérebro fino + memória em dois níveis + loop de aprendizado que fecha
> sozinho. Onboarding, auditoria, destilação e atualização segura em um pacote local-first.
> skill-creator é da Anthropic (licença incluída).
