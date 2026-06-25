# Os 4 princípios do Karpathy (comportamento de agente numa tarefa)

> Origem: tweet do Karpathy de jan/2026 sobre os erros recorrentes de agente de código → repo
> `forrestchang/andrej-karpathy-skills` (43k+ estrelas em 1 semana).
> Tweet: https://x.com/karpathy/status/2015883857489522876
>
> Camada: isto NÃO entra nos 6 princípios-AIOS (`principios-aios.md`) — aqueles regem a ARQUITETURA
> do cérebro. Estes regem a EXECUÇÃO de uma tarefa. Vivem na seção "Planejar, delegar, verificar"
> do CLAUDE.md. Ler sob demanda; o gatilho seco de cada um já está reforçado lá em cima.

## Por que isto importa para o AIOS

O sistema frequentemente já cobre os 4 em prosa ("porquê antes do como", "sem vibe code", "critério
é o último estado"). O que o Karpathy adiciona não é conteúdo, é FORMA: cada princípio é
`frase-âncora curta → bullets acionáveis → um "test" verificável`. Esse formato é o que faz o agente
PARAR e checar, em vez de só "ter lido a recomendação". Por isso a destilação reforça a redação dos
gatilhos no CLAUDE.md, em vez de adotar o arquivo genérico dele (que é pra dev sem contexto).

## Os 4 princípios (verbatim) + tradução para o trabalho do operador

O original é sobre CÓDIGO. Adapte cada princípio para o domínio real do operador, porque o vício
muda de forma fora do código.

### 1. Think Before Coding — *pensar antes de fazer*
**Âncora:** não assumir, não esconder confusão, expor os trade-offs.
- Diga as suposições em voz alta. Em dúvida, pergunte.
- Se há mais de uma interpretação, mostre as duas — não escolha em silêncio.
- Se existe caminho mais simples, fale. Discorde quando for o caso.
- Se algo está confuso, pare. Nomeie o que confunde. Pergunte.

**Tradução para o domínio do operador:** o vício aqui não é assumir formato de arquivo; é começar
a executar antes de saber o objetivo. Confirmar o que se quer antes de construir, não refazer depois.

### 2. Simplicity First — *simplicidade primeiro*
**Âncora:** o mínimo que resolve. Nada especulativo.
- Nenhuma feature além do pedido.
- Nenhuma abstração pra código de uso único.
- Nenhuma "flexibilidade"/"configurabilidade" não pedida.
- Nenhum tratamento de erro pra cenário impossível.
- Escreveu 200 linhas e cabia em 50? Reescreve.
- Teste: "um engenheiro sênior diria que isto está complicado demais?" Se sim, simplifica.

**Tradução para o domínio do operador:** entregar o mínimo que resolve o brief, respeitar teto de
passes definido, não retrabalhar o que já passou. Não é code golf; é não inflar o escopo nem o
número de iterações.

### 3. Surgical Changes — *mudança cirúrgica*
**Âncora:** mexer só no necessário. Limpar só a própria bagunça.
- Não "melhorar" código/comentário/formatação adjacente.
- Não refatorar o que não está quebrado.
- Casar com o estilo existente, mesmo que você faria diferente.
- Viu código morto não relacionado? Mencione — não apague.
- Removeu algo? Só os imports/variáveis que SUA mudança deixou órfãos. Não apague código morto
  pré-existente sem pedir.
- Teste: toda linha mudada rastreia direto ao que o operador pediu.

**Tradução para o domínio do operador:** ao editar qualquer arquivo do projeto, mudar só o que foi
pedido. Não retocar seções adjacentes "de brinde". Toda mudança rastreia ao pedido.

### 4. Goal-Driven Execution — *execução guiada por meta*
**Âncora:** definir o critério de sucesso. Iterar até verificar.
- Transformar ordem imperativa em meta verificável:
  - "adiciona validação" → "escreve teste pra input inválido, depois faz passar"
  - "conserta o bug" → "escreve teste que reproduz, depois faz passar"
- Tarefa de vários passos: declarar plano curto no formato
  ```
  1. [passo] → verify: [check]
  2. [passo] → verify: [check]
  ```
- Critério forte deixa o agente iterar sozinho. Critério fraco ("faz funcionar") exige clarificação
  o tempo todo.

**Tradução para o domínio do operador:** o que o formato `passo → verify` adiciona é tornar o check
EXPLÍCITO antes de executar. Nunca entregar ao operador algo que não passou pela verificação
definida no início da tarefa.

## Tabela de anti-padrões (do repo, traduzida)

| Princípio | Anti-padrão | Correção |
|---|---|---|
| Think Before | Assume formato/escopo/campo em silêncio | Lista as suposições, pergunta antes |
| Simplicity | Strategy pattern pra um cálculo de desconto | Uma função até a complexidade ser REAL |
| Surgical | Reformata, adiciona type hint enquanto conserta bug | Só as linhas que consertam o problema relatado |
| Goal-Driven | "Vou revisar e melhorar o código" | "Teste que reproduz o bug X → faz passar → sem regressão" |

## A frase-chave do repo
"Código bom é o que resolve o problema de HOJE de forma simples, não o problema de amanhã
prematuramente." — o erro dos exemplos "complicados" não é estarem errados; é o TIMING: adicionam
complexidade antes de ela ser necessária.
