---
name: destilar-sessoes
description: "Mutirao RETROATIVO de VARIOS DIAS: varre transcripts de uma janela (default 7) e destila o backlog que ficou pra tras. Usar em \"faz um catch-up\", \"destila as sessoes\", \"processa o que ficou pra tras\", \"ve o que aprendeu desses dias\", \"atualiza a memoria com o acumulo\", ou com muitas sessoes pendentes na fila. NAO e por-sessao desta conversa (fecha-sessao), nem briefing da proxima janela (handoff)."
---

# Catch-up de aprendizado — mutirao retroativo do que passou batido

Na pratica quase ninguem encerra toda sessao com o ritual `fecha-sessao`. Entao o aprendizado de
dias inteiros fica parado na fila e o sistema nao aprende. Esta skill faz o **catch-up em lote**:
varre os transcripts de uma janela de dias, destila o que importa e atualiza a memoria — de uma
vez, manualmente, de tempos em tempos.

Distincao das skills irmas (pra nao colidir):
- `fecha-sessao` = UMA sessao, no encerramento, leve. Esta = MUITAS sessoes acumuladas, em mutirao.
- `handoff` = briefing pra PROXIMA janela continuar. Esta = aprender do PASSADO.

## Principio-guia (criterio acima de burocracia)

A skill tem que ter BOM CRITERIO: decidir sozinha o que vale processar e o que vale gravar, sem
encher o sistema de ruido. Na duvida entre gravar e nao gravar, **nao grava** — regra fraca lida
todo turno dilui o sinal (cerebro fino e indice, nao deposito). O mesmo gate de relevancia
ALTA/MEDIA/BAIXA do `fecha-sessao` vale aqui, por sessao.

## Como roteia os tiers (ler `memoria/references/tiers-de-modelo.md`)

- **Pre-filtro** (rodar script): mecanico, **tier-3**. Sao os scripts Python, sem modelo.
- **Extracao por lote**: **tier leve** (tier-2; pode cair pra tier-3 se o lote for pequeno e o
  tier-3 nao for um modelo de janela curta ja estourada). Subagentes em paralelo. So LEEM e PROPOEM.
- **Consolidacao**: **tier-2**. Um subagente dedupa e cruza com a memoria existente. So PROPOE.
- **Curadoria e gravacao**: **tier-1, NUNCA subagente.** Mexer em memoria pede o contexto da
  relacao com o operador. Os subagentes nao escrevem memoria — so o tier-1 (voce/o principal).

Comecar pelo tier mais baixo que resolve; subir so se a tarefa exigir. Nao passar `effort` pra um
modelo de tier-3 que nao o suporte.

## Regras inegociaveis

- **Dado sensivel NUNCA entra.** Dado financeiro (renda, valores, gastos, preco, saldo), credencial,
  segredo: os extratores omitem ou parafraseiam SEM numero; a curadoria nao grava nada disso. Bloco
  `<private>...</private>` e zona morta: tratar como inexistente.
- **Curadoria fica no tier-1.** Subagente le e propoe; quem decide e grava e voce.
- **Manutencao invisivel.** Isto e backstage. Nao narrar sync/log/frontmatter no chat; relatar o
  catch-up em 1 linha discreta no fim.
- **Dedup e poda.** Nao criar memoria que ja existe — preferir ATUALIZAR. Contradicao: a versao
  RECENTE/mais madura vence a antiga.
- **Transcript so via script/subagente, nunca no contexto principal.** Despejar transcript bruto
  aqui incha a janela. Por isso o pre-filtro e a extracao acontecem fora.

## Pipeline (5 etapas)

### 1. Localizar sessoes da janela (tier-3, script)
Decidir a janela com o operador se ele nao disser (default razoavel: 7 dias, ou "desde o ultimo
catch-up"). Duas fontes, complementares:
- A fila `memoria/memory/_sessions-pendentes.log` (o que o hook registrou).
- Os transcripts recentes do Claude Code, em `~/.claude/projects/<seu-projeto>/*.jsonl`, filtrados
  por data — o script faz isso (pega o que a fila perdeu).

### 2. Pre-filtrar (tier-3, script)
```bash
cd <pasta de trabalho temp, ex: <PASTA_RAIZ>/_catchup>
python <skill>/scripts/extrai.py --src ~/.claude/projects/<seu-projeto> --days 7   # ou --since AAAA-MM-DD
python <skill>/scripts/grupos.py                                                    # auto: ~60 KB por lote
```
`extrai.py` cospe um .txt enxuto por sessao util (so voz humana + texto do assistant, ordenado
no tempo), pula sessao sem fala humana real e respeita a janela. `grupos.py` agrupa em lotes
cronologicos balanceados (a saida `grupos.json` lista os arquivos de cada lote). Conferir o
print: numero de sessoes uteis e de lotes faz sentido?

### 3. Extrair em paralelo (tier leve, subagentes)
Para cada lote em `grupos.json`, disparar UM subagente extrator (em paralelo, mesmo turno). A
ordem de servico de cada um = o conteudo de `references/extrator-brief.md` + a lista de arquivos
daquele lote. Cada subagente devolve o markdown estruturado (voz verbatim, correcoes/iteracoes,
fatos, preferencias, maturidade). Eles so LEEM e PROPOEM.

### 4. Consolidar (tier-2, um subagente)
Quando todos voltarem, disparar UM subagente consolidador com `references/consolidador-brief.md`
+ os N blocos de achados + a memoria JA existente (MEMORY.md e arquivos relevantes). Ele dedupa,
resolve contradicao a favor do recente, cruza com a memoria (marca JA EXISTE / NOVO / CONTRADIZ)
e gera um `SINTESE.md` enxuto. So PROPOE.

### 5. Curar e gravar (tier-1, VOCE — nunca subagente)
Ler o `SINTESE.md` e decidir, com criterio:
- Aplicar o gate de relevancia por candidato (ALTA grava, BAIXA descarta).
- **Procedural** (jeito de FAZER que uma skill cobre) -> consertar a SKILL, nao gravar memoria
  solta (ver `memoria/references/auto-melhoria-skills.md`).
- **Semantico** -> memoria. Se ja existe, ATUALIZAR (reforca, "voltou em DATA"); se nova, arquivo
  curto + ponteiro no `MEMORY.md`.
- Contradicao: gravar a versao recente, aposentar/ajustar a antiga.
- **Veredito de eficacia (FASE 5, mec 2):** se uma regra EXISTENTE foi posta a prova nos dias
  processados — falhou (o operador corrigiu de novo o que ela ja mandava) ou guiou o acerto —
  registre 1 linha em `memory/_eficacia-regras.log` (`slug.md  reforcar|eficaz  motivo`), so quando
  a ligacao for clara. Protege regra eficaz da poda e alimenta o /audit. Mesmo protocolo da fecha-sessao.
- Conferir de novo: zero dado sensivel, nada de `<private>`.
- **Esvaziar a fila** `_sessions-pendentes.log` ao fim (marcar processado).
- Limpar a pasta de trabalho temp (transcripts enxutos sao descartaveis).
- Relatar em **1 linha** o que entrou. Backstage, nao protagonista.

## Economia (regra mestra)
Catch-up nao e reprocessar tudo palavra a palavra. O pre-filtro e a extracao paralela existem
pra isso. Se um lote nao rende nada nitido, "nada novo" e resposta correta. O ganho e o acumulo
de poucas regras certas, nao o volume.

## Roadmap: versao automatica (NAO implementar aqui)
Esta skill e o catch-up MANUAL. Em paralelo, fora do escopo dela, ha a ideia de um **subagente
leve rodando ao longo dos dias** que faz o mesmo continuamente — extrai e enfileira candidatos
conforme as sessoes acontecem, sem esperar o mutirao. Ele REUSARIA os scripts e os briefs daqui
(`extrai.py`, `extrator-brief.md`), enfileirando achados pra fila de curadoria; a etapa 5
(curadoria/gravacao) continua manual no tier-1, com gate humano — captura nunca escreve memoria
direto. Quando for construir, partir destes mesmos artefatos.
