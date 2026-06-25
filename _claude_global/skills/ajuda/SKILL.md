---
name: ajuda
description: "Aciona quando o operador descreve uma DOR sem saber a solução: 'problema: X', 'como eu faço X', 'preciso de uma ferramenta pra Y', 'qual a melhor forma de Z', 'tem algo grátis que faça isso', ou qualquer descrição de dificuldade sem solução definida. Pesquisa e recomenda o caminho mais eficiente — open source primeiro, leque de 2-3 opções + veredito. NAO é tutorial de ferramenta já escolhida nem pesquisa de referência visual (referencias-design)."
---

# /ajuda — qual o caminho mais eficiente pra resolver isso?

O operador tem uma DOR. Não sabe qual ferramenta, método ou abordagem usar. Esta skill
pesquisa e recomenda — sem assumir que ele quer a solução mais complexa.

## Princípio

Open source e grátis primeiro. Solução simples antes de solução elaborada. Se já existe
ferramenta pronta que resolve em 5 minutos, não construir do zero.

## Fluxo

### 1. Entender a dor (se não estiver clara)

Se o pedido for vago, fazer UMA pergunta só:
- Qual o contexto? (volume, frequência, plataforma, orçamento)

Se estiver claro o suficiente, pular direto pro passo 2.

### 2. Pesquisar (WebSearch se necessário)

Buscar opções reais — não inventar. Prioridade:
1. Ferramenta open source / gratuita que resolve direto
2. Serviço freemium com tier grátis suficiente
3. Solução paga só se as anteriores não resolverem

### 3. Entregar leque de 2-3 opções + veredito

Formato:

**Opção 1 — [nome] (grátis/pago)**
O que faz, como resolve o problema, limitação principal.

**Opção 2 — [nome]**
...

**Veredito:** qual eu usaria e por quê (1 linha).

Se uma opção domina claramente, dizer isso sem enrolar.

## Não confundir

- Já escolheu a ferramenta e quer saber como usar → responde direto, sem acionar esta skill
- Quer referência visual de design → skill de referências de design
- Quer automatizar algo repetitivo → /level-up
