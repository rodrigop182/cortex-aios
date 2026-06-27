---
name: continuar-sessao
description: Invoke this skill when the user asks to resume, pick up, or retrieve context from a previous session. Fire it on any signal of crossing a session boundary: "retoma", "volta pro que tava", "o que a gente tava fazendo", "pega o handoff", "last handoff", "o que ficou pendente", "aonde paramos", or any "what was I doing before?" variant. The user's intent is: I'm in a fresh conversation and need to know what was left from before. Do NOT invoke when the user is continuing a task already visible in the current conversation, creating a new handoff, or starting entirely new work. (Nome NÃO é "continuar": colide com o alias nativo /continue do /resume.)
---

# /continuar-sessao

## Roteamento (decidir qual handoff, nesta ordem)

1. **Slug explícito** (`/continuar-sessao funil-empresa`) → achar o .md que contém o slug no nome, retomar direto. Sem pop-up.

2. **Pista de assunto** (citou cliente/tema/"a landing"/"o CORTEX" etc.) → achar o handoff que bate, retomar direto. Sem pop-up.

3. **Sem argumento ou pista genérica** ("continuar", "mais recente", "o que fechei") → mostrar painel compacto: 1 linha por frente (título + próximo passo), o operador escolhe pelo nome ou número. Nunca chutar. Formato:
   ```
   Frentes abertas:
   1. projeto-site — aguardando acesso ao repo
   2. funil/empresa — decidir marca pessoal vs estúdio, PDF dos 20 furos
   3. CORTEX manutenção — auditoria critérios vagos, /frentes, /fecha-sessao
   Qual retoma?
   ```

4. **Assunto novo** → ignorar handoffs.

## Execução (teto mínimo)

- Ler o handoff escolhido. (1 Read)
- Se vier `[PODE ESTAR VELHO]` ou divergência óbvia: 1 checagem barata (`git status --short` + mtime num comando). Se a sessão já estiver pesada (>100k), delegar ao `executor-rapido` e aguardar o delta em 2-4 linhas.
- Se o hook `SessionStart` avisar que existe handoff, usar o aviso só como ponteiro para localizar o arquivo. O aviso não autoriza retomar sozinho.
- Abrir com: **etiqueta** → `estamos em X, feito Y, falta Z` → próxima ação.

## Limpeza depois da retomada

- Se a tarefa retomada foi concluída e há confiança alta, remover o handoff canônico em `{{CAMINHO_CLAUDE}}\skills\handoff\handoff-session\` e avisar em 1 linha.
- Confiança alta = vi a conclusão nesta sessão, ou o estado em disco/memória registra claramente que acabou.
- Se houver dúvida, manter o handoff. Não limpar no escuro.
- Handoff `AUTO-*` ou de outro agente só limpa com conclusão clara do mesmo assunto.

## Proibido

- Narrar o bastidor ("vou conferir...", "o disco diverge...") — resultado só.
- Fazer varredura (diff, grep largo, ler múltiplos arquivos) durante a retomada — isso é execução, começa só no "vai" dele.
- Chutar "o mais recente" quando o pedido não tem pista suficiente. Sem pista, listar frentes abertas em painel compacto.
