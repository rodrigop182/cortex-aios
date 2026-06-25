# Tiers de modelo — roteamento de subagentes por custo-benefício

Régua de como o CORTEX escolhe QUEM faz cada tarefa (modelo do subagente). O critério é
genérico; só o **mapa tier→modelo** é por-usuário (depende do que o seu plano dá).

## Princípio: pensar em TIERS, não em nomes

Modelos trocam rápido (a cada poucas semanas). Então o critério é por **tier abstrato**, e só o
**mapa tier→modelo** muda quando sai modelo novo. Nunca cravar nome de modelo no fluxo; ler do mapa.

- **Tier 1** = mais inteligente/caro/lento.
- **Tier 2** = equilíbrio capacidade/custo.
- **Tier 3** = mais rápido/barato, "burrinho".

**Regra de ouro:** começar pelo tier MAIS BAIXO que resolve a tarefa; subir só se a tarefa exige.
Usar os **três**, não só dois — o tier 3 dá conta de metade ou mais do trabalho diário.

## Workflow e lote (o multiplicador da economia)

A economia maior não é só escolher o tier certo pra UMA tarefa: é distribuir trabalho REPETITIVO
pra muitos subagentes de tier baixo, em vez de fazer tudo no tier 1 em série.

- **Tarefa de muitos passos ou em lote** (varrer N arquivos, converter, refatorar o mesmo padrão,
  extrair de várias fontes): vira um workflow/pipeline de subagentes tier-2/3, em paralelo quando
  os itens são independentes. O tier 1 entra só na decisão e na síntese final.
- **Regra prática:** se você se pegar fazendo a mesma coisa em série no tier 1, pare: é candidato a
  lote barato. Um uso pesado de tier-3 num workflow custa uma fração de um tier-1 fazendo tudo à mão.
- Dois operários nomeados prontos: `executor-rapido` (tier-3) pro mecânico PURO determinista, e
  `executor-mecanico` (tier-2) pra execução com alguma nuance/análise. Roteie cada tarefa pro tier certo.

## Bloqueio de fan-out (REGRA GLOBAL, precede workflow e skills)

Ao disparar subagentes em LEQUE (vários ao mesmo tempo, seja em workflow, skill ou pipeline
paralelo), aplicar SEMPRE:

1. **Cravar o tier por etapa.** Sem cravação explícita, o subagente herda o modelo da sessão
   pai — que é quase sempre o tier-1 (o mais caro). Resultado: N subagentes tier-1 rodando em
   paralelo, esgotando cota sem necessidade.
2. **Tier-1 a conta-gotas.** Decisão, síntese, curadoria de memória/regras. Nada mais.
3. **Braçal no tier mais baixo que resolve.** Busca, extração, conversão, edição mecânica, build,
   log: tudo vai pro tier-2 ou tier-3. Subir de tier só se a tarefa exigir de verdade.
4. **Largura limitada.** Número de subagentes paralelos: `min(16, núcleos - 2)` como teto razoável.
   Dimensionar pelo trabalho real, não pelo "quanto mais rápido melhor".

O risco não é rodar muitos agentes; é rodar muitos agentes no tier errado. Um fan-out de tier-3
em paralelo é barato e rápido. O mesmo fan-out com tier-1 por herança de sessão queima cota
significativa. A diferença é só cravar o tier antes de disparar.

## O que cada tier faz

**Tier 1 — raciocínio e julgamento.** Decisão de design/estratégia, arquitetura, conselho/voz do
OS, curadoria e edição de memória/regras, debug cabeludo, síntese final de material colhido.
Effort `high`/`xhigh`/`max`. NUNCA descer disto de tier (precisa do contexto da relação).

**Tier 2 — execução com algum julgamento.** Extração estruturada, consolidação de muitos inputs,
código não-trivial, varredura ampla COM análise, edição que pede algum gosto ("deixa mais
harmônico"), recon antes de mexer. Tarefa que carrega muito contexto (>200K) cai aqui por causa
da janela. Effort `medium`/`high`.

**Tier 3 — mecânico determinístico.** Edição apontada (CSS/texto/cor/espaço em arquivo X),
conversão/tratamento de arquivo, classificação, formatação, extração simples, busca/lista,
transformação repetitiva em lote. Tudo cujo "como fazer" já está 100% definido.

Classificar pelo PESO da tarefa, não pela palavra.

## Mapa tier→modelo (CONFIGURÁVEL por usuário/plano)

Edite só estas linhas conforme o que o seu plano dá. É a única coisa que muda entre usuários e
quando sai modelo novo. Os nomes abaixo são EXEMPLO (válidos em meados de 2026); confira os
modelos atuais e ajuste.

**Plano completo (tem acesso aos três tiers) — exemplo:**
```
tier1 = <modelo de raciocínio mais forte>
tier2 = <modelo equilibrado>
tier3 = <modelo rápido/barato>
```

**Plano mais enxuto (sem o tier-1 dedicado) — exemplo:**
```
tier1 = <modelo equilibrado>
tier2 = <modelo equilibrado>
tier3 = <modelo rápido/barato>
```
Sem acesso a um tier, ele colapsa pro de baixo. O critério de roteamento NÃO muda; só o mapa.

## Limitações técnicas a respeitar

Cada modelo tem limites próprios (janela de contexto, suporte ao parâmetro `effort`, thinking).
Antes de mapear um tier a um modelo, confira as capacidades dele e respeite-as:

- Modelo de tier-3 costuma ter **janela menor** e às vezes **não aceita o parâmetro `effort`**.
  Se for jogar tarefa de contexto gigante no tier-3, suba pro tier-2; e não passe `effort` pra um
  modelo que não o suporta (dá erro).
- Modelo novo da plataforma → confira a janela, o suporte a `effort`/thinking e ajuste o mapa.

## Calibração — observar com o tempo

Acompanhar se o **tier-3** dá conta do que recebe. O risco real NÃO é "o modelo barato é burro" —
é classificar como mecânica uma tarefa que tem julgamento escondido.

- **Sinais de falha do tier-3:** perde nuance, segue a instrução ao pé da letra sem ver a exceção,
  erra quando precisa entender contexto. → quando acontecer, **suba a tarefa pro tier-2**, não
  baixe o critério; anote o caso aqui.
- A curadoria e a edição de memória/regras quase sempre exigem **tier-1** (precisam do contexto da
  relação e pegam contradições que o tier baixo não vê). Mantenha-as no topo.

## Manutenção (modelos mudam)

Modelo novo → atualizar SÓ o mapa (3 linhas). O critério dos tiers é estável.

## Orquestração: o tier-1 ORQUESTRA, não executa na mão (regra global do CORTEX)

Regra do NÚCLEO do CORTEX — desconstrói más práticas que vêm setadas por padrão no modelo.

1. **NUNCA acionar subagente do tier-1 por padrão só porque o chat principal é tier-1.** O chat
   principal é o ORQUESTRADOR: decide, delega e verifica. Subagente só recebe tier-1 se a TAREFA
   dele for genuinamente de tier-1 (raciocínio/julgamento/síntese pesada). Disparar subagente do
   tier mais alto pra trabalho mecânico é desperdício e mau hábito padrão — cortar.
2. **Sessão pesada de subagentes tier-2/tier-3 é BOA, não ruim.** Quando o orquestrador distribui
   o braçal pra muitos subagentes baratos em paralelo, ele NÃO está fazendo na mão — está
   orquestrando, que é o papel dele. Preferir isso a executar serial.
3. **Workflow / fan-out é proativo e por rotina**, sempre que paralelizar ganha tempo e a tarefa é
   independente + verificável. NÃO depende de modo especial nem de o usuário pedir.
4. **Auditoria é SEMPRE adversarial — regra fixa.** O subagente que AUDITA/valida NUNCA é o mesmo
   que produziu (nem vê o raciocínio de quem fez). Quem fez não se auto-aprova: sempre um par
   independente tenta REPROVAR.

Por quê: o default do modelo é "fazer tudo sozinho no tier mais alto aberto". O CORTEX desconstrói
isso — o tier-1 é caro e o gargalo é a janela/velocidade dele; rende mais orquestrando barato e
verificando do que digitando cada edição.
