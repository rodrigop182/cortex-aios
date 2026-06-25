# Ciclo de contexto: quando limpar e quando passar o bastão

A janela de contexto do Claude Code não é infinita. Conforme a conversa cresce, ela fica mais
lenta, mais cara e o modelo perde precisão (a partir de certo ponto, "burrice" por excesso de
contexto). Três mecanismos lidam com isso. Saber qual usar em cada momento é metade da eficiência
do CORTEX, e o usuário quase nunca conhece esses mecanismos, então o CORTEX deve ensiná-los.

## Os três mecanismos

1. **Compactação automática (nativa do Claude Code).** Quando o contexto se aproxima do limite, o
   Claude Code resume a conversa sozinho e segue. Você não precisa fazer nada pra não "estourar".
   Mas o resumo é genérico: ele decide o que manter e você perde nuance. Serve pra continuar a
   MESMA tarefa, não como estratégia de longo prazo.

2. **`/clear`: zerar entre tarefas.** Quando você TERMINA uma tarefa ou MUDA de assunto, dê
   `/clear`. Começar limpo evita arrastar contexto velho que não serve, melhora as respostas e
   reduz custo. É a prática recomendada: limpar o contexto entre tarefas distintas. O gatilho é a
   TROCA DE TAREFA, não o tamanho da conversa.

3. **`/handoff` + `/continuar-sessao`: atravessar a fronteira de sessão.** Quando uma tarefa de
   PESO vai continuar depois (amanhã, outra janela) e você não quer perder o fio, o CORTEX escreve
   um `/handoff`: um briefing curado do estado (o que ficou pronto, o próximo passo, os arquivos
   relevantes). Na janela seguinte, `/continuar-sessao` lê esse briefing e retoma exatamente de
   onde parou. É "compactação curada": diferente do resumo automático, aqui o CORTEX escolhe o
   sinal que sobrevive.

## A regra prática (o gatilho é semântico, não o tamanho)

- **Mesma tarefa, conversa esticou:** deixe a compactação automática cuidar. Não precisa handoff.
- **Acabou a tarefa ou vai trocar de assunto:** `/clear`. (Pergunta off-topic curta nem isso.)
- **Tarefa de peso que continua depois:** `/handoff` ao fechar, `/continuar-sessao` ao abrir.

O gatilho NÃO é "cheguei a X tokens". Tamanho é só um proxy. O gatilho bom é a **fronteira de
trabalho**: terminei, troquei de assunto, ou vou parar e retomar. Um teto de tamanho serve como
rede de segurança, não como sinal primário.

## Por que o handoff curado vence só-clear ou só-compactação

Pra trabalho trivial, `/clear` basta. Pra trabalho de peso que cruza sessões, o handoff ganha
porque é seletivo: o resumo automático é genérico e arrasta ruído; o handoff guarda só o que a
próxima janela precisa pra acertar de primeira. É o mesmo princípio do CORTEX: chegar pronto, não
chegar cheio.

## O papel do CORTEX (proativo)

O usuário não precisa saber disto de cor. O CORTEX observa a conversa e, quando faz sentido,
oferece: "essa tarefa parece encerrada, quer dar `/clear`?" ou "isto é de peso e vai continuar,
faço um `/handoff`?". Educar uma vez (no `/como-funciona`) e oferecer no momento certo, em vez de
deixar o usuário arrastar uma janela saturada sem saber por quê.
