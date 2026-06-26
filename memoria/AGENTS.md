# AGENTS.md - CORTEX OS para Codex

Você está na pasta CORTEX do usuário. Esta pasta guarda memória, regras, projetos e referências para
um agente de IA operar com contexto.

## Como trabalhar

- Responda em PT-BR, direto e com ação primeiro.
- Não invente número, cliente, depoimento, estatística ou prova. Se faltar dado, use
  `[PREENCHER: ...]`.
- Leia apenas os arquivos necessários para a tarefa.
- Preserve dados do usuário: contexto, memória, projetos, decisões, credenciais e qualquer trecho
  marcado com `<private>...</private>`.
- Para projeto específico, procure primeiro uma ficha em `projects/`.
- Para regras gerais, consulte `memory/MEMORY.md` e `references/` sob demanda.

## Arquivos principais

- `context/sobre-mim.md`: perfil do usuário.
- `context/sobre-operacao.md`: como o trabalho funciona.
- `context/prioridades.md`: foco dos próximos 90 dias.
- `memory/MEMORY.md`: perfil compacto e índice de memórias.
- `references/`: guias e regras.
- `projects/`: projetos e clientes.
- `decisions/log.md`: decisões importantes.

## Primeiro uso

Se o perfil estiver vazio, ofereça uma das duas rotas:

- rodar `/onboard` no Claude Code, se o usuário também usa Claude;
- preencher manualmente os arquivos do guia `CONFIGURAR-SEM-IA.md` no pacote fonte.

Se o usuário pedir uma recomendação e os arquivos de contexto estiverem vazios, diga que falta
configurar o perfil e faça só as perguntas essenciais.

## Codex não tem hooks do Claude Code

No Codex, trate automações como rotina manual:

- no fim de uma sessão importante, registre aprendizados em `decisions/log.md` ou `memory/MEMORY.md`;
- quando uma correção se repetir, proponha virar regra em `references/` ou no projeto certo;
- para atualização do produto, siga `ATUALIZAR-COM-CODEX.md` no pacote fonte;
- para auditoria de saúde, use os checklists em `references/` e `CHECKLISTS/` quando disponíveis.

## Segurança

Nunca versionar ou mover para memória:

- senha;
- token;
- chave de API;
- webhook;
- extrato;
- saldo;
- dado financeiro;
- dado de cliente sem autorização.

Se precisar de exemplo, peça dado fictício.

## Critério de boa resposta

- Usa o contexto local quando ele é relevante.
- Não carrega pasta inteira por garantia.
- Recomenda próximo passo concreto.
- Explica risco quando a ação pode sobrescrever, apagar, publicar ou expor dado.
- Deixa rastro mínimo quando a decisão precisa sobreviver à sessão.
