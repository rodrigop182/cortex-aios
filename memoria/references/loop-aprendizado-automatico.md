# Loop de aprendizado automático do CORTEX (desenho)

Como o CORTEX aprende sozinho com o uso. Substitui o fluxo manual `fecha-sessao` (que o operador
nunca rodava → 18 sessões pararam na fila → o sistema aprendia zero). Liga em [[cortex-visao-produto]],
`projects/cortex-roadmap.md` (F1+F2) e [[cortex-3-loops-auto-desenvolvimento]].

## A dor que justifica tudo

"A IA não presta pro que eu faço" = três falhas, não burrice do modelo: não **contextualizou**, não
**especificou**, não usou o **método certo**. Quem não é programador NUNCA vai fazer as três sozinho.
O CORTEX cobre por ele:
- **contexto** ← memória que aprende quem ele é, como fala, o que gosta;
- **especificação** ← entrevista proativa antes de tarefa de peso;
- **método certo** ← o agente sabe a abordagem (pesquisou o estado da arte, tem as skills) e aplica
  sem o usuário saber pedir. Esta é a **proatividade**, o coração do produto.

Princípio: cada sessão deixa a próxima mais fácil, com menos iteração e menos token. Tradeoff: custo
fixo de contexto por turno, que se paga no médio/longo prazo (a métrica em `metricas/` prova ou refuta).

## O fluxo real do usuário (onde plugar)

Uma janela principal que migra via **handoff → continuar**. O operador não usa `fecha-sessao`; às
vezes fecha chat no X sem avaliar. Então o aprendizado tem que entrar no gesto que ele JÁ faz
(handoff) e no que fecha sozinho (SessionEnd), nunca num passo manual extra.

## O loop reformulado

1. **CAPTURA** — `registrar_sessao.py` (SessionEnd) enfileira toda sessão em `_sessions-pendentes.log`,
   inclusive as fechadas no X. [já existe]
2. **DESTILA** (automático: no handoff + varredura da fila por subagente) — um subagente Sonnet lê o
   transcript e extrai três coisas:
   - **sobre o operador**: contexto, preferência, voz, o que não gosta;
   - **MÉTODO por tipo de tarefa**: qual abordagem/skill deu certo (ex: "landing → briefing +
     referência FCC"). É o que alimenta a proatividade depois;
   - **erro a não repetir**.
3. **GATE de qualidade automático** — antes de gravar, checa dedup/contradição contra a memória
   existente (a literatura alerta: regra gerada por LLM vem redundante/contraditória). Não grava lixo.
4. **GRAVA sozinho** na memória pessoal (decisão do operador: grava sozinho + visibilidade). Reversível
   no git. O gate humano pesado fica só pro TEMPLATE (`/templatar`), nunca pra memória pessoal dele.
5. **MEDE** — no mesmo passe, computa a métrica de 1-shot (iterações por tarefa) → `metricas/1shot-log.csv`.
   (Definição em `metricas/README.md`.)
6. **VISIBILIDADE** — no `continuar`, 1 linha do que foi aprendido (transparência, não aprovação).

## O que muda nas peças existentes

- **handoff**: além de salvar o estado da tarefa, dispara DESTILA+MEDE da janela que está fechando.
  Vira o "fecha-sessao de fato" do operador.
- **continuar**: mostra em 1 linha o que a sessão anterior ensinou.
- **fecha-sessao**: deixa de depender de comando manual; sua lógica de destilação passa a rodar via
  subagente, disparada pelo handoff e pela varredura da fila. Mantém o Gate de relevância e o
  roteamento procedural (conserta skill) vs semântico (grava memória).
- **nudge_destilacao**: em vez de só cutucar, é o gatilho da varredura automática da fila.

## Por que automático (e não aprovação manual)

O operador tem preguiça de curar (todo usuário tem). Aprovação manual = fila acumula = loop morre (foi
o que aconteceu). Automático com visibilidade + reversível no git + gate de qualidade é o único
desenho que de fato fecha o loop. É também o que torna o produto viável pra quem não é programador.

## Estado

Desenhado 21/06. Fundação da métrica criada (`metricas/`). A fazer: plugar destila+mede no handoff,
varredura automática da fila, gate de dedup, visibilidade no continuar. Processar as 18 pendentes
como primeira rodada (prova + zera a dívida).
