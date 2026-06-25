# Manutenção 100% backstage — arquitetura

> Princípio de produto cravado pelo {{USUARIO}}go (23/06): "o CORTEX é user-friendly; a gestão dele
> (memória, sessão, regra nova, crítica, elogio) roda em SEGUNDO PLANO e NÃO spama o chat que o
> usuário usa pra fazer os projetos dele. Fica num log, e me ajuda a melhorar depois — sem o
> usuário precisar lembrar de nada." Reforça [[manutencao-memoria-invisivel]] (que existia mas não
> era cumprida) e responde ao furo "o usuário pode esquecer de fechar-sessão".

## Os dois furos que isto fecha
1. **Eu narrar manutenção no chat** — comportamental. Já era regra; estava sendo violada. Paro.
2. **Hooks injetarem aviso no contexto da sessão de trabalho** — estrutural. nudge_destilacao,
   nudge_referencias, guarda_tamanho, captura_regra hoje jogam `additionalContext` que entra na
   leitura do Claude e às vezes vaza pro chat, e sempre ocupa contexto/distrai. ERRADO durante o
   trabalho do usuário.

## A regra
A captura de aprendizado (regra nova, retrabalho, crítica, elogio, acerto/erro) escreve em LOG
SILENCIOSO e fica 100% quieta durante a sessão de trabalho — ZERO additionalContext no chat.
O log vira regra/ajuste DEPOIS, num processamento fora da conversa de trabalho.

## O furo do "esquecer de fechar-sessão" (o que torna user-friendly)
O processamento NÃO pode depender de ritual manual (`/fecha-sessao`) — o {{USUARIO}}go quase nunca
fecha. Então o gatilho do processamento é AUTOMÁTICO, não humano:
- **Vigia de inatividade** (Task Scheduler, já existe): detecta sessão abandonada 2h+ e processa.
- **catch-up-aprendizado** (skill, já existe): processa em lote a fila que ficou pra trás.
- **SessionEnd** quando dispara naturalmente.
O log é a fonte da verdade que sobrevive ao "esqueci de fechar": mesmo sem ritual, o aprendizado
está gravado e será destilado no próximo passe automático. Nada se perde por esquecimento.

## Os logs (fonte da verdade backstage)
- `_regras-detectadas.log` — sinais de regra/preferência durável (captura_regra). JÁ EXISTE.
- `_feedback.log` (NOVO) — acertos, erros, críticas, elogios que o {{USUARIO}}go dá conversando. Cada
  linha: timestamp + tipo (acerto|erro|critica|elogio) + trecho. Destilado depois pra virar regra
  ou ajuste de comportamento. O {{USUARIO}}go não vê a máquina rodando; só sente o sistema melhorar.
- `_sessions-pendentes.log` — fila de sessões a destilar. JÁ EXISTE.

## O que muda nos hooks
- captura_regra: continua detectando, mas o `additionalContext` deixa de ser injetado no chat de
  trabalho por padrão. Escreve no log. (Decisão {{USUARIO}}go: só log, processa no fechamento/automático.)
- nudge_* e guarda_tamanho: rodam no SessionStart (não no meio do trabalho), então o ruído é menor;
  ainda assim, manter o additionalContext CURTO e claramente backstage, e eu NUNCA repasso pro chat.

## Princípio que fica
Manutenção do sistema é invisível e não depende de o usuário lembrar de nada. O trabalho dele no
chat fica limpo; o aprendizado acontece sozinho, no backstage, e só se manifesta como o sistema
ficando melhor. Casa com [[cortex-a-promessa]] e [[auto-manutencao-memoria]].
