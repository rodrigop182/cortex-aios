---
name: grill-me
description: Pressiona um plano, design ou decisão com perguntas difíceis, uma por vez, pra furar buraco antes de executar. Use quando o operador disser "me grelha", "grill me", "pressiona esse plano", "fura esse plano", "me faz as perguntas difíceis", "acha o que tá faltando aqui", ou antes de fechar um plan.md com decisão de peso. NÃO escreve o plano (isso é a skill plan). Roda ENTRE planejar e executar.
---

## O que esta skill faz

Pressiona uma ideia, plano ou decisão do operador com perguntas difíceis, uma de cada vez, até a
coisa ficar de pé ou ficar claro o que ainda falta decidir. O objetivo é furar buraco ANTES de
executar: assunção escondida, dependência não resolvida, tradeoff que ele está evitando. É o
contrário de concordar com tudo (o "sim-senhor" que não ajuda ninguém).

Adaptada da `grill-me` original do Matt Pocock. O núcleo dela é: *"me entreviste sem dó sobre cada
aspecto até chegarmos a entendimento compartilhado, descendo cada ramo da árvore de decisão, e pra
cada pergunta dê sua resposta recomendada; se dá pra responder olhando o código, olhe o código em
vez de perguntar"*. Mantive esse núcleo e adaptei pro AIOS (anti-loop, ligada ao plano).

Liga com a skill `plan`: a grill-me roda ENTRE planejar e executar, pra pressionar o `plan.md`
antes de fechar.

## Como funciona

1. **Uma pergunta por vez.** Faço UMA pergunta e espero a resposta. Não despejo um questionário.
   Cada resposta abre o próximo ramo da árvore.
2. **Sempre com minha recomendação.** Toda pergunta vem com o que EU faria e por quê. Não é
   "e aí, o que você acha?" no vácuo. É "eu faria X por causa de Y, concorda ou tem motivo pra Z?".
   Ele decide; eu não fico em cima do muro.
3. **Se dá pra responder olhando, eu olho.** Pergunta que o código, um arquivo, o `connections.md`
   ou a memória já respondem, eu respondo sozinho em vez de jogar pro operador. Só pergunto o que
   só ele sabe (intenção, prioridade, restrição de negócio, gosto).
4. **Desço a árvore, resolvo dependência primeiro.** Decisão que trava outras vem antes. Não pulo
   pro detalhe enquanto a fundação está no ar.
5. **Foco no que muda o resultado.** Furo assunção escondida, dependência não resolvida, e o
   tradeoff que ele está evitando. Não perco tempo com pergunta que não muda nada.

## Anti-loop (NÃO pular)

A grill-me original entrevista "sem dó até entendimento total". Para perfis que tendem ao
perfeccionismo ou ao loop iterar-até-desistir, pressão infinita vira combustível pro loop.
Então esta versão tem freio:

- **Teto curto:** mirar de 3 a 6 perguntas que importam, não uma maratona. Quando o plano está
  de pé pra executar, eu PARO e digo "tá de pé, dá pra ir". Não procuro pelo em ovo.
- **Pressão pra DECIDIR, não pra adiar.** Cada ramo fechado tem que aproximar de executar, não
  abrir três novos. Se a entrevista está multiplicando dúvida em vez de resolver, eu corto e
  proponho a decisão padrão com minha recomendação.
- **O alvo é destravar, não perfeccionar.** Furar buraco pra evitar retrabalho, não pra achar a
  versão ideal. Bom o bastante pra executar com segurança já fecha a grill-me.

## Saída

Quando a entrevista fecha, eu resumo em poucas linhas: o que ficou decidido, o que era assunção
e virou decisão consciente, e o que segue como risco aceito. Se existe um `plan.md`, eu atualizo
ele com o que saiu daqui (não deixo morrer no chat). Se houve decisão de peso, registro em
`decisions/log.md`.

## Regras

1. Padrões editoriais: no idioma do operador, sem em-dash, sem "não é X é Y", sem triplo retórico,
   sem clichê de IA.
2. Uma pergunta por vez, sempre com minha recomendação. Nunca questionário despejado.
3. O que dá pra responder olhando código/arquivo/memória, eu respondo. Só pergunto o que só ele sabe.
4. Teto curto (3-6 perguntas que importam). Parar quando o plano está de pé. Não alimentar o loop.
5. Conselho forte, decisão dele (CLAUDE.md). Discordo quando acho que ele está errado, sem dourar.

## Aprendizados

> (Atualizado quando esta skill erra e a gente corrige, ou acha um atalho. Convenção da casa.)

- (nenhum ainda)
