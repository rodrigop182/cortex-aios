# Grafo de skills — como elas se ligam, colidem e se mantêm

O operador cria e baixa skills ao longo do tempo. Sem manutenção, três coisas apodrecem: (a) skills
que **deveriam se chamar** não se citam (link faltante), (b) skills novas **colidem no gatilho** com
irmãs antigas (a description de uma rouba o disparo da outra), (c) descriptions ficam
**desatualizadas** (citam fluxo/arquivo que mudou). Este arquivo é o mapa vivo + o checklist de
faxina. A doutrina de auto-melhoria das skills mora em `auto-melhoria-skills.md`; a de comprimir
description mora em `skill-description-eficiente.md`.

## As famílias (quem orquestra quem)

> Preencha as famílias de skills do seu sistema aqui. Exemplo de estrutura:

- **[Nome da família]** — orquestrador `[skill-orquestradora]` roteia para: `[skill-a]`,
  `[skill-b]`, `[skill-c]`. Entrada→saída declaradas em cada SKILL.
- **[Outra família]** — `[skill-motor]` ← `[skill-de-setup]` (executa antes) ← `[skill-de-ref]`
  (usada como insumo antes).
- **Aprendizado / memória do OS** — `fecha-sessao`, `handoff`, `diario`, `skill-creator`. É a
  família que se auto-mantém (inclui manter as outras skills).

## Links faltantes (skills que se conversam e não se citam)

> Diagnóstico. Aplicar mudança cirúrgica é autonomia; refatorar/apagar vai como proposta.

*(Adicione aqui os diagnósticos encontrados no `/audit`, com data e status.)*

- **[DATA]** — [Descrição do link faltante. Status: FEITO / PENDENTE / FALSA LACUNA.]

## Colisões de gatilho conhecidas

*(Registre aqui colisões identificadas entre skills com gatilhos sobrepostos.)*

- **[DATA]** — [Descrição da colisão. Status: RESOLVIDO / PENDENTE.]

## Descriptions a verificar (suspeita de desatualização)

*(Liste skills cujas descriptions podem estar desatualizadas para revisão no próximo /audit.)*

- [nome-da-skill] — [motivo da suspeita]

## Checklist de faxina do grafo (rodar no `/audit` ou sob pedido)

1. Listar todas as SKILL.md (`{{CAMINHO_MEMORIA}}/.claude/skills/*/SKILL.md`).
2. Para cada exclusão "isso é a skill X" numa description, conferir se X ainda existe com esse nome.
3. Caçar colisão: duas+ descriptions com o mesmo gatilho de fala e domínios que se sobrepõem.
4. Caçar link faltante: orquestrador que não cita uma operária do mesmo domínio; skill que produz
   uma saída que é entrada natural de outra e não a menciona.
5. Caçar placeholder/órfã (description em branco ou sem gatilho real).
6. Entregar o diagnóstico ao operador como LEQUE de correções (ele decide), não aplicar em massa —
   mexer em description é design e pode quebrar disparo (ver `skill-description-eficiente.md`).
