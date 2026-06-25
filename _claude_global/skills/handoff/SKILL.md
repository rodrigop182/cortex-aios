---
name: handoff
description: Avalia se vale fechar a janela atual e abre nova com briefing em handoff-session/ pra a próxima instância começar com contexto completo. Usar quando o operador disser "vale trocar de janela?", "devo dar /clear?", "faz um handoff", ou quando você perceber que a conversa ficou longa/mudou de assunto/está relendo contexto velho. NÃO é resumo de conteúdo pro usuário; é instrução pra a PRÓXIMA instância.
---

# Handoff — passagem de bastão entre janelas

Contexto longo e relido é cobrado a cada turno. Quando a conversa cresce, fica mudando de assunto
ou arrasta tarefa antiga, cada novo turno custa mais e você começa a perder o fio. A saída é
fechar a janela e abrir uma nova, mas zerar perde tudo. Esta skill resolve as duas pontas: **dizer
quando vale trocar** e **gravar um briefing** pra a janela nova começar onde esta parou, sem
reler a conversa toda.

Handoff serve a **dois casos**, não só um:

1. **Trocar de janela (contexto saturado).** A conversa ficou grande/confusa; você fecha e reabre
   limpo, levando o estado no briefing. É o caso clássico (Parte 1).
2. **Derivar uma fatia paralela sem poluir a sessão atual.** No meio de uma tarefa você (ou o
   operador) percebe algo fora de escopo: um bug, um refactor, um protótipo. Em vez de esticar a
   sessão atual (que dilui o foco e empurra pro "modo burro") ou dar /clear (que mata o progresso
   atual), você recorta SÓ aquela fatia num briefing e passa pra OUTRO agente. As duas sessões
   seguem independentes. Esse caso está na Parte 3.

## Parte 1: vale trocar de janela?

Quando o operador perguntar (ou você perceber), avalie com sinceridade. Sinais de que SIM, vale
trocar:

- **Mudou de assunto.** A tarefa de agora não tem nada a ver com o começo da conversa. Todo o
  contexto antigo só está pesando.
- **Conversa longa com tarefa concluída.** O que precisava ser feito ficou pronto e agora começa
  coisa nova. Janela limpa é mais barata e mais nítida.
- **Você está relendo muito.** Se a cada turno você precisa varrer um monte de histórico pra
  lembrar do que importa, o sinal/ruído caiu.
- **Está confuso ou se repetindo.** Perder detalhe, refazer coisa já feita, misturar tarefas:
  tudo sintoma de contexto saturado.

Sinais de que NÃO vale (não empurre handoff à toa):
- Tarefa em andamento no meio de um raciocínio: trocar agora quebra o fluxo.
- Conversa ainda curta e focada: o ganho não paga o atrito de reabrir.

**Autonomia: gere o briefing sozinho ao saturar.** Quando os sinais de SIM aparecerem COM tarefa
em aberto, NÃO pergunte "quer que eu gere o handoff?" — grave o briefing direto em
`handoff-session/` (Parte 2) e avise em uma linha: "Salvei um handoff em <arquivo>; se quiser,
pode dar /clear que a próxima janela pega o contexto." Se NÃO valer, diga que ainda está tranquilo
e siga, sem gerar nada.

**Importante:** quem dá o /clear é o operador, não você. Você gera e salva o briefing sozinho,
mas a troca de janela é dele. Nunca finja que trocou de janela. E gerar o briefing não é retomar
tarefa: retomada continua só sob pedido (ver Parte "Como a janela NOVA usa isso").

## Parte 2: gerar o briefing

Grave um arquivo .md em `handoff-session/` dentro desta skill. Esse arquivo é escrito **pra
próxima instância de você ler**, não pro operador. Então escreva como instrução de trabalho,
direto ao ponto, sem floreio.

**UM arquivo por sessão — atualizar, nunca recriar.** O briefing é vivo: existe UM .md por
sessão e ele é mantido fresco ao longo dela (em marcos naturais) e consolidado quando o operador
pede "faz um handoff". Se já existe o .md DESTA sessão, NÃO crie outro: reabra o mesmo, atualize
só as seções que mudaram, mantenha o resto. Pedir handoff = "consolida agora", não "recomeça do
zero" — economiza trabalho e evita lixo duplicado.

Nome do arquivo: `handoff-AAAA-MM-DD-<assunto-curto>.md` (data atual real + slug do assunto). UM
por sessão/assunto: na mesma sessão, reusar esse nome e sobrescrever o conteúdo, não criar
variantes por horário. Arquivo novo só pra OUTRA sessão ou recorte de fatia paralela (Parte 3).

### Estrutura do briefing

```markdown
# Handoff — <assunto> — <data>

## Foco da próxima sessão
<1 linha: pra que serve a janela nova. Se o operador passou um argumento/propósito ao pedir o
handoff, é ISSO aqui — o briefing inteiro se molda a esse foco.>

## Onde paramos
<1-2 parágrafos: o que estava sendo feito e o estado atual. Concreto.>

## O que já está pronto
- <itens concluídos, com caminho de arquivo quando houver>

## O que falta / próximo passo
- <a próxima ação concreta, na ordem>

## Decisões que o operador já tomou (não re-perguntar)
- <decisões fechadas, pra a próxima janela não reabrir o que já foi decidido>

## Armadilhas / o que NÃO fazer
- <erros já descobertos, becos sem saída, coisas que ele já rejeitou>

## Skills a invocar na janela nova
- <skills que dão o "tempero" da próxima sessão. A janela nova já entra com a skill certa sem ter
  que pensar.>

## Arquivos-chave
- <caminhos dos arquivos relevantes, pra a próxima janela abrir direto sem caçar>
```

Preencha só o que existe; seção vazia, corta. O valor está em **decisões já tomadas** e
**armadilhas** — é o que a janela nova não tem como adivinhar e o que mais gera retrabalho se
perder. (Se uma correção se repetiu, ela também merece virar memória permanente pela regra
evitar-retrabalho, não só o handoff.)

**Regras de escrita do briefing:**

- **Foco primeiro.** Se o operador disse pra que serve a próxima sessão, trate isso como o norte
  do documento e adapte tudo a ele. Sem saber o foco, não dá pra escrever um bom handoff — se ele
  não disser, pergunte em uma linha.
- **Ponteiro, não cópia.** Não duplique no briefing o que já existe em outro artefato (outro .md,
  issue, PRD, código). Aponte o caminho/link. Handoff que repete conteúdo incha e fica caro de
  reler — exatamente o que essa skill existe pra evitar.
- **Redija dado sensível.** Nunca escreva chave de API, senha, token, webhook ou PII no .md. Se
  precisar referenciar, diga "a credencial X" sem o valor.
- **Só markdown, agente nenhum amarrado.** O briefing é um .md puro: serve tanto pra outra janela
  do Claude quanto pra outro agente — útil se quiser review adversarial entre agentes diferentes.

### Limpeza

Os .md em `handoff-session/` são temporários — servem pra atravessar a troca de janela, não pra
virar arquivo morto. **Critério de limpeza é "a tarefa foi resolvida?", não "quantos dias tem".**

- **Handoff cuja tarefa você tem CONFIANÇA que foi resolvida** (viu a conclusão, ou a
  memória/diário registra feito) → apague e avise em 1 linha. Tarefa feita, briefing morto,
  remove.
- **Handoff que você NÃO tem certeza se andou** → NÃO apague no escuro (apagar é irreversível,
  bate na trava "apagar pede OK"). Mantenha e, se atrapalhar a decisão de qual retomar, pergunte.

Confiança alta = apaga e avisa; dúvida = mantém e pergunta. Não deixe a pasta virar depósito de
tarefa já entregue.

## Parte 3: handoff de fatia paralela (sem largar a sessão atual)

Às vezes o gatilho não é "a conversa ficou grande", e sim **surgiu um sub-trabalho fora de
escopo** no meio do caminho: um bug que você notou, um refactor que aparece, um protótipo que
precisa ser visto em código antes de decidir. Esticar a sessão atual pra fazer isso dilui o foco
e te empurra pro modo burro; dar /clear mata o progresso do que você já estava fazendo. A saída é
recortar **só essa fatia** num briefing e mandar pra outro agente, mantendo a sessão atual pura.

Como fazer:

- Gere o briefing normal (Parte 2), mas com o **Foco** recortado SÓ no sub-trabalho — não no
  que a sessão atual estava fazendo. Leve só o contexto que aquela fatia precisa.
- **Não dê /clear.** A sessão atual continua viva. O handoff vai pra OUTRA janela; as duas correm
  independentes. Isso é diferente da Parte 1, onde você está fechando a janela atual.
- Recortar a fatia também **afia a sessão atual**: ao declarar "isso é fora de escopo, vai pra
  outro lugar", o assunto sai do seu radar aqui e você volta a focar no objetivo original.
- **Padrão ida-e-volta (protótipo).** Vale derivar uma fatia, trabalhar nela em outra janela, e
  essa janela gerar um handoff DE VOLTA pra sessão original com só os aprendizados não-óbvios
  (o que não ficou capturado no próprio código). É um "sub-agente faça-você-mesmo": uma janela
  isolada faz o trabalho pesado, comprime o aprendizado, devolve pro pai.

## Como a janela NOVA usa isso (gatilho explícito)

**Aviso automático (hook SessionStart):** toda sessão nova, o hook `scripts/detectar_handoff.py`
(registrado no `settings.json`) verifica `handoff-session/` e, se houver briefing, injeta no
contexto um aviso "HANDOFF DISPONIVEL: ..." apontando o .md mais recente. É só um aviso — ele
NÃO manda retomar. Serve pra saber de primeira que o handoff existe e ir direto ao arquivo certo
quando o operador pedir, sem tropecar em `_sessions-pendentes.log` (isso é da `fecha-sessao`,
outra coisa).

Regra de decisão: **conversa nova começa limpa por padrão. Só retoma o handoff se o operador
pedir.** Existir um .md em `handoff-session/` (ou o aviso do hook) NÃO significa retomar
automaticamente — senão toda sessão nova empurraria a tarefa antiga, mesmo quando ele quer
começar outra coisa.

- Ele diz **"continua de onde paramos"**, "lê o handoff", "retoma o pipeline", ou cita a tarefa
  anterior → abra o handoff certo em `handoff-session/`, leia, e retome do "próximo passo",
  respeitando decisões e armadilhas. **Qual handoff, quando há mais de um:** NÃO assuma o mais
  recente — "mais recente" é palpite de máquina, quem sabe o que ele quer continuar é ele. Se há
  1 só, vá direto. Se há vários, abra cada um, leia o "Foco", e case com o que ele disse; se a
  frase dele aponta claramente um, vá nele; se NÃO dá pra saber, PERGUNTE listando foco+data de
  cada candidato (um toque pra ele escolher), não chute.
- Ele NÃO diz nada / abre assunto novo → janela nova, trabalho novo. Não leia o handoff, não
  mencione. O arquivo fica parado até ele querer.
- Diferente da skill `fecha-sessao`: essa SIM roda sozinha no início se houver pendência (destila
  regras de trabalho, leve). Retomar TAREFA é só sob pedido; destilar REGRA é automático. Não
  confundir os dois.
- **Assimetria do próprio handoff (importante):** GERAR o briefing ao saturar é automático
  (Parte 1); RETOMAR a tarefa numa janela nova é só sob pedido. O briefing é uma rede de
  segurança que sempre existe quando o contexto satura; usar ela é decisão do operador a cada
  janela. Não retomar sozinho só porque há .md salvo.

## Checagem anti-duplicata

Se o operador pedir `/handoff` logo depois de você já ter gerado um briefing nesta mesma sessão,
verifique antes de fazer qualquer coisa: algo mudou desde o último briefing?

- **Nada mudou:** responda em 1 linha que o handoff já está salvo e ele pode dar `/clear`. Não
  regere, não reabra, não refaça.
- **Houve progresso novo:** atualize o briefing existente (seções que mudaram, não reescreva tudo)
  e avise.

O gatilho do "não refaço" é "já fiz e nada mudou", não o relógio (não é "fiz há menos de X
minutos"). Um handoff 5 minutos atrás com trabalho novo no meio merece atualização; um handoff de
ontem sem mudança nenhuma não merece recriação.

## Verificação final

1. Identifiquei qual caso é (trocar de janela vs. derivar fatia paralela) e avaliei de verdade se
   vale (não empurrei handoff no meio de um raciocínio em andamento)?
2. Deixei claro que quem dá o /clear é o operador? (E que na fatia paralela NÃO se dá /clear — a
   sessão atual segue viva.)
3. Sei o foco da próxima sessão (perguntei se ele não disse) e moldei o briefing a esse foco?
4. Se gerei briefing, ele está escrito pra a próxima instância (instrução), não pro humano
   (resumo)?
5. Inclui decisões já tomadas e armadilhas (as duas seções que mais evitam retrabalho), e a seção
   de skills a invocar?
6. Usei ponteiro em vez de copiar artefato que já existe, e não deixei vazar dado sensível no .md?
7. Salvei em handoff-session/ com nome datado, e lembrei da limpeza?
