# Changelog — CORTEX OS

Mudanças de cada versão, da mais recente pra mais antiga. Formato baseado em
[Keep a Changelog](https://keepachangelog.com); versões seguem [SemVer](https://semver.org).

A skill `/atualizar` troca a camada PRODUTO (ver `MANIFESTO-UPDATE.md`) e preserva seu dado.
Antes de atualizar, leia a seção da versão pra qual você está indo.

---

## [1.8.1] - 2026-06-26

Melhorias de distribuição, instalação sem IA, configuração manual e suporte a Codex.

### Adicionado

- `INSTALAR-SEM-IA.md`: rota de instalação sem depender de agente.
- `CONFIGURAR-SEM-IA.md`: preenchimento manual do perfil quando o usuário não quer rodar `/onboard`.
- `ATUALIZAR-SEM-IA.md`: atualização manual com dry-run.
- `ATUALIZAR-COM-CODEX.md`: roteiro para Codex aplicar update preservando dados.
- `AGENTS.md` e `memoria/AGENTS.md`: porta de entrada para Codex na pasta instalada.

### Atualizado

- `COMECE-AQUI.txt`, `README.md`, `INSTALAR.md`, `MAPA-DO-PACOTE.md` e `ADAPTADORES.md` agora deixam
  explícitas as rotas com agente, sem IA e com Codex.
- `MANIFESTO-UPDATE.md` inclui os novos documentos como camada de produto atualizável.
- `atualizar.py` agora copia `memoria/AGENTS.md` para a pasta CORTEX viva quando roda com
  `--cortex-dir`, além das skills locais.

### Migração

- De 1.8.0 para 1.8.1, o `/atualizar` preserva dados e adiciona os novos guias de instalação,
  configuração e Codex. Depois do update, confira se `AGENTS.md` existe na pasta CORTEX viva quando
  usar Codex.

---

## [1.8.0] — 2026-06-25

Dashboard de workflows, scripts de destilação e melhorias de retomada de sessão.

### Adicionado

- **`/workflows-ao-vivo`** (skill global nova): dashboard HTML local que acompanha workflows rodando em tempo real — agentes, modelos, tokens, tool calls, duração. Abas: Multi-agente, Custos (ccusage 14 dias), Scripts Python. Servidor Python stdlib, zero dependência externa.
- **`destilar-sessoes/scripts/narra.py`**: gera narrativa cronológica por projeto a partir dos enxutos (rolling summary via Haiku). Complementa o `sintetiza.py`.
- **`destilar-sessoes/scripts/sintetiza.py`** (atualizado): agrupamento por projeto antes de lotejar, fix encoding UTF-8, truncamento por arquivo, timeout 300s.
- **`destilar-sessoes/scripts/README.md`**: guia dos 3 scripts (extrai + sintetiza + narra), tabela de placeholders e ordem de execução.
- **`armadilhas-tecnicas.md`** (expandido): +9 seções — Python encoding/BOM no Windows, caminhos com unicodeescape, operações atômicas (os.replace), CLI claude -p timeout, MCP servers (carregamento e configuração), Playwright órfãos no Windows, comparação de versão semântica, troca de modelo mid-session.

### Atualizado

- **`/continuar-sessao`**: filtro anti-infra obrigatório (ignorar handoffs de manutenção/sync ao buscar o "mais recente"); roteamento por peso de sessão (>100k tokens delega conferência de disco ao `executor-rapido`); critério de pop-up por rajada (2+ handoffs de trabalho fechados em <5min, não apenas "mesmo minuto").

### Migração

- De 1.7.x pra 1.8: o `/atualizar` instala a skill `workflows-ao-vivo` e os scripts novos. Nenhum dado seu é tocado. Se já tinha uma versão anterior da skill `continuar-sessao`, ela é substituída pela versão com filtro anti-infra.

---

## [1.7.0] — 2026-06-24

Limpeza de skills obsoletas, regras de ferramentas no núcleo, e `/salvar-referencia` vira comportamento nativo.

### Removido

- **`catch-up-aprendizado`** era duplicata de `destilar-sessoes` — removida do template.
- **`ingerir-referencia`** substituída por regra nativa no CLAUDE.md: diga "guarda isso" ou "salva como referência" — sem skill separada.
- Referência a `segundo-cerebro` removida do `ARQUITETURA.md` (pasta nunca existiu no template).

### Adicionado

- **Bloco "Armadilhas de ferramentas"** no `CLAUDE.md` (núcleo): Bash tool corrompe `:` em args git (usar PowerShell); `git add .` em monorepo é armadilha (usar escopo exato); PowerShell `Set-Content -Encoding utf8` gera BOM (usar `-AsByteStream`); backup obrigatório antes de update.
- **Regra de model explícito em agent()** no bloco de Orquestração: nunca omitir `model` em subagente — herdar o tier da sessão queima cota.
- **`/salvar-referencia` como comportamento nativo** no CLAUDE.md — skill `ingerir-referencia` removida.

### Migração

- De 1.6.x pra 1.7: o `/atualizar` remove `catch-up-aprendizado` e `ingerir-referencia` automaticamente (são PRODUTO). Nenhum dado seu é tocado.

---

## [1.6.3] — 2026-06-23

Faxina de distribuição: os seeds de log param de sujar os hooks instalados.

### Corrigido

- **`instalar.ps1` não copia mais a pasta-placeholder `hooks/{{CAMINHO_MEMORIA}}/`.** Ela guarda
  os 3 seeds de log (`_eficacia-regras.log`, `_feedback.log`, `_regras-detectadas.log`) que viajam
  no pacote, mas cujo lugar é a pasta de memória resolvida — não `~/.claude/hooks/`. Antes o
  `Copiar-ComBackup` os arrastava literal pros hooks vivos (lixo cosmético inofensivo). Agora são
  filtrados junto com `__pycache__`/`.pyc`. O `INSTALAR-AGENTE.md` (caminho manual) ganhou a mesma
  instrução de pular a pasta. Os seeds continuam no pacote para viajar.

### Removido

- **`__pycache__` da fonte do template.** Cache do Python (regenerável) que não deve viajar no
  pacote; removido das 3 pastas onde havia (`hooks/`, `skills/atualizar/scripts/`,
  `skills/handoff/scripts/`).

---

## [1.6.2] — 2026-06-23

Retrieval por tópico: a memória deixa de depender 100% do modelo lembrar de abrir o guia certo.

### Adicionado

- **Hook `retrieval_topico.py` (`UserPromptSubmit`).** Detecta o tema do prompt por um mapa
  curado keyword→arquivo e **injeta o conteúdo** do guia/regra relevante no contexto, antes do
  Claude responder (não só o caminho). Para guia de nicho injeta a seção acionável (do
  `## Regras extras` ao fim); para regra de sistema, o arquivo. Disciplina anti-dumbzone: teto
  de **2 arquivos por turno**, match por palavra inteira **sem acento** (casa "conversão" e
  "conversao"), e silêncio total quando nada casa ou a entrada é inválida (stdin vazio/JSON
  malformado nunca quebram o turno). Lê o stdin e escreve o stdout em **UTF-8 explícito** (o
  default cp1252 do Windows quebraria acento e setas).
- **Placeholder `{{PASTA_CORTEX}}`** (resolvido na instalação) → a pasta CORTEX de trabalho, de
  onde o hook lê `references/`. Documentado no `INSTALAR-AGENTE.md`. Não confundir com
  `{{CAMINHO_MEMORIA}}` (memória pessoal por-projeto) nem `{{PASTA_REFERENCIAS}}` (ingestão).
  Opcional: quem não quiser o retrieval remove a entrada do `settings.json` e ignora o placeholder.

---

## [1.6.1] — 2026-06-23

Correção de distribuição: o fallback manual (`instalar.ps1`) deixa de nascer com hooks mortos.

### Corrigido

- **`instalar.ps1` agora instala e configura o `settings.json`.** Antes ele copiava os hooks
  mas não o `settings.json` — então, por esse caminho, nenhum hook era registrado (nasciam
  mortos). Agora copia o `settings.json` do pacote e resolve o `{{CAMINHO_CLAUDE}}` pro caminho
  real (preservando UTF-8 **sem BOM**), e faz o mesmo nos `.py` de hooks/skills. Se já existir um
  `settings.json`, **não sobrescreve** — instrui o merge manual da seção `hooks`. Resta só o
  ajuste de `{{CAMINHO_MEMORIA}}` nos hooks de aprendizado (avisado de forma clara no fim). O
  caminho primário (`INSTALAR-AGENTE.md`) já tratava isso; agora o fallback também.

---

## [1.6.0] — 2026-06-23

Loop de QUALIDADE da memória (a memória não só cresce — ela se mede e se poda sozinha, com gate) e
distribuição à prova de bala (o `/atualizar` agora também faz deploy pros lugares vivos).

### Adicionado

- **Loop de qualidade da memória (o "fecha a torneira"):**
  - `hooks/registra_uso_memoria.py` (hook `PostToolUse:Read`): instrumenta, em silêncio, qual regra
    foi lida de fato. É a evidência de uso que faltava pra saber o que está vivo.
  - `hooks/poda_por_evidencia.py` reescrito com **3 camadas anti-poda-de-regra-viva**:
    presença-no-índice (regra com ponteiro no `MEMORY.md` é viva, mesmo sem leitura registrada) +
    eficácia (lê o `_eficacia-regras.log`) + uso/idade/status. Modo padrão só imprime relatório
    (gate humano); `--mover` arquiva (reversível) e re-checa as travas.
  - `_eficacia-regras.log`: a destilação (fecha-sessao / aprender-do-dia / catch-up) escreve um
    veredito por regra posta à prova (`eficaz` protege da poda; `reforcar` manda reescrever, não
    podar). Quem tem contexto pra ligar feedback à regra é o agente, não um script.
  - Seção **"Saúde da memória"** no `/audit` (Passo 1c): roda o medidor read-only e leva o resumo
    pro relatório.
- **`hooks/guarda_tamanho_memoria.py`** (hook `SessionStart`): avisa quando o `MEMORY.md` passa do
  teto que o Claude Code carrega, pra o índice fino não reestourar em silêncio.
- **Deploy pros lugares vivos no `/atualizar`:** `--claude-dir` e `--cortex-dir` copiam os
  hooks/skills atualizados pra `~/.claude` e pra pasta CORTEX (o que o Claude Code de fato carrega).
  Não-destrutivo: preserva placeholders já resolvidos, nunca apaga dado nem `settings.json`
  mesclado, faz backup datado por destino e marca o que precisa de ajuste manual. Se o destino é um
  repo git, põe os backups/cache no `.gitignore` sozinho (convive com quem versiona o CORTEX).

### Mudado

- `captura_regra.py` e `captura_feedback.py` ganharam **guard anti-envelope**: ignoram envelopes de
  sistema (`<task-notification>`, `<system-reminder>`, etc.) que chegam via `UserPromptSubmit` mas
  não são fala do usuário — antes inflavam os logs com lixo.
- `continuar-sessao` e `detectar_handoff.py`: **retomada silenciosa** — a conferência de estado é
  backstage (não narrar a investigação no chat), com roteamento por assunto/recência e pop-up só no
  empate real.

### Migração

- **De 1.5 pra 1.6:** os hooks novos (`registra_uso_memoria`, `poda_por_evidencia`) precisam ter
  `{{CAMINHO_MEMORIA}}` resolvido, e o `settings.json` precisa ganhar a entrada `PostToolUse:Read`.
  O roteiro manual passo a passo (que o próprio Claude Code executa) está em
  **`MIGRAR-1.5-para-1.6.md`**. A partir de 1.6, o `/atualizar --claude-dir/--cortex-dir` faz o
  deploy sozinho. Todo update faz backup datado ANTES e nunca toca no seu dado.

## [1.5.0] — 2026-06-21

Instalação à prova de leigo (o próprio Claude Code instala) e onboarding que EDUCA, não só
entrevista.

### Adicionado

- **Instalação agente-guiada:** `INSTALAR-AGENTE.md` (roteiro que o Claude Code do novo usuário
  segue pra instalar tudo com segurança: backup, cópia pros lugares certos, merge do
  `settings.json` com os caminhos reais, verificação, e leva ao `/onboard`) + `COMECE-AQUI.txt`
  na raiz com o prompt pronto pra colar. Ninguém mais precisa rodar PowerShell nem caçar pasta:
  cola uma frase e o agente instala. O `instalar.ps1`/`.sh` viram fallback manual.
- **Onboarding que educa (não só entrevista):** o `/onboard` abre situando o novo usuário (o que
  é o CORTEX e por quê, como pedir pela dor, `/clear` + `/handoff` + `/continuar-sessao`, as
  skills) antes da entrevista, pensando em quem é vibecoder.
- **Passo de modelos e custo no `/onboard`:** ensina os tiers (forte/equilibrado/barato), monta o
  mapa tier→modelo pelo plano do usuário (com a decisão sempre dele), e estimula usar os modelos
  baratos e workflows no uso médio em vez de queimar o modelo forte à toa.
- **Boas práticas de custo** no `/como-funciona` (bloco "gastar bem") e em `tiers-de-modelo.md`
  (workflow e lote como multiplicador de economia).

### Mudado

- `INSTALAR.md` agora abre pela forma fácil (agente-guiada); o passo a passo manual virou a
  segunda parte.

## [1.4.0] — 2026-06-21

Primeiro contato à prova de leigo: o agente do novo usuário se situa sozinho. Mais duas regras de
método.

### Adicionado

- **Bootstrap pro agente:** o `CLAUDE.md` (full e lite) agora instrui o próprio assistente, na
  primeira leitura, a detectar que o CORTEX ainda não foi configurado (placeholders `{{...}}`
  literais) e a oferecer `/onboard` antes de executar às cegas. Quem recebe o CORTEX não precisa
  saber por onde começar: o agente dele explica e conduz.
- **Regra "onde cada regra mora"** (`memoria/README.md`): cada regra vai pro destino que a faz
  carregar só quando é relevante (projeto → `CLAUDE.md` do projeto; skill → corpo da skill; geral
  → cérebro), pra o cérebro fino não inchar.
- **Tarefa visual no protocolo de execução** (`references/protocolo-execucao.md`): antes de
  desenhar mockup ou asset de algo real, buscar a referência real (medir antes de chutar).

## [1.3.0] — 2026-06-21

Pasta de trabalho fixa: o CORTEX agora se instala numa pasta cravada que você abre sempre, pra a
memória e as skills te seguirem de verdade (à prova de leigo).

### Mudado

- **Pasta de trabalho padrão cravada:** o instalador agora usa `C:\CORTEX` (Windows) / `~/CORTEX`
  (Mac/Linux) como pasta única, em vez de `cortex-memoria`. A memória vai **flat** na raiz dessa
  pasta (não numa subpasta), pra os caminhos relativos do cérebro e a descoberta de skills
  resolverem só de abrir a pasta. Você pode mudar o lugar com `--destino` / `-Destino`.
- **Aviso na raiz:** o instalador cria `_ABRA-ESTA-PASTA-NO-VSCODE.md` dentro da pasta, explicando
  por que abrir sempre a mesma pasta (o Claude Code indexa memória e skills por pasta).

### Corrigido

- **Skills do motor sumiam no Mac/Linux:** o `instalar.sh` copiava a memória com `cp -r .../*`, que
  pula arquivos ocultos — então `.claude/skills/` (onde moram `/onboard`, `/regras`...) ficava de
  fora. Agora copia com `cp -r .../.` (inclui os ocultos).
- Removida a instrução órfã de trocar `{{CAMINHO_MEMORIA}}` no `CLAUDE.md`: o cérebro usa caminhos
  relativos, que resolvem sozinhos quando você abre a pasta CORTEX.

### Migração

- Quem já instalou em `cortex-memoria` pode continuar lá (nada quebra). Pra adotar o padrão novo,
  reinstale apontando o destino, ou mova sua pasta pra `C:\CORTEX` / `~/CORTEX` e passe a abri-la
  sempre. O `/atualizar` assume `C:\CORTEX` / `~/CORTEX` por padrão; use `--instalado` se a sua
  estiver em outro lugar.

## [1.2.0] — 2026-06-21

Roteamento de modelos por tier, catch-up de aprendizado, ciclo de contexto completo entre sessões,
e remoção da dependência de memória de terceiros.

### Adicionado

- `references/tiers-de-modelo.md`: régua de roteamento de subagentes por tier abstrato (1/2/3), com
  mapa tier para modelo configurável pelo seu plano. O CORTEX usa o modelo certo pra cada tarefa.
- Skill `/catch-up-aprendizado`: mutirão retroativo que destila o aprendizado de vários dias de uma
  vez, pra quando você não fecha cada sessão com ritual.
- Skill `/continuar-sessao`: retoma do handoff certo ao abrir a próxima janela. Fecha o ciclo com
  o `/handoff`.
- `references/ciclo-de-contexto.md` + bloco no `/como-funciona`: quando usar `/clear`, `/handoff` e
  `/continuar-sessao`, e como pedir tarefas (descreva a dor, o CORTEX traz as formas de resolver).

### Removido

- Integração com ferramenta de memória de terceiros saiu por completo. O CORTEX cura o "como
  trabalhar"; o histórico técnico bruto fica nos transcripts do Claude Code, sem dependência
  externa. (`INTEGRACAO-CLAUDE-MEM.md` e todas as referências removidos.)

### Migração

- `/atualizar` troca só a camada PRODUTO e preserva seu dado. Se você instalou alguma ferramenta de
  memória de terceiros por conta própria, ela continua no seu PC; o CORTEX só deixa de recomendá-la
  e de acioná-la.

## [1.1.0] — 2026-06-21

Loop de retorno (você devolve melhorias pra quem te passou o CORTEX) e fronteira de dados mais à
prova de erro.

### Adicionado

- Skill `/contribuir`: empacota uma skill ou regra sua, limpa de dado pessoal, pra devolver a quem
  te passou o CORTEX. Quem mantém a sua versão avalia e decide se ela entra na próxima atualização.

### Mudado

- `MANIFESTO-UPDATE.md` ganhou a seção **DADO BLINDADO** (espelhando o `.chezmoidata` do chezmoi):
  o subconjunto do dado que nunca sai da máquina (contexto, voz, memória, decisões, segredos,
  trechos `<private>`). Torna a fronteira do que pode ou não sair do PC mais à prova de erro.

---

## [1.0.0] — 2026-06-20

Primeira versão distribuível. Cérebro fino + memória em dois níveis + loop de aprendizado que
fecha sozinho por hooks.

### Adicionado

- Cérebro global em dois modos: `CLAUDE.md` (full) e `CLAUDE-LITE.md` (janela menor).
- Skills globais (`~/.claude/skills/`): `skill-creator`, `fecha-sessao`, `handoff`, `atualizar`.
- Skills do motor (`memoria/.claude/skills/`): `onboard`, `regras`, `como-funciona`, `audit`,
  `level-up`, `plan`, `grill-me` e outras.
- Agente `executor-mecanico` pra tarefa mecânica já decidida.
- Hooks de automação: `guarda_seguranca` (bloqueia destrutivo óbvio), `nudge_destilacao`,
  `precompact_flush`, `sync_push`/`sync_pull` (sync opcional entre máquinas, via repo git).
- Instaladores `instalar.ps1` / `instalar.sh` com confirmação antes de sobrescrever
  `CLAUDE.md` e a pasta de memória, e **backup automático** de skills/agents/hooks próprios do
  usuário em `~/.claude/_backup-cortex-<data>/` antes de qualquer sobrescrita.
- Skill `/atualizar`: troca só a camada PRODUTO e preserva DADO (memória, voz, nicho, contexto,
  projetos). Fronteira definida em `MANIFESTO-UPDATE.md`.
- Governança pra distribuição: `LICENSE` (MIT), `NOTICE.md`, `SECURITY.md`/`SEGURANCA.md`,
  `PRIVACIDADE.md`.
- Blindagem da tag `<private>`: conteúdo marcado nunca vai pro sync (strip na origem ou
  push abortado se vazar).

### Notas

- O sync (`sync_push`/`sync_pull`) é **opcional**: só faz sentido se você usa o CORTEX em mais de
  uma máquina com um repo git privado. Com uma máquina só, remova esses dois hooks do
  `settings.json`.
