---
name: continuar-sessao
description: Invoke this skill when the user asks to resume, pick up, or retrieve context from a previous session. Fire it on any signal of crossing a session boundary: "retoma", "volta pro que tava", "o que a gente tava fazendo", "pega o handoff", "last handoff", "o que ficou pendente", "aonde paramos", or any "what was I doing before?" variant. The user's intent is: I'm in a fresh conversation and need to know what was left from before. Do NOT invoke when the user is continuing a task already visible in the current conversation, creating a new handoff, or starting entirely new work. (Nome NAO e "continuar": colide com alias nativo /continue do /resume.)
---

# /continuar-sessao — retomar de onde paramos

Atalho pra retomar o trabalho depois de um `/clear` ou de fechar a janela. Par do `handoff`:
o `handoff` escreve o briefing ao FECHAR; esta skill o LE ao ABRIR a próxima. Fecham o ciclo.

## Roteamento (decidir qual handoff, nesta ordem)

1. **Pista de assunto** (citou cliente/tema/"a landing"/"o CORTEX" etc.) → achar o handoff que
   bate, retomar direto. Sem pop-up.

2. **Pista genérica ou de recência** ("continuar", "mais recente", "o que fechei") → pegar o
   handoff de **trabalho** com maior mtime em `handoff-session/`, ignorando handoffs de
   infra/manutenção (destilação, sync, auditoria, fila de aprendizado).
   - Se 2+ handoffs de trabalho fechados em <5 min entre si (rajada recente) → AskUserQuestion
     listando foco + data. Fora disso: crava o mais recente e segue sem perguntar.

3. **Assunto novo** → ignorar handoffs.

> **FILTRO ANTI-INFRA:** "mais recente" = última sessão de TRABALHO (projeto, entrega, cliente),
> NUNCA a última atividade de manutenção do sistema (destilação, sync, auditoria, faxina). Se o
> handoff de maior mtime for de infra, descer pro próximo até achar trabalho.

## Execução

- Ler o handoff escolhido. (1 Read)
- Se vier `[PODE ESTAR VELHO]` ou divergência óbvia: 1 checagem barata.
  - Sessão leve (fresca, <100k tokens): fazer inline com 1-2 comandos.
  - Sessão pesada (>100k tokens): delegar ao `executor-rapido` e aguardar o delta em 2-4 linhas.
    Não fazer a conferência inline — custa mais tokens do que vale.
- Abrir com: **etiqueta** → `estamos em X, feito Y, falta Z` → próxima ação.

## Proibido

- Narrar o bastidor ("vou conferir...", "o disco diverge...") — resultado consolidado só.
- Fazer varredura (diff, grep largo, ler múltiplos arquivos) durante a retomada — execução começa
  só no "vai" do operador.
- Pop-up fora da rajada recente (critério: 2+ handoffs de trabalho fechados em <5 min).
- Ler o "Foco" de vários handoffs antes de decidir qual retomar — ler só o escolhido.
