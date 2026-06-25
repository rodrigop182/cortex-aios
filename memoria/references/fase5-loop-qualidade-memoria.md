# FASE 5 — Loop de qualidade da memória (medir, reforçar, podar)

> Desenhado e implementado em 2026-06-23 (rumo HÍBRIDO escolhido pelo {{USUARIO}}go). Saiu de um workflow
> de 3 designs + 3 críticas adversariais. É o mecanismo que sustenta "nunca explicar 2x" de verdade:
> sem ele o CORTEX só ACUMULA regras (a "torneira aberta") e nunca sabe se uma regra funciona.

## O reframe (o achado que mudou o rumo)

Medir eficácia 100% automático **não funciona**. O feedback do {{USUARIO}}go é genérico ("agora sim",
"de novo o mesmo erro") — ele nunca cita o slug da regra. Cruzar `_feedback.log` × regra por janela
de tempo dilui o sinal e vira ruído (3 críticos independentes reprovaram). Conclusão:

- **USO** (o que é consultado) → mede-se automático, é barato e honesto.
- **EFICÁCIA** (a regra evitou/causou retrabalho?) → precisa de CONTEXTO. Quem liga "ele corrigiu de
  novo o que a regra X mandava" é o Claude na destilação, não um script. Vira passo da destilação.

Daí a arquitetura **híbrida**: automático mede uso e poda o morto; a eficácia é humano-assistida.

## Os 3 mecanismos

1. **Instrumentação de uso** — `hooks/registra_uso_memoria.py` (PostToolUse/Read). Loga em
   `_uso-memoria.log` toda vez que um arquivo de regra individual é aberto. Uso ATIVO. Silencioso.
2. **Eficácia** — a destilação escreve `_eficacia-regras.log` (`slug.md  eficaz|reforcar  motivo`).
   `eficaz` = a regra guiou o acerto; `reforcar` = a regra existe mas falhou (reescrever, não podar).
   Escrito por `fecha-sessao`, `aprender-do-dia`, `catch-up` — só quando a ligação for clara.
3. **Poda por evidência** — `hooks/poda_por_evidencia.py` (sob demanda, NUNCA hook). Propõe regra
   morta; gate humano move pra `archives/` (reversível). Lido pelo `/audit` ("Saúde da memória").

## As 3 camadas que impedem podar regra viva (o erro caro)

1. **Presença no índice** — regra com ponteiro no `MEMORY.md` é viva por presença, mesmo sem Read.
   Tapa o furo do mec 1 (regra injetada via índice/recall não dispara Read mas não é morta). Checado
   na hora lendo o índice — sem hook novo, sem inflar log (descartou-se o "hook de injeção" do design
   original, que tinha bug de regex com path absoluto e colisão de formato no log).
2. **Eficácia** — `eficaz` protege da poda; `reforcar` vai pra "A REESCREVER", nunca pra poda.
3. **Uso + idade + status** — só vira candidata a MORTA quem está FORA do índice, sem leitura há
   `DIAS_SEM_USO` (60d), idade > `DIAS_MIN_IDADE` (21d), status não `ativo`/`pausa`. Trava de
   maturidade: 30d de instrumentação antes de podar por falta-de-uso (só `status: resolvido` órfão
   passa antes). O `--mover` re-checa índice + maturidade — a trava não some por quem chamou.

## Quem roda, quando

- **Uso:** automático (hook Read), toda sessão.
- **Eficácia:** na destilação (`fecha-sessao` por sessão; `aprender-do-dia` no dia; `catch-up` em
  lote). Backstage, nunca narrado.
- **Poda:** `/audit` (relatório) e `catch-up` só PROPÕEM; arquivar é `--mover`, gate humano à parte.

## Bugs reais que a crítica adversarial pegou (corrigidos em 23/06)

- `captura_feedback.py` e `captura_regra.py` capturavam `<task-notification>`/`<system-reminder>`
  como feedback/regra (envenenavam os logs) → **guard anti-envelope** (`if prompt.lstrip().startswith("<")`).
- Atribuição feedback→regra por janela temporal = ruído → **abandonada** (eficácia via destilação).
- Hook de injeção no SessionStart (formato log 2-vs-3 campos, regex perde path absoluto, protegeria
  regra `resolvido`) → **abandonado** em favor de checar o índice na hora.

## Estado e o que falta

Implementado (híbrido) e testado em sandbox. O loop de PODA fecha automático e seguro; o de EFICÁCIA
depende da destilação que o {{USUARIO}}go já roda. **Maturação:** a poda por falta-de-uso só fica confiável
após ~30 dias de instrumentação real (`_uso-memoria.log` nasceu em 23/06). Até lá, presença-no-índice
e status `resolvido` são as travas ativas. Lastro conceitual: [[cortex-3-loops-auto-desenvolvimento]] (M3/M4).
