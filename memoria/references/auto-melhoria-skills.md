# Auto-melhoria de skills (o sistema conserta as próprias ferramentas)

`como-o-sistema-aprende.md` diz "skill que falha, skill que melhora". Aqui está o COMO: o gatilho
que faz isso acontecer sozinho, em vez de ser uma boa intenção. O grafo (links/colisões) mora em
`grafo-de-skills.md`; comprimir description em `skill-description-eficiente.md`; criar skill nova
é regra dos 3 (memória `autonomia-criar-skill`). Esta peça é sobre MELHORAR skill que JÁ existe.

## A regra: correção procedural conserta a skill, não vira memória solta

A regra evitar-retrabalho (memória [[evitar-retrabalho-correcao-repetida]]) já classifica o que o
operador corrige em procedural / semântico / episódico. O **procedural** (um jeito de fazer, um passo
de workflow que se repetiu errado) NÃO vira memória de feedback — vira **correção dentro da skill que
errou**. Esse é o elo que faltava: a memória de feedback estava virando depósito de coisa que devia
ter consertado a ferramenta.

Pergunta-roteador, toda vez que for gravar um aprendizado:
> "Isso é um jeito de FAZER algo que uma skill cobre (ou deveria cobrir)?"
> - Sim → conserta a SKILL (passo abaixo). Não incha o MEMORY.md.
> - Não → segue o fluxo normal (feedback/memória, log/diário).

## Quando disparar a melhoria de uma skill (radar ligado, sem spam)

1. **A skill agiu errado e o operador corrigiu.** Disparou no momento errado, pulou um passo, gerou
   formato que foi rejeitado, citou skill irmã que não existe mais. Conserta na hora ou anota pra
   consertar (não deixa a próxima janela repetir).
2. **O operador citou uma skill no meio da crítica.** Se ele fala o nome de uma skill enquanto
   explica uma fricção, trate como sinal de melhoria da skill, mesmo sem a frase "melhora a skill".
   Primeiro tente entender sozinho qual regra, gatilho, limite ou exemplo precisa entrar; pergunte
   só se houver risco de mudar o contrato da skill.
3. **Durante a sessão, o CORTEX percebeu fricção recorrente.** Se o operador não cita a skill, mas
   o problema nasce claramente de um procedimento coberto por uma skill existente, deixe na fila de
   melhoria ou aplique o ajuste cirúrgico na hora. O ideal é o sistema aprender sem exigir que o
   operador nomeie a ferramenta.
4. **Mesma correção procedural 2-3x** (regra do 2-3 do evitar-retrabalho): se o mesmo ajuste manual
   foi feito por cima do output de uma skill duas/três vezes, a skill está incompleta. Embute o
   ajuste nela.
5. **Na destilação** (`fecha-sessao` / `aprender-do-dia`): ao varrer o transcript, se o aprendizado
   da sessão é sobre COMO uma skill se comportou, o destino é a skill, não uma regra nova de
   feedback. A destilação passa a perguntar isso antes de gravar.
6. **Na faxina do grafo** (`/audit`): colisão de gatilho, link faltante, description desatualizada
   viram propostas de melhoria (ver `grafo-de-skills.md`).

## Como melhorar a skill (cirúrgico, sem reescrever)

- **Erro de comportamento** (pulou passo, formato errado): adiciona/ajusta a regra na seção certa
  do corpo do SKILL.md, ou cria/alimenta uma seção **"Aprendizados"** no fim com a armadilha e a
  correção. Mudança mínima, não reescreve a skill.
- **Erro de disparo** (acionou na hora errada, ou não acionou): mexe na `description:` — e aí entra
  `skill-description-eficiente.md` (preservar gatilho/exclusão, cortar gordura). Erro de disparo
  por colisão com irmã: resolver no grafo, não só numa skill isolada.

## Limites (o que NÃO fazer sozinho)

- **Não reescrever a fundo nem fundir/apagar skill** sem o operador. Embutir uma correção pontual e
  ajustar gatilho: autonomia (cérebro pessoal). Refazer a arquitetura de uma família, apagar skill,
  mudar o que ela entrega: leque de propostas, o operador decide.
- **Não inflar a description** ao "melhorar". Melhorar gatilho quase sempre é cortar ambiguidade,
  não somar frase. Cada caractere da description custa token todo turno.
- **Regra dos 3 pra skill NOVA continua valendo.** Auto-melhoria é sobre as que existem; criar uma
  nova só quando o fluxo se repetiu ~3x (`autonomia-criar-skill`).

## Verificação

1. O aprendizado é procedural? Então foi pra DENTRO da skill, não pro MEMORY.md como feedback solto?
2. Se o operador citou a skill, tratei isso como sinal de melhoria ou descartei com motivo claro?
3. Mudança cirúrgica (regra nova / seção Aprendizados / ajuste de gatilho), não reescrita?
4. Espelhei no backup e nas versões de outros agentes quando existirem?
5. Se mexi em gatilho, passei pelo teste da `skill-description-eficiente.md` (ainda dispara, não
   colide com a irmã)?
6. Se era refatoração grande / apagar / fundir, parei e levei como proposta pro operador?
