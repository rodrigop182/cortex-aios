---
name: orcamento-contexto-250k
description: Area util de contexto deve ser calculada sobre 250k tokens por janela antes de handoff, salvo medicao local diferente.
metadata:
  type: reference
---

# Orcamento de contexto 250k

Criterio inicial: a area util da operacao e 250k tokens por janela. Acima disso, a qualidade operacional tende a cair e o caminho certo e handoff.

**Why:** O CORTEX deve otimizar o custo fixo contra a janela que vale usar na pratica, nao contra o teto tecnico do modelo.

**How to apply:** Ao decidir boot, `MEMORY.md`, descricoes de skill, retrieval ou leitura automatica, perguntar se aquilo merece disputar a area util configurada. Se nao merece, vira ponteiro, busca sob demanda ou fica fora do turno.
