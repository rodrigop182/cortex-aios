# AGENTS.md - CORTEX OS para Codex

Bootstrap do Codex na pasta CORTEX instalada. Conteúdo pesado mora em `references/`, `projects/`, `context/` e `memory/`.

## Regras de resposta

- PT-BR, direto, ação primeiro.
- Nunca inventar número, cliente, estatística, prova ou depoimento.
- Faltou dado: usar `[PREENCHER: x]`.
- Ler só os arquivos necessários.
- Preservar dados do usuário, credenciais e qualquer trecho em `<private>...</private>`.

## Como trabalhar

- Projeto específico: procurar primeiro a ficha em `projects/`.
- Regra geral: consultar `references/` sob demanda.
- Memória pessoal: usar `memory/MEMORY.md` como índice, não carregar tudo por garantia.
- Arquivo quente: se releu 3+ vezes, criar ou usar `.cortex/SUMMARY.md` no projeto.

## Padrões do sistema

- Markdown para agente: `references/padrao-markdown-agentes.md`
- Léxico operacional: `references/lexico-operacional-cortex.md`
- Roteamento de regra vs. sistema: `references/criterio-roteamento-cortex.md`
- Regra nova só fica pronta quando governa: `references/criterio-explicitacao-peso-retroativo-cortex.md`
- Paridade multiagente: `references/paridade-multiagente-cortex.md`
- Skills Codex: pessoais em `~/.agents/skills`; `~/.codex/skills` reservado para `.system`.
- Auto-melhoria de skills: `references/auto-melhoria-skills.md`
- Torneiras de token: `references/controle-torneiras-token.md`, quando existir

## Arquivos principais

- `context/`: perfil, operação e prioridades
- `memory/MEMORY.md`: perfil compacto e índice
- `references/`: guias, regras e critérios
- `projects/`: clientes e projetos
- `decisions/log.md`: decisões importantes

## Primeiro uso

Se o perfil estiver vazio, oferecer:
- `/onboard` no Claude Code, se existir
- preenchimento manual pelo guia do pacote

Se o contexto essencial estiver vazio, fazer só as perguntas mínimas antes de recomendar.

## Codex sem hooks

No Codex, tratar automações como rotina manual:
- registrar decisão importante em `decisions/log.md`
- promover correção recorrente para regra ou referência
- portar melhoria de sistema para Claude Code + Codex quando fizer sentido; Cursor/Cline recebem o que for portátil em markdown/script
- seguir o guia de atualização do pacote quando mexer no produto

## Segurança

Nunca versionar, memorizar ou expor:
- senha
- token
- chave de API
- webhook
- dado financeiro
- dado sensível de cliente sem autorização

## Critério de boa resposta

- usa o contexto local quando ele é relevante
- não carrega pasta inteira por garantia
- recomenda próximo passo concreto
- explica risco quando a ação pode sobrescrever, apagar, publicar ou expor dado
- deixa rastro mínimo quando a decisão precisa sobreviver à sessão
