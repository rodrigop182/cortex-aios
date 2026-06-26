---
name: fecha-sessao
description: "Destila o aprendizado de UMA SESSAO em regras curtas de como trabalhar com o operador e atualiza a memoria. Escopo = esta conversa ou a pendente no log. Usar em \"fecha o dia\", \"fecha essa sessao\", \"encerra essa conversa\", \"resume o que aprendemos\", ao perceber que esta conversa encerra, ou com pendencia em _sessions-pendentes.log. LEVE: regras, nao relatorio. NAO processa varios dias acumulados (isso e destilar-sessoes)."
---

# Fecha-sessao — destilar regras de trabalho a cada dia

O operador quer que cada conversa deixe o AIOS um pouco melhor em trabalhar com ele. Não um
relatório pesado a cada sessão (isso queima token à toa), e sim **poucas regras curtas** que se
acumulam: preferências, jeito de decidir, o que evitar. Com o tempo, o AIOS chega em cada sessão
já sabendo como ele gosta de trabalhar.

## A mecânica (por que tem hook + por que é o AIOS que destila)

Um hook do Claude Code roda um comando de shell — ele **não raciocina**. Então a divisão é:

- **Hook `SessionEnd`** (configurado no settings.json) chama `scripts/registrar_sessao.py`, que
  só anexa uma linha em `memory/_sessions-pendentes.log`: data + caminho do transcript da sessão
  que acabou. É o rastro.
- **Hook `PreCompact`** chama
  `hooks/precompact_flush.py`, que anexa no MESMO log uma linha marcada
  `FLUSH-PRECOMPACT (auto|manual)`. Isso fecha a brecha do contexto que compacta NO MEIO de uma
  sessão longa (o SessionEnd só dispara ao fechar a janela; sem o flush, o aprendizado daquele
  trecho sumiria). Trate essa linha igual a uma sessão pendente: destile o transcript dela. A
  única diferença: a sessão pode AINDA estar rolando (foi só uma compactação), então pode haver
  mais de uma linha pro mesmo session_id — destile uma vez por transcript, sem duplicar.
- **O AIOS destila** na sessão seguinte: ao ver que há sessão pendente no log, lê o transcript
  daquela conversa e transforma o aprendizado em regras curtas na memória. Depois marca como
  processado.

O AIOS não consegue "perceber o /clear no momento" — quando o clear acontece, a janela já foi.
Por isso o rastro do hook e a destilação na próxima sessão.

## Quando rodar a destilação

- **Início de sessão, se houver pendência:** se `memory/_sessions-pendentes.log` tem linha(s) não
  processada(s), destile antes de começar o trabalho novo. Rápido.
- **Sob pedido:** "fecha o dia", "resume nossas regras", "o que aprendeu hoje".
- **Fim de conversa longa:** se deu pra perceber que está encerrando, ofereça destilar antes do
  clear.

## Gate de relevância (rodar ANTES de destilar cada sessão)

Nem toda sessão merece virar regra. O operador nem sempre encerra/dá handoff — muita sessão é
DÚVIDA pessoal ou tarefa trivial, e gravar isso incha o cérebro fino (proibido pelo CLAUDE.md:
"índice, não depósito"). Antes de destilar, classifique a sessão em uma faixa pela pergunta "isso
se relaciona com as DEMANDAS do operador (cliente, projeto, infra do AIOS, marca/produto, jeito
de trabalhar)?":

- **ALTA — destilar a fundo.** Mexeu em demanda real: trabalho de cliente, projeto próprio,
  infra/skills/memória do AIOS, decisão de marca ou produto, correção que vira regra, armadilha
  técnica reutilizável. Extraia 1-3 regras.
- **MÉDIA — destilar leve, só se sobrar algo nítido.** Trabalho real mas pequeno, ou exploração
  que rendeu UMA armadilha/preferência clara. Se não tiver nada cristalino, não force: pode ser
  "nada novo".
- **BAIXA — não gravar regra (no máximo 1 linha no diário, se houver marco).** Dúvida pessoal,
  pergunta de conhecimento geral, teste, brincadeira, tarefa trivial sem laço com as demandas.
  Marcar como processada e seguir. Gravar regra daqui é poluição.

Na dúvida entre faixas, puxe pra baixo: é mais barato perder uma regra fraca do que inchar o
índice. O critério detalhado mora na memória `criterio-relevancia-destilacao`.

## Como destilar (leve, não pesado)

1. Leia o transcript da sessão pendente (caminho está no log). Não releia inteiro palavra a
   palavra — varra atrás de: correções que o operador fez, preferências que ele afirmou, decisões
   de projeto, armadilhas técnicas descobertas.
2. Extraia **só o que vale pro futuro** — regra de comportamento, não fato efêmero.
   Pergunta-filtro: "isso me faria trabalhar melhor com ele numa próxima conversa qualquer?" Se
   não, descarta.
3. Para cada regra que passou no filtro, ROTEIE primeiro: **"isso é um jeito de FAZER algo que
   uma skill cobre (ou deveria cobrir)?"**
   - **Sim (procedural)** → conserta a SKILL que errou, não grava memória de feedback solta
     (senão o MEMORY.md vira depósito de coisa que devia ter virado correção de ferramenta).
     Embute a regra no SKILL.md (seção certa ou "Aprendizados").
     Detalhe em `references/auto-melhoria-skills.md`.
   - **Não (semântico)** → memória. Se já existe memória parecida (`type: feedback`),
     **atualize** ela (reforça, soma "voltou em DATA"). Não duplique. Se é nova, crie um arquivo
     curto (`type: feedback` pra jeito de trabalhar, `type: project` pra contexto) e adicione o
     ponteiro no MEMORY.md.
   - Correção que já apareceu 2-3x: isso é retrabalho, trate com o rigor da regra
     evitar-retrabalho (memória evitar-retrabalho-correcao-repetida; que também roteia
     procedural → skill).
   - **Veredito de eficácia da regra EXISTENTE (backstage, só quando a ligação for clara):**
     diferente de gravar regra nova, aqui você JULGA uma regra que já existe e foi posta à prova
     nesta sessão. Você tem o contexto da conversa pra ligar o feedback à regra certa — um script
     não tem (o operador diz "agora sim", não "a regra X funcionou"). Registre 1 linha em
     `memory/_eficacia-regras.log` (formato no cabeçalho do arquivo) SÓ quando a ligação for nítida:
     - Ele corrigiu DE NOVO algo que uma regra já mandava (a regra existe mas não pegou) →
       `slug.md  reforcar  <motivo curto>`. NÃO é pra podar: a redação está fraca, marca pra reescrever.
     - Uma regra claramente guiou o acerto e ele reconheceu ("agora sim", "era isso") →
       `slug.md  eficaz  <motivo curto>`.
     Na dúvida, NÃO registre — atribuição inventada é pior que ausência. Esse log protege regra eficaz
     da poda (`poda_por_evidencia.py`) e alimenta a "Saúde da memória" do `/audit`. Nunca narrar.
4. **COMPILAR o perfil compacto (o que barateia o dia 30):** atualize o bloco `=== PERFIL
   COMPACTO ===` no topo do `MEMORY.md`. É aqui que o aprendizado vira ATALHO, não leitura
   repetida. Para cada coisa nova que você aprendeu hoje e que evitaria uma pergunta no futuro,
   destile UMA linha curta em "Preferências já aprendidas" ou "Atalhos de contexto (o que não
   preciso mais perguntar)". Regras de ouro:
   - **Compilar, não acumular.** Se a nova linha torna uma antiga obsoleta, SUBSTITUA. O perfil
     fica do mesmo tamanho ou parecido, mais afiado. Não deixe crescer sem limite (carrega por
     sessão; inchar aqui mata a economia).
   - **Cada linha = uma pergunta a menos.** Se não evita uma pergunta/leitura futura, não entra.
   - **Trivial não entra** (mesma régua da destilação). Off-topic nunca.
   - **Fronteira do que NÃO entra:** o perfil compacto guarda só COMO TRABALHAR com você
     (preferências, voz, atalhos de contexto). Histórico técnico bruto (o que aconteceu, quais
     arquivos, decisões de código) NÃO entra aqui: esse volume vive nos transcripts do Claude
     Code, não na memória do CORTEX.
   O objetivo: a cada semana o perfil cobre mais, o CORTEX entrevista menos e relê menos, o custo
   por tarefa cai até estabilizar. É isso que faz o dia 30 ser mais barato que o dia 1.

5. **Uma linha do dia (opcional, leve):** se a sessão teve um marco que vale lembrar, registre
   uma linha só de contexto (ex: "2026-06-15: montado o pipeline X"). Sem detalhe técnico —
   isso o código guarda.
6. Marque a pendência como processada: limpe a(s) linha(s) do `_sessions-pendentes.log` (ou
   esvazie o arquivo se processou tudo).
7. **Higiene de estado (barata, só se a sessão mexeu nisso):** se durante o dia algum projeto
   com `status: pausa/resolvido` no frontmatter foi retomado, concluído ou abandonado, atualize
   o `status` daquela memória (ou aposente-a). NÃO varrer todas as memórias toda vez — só tocar
   no que a sessão de fato mudou. O `status` existe pra não arrastar estado vencido como se fosse
   atual.

## O que é regra boa (curta, útil)

- "Ele decide o caminho, eu executo — não encher de opções quando há default óbvio."
- "No técnico, aconselhar com critério próprio, não obedecer ao pé da letra."
- "Sem clichê de marketing, sem em-dash, sem triplos retóricos."

O que NÃO entra: o que já está no CLAUDE.md, detalhe técnico do que foi codado, fato que só
valia naquela tarefa.

## Economia (a regra mestra)

Isso tem que ser BARATO. Destilar é ler o necessário do transcript e escrever 1-3 regras curtas,
não reprocessar a conversa inteira nem gerar documento. Se não houver nada novo que valha, **não
grave nada** — dizer "nada novo pra anotar hoje" é uma saída válida e correta. O ganho vem do
acúmulo de regras simples ao longo do tempo, não do volume de cada dia.

## Verificação final

1. Destilei regras de COMO trabalhar com ele (não resumo técnico do que foi feito)?
2. Ficou curto (1-3 regras), atualizando memória existente em vez de duplicar?
3. Marquei a pendência como processada no log?
4. Se não havia nada novo, tive a disciplina de não gravar lixo?
