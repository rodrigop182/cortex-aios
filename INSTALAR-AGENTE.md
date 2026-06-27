# INSTALAR-AGENTE.md - roteiro de instalação do CORTEX OS

> **Para o Claude Code (o agente).** Você está instalando o CORTEX OS no computador do seu
> usuário, que provavelmente NÃO é programador. Siga estes passos À RISCA, em ordem, conversando
> em português simples. **Regra de ouro: nunca sobrescreva nem apague nada do usuário sem antes
> copiar pro backup.** Faça um passo, confirme que deu certo, e só então siga pro próximo. Na
> dúvida, pergunte em vez de adivinhar.

## Contexto que você precisa ter

Este pacote (a pasta onde este arquivo está) tem duas partes:

- `_claude_global/` → vai pra pasta global do Claude Code (`~/.claude`). É o cérebro, as skills
  globais, os agents e os hooks.
- `memoria/` → vai FLAT pra uma pasta de trabalho fixa (a "pasta CORTEX"). É a memória e as
  skills do motor (`/onboard`, `/regras`...).

Objetivo final: o usuário abre UMA pasta no VSCode (a pasta CORTEX) e tem cérebro + skills
funcionando, e roda `/onboard`.

## Passo 0 - Detectar o ambiente

1. Descubra o sistema operacional (Windows / macOS / Linux).
2. Defina os caminhos e mostre-os ao usuário:
   - **Pasta global do Claude:** `~/.claude` (Windows: `C:\Users\<usuário>\.claude`).
   - **Pasta CORTEX** (trabalho fixo): padrão Windows `C:\CORTEX`, Mac/Linux `~/CORTEX`.
     Pergunte se ele prefere outro lugar; se não responder, use o padrão.
   - **Pasta do pacote:** onde este `INSTALAR-AGENTE.md` está (você acabou de descompactar).
3. Diga em uma linha o que vai fazer e avise que vai pedir permissão pra alguns comandos.

## Passo 1 - Backup (rede de segurança, OBRIGATÓRIO)

Crie `~/.claude/_backup-cortex-<data-hora>/`. Se JÁ existirem, **copie** (não mova) pra lá, antes
de tocar em qualquer coisa: `CLAUDE.md`, `settings.json`, e as pastas `skills/`, `agents/`,
`hooks/`. Se o usuário não tinha nada disso, ótimo, siga. **Nunca pule este passo**, é o que
deixa tudo reversível.

## Passo 2 - Cérebro global (CLAUDE.md)

- **Modo:** instale sempre o FULL. Se o usuário disser que tem plano básico ou janela de contexto curta, veja `lite/MODO-LITE.md` para a alternativa.
- Copie `_claude_global/CLAUDE.md` para `~/.claude/CLAUDE.md`.
  O antigo já está no backup do Passo 1.
- **NÃO preencha os `{{...}}` agora.** O `/onboard` faz isso depois. Eles devem continuar
  literais neste momento, é o sinal de "ainda não configurado".

## Passo 3 - Skills e agents globais

- Copie todo o conteúdo de `_claude_global/skills/` para `~/.claude/skills/`. **Mescle:** não
  apague skills que o usuário já tenha; as que colidirem de nome já foram pro backup.
- Copie `_claude_global/agents/` para `~/.claude/agents/` do mesmo jeito.
- Pule arquivos dentro de `__pycache__` e com extensão `.pyc`.

## Passo 4 - Memória na pasta de trabalho (FLAT), o passo que mais quebra

Copie TODO o conteúdo de `memoria/` para a pasta CORTEX, **FLAT na raiz** (o conteúdo de
`memoria/` vai direto em `C:\CORTEX`, e NÃO em `C:\CORTEX\memoria`).

- ⚠️ **O erro clássico é esquecer os arquivos ocultos**, em especial `.claude/skills/`. Sem
  eles, o `/onboard` e as outras skills do motor somem.
  - **Mac/Linux:** `cp -r memoria/. <CORTEX>/` (o `/.` no fim leva os ocultos).
  - **Windows:** `Copy-Item memoria\* -Destination <CORTEX> -Recurse -Force` PODE pular ocultos.
    Depois, **copie a pasta `.claude` explicitamente** e confirme que `<CORTEX>\.claude\skills`
    existe.
- **Confira agora:** a pasta CORTEX tem que conter `README.md`, `intake.md` e a pasta
  `.claude/skills/` com `onboard`, `regras`, `como-funciona`, `audit`... Se não tiver, repita
  a cópia dos ocultos antes de seguir.

## Passo 5 - Aviso "abra esta pasta"

Crie `<CORTEX>/_ABRA-ESTA-PASTA-NO-VSCODE.md` com um texto curto: que o usuário deve abrir SEMPRE
essa pasta no VSCode, porque o Claude Code indexa memória e skills POR PASTA (abriu outra, o
CORTEX não o reconhece).

## Passo 6 - Hooks + settings.json (o loop automático)

Os hooks fazem o aprendizado fechar sozinho. Eles precisam de caminhos reais, e é aqui que a
instalação manual costumava travar. Você resolve isso porque SABE os caminhos. Faça:

1. Copie `_claude_global/hooks/*` para `~/.claude/hooks/`, **mas NÃO copie a pasta
   `hooks/{{CAMINHO_MEMORIA}}/`** (são seeds de log que viajam junto; o lugar deles é a pasta de
   memória resolvida, não `~/.claude/hooks/`). Copie só os `.py`. Se já tiver copiado tudo, apague
   a pasta `~/.claude/hooks/{{CAMINHO_MEMORIA}}/` depois.
2. **settings.json:**
   - Se o usuário NÃO tem `~/.claude/settings.json`: copie `_claude_global/settings.json` pra lá.
   - Se JÁ tem: **mescle só a seção `"hooks"`** (acrescente as entradas do CORTEX; não apague nem
     sobrescreva o que já é dele).
3. **Troque os placeholders pelos caminhos REAIS** (você os conhece; use barras `/`):
   - `{{CAMINHO_CLAUDE}}` → o caminho absoluto de `~/.claude`.
   - `{{CAMINHO_MEMORIA}}` (aparece em `precompact_flush.py`, `nudge_destilacao.py`,
     `guarda_tamanho_memoria.py`, `captura_regra.py`, `captura_feedback.py`,
     `registra_uso_memoria.py`, `poda_por_evidencia.py` e em
     `skills/fecha-sessao/scripts/registrar_sessao.py`) → a pasta `memory/` da memória do
     projeto, dentro de `~/.claude/projects/<pasta-do-projeto>/memory`.
     **Resolva TODAS as ocorrências** (`grep -rl "{{CAMINHO_MEMORIA}}"`), senão o loop de
     aprendizado (captura de regra + fila de sessões + medidor de uso/poda) quebra silencioso.
   - `{{PASTA_REFERENCIAS}}` (aparece em `nudge_referencias.py`, se ativar auditoria sob demanda) → a pasta onde o operador joga
     material de referência para ingerir (ex: `C:\CORTEX\referencias` ou `~/cortex/referencias`).
     **Opcional:** se o operador não usa ingestão de referências, ignore este placeholder.
   - `{{PASTA_CORTEX}}` (aparece em `retrieval_topico.py`) → a **pasta CORTEX** de trabalho (onde
     o conteúdo de `memoria/` foi copiado FLAT, ex: `C:\CORTEX` ou `~/CORTEX`). O hook lê
     `{{PASTA_CORTEX}}/references` para injetar guia/regra por tópico. **NÃO confundir** com
     `{{CAMINHO_MEMORIA}}` (memória pessoal por-projeto) nem com `{{PASTA_REFERENCIAS}}` (ingestão).
     **Opcional:** se preferir não usar o retrieval automático, remova a entrada do
     `retrieval_topico.py` do `settings.json` e ignore este placeholder.
   - `{{REPO_SYNC}}` (aparece em `sync_pull.py` e `sync_push.py`) → o repositório git de
     sincronização entre máquinas (a pasta que contém `.git/`). **Esse caminho é diferente do
     `{{CAMINHO_MEMORIA}}` acima.** Só é necessário se o usuário usar o CORTEX em mais de um
     computador; se não usar, remova os dois hooks de sync do `settings.json` (ver passo 4).
4. **Sync entre máquinas:** pergunte "você vai usar o CORTEX em mais de um computador?".
   - **Não:** remova do settings.json as duas entradas que chamam `sync_pull.py` e `sync_push.py`.
   - **Sim:** deixe, e avise que ele roda `/sync` depois pra configurar o repositório PRIVADO.
5. Se algo nos hooks ficar incerto, **NÃO trave a instalação:** avise que o loop automático ficou
   pendente, que o resto funciona, e que por enquanto ele roda `/fecha-sessao` à mão. Os hooks são
   um bônus, não um bloqueio.

## Passo 7 - Verificar (antes de declarar pronto)

- `~/.claude/CLAUDE.md` existe e tem conteúdo. (Os `{{NOME}}` e cia. ainda literais: correto.)
- `~/.claude/skills/` tem as skills globais; a pasta CORTEX tem `.claude/skills/` com o `/onboard`.
- Procure `{{` em `settings.json` e nos arquivos de `hooks/` que você instalou. Se sobrou algum
  `{{CAMINHO_...}}` (fora do `CLAUDE.md`, onde é esperado), conserte antes de seguir.
- Liste pro usuário, em 3-4 linhas, o que foi instalado e onde.

## Passo 8 - Dizer ao usuário como começar (CRÍTICO)

As skills do CORTEX (`/onboard`, `/regras`...) moram NA PASTA CORTEX. Então, em ordem:

1. Peça pra ele **abrir essa pasta no VSCode**: menu **Arquivo > Abrir Pasta** e escolher a pasta
   CORTEX (a que tem o `_ABRA-ESTA-PASTA-NO-VSCODE.md` dentro).
2. Com o Claude Code aberto NELA, ele roda **`/onboard`** (entrevista de ~5 minutos).
3. Reforce: ele deve abrir SEMPRE essa pasta pra o CORTEX reconhecê-lo.

## Se algo der errado

Tudo que você sobrescreveu está em `~/.claude/_backup-cortex-<data-hora>/`: pra reverter, é só
restaurar de lá. Veja também `TROUBLESHOOTING.md` neste pacote.
