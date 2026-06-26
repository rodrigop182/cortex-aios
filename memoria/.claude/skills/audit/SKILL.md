---
name: audit
description: Use quando o operador pedir uma auditoria do AIOS, pra dar nota ao setup, ou disser "meu AIOS tá funcionando?", "audita meu sistema", "acha as lacunas". Produz um placar pelos 6 princípios de AIOS com lastro, com os 3 maiores buracos rankeados por alavancagem.
---

## O que esta skill faz

Roda a **Auditoria pelos 6 princípios de AIOS** (ver `references/principios-aios.md`).
Lê (nunca escreve) o manual de operação, memória, skills, agentes, MCPs, decisões, referências e
hooks. Dá nota a cada princípio. Mostra forças e os 3 maiores buracos por alavancagem, com próximos
passos.

**Escopo é estrutural — "o AIOS tá bem montado?"** NÃO é planejador de capacidade. Buraco
de capacidade ("você podia montar um brief diário se conectasse o calendário") é do
`/level-up`. A auditoria responde: os arquivos, pastas, registros e conexões estão em ordem?

A primeira rodada é a linha de base. Re-rode toda semana pra ver a nota subir. É o gancho
de composição.

## Contexto de hoje

- **Data:** !`date +%Y-%m-%d`
- **Raiz do projeto:** o diretório atual

## Os 6 princípios (ver `references/principios-aios.md`) — total 100

| # | Princípio | Teste | Pts |
|---|---|---|---|
| 1 | **Cérebro fino, no teto** | CLAUDE.md alto sinal e curto (~80-120 linhas); pesado fora, só ponteiro | 15 |
| 2 | **Memória em dois níveis** | Curado no prompt vs. buscável sob demanda; memória persistente viva e curada | 20 |
| 3 | **Regras negativas fortes** | Erros caros gravados como proibição explícita, não só preferência | 15 |
| 4 | **Capacidade sob demanda** | Skills carregam por gatilho; alcança domínios; pesquisa/volume vai pra subagente | 20 |
| 5 | **Loop de aprendizado FECHA sozinho** | Aprende sem digitar comando; erro repetido vira regra; flush antes de perder contexto | 20 |
| 6 | **Transparência sobre autonomia** | Mudança de regra/memória é visível e revisável; nada muta no escuro | 10 |

## Execução

### Passo 1: Descobrir o formato do projeto

Procure por **padrão e intenção**, não caminhos exatos. Use Glob e Read:

- **Manual:** `CLAUDE.md` na raiz.
- **Memória:** `MEMORY.md`, `~/.claude/projects/<id>/memory/`, ou pasta `memory/`.
- **Skills:** `.claude/skills/*/SKILL.md` — conte + frontmatter. (Considere também as skills
  GLOBAIS do operador em `~/.claude/skills/`, que o AIOS pode acionar.)
- **Agentes:** `.claude/agents/*.md`.
- **Conexões** (qualquer um = "alcançável"): MCPs (`.mcp.json`, `settings.json`), scripts
  de API em `scripts/`, pipelines de export, chave `.env` + `references/{tool}-api.md`.
- **Registro de conexões:** `connections.md`.
- **Decisões:** `decisions/log.md`.
- **Referências / SOPs:** `references/`, `docs/`.
- **Projetos:** `projects/`.
- **Hooks / jobs agendados:** `settings.json` hooks, ou skills `manha-*`/`diario-*`/`semanal-*`.

Não penalize por nome fora do canônico se a intenção estiver capturada.

### Passo 1b: Validar ponteiros de skill (caça a nome morto)

Mata a classe inteira de "ponteiro morto" (skill renomeada/apagada ainda citada em arquivo vivo,
que faz o agente acionar o vazio ou perguntar o que o sistema já sabe).

1. Monte o **conjunto VIVO** de nomes de skill: os diretórios em `~/.claude/skills/*/` +
   `memoria/.claude/skills/*/` (o nome da pasta = nome da skill).
2. Faça grep por nomes de skill citados (padrão `` `nome-de-skill` `` em crase) nos arquivos VIVOS:
   `CLAUDE.md`, `memoria/references/`, `memoria/projects/`, `clientes/*/CLAUDE.md`, `connections.md`.
   IGNORAR histórico imutável: `decisions/log.md` (append-only), `handoff-session/`, `backups/`,
   `file-history/`, `*.jsonl`.
3. Todo nome citado que NÃO está no conjunto vivo = **ponteiro morto**. Liste cada um com
   arquivo:linha e o substituto provável (ou "skill removida").

Cada ponteiro morto encontrado entra no relatório e derruba o princípio 6 (muta/aponta no escuro).
Zero ponteiros mortos = ✅ na linha do relatório.

### Passo 1c: Saúde da memória (loop de qualidade)

Roda o medidor de qualidade do acervo de regras (read-only, NÃO move nada). Só execute se o hook
existir (instalação com o loop de aprendizado ligado): rode com `python -B` o
`poda_por_evidencia.py` que está na sua pasta de hooks do Claude (`~/.claude/hooks/`).

Ele cruza presença-no-índice + uso (Read) + veredito de eficácia (`_eficacia-regras.log`, escrito
pela destilação) e separa em quatro: **candidatas a poda** (regra morta, fora do índice), **a
reescrever** (regra que falhou — marcada `reforcar`), **passivas** (no índice mas nunca aberta —
revisar o ponteiro), **eficazes** (confirmadas úteis). Leve o resumo pro relatório (seção "Saúde da
memória"). NÃO arquive nada aqui: poda é gate humano à parte (`--mover`), nunca dentro do audit.
Alimenta os princípios 2 e 5.

### Passo 2: Pontuar cada princípio

#### 1. Cérebro fino, no teto (15)

| Critério | Pts | Como detectar |
|---|---|---|
| CLAUDE.md existe e é substantivo | 4 | Ler CLAUDE.md |
| No teto de tamanho (~80-120 linhas; penalizar >150) | 6 | Contar linhas; -2 por faixa de 30 linhas acima de 120 |
| Conhecimento pesado FORA, só ponteiro no índice | 5 | `references/` populado; CLAUDE.md aponta, não despeja parágrafo |

#### 2. Memória em dois níveis (20)

| Critério | Pts | Como detectar |
|---|---|---|
| Memória persistente com várias entradas vivas | 6 | MEMORY.md ou memory/ com >3 |
| Separação clara carrega-sempre vs. sob-demanda | 5 | CLAUDE.md fino + `references/`/`memory/` lidos sob demanda |
| Decisões registradas (append-only) | 4 | `decisions/log.md` com ≥1 |
| Identidade / papel / voz capturados | 5 | context/ + references/voz.md |

#### 3. Regras negativas fortes (15)

| Critério | Pts | Como detectar |
|---|---|---|
| Proibições explícitas no CLAUDE.md (nunca X) | 7 | Contar regras "nunca/não" substantivas; ≥3 = cheio |
| Erros caros viraram regra gravada | 8 | Memórias de retrabalho/correção (regra evitar-retrabalho; memory/ com "NUNCA") |

#### 4. Capacidade sob demanda (20)

"Alcançável" conta por QUALQUER mecanismo: MCP, script, export, ou chave + ref. Domínios típicos:
receita, clientes, calendário, comunicação, tarefas, conhecimento/arquivos, publicação.

| Critério | Pts | Como detectar |
|---|---|---|
| 3+ skills instaladas, carregadas por gatilho | 6 | Contar `.claude/skills/*/SKILL.md` locais + globais; têm `description`/trigger |
| 1+ skill feita pelo usuário | 4 | Nomes fora de: onboard, audit, level-up, skill-creator |
| Cobertura de domínios alcançáveis | 6 | ~0.85 pt por domínio. Teto 6. |
| Usa subagente pra pesquisa/volume | 4 | `.claude/agents/` ≥1, OU evidência de delegação a subagente no log/memória |

#### 5. Loop de aprendizado FECHA sozinho (20) — o que mais distingue

| Critério | Pts | Como detectar |
|---|---|---|
| Destilação de aprendizado dispara SEM comando | 8 | Hook (Stop/SessionEnd/PreCompact) que roda aprender-do-dia/fecha-sessao automático |
| Flush antes de perder contexto | 5 | Hook PreCompact que grava o durável antes da compactação |
| Erro repetido vira regra (com dedup/poda) | 4 | regra evitar-retrabalho + sinal de uso (memory/ crescendo com correções) |
| Sinal de uso recente | 3 | `decisions/log.md` ou memory/ mexidos em 30d |

> Nota: este é o princípio onde a maioria dos AIOS perde ponto. Ter a SKILL de aprender
> não basta — o teste é se ela DISPARA sozinha. Skill que depende de digitar comando = meio ponto.

#### 6. Transparência sobre autonomia (10)

| Critério | Pts | Como detectar |
|---|---|---|
| Memória/regras em arquivo visível e editável | 5 | memory/, references/, decisions/ em markdown legível (não banco opaco) |
| Mudança de regra é registrada/revisável | 5 | `decisions/log.md` registra o porquê; nada muta no escuro |

### Passo 3: Top 3 buracos por alavancagem

alavancagem = (pontos perdidos) × (multiplicador de impacto).

- Loop de aprendizado não fecha sozinho: **3x** · CLAUDE.md ausente/estourado: **3x**
- 0 skills ou nenhuma sob demanda: **2x** · 0 regra negativa: **2x** · ≤2 domínios: **2x**
- Sem memória em dois níveis: **2x** · Sem log de decisões: **1.5x** · Muta no escuro: **1.5x**
- Resto: **1x**

Ordene desc. Pegue top 3. Pra cada, escreva um próximo passo concreto.

### Passo 4: Imprimir o relatório

Markdown no chat:

```
# Auditoria do AIOS — {data}
**Nota: {total}/100** ({estágio})

Estágios: 0-39 Fundação · 40-69 Montado · 70-89 Compondo · 90-100 Autônomo

## Placar (6 princípios — ver references/principios-aios.md)
1. Cérebro fino           {barra}  {n}/15  {label}
2. Memória 2 níveis       {barra}  {n}/20  {label}
3. Regras negativas       {barra}  {n}/15  {label}
4. Capacidade sob demanda {barra}  {n}/20  {label}
5. Loop aprende sozinho   {barra}  {n}/20  {label}
6. Transparência          {barra}  {n}/10  {label}
(barra = ## proporcional ao teto do princípio; label: "Forte" ≥80% do teto, "Sólido" 55-79%, "Fino" 30-54%, "Faltando" <30%)

## Ponteiros de skill
{✅ Nenhum ponteiro morto} OU {⚠️ N ponteiros mortos: `nome` em arquivo:linha → substituto}

## Saúde da memória (loop de qualidade)
{✅ Acervo saudável} OU {N a podar · M a reescrever · K passivas · J eficazes}
{se houver: listar candidatas a poda e a reescrever, 1 linha cada, com o motivo}

## Forças
- {1-3 bullets}

## Top 3 buracos (por alavancagem)
1. **{buraco}** (-{pts} × {mult}) → {próximo passo}
2. ...
3. ...

## Próximo sugerido: {ação de maior alavancagem}

---
Só lacunas estruturais. Pra explorar o que seu AIOS PODERIA fazer e não faz, rode /level-up.
```

### Passo 5: Oferecer salvar

Pergunte: "Salvo essa auditoria em `audits/audit-{data}.md` pra acompanhar a nota?" Se sim,
escreva (criando `audits/`). É o único efeito de escrita.

## Notas

- **Read-only por padrão.** Só escreve o relatório, se pedido.
- **Honesto, não generoso.** 95/100 é flex. A maioria fica 40-70.
- **Velocidade importa.** Relatório em menos de 60s. Leia frontmatter, não skills inteiras.
- **Padrões editoriais.** No idioma do operador, sem em-dash, sem triplos, sem inventar dado.
