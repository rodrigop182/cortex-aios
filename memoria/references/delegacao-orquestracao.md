# Delegação e orquestração

## Gatilhos de delegação (3 níveis, testados em 24/06/2026)
- "delega: [tarefa]" → manda pro executor no tier certo (Haiku se mecânico puro, Sonnet se precisar de julgamento). Leve, sem overhead de Workflow.
- "isso é lote, vale Workflow?" → quando ele mandar 3+ tarefas independentes, EU aviso proativamente e aguardo confirmação antes de disparar.
- "ultracode" na mensagem → dispara Workflow completo com múltiplos agentes em paralelo. Usar só quando a tarefa tem escala real que justifica o overhead.
Diferença entre delega e ultracode: "delega" = 1 subagente pra 1 tarefa; "ultracode" = orquestração completa com N agentes em paralelo. Não confundir.

## Bloqueio global de fan-out
Ao disparar subagentes em LEQUE, CRAVAR o tier por etapa, NUNCA herdar Opus, NUNCA passar de ~12 simultâneos. Regra completa, tiers e porquê em [[delegar-subagente-sonnet-global]].

## Orquestração (regra global)
O Opus deste chat é o ORQUESTRADOR — decide, delega, verifica; NÃO executa tudo na mão. (1) NUNCA acionar subagente Opus por padrão só porque o chat é Opus; subagente só é tier-1 se a TAREFA for tier-1. (2) Sessão pesada de Sonnet/Haiku em paralelo é BOA (orquestrar ≠ fazer na mão). (3) Workflow/fan-out é proativo e por rotina quando paraleliza com ganho — não depende de "ultracode" nem de pedido. (4) AUDITORIA é SEMPRE adversarial: quem audita NUNCA é quem fez. Detalhe e mapa de tiers em `references/tiers-de-modelo.md`.

> Pensar antes, simplificar, mexer cirurgicamente e verificar no fim reforçam esta seção, sem virar
> mais uma régua paralela.
