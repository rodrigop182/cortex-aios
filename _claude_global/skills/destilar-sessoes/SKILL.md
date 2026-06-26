---
name: destilar-sessoes
description: "Mutirao RETROATIVO de VARIOS DIAS: varre transcripts de uma janela (default 7) e destila o backlog que ficou pra tras. Usar em \"faz um catch-up\", \"destila as sessoes\", \"processa o que ficou pra tras\", \"ve o que aprendeu desses dias\", \"atualiza a memoria com o acumulo\", ou com muitas sessoes em _sessions-pendentes.log. NAO e por-sessao desta conversa (fecha-sessao), nem briefing da proxima janela (handoff)."

---

# Destilar sessoes — mutirao retroativo do que passou batido

O operador quase nunca encerra com o ritual `fecha-sessao`. Entao o aprendizado de dias inteiros
fica parado na fila e o sistema nao aprende. Esta skill faz o **catch-up em lote**: varre os
transcripts de uma janela de dias, destila o que importa e atualiza a memoria — de uma vez,
manualmente, de tempos em tempos.

Distincao das skills irmas (pra nao colidir):
- `fecha-sessao` = UMA sessao, no encerramento, leve. Esta = MUITAS sessoes acumuladas, em mutirao.
- `handoff` = briefing pra PROXIMA janela continuar. Esta = aprender do PASSADO.

## Principio-guia (criterio acima de burocracia)

"Nem sempre sei o que e melhor, mas sei o que preciso resolver." A skill tem que ter BOM
CRITERIO: decidir sozinha o que vale processar e o que vale gravar, sem encher o sistema de
ruido. Na duvida entre gravar e nao gravar, **nao grava** — regra fraca lida todo turno dilui o
sinal (cerebro fino e indice, nao deposito). Casa com `criterio-relevancia-destilacao` e
`fecha-sessao` (o gate de relevancia ALTA/MEDIA/BAIXA vale aqui tambem, por sessao).

## Como roteia os tiers (ler `memoria/references/tiers-de-modelo.md`)

- **Pre-filtro** (rodar script): mecanico, **tier-3**. Sao os scripts Python, sem modelo.
- **Extracao por lote**: **tier leve** (tier-2; pode cair pra tier-3 se o lote for pequeno e o
  tier-3 nao for Haiku com 200K estourado). Subagentes em paralelo. So LEEM e PROPOEM.
- **Consolidacao**: **tier-2**. Um subagente dedupa e cruza com a memoria existente. So PROPOE.
- **Curadoria e gravacao**: automatica via sintetiza.py. Criterio afinado: recorrencia + acionavel + duravel + reconhecimento da voz do operador. Teto de 35 regras por artigo; poda automatica de stale e redundante.

Comecar pelo tier mais baixo que resolve; subir so se a tarefa exigir. Nao passar `effort` pra
Haiku (tier-3 mapeado a Haiku nao aceita).

Ao disparar cada subagente, CRAVAR o `model` do tier no Agent (tier-2 = `model: sonnet`,
tier-3 = `model: haiku`). NUNCA deixar no default: subagente sem `model` HERDA o Opus e o lote
mecanico sai caro/lento. O `subagent_type: executor-mecanico` ja vem em Sonnet pronto.

## Regras inegociaveis

- **Resumo obrigatorio ao final.** Ao terminar o catch-up, entregar ao operador um resumo de 3-8 bullets do que o CORTEX absorveu: quais conceitos foram atualizados, quais regras novas entraram, quais foram podadas. Sem resumo = skill incompleta.
- **Suporte a sessoes do Codex.** O extrai.py deve processar tambem os rollouts em `~/.codex/sessions/AAAA/MM/DD/rollout-*.jsonl` (formato OpenAI: `type: response_item`, `payload.role`, `payload.content[].type: input_text/output_text`).
- **Cruzar com handoffs ativos.** O extrai.py tambem gera `_handoff-context.txt` a partir de `~/.claude/skills/handoff/handoff-session/`. O sintetiza.py usa esse arquivo so como contexto de exclusao: estado de projeto e proximo passo que ja estao em handoff nao viram wiki/memoria duplicada.
- **Dado financeiro NUNCA entra.** Renda, valores, gastos, preco de proposta, saldo, "quebrado":
  os extratores omitem ou parafraseiam SEM numero; a curadoria nao grava nada disso. Bloco
  `<private>...</private>` e zona morta: tratar como inexistente. (memorias
  `dado-financeiro-e-tag-private`, `seguranca-wework`.)
- **Curadoria**: automatica (sintetiza.py via Haiku). O operador pode revisar _lote-diario.log, mas nao e obrigado; o criterio duro ja filtra.
- **Manutencao invisivel.** Isto e backstage. Nao narrar sync/log/frontmatter no chat; relatar o
  catch-up em 1 linha discreta no fim. (memoria `manutencao-memoria-invisivel`.)
- **Dedup e poda.** Nao criar memoria que ja existe — preferir ATUALIZAR. Contradicao: a versao
  RECENTE/mais madura vence a antiga (a curva de maturidade existe pra isso). (memorias
  `criterio-relevancia-destilacao`, `evitar-retrabalho-correcao-repetida`.)
- **Transcript so via script/subagente, nunca no contexto principal.** Despejar transcript bruto
  aqui incha a janela. Por isso o pre-filtro e a extracao acontecem fora.

## Pipeline (5 etapas)

### 1. Localizar sessoes da janela (tier-3, script)
Decidir a janela com o operador se ele nao disser (default razoavel: 7 dias, ou "desde o ultimo
catch-up"). Duas fontes, complementares:
- A fila `memoria/memory/_sessions-pendentes.log` ou equivalente (o que o hook registrou).
- Os transcripts recentes em `~/.claude/projects/<projeto>/*.jsonl`, filtrados por
  data — o script faz isso (pega o que a fila perdeu).
- Os rollouts recentes do Codex em `~/.codex/sessions/**/rollout-*.jsonl`.
- Os handoffs ativos em `~/.claude/skills/handoff/handoff-session/*.md`, usados so para evitar duplicata.

### 2. Pre-filtrar + Sintetizar (2 scripts, zero subagente no Opus)

Pipeline Karpathy — custo estimado ~1-3k tokens por lote de sessoes:

```bash
cd C:/Projetos/_catchup
python ~/.claude/skills/destilar-sessoes/scripts/extrai.py --src ~/.claude/projects/<projeto> --days 7
python ~/.claude/skills/destilar-sessoes/scripts/mede_1shot.py
python ~/.claude/skills/destilar-sessoes/scripts/sintetiza.py --wiki <CORTEX>/memoria/wiki
```

**extrai.py** — determinístico, zero modelo. Cospe .txt enxuto por sessao em `_catchup/enxutos/`.
**mede_1shot.py** — chama Haiku e anexa linhas de 1-shot em `memoria/metricas/1shot-log.csv`.
**sintetiza.py** — chama `claude -p` com Haiku por lote (~50KB). Extrai achados por CONCEITO
(nao por sessao), merge em `C:/Projetos/memoria/wiki/<conceito>.md`, regenera `wiki/index.md`.

Conceitos rastreados (definidos no sintetiza.py):
- como-trabalhar-com-operador, design-regras-duras, execucao-e-delegacao
- ferramentas-e-armadilhas, projetos-clientes, cortex-e-sistema

CRITERIO DURO embutido: so grava se apareceu 2+ vezes OU foi correcao explicita.
1x isolado -> ignorado pelo script (vai pro handoff se for importante).

### 3. Limpar (automatico)
Apagar `_catchup/enxutos/` apos rodar — descartaveis, wiki ja absorveu o conteudo.

## Economia (regra mestra)
Catch-up nao e reprocessar tudo palavra a palavra. O pre-filtro e a extracao paralela existem
pra isso. Se um lote nao rende nada nitido, "nada novo" e resposta correta. O ganho e o acumulo
de poucas regras certas, nao o volume.

## Roadmap: versao automatica (NAO implementar aqui)
Esta skill e o catch-up MANUAL. Em paralelo, fora do escopo dela, ha a ideia de um **subagente
leve rodando ao longo dos dias** que faz o mesmo continuamente — extrai e enfileira candidatos
conforme as sessoes acontecem, sem esperar o mutirao. Ele REUSARIA os scripts e os briefs daqui
(`extrai.py`, `extrator-brief.md`), enfileirando achados pra fila de curadoria; a etapa 5
(curadoria/gravacao) continua manual no Opus/usuario principal, com gate humano — captura nunca
escreve memoria direto. Quando for construir, partir destes mesmos artefatos. Lastro:
`cortex-3-loops-auto-desenvolvimento` (M3/M4 a fazer).
