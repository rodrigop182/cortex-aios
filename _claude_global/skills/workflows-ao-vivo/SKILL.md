---
name: workflows-ao-vivo
description: Sobe um dashboard visual (HTML) que mostra os workflows do Claude Code rodando ao vivo — fases, agentes, status, tokens, duração e custos, lendo os logs em disco com auto-refresh. Usar quando o operador disser "abre o painel de workflows", "quero ver os subagentes ao vivo", "dashboard de workflows", "acompanhar o workflow", "/workflows-ao-vivo", ou quando um workflow estiver rodando. NAO roda workflows (isso é a tool Workflow) nem é a TUI nativa /workflows (que não existe na extensão VSCode).
---

# Workflows ao vivo

Interface de acompanhamento dos workflows multi-agente do Claude Code. A TUI nativa
`/workflows` não existe na extensão VSCode, então este painel substitui:
um servidor Python local lê os logs que cada workflow grava em disco e serve um
dashboard HTML que se atualiza sozinho.

## Como funciona

Cada workflow grava, enquanto roda, em
`~/.claude/projects/<proj>/<sessao>/subagents/workflows/wf_<id>/`:
- `journal.jsonl` — eventos `started`/`result` por agente (o pulso: started sem result = rodando).
- `agent-<id>.jsonl` — prompt, modelo, tokens (`usage.output_tokens`), timestamps e texto de cada agente.

O `server.py` varre esses arquivos a cada request e o `dashboard.html` faz polling a cada 1.5s.

## Acionar

```
python "{{CAMINHO_MEMORIA}}/../_claude_global/skills/workflows-ao-vivo/scripts/server.py"
```

- Sobe em `http://127.0.0.1:8787` (acha a próxima porta livre se ocupada) e abre o navegador.
- `--no-open` não abre o browser sozinho. `--port N` força a porta.
- Deixar rodando num terminal separado; fica de pé acompanhando qualquer workflow.
- Encerrar com Ctrl+C.

Ao invocar a skill: rodar o server em background (`run_in_background`) e dar a URL ao operador.

## O que mostra

**Aba Multi-agente:**
- Lista de workflows (ativos primeiro, com borda colorida pulsante; depois recentes).
- Por workflow: status, agentes (concluídos/total + quantos não rodaram), modelos em chips
  (ex "Opus ×4", "Sonnet ×12"), tokens de saída, total de tool calls, duração e horário de início.
- Expandir → agentes, cada um com status (concluído/rodando/não rodou), modelo, turns, duração,
  ferramentas usadas (Read×17, Edit×32…) e tokens.
- Clicar num agente → modal com stats completos, lista de ferramentas, prompt e saída parcial.
- Badge "travado" para agentes stale (sem progresso por tempo).
- Botão "encerrar" para remover workflow travado da view.

**Aba Custos:**
- Tabela dos últimos 14 dias via `npx ccusage daily --json`.
- Colunas: data, custo total, tokens entrada/saída/cache, modelos usados.
- Atualiza a cada ~30s.

**Aba Scripts Python** (opcional — configure no server.py se usar manutencao_cortex.py):
- Lista de processos Python rodando + logs recentes do script de manutenção.

## Status de agente

- **concluído**: tem resultado no journal.
- **rodando** (pulsante): produziu mensagens mas ainda sem resultado.
- **não rodou** (cinza): entrada enfileirada que não chegou a despachar. Não conta como modelo.

## Identidade

Tokens de cor no topo do `dashboard.html` (`:root`) — edite lá para adaptar ao design do operador.
Por padrão usa paleta neutra (preto/creme/laranja) substituível.

## Limites conhecidos

- A "fase" do workflow não é gravada de forma estruturada nos logs; agentes aparecem por arquivo,
  não agrupados por fase. Se o journal passar a registrar fase, agrupar aqui.
- ccusage requer `npx` disponível no PATH.
