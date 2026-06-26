# Paridade multiagente do CORTEX

Uso: sob demanda
Escopo: sistema
Gatilho: qualquer melhoria em regra, memoria, skill, hook, script, template, MCP ou automacao do CORTEX
Nao usar para: detalhe local que so existe dentro de um projeto de cliente

Regra-mae: **toda melhoria do CORTEX nasce multiagente por padrao.**

Feito nao e "funciona na janela atual". Feito e: a mudanca declara alvo, foi aplicada nas superficies vivas que fazem sentido e deixa pendencia explicita quando nao puder ser portada.

## Alvos

| Alvo | Onde governa | Quando atualizar |
| --- | --- | --- |
| Compartilhado | `memoria/`, `memoria/references/`, `memoria/decisions/`, scripts neutros, handoffs | regra, criterio, decisao ou automacao que qualquer agente deve encontrar |
| Claude Code | `CLAUDE.md`, `C:\Users\rodri\.claude\`, hooks, agents, skills | orquestracao, memoria dinamica, hook, skill madura, decisao estrategica |
| Codex | `AGENTS.md`, `C:\Users\rodri\.codex\AGENTS.md`, `C:\Users\rodri\.agents\skills\`, plugins/config Codex | execucao, codigo, analise, landing, scripts, uso em Codex CLI |
| Cursor/Cline | markdown portatil, scripts neutros, referencias em `memoria/` | quando a regra nao depende de hook/skill proprietaria |
| Nao portar | decisao registrada com motivo | quando a capacidade so existe em uma superficie |

## Protocolo de implementacao

1. **Declarar alvo antes de editar**
   - Compartilhado, Claude Code, Codex, Cursor/Cline portatil ou nao portar.

2. **Comecar pelo compartilhado**
   - Se a regra precisa sobreviver a troca de agente, a fonte canonica fica em `memoria/`.
   - Bootstrap so aponta. Detalhe pesado fica em referencia.

3. **Portar para as superficies vivas**
   - Claude Code: `CLAUDE.md` e `~/.claude` quando a regra dispara ali.
   - Codex: `AGENTS.md`, `~/.codex/AGENTS.md` e `~/.agents/skills` quando a regra dispara ali.
   - Cursor/Cline: manter markdown e scripts sem dependencia exclusiva quando der.

4. **Reconciliar espelhos**
   - Se existe template, espelho ou pacote distribuivel, atualizar junto ou registrar pendencia.
   - Nao deixar fonte nova e skill velha competindo.

5. **Auditar**
   - Conferir por busca que a regra e encontravel.
   - Conferir que nao existe versao antiga mais fraca governando o mesmo fluxo.
   - Conferir git cirurgico antes de publicar.

## Checklist de pronto

- [ ] A mudanca declara alvo.
- [ ] Fonte compartilhada existe quando a regra cruza agentes.
- [ ] Claude Code recebeu ponteiro ou patch se afetado.
- [ ] Codex recebeu ponteiro ou patch se afetado.
- [ ] Cursor/Cline receberam o que for portatil, ou existe motivo de nao portar.
- [ ] Template/espelho foi atualizado quando distribuivel.
- [ ] Decisao registrada se o porte nao for obvio.
- [ ] Busca confirma que nao sobrou regra velha competindo.

## Anti-padroes

- "Depois eu porto."
- "Esta no Claude, entao o Codex vai saber."
- "Esta no AGENTS, entao o Claude vai saber."
- "Esta no chat, entao virou sistema."
- "Cursor/Cline ve depois."

## Criterio de eficacia

A melhoria funcionou quando, em sessoes futuras, qualquer agente relevante encontra a mesma regra sem depender da memoria da conversa e nao volta a reproduzir o erro que motivou a mudanca.
