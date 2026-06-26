---
name: level-up
description: Use toda semana pra achar e enviar uma automação nova. Caminha a entrevista por descoberta, escopo e construção. Gatilhos "vamos evoluir", "o que automatizo essa semana", "acha alavanca", ou ritual de sexta. Uma rodada = um artefato enviado.
---

## O que esta skill faz

Caminha o operador toda semana para achar, escopar e enviar uma automação nova.
**Uma entrevista = um artefato.** Depois de algumas rodadas, ele começa a achar oportunidade
sozinho no meio da semana porque as perguntas viraram default interno.

É o mecanismo de re-fiação do cérebro. O kit não precisa de cron pra ancorar comportamento;
precisa do `/level-up` rodando toda sexta.

## O que `/level-up` NÃO é

- Não é `/audit`. `/audit` é estrutural; `/level-up` é funcional ("que alavanca de negócio
  estou perdendo?"). Rode `/audit` antes se a estrutura está bagunçada.
- Não é planejador de vários candidatos. Uma rodada = um artefato.
- Não é coach. O operador faz o pensamento. A skill conduz a entrevista.

## Sua lente / o seu norte (sempre presente)

O norte é o **objetivo de longo prazo declarado no onboard** (produto próprio, escala, mudança
de área, ou o que o operador definiu na Q3). Em toda candidata, pergunte: *isso reduz trabalho
de baixo valor, ou constrói o que importa?* Dê peso extra a alavancas que movem pro norte.
Automação que só faz mais do mesmo sem escalar é alavanca fraca.

## Entradas que a skill lê

- `context/prioridades.md`, `context/sobre-mim.md`, `context/sobre-operacao.md`
- `projects/*.md` — projetos ativos
- `connections.md` — o que é alcançável
- `decisions/log.md` — decisões recentes
- skills (locais + globais do operador) — o que já existe
- `audits/audit-{data}.md` recente, se houver

## Execução — três fases

### Fase 1 — Descoberta (achar o candidato)

Surfe 1-3 candidatos por alavancagem. Pergunte em ordem, conversando:

1. *"Me conta sua semana. O que você fez 3+ vezes?"* (frequência)
2. *"Algo que foi manual, chato, ou copia-e-cola?"* (drudgery)
3. *"Algo onde você pensou 'um estagiário esperto resolvia'?"* (delegação)
4. *"Se 500 clientes chegassem amanhã, o que quebraria primeiro?"* (gargalo)
5. *"O que te daria 500 clientes amanhã?"* (alavanca de crescimento)

Quando encaixar, puxe o operador para pensar em partes pequenas:
- *"Até que ponto dá pra usar IA aqui?"*
- *"Você não precisa automatizar o trabalho todo. Qual pedaço mais repetido já valeria?"*
- *"Se não dava mês passado, talvez agora dê. O que mudou nas ferramentas ou no processo?"*

**Saída da Fase 1:** lista de 1-3 candidatos, uma linha de "por que é alavanca" cada,
marcando quais movem pro norte de longo prazo. Pergunte: *"Escolhe um pra escopar."*

### Fase 2 — Escopo (transformar um candidato em spec)

O operador escolhe. Caminhe os 5 passos:

**1 — Achar o gargalo.** Qual bottleneck resolve, ou qual alavanca abre? Amarre à Fase 1.

**2 — EAD: Eliminar / Automatizar / Delegar.**
- **Eliminar primeiro:** *"E se a gente só parar de fazer isso?"* Se "nada quebra" → a skill
  sai feliz. *"Não automatize desperdício."* É vitória, registre em `decisions/log.md` e pare.
- **Automatizar:** regra 60/30/10 (~60% determinístico, ~30% IA-assistido, ~10% manual).
- **Delegar:** complexo/variável/julgamento demais → sugira uma pessoa. Registre e saia.

**3 — Mapear o processo.** Cinco elementos: Gatilho, Fontes de dado, Transformações,
Pontos de decisão, Destino. Se ele não consegue articular: *"Se não dá pra explicar pra uma
pessoa, não dá pra explicar pra uma IA. Rabisca no papel e volta."* Pare.

**4 — Nível de autonomia.**

| Nível | Nome | O que acontece |
|---|---|---|
| L0 | Manual | Sem IA |
| L1 | Sugerido | IA sugere, humano decide cada passo |
| L2 | Rascunho | IA rascunha, humano revisa e edita |
| L3 | Supervisionado | IA roda, humano valida periodicamente |
| L4 | Autônomo | IA ponta a ponta |

**Padrão = o nível mais baixo que resolve.** Empurre contra L4 sem ter rodado os baixos.
*"Workflows ganham de agentes. Se uma decisão não PRECISA ser da IA, não deixe a IA fazer."*

**5 — Amarrar a um KPI.** Qual dos três baldes move: mais clientes / mais valor por cliente
/ menos custo. Mais uma métrica específica. **Se não nomear balde + métrica, a skill para.**
*"Se sua automação não move um número, por que construir?"*

**Saída da Fase 2:** spec escopada gravada em `decisions/log.md` como entrada datada com os
5 elementos + nível de autonomia + KPI.

### Fase 3 — Construção (enviar o artefato)

Pergunte: *"Como você quer enviar isso?"* Opções na ordem do Boring-is-Beautiful:

1. **Só prompt** — template salvo que ele roda na mão. Zero infra.
2. **Skill determinística** — SKILL.md que roda script (sem IA). Pra transformações com regra.
3. **Skill IA-assistida** — SKILL.md com uma chamada de IA. Rascunha, classifica, resume.
4. **Sub-agente** — multi-passo. Último recurso. Só se precisa mesmo de raciocínio + tools.

**Padrão = a opção não-IA mais alta que resolve.** Ele tem que escolher mais autonomia.

Roteie pro scaffolder certo (`skill-creator` se disponível, senão escreva o SKILL.md inline
com frontmatter e local). **Todo artefato gerado leva no topo:**

```markdown
---
bike-method-fase: 1  # Fase 1 — rodinhas. Rode manual primeiro.
---
```

Isso trava na Fase 1 do Bike Method no primeiro build. A fase só avança por edição explícita.

## Contrato de saída

Toda rodada produz: (1) uma entrada em `decisions/log.md`, (2) um artefato (prompt, skill ou
agente), (3) um fechamento de uma tela com o lembrete da Fase 1 do Bike Method.

## Regras de implementação

1. **Uma entrevista = um artefato.**
2. **Fase de descoberta sempre primeiro**, mesmo se ele chega com ideia pronta.
3. **EAD força "eliminar primeiro".** Se a resposta é eliminar, saia feliz, é vitória.
4. **Padrão = nível de autonomia mais baixo que funciona.** Empurre contra L4.
5. **Padrão Boring-is-Beautiful no Machine.** Default = opção não-IA mais alta.
6. **Amarrar a KPI é obrigatório.** Sem balde + métrica, a skill para.
7. **Bike Method em todo artefato.** `bike-method-fase: 1` no frontmatter.
8. **Read-only nos arquivos do usuário, exceto `decisions/log.md` e o artefato novo.**
9. **Lente do norte de longo prazo em toda candidata.** Marque o que escala vs. o que só serve o imediato.
10. **Padrões editoriais.** No idioma do operador, sem em-dash, sem "não é X é Y", sem triplos,
    sem inventar dado.
