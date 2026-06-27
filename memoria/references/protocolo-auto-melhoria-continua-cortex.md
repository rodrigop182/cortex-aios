# Protocolo de auto-melhoria continua do CORTEX

Uso: todo fechamento de tarefa relevante
Escopo: sistema
Gatilho: "como pedir para melhorar o cortex", "isso foi friccao", "isso deveria ser automatico", "quando eu falar X puxe Y", "nao quero falar de cortex todo dia"
Nao usar para: entrega de cliente sem sinal de friccao do sistema

## Contrato

O CORTEX tem como principio melhorar a cada dia de uso a partir do atrito real que o usuario gera com o agente, para a proxima sessao exigir menos explicacao, menos correcao e menos ritual.

O operador nao precisa abrir uma conversa diaria sobre o CORTEX. O agente deve fazer um micro-check no fim de tarefa relevante e agir quando houver sinal claro.

Perguntas internas obrigatorias:

- Houve friccao que deve virar regra, alias, skill ou fila?
- Alguma memoria/referencia existia, mas nao foi acionada pelo jeito que o operador falou?
- Alguma regra nova substitui ou consolida regra antiga?
- A mudanca vale so para este usuario, para os agentes locais, para o distribuivel ou para todos?
- A correcao e pequena e reversivel? Se nao for, precisa parar e pedir confirmacao.

Se a resposta for sim e a mudanca for pequena, o agente executa. Se for grande, deixa uma fila objetiva ou pergunta. Se for irrelevante, nao comenta.

## Como o operador pode pedir sem pensar muito

Frases curtas que bastam:

- "isso foi friccao" -> avaliar regra, skill, alias ou fila.
- "quando eu falar X, puxe Y" -> adicionar alias de retrieval e testar.
- "isso deveria ser automatico" -> avaliar level-up, hook ou checklist.
- "guarda esse padrao" -> gravar regra no escopo certo.
- "isso e so meu" -> nao portar para template.
- "isso vale pro distribuivel" -> portar mecanismo generico, sem linguagem pessoal.
- "nao quero falar de CORTEX todo dia" -> aplicar este protocolo e reduzir reuniao sobre sistema.
- "ja pedi isso varias vezes" -> tratar como falha de aprendizado anterior e corrigir a causa-raiz agora.
- "na proxima sessao tem que vir melhor" -> gravar regra/alias/fila para reduzir atrito futuro.

## Acoes permitidas por default

- Alias pequeno de retrieval para arquivo existente: aplicar e testar positivo/negativo.
- Regra clara e reversivel: consolidar em referencia curta e apontar no bootstrap.
- Regra incerta: append em `_fila-regras.md`, sem inflar `MEMORY.md`.
- Decisao de governanca: append em `decisions/log.md`.
- Bug de skill/hook: patch minimo, teste local e resumo.

## Freios

Parar e pedir confirmacao antes de:

- ligar automacao nova que escreve sozinha em memoria;
- ativar hook no boot;
- apagar, mover ou podar memoria;
- mudar custo/modelo/sync/git/seguranca;
- levar jeito pessoal de um usuario para o distribuivel.

## Visibilidade

No final da tarefa:

- Se algo mudou no CORTEX: relatar uma linha `CORTEX: ...`.
- Se nada mudou: nao comentar. Silencio evita transformar todo turno em manutencao.

## Relacao com outros arquivos

- Guardrails de mudanca: `references/guardrails-autoevolucao-cortex.md`
- Contexto e compactacao: `references/politica-contexto-memoria-compactacao.md`
- Paridade multiagente: `references/paridade-multiagente-cortex.md`
- Auto-melhoria de skills: `references/auto-melhoria-skills.md`
