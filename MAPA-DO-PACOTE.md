# Mapa do pacote - CORTEX OS

Este mapa mostra onde cada parte mora e qual papel ela tem. Use antes de instalar, atualizar ou
propor qualquer reorganização.

## Primeira experiência

Arquivos que vendem a ideia, reduzem ansiedade e levam o usuário para a instalação certa.

- `COMECE-AQUI.txt`: entrada de 1 minuto para usuário não técnico.
- `vitrine/`: página estática do produto, com promessa, demo visual e compatibilidade.
- `DEMO-5-MIN.md`: roteiro para provar valor depois do onboard.
- `ADAPTADORES.md`: níveis de suporte por runtime.
- `INSTALAR-SEM-IA.md`: rota de instalação sem depender de agente.
- `CONFIGURAR-SEM-IA.md`: rota de configuração manual do perfil.
- `ATUALIZAR-SEM-IA.md`: rota de atualização manual com dry-run.
- `ATUALIZAR-COM-CODEX.md`: roteiro para Codex aplicar update preservando dados.
- `AGENTS.md`: ponteiro para uso do pacote pelo Codex.
- `README.md`: visão completa do produto.

## Instalação

Arquivos que colocam o CORTEX nos lugares certos da máquina do usuário.

- `INSTALAR-AGENTE.md`: roteiro para o próprio agente instalar com backup e checagem.
- `INSTALAR-SEM-IA.md`: instrução simples para rodar o instalador sozinho.
- `INSTALAR.md`: instalação manual e explicação detalhada.
- `instalar.sh`: instalador Mac, Linux e Git Bash.
- `instalar.ps1`: instalador Windows PowerShell.
- `lite/`: modo de cérebro menor para contexto curto.

## Produto atualizável

Arquivos que pertencem ao CORTEX como produto e podem ser substituídos por uma versão nova.

- `MANIFESTO-UPDATE.md`: fonte da fronteira entre produto e dado do usuário.
- `CHANGELOG.md`: histórico de versões.
- `VERSION`: versão do pacote.
- `TROUBLESHOOTING.md`: falhas comuns e correções.
- `SEGURANCA.md`, `SECURITY.md`, `PRIVACIDADE.md`: segurança, reporte e privacidade.
- `ATUALIZAR-SEM-IA.md` e `ATUALIZAR-COM-CODEX.md`: rotas de update fora do Claude Code.
- `_claude_global/`: camada que vai para `~/.claude`.
- `_claude_global/skills/atualizar/`: motor que troca produto preservando dado.

## Cérebro global

Camada carregada pelo Claude Code fora da pasta CORTEX.

- `_claude_global/CLAUDE.md`: cérebro full.
- `_claude_global/settings.json`: registro dos hooks.
- `_claude_global/settings.LEIA-ME.md`: instruções de settings.
- `_claude_global/skills/`: skills globais como atualização, handoff e fechamento de sessão.
- `_claude_global/agents/`: agentes auxiliares.
- `_claude_global/hooks/`: automações de segurança, captura, sync e destilação.

## Pasta CORTEX viva

O conteúdo de `memoria/` é copiado flat para a pasta que o usuário abre sempre no VSCode. Exemplo:
`C:\CORTEX` no Windows ou `~/CORTEX` no Mac/Linux.

- `memoria/README.md`: guia da memória.
- `memoria/AGENTS.md`: instruções para Codex na pasta CORTEX instalada.
- `memoria/intake.md`: perguntas do onboard.
- `memoria/regras-base.md`: regras base.
- `memoria/connections.md`: integrações e alcance do sistema.
- `memoria/.claude/skills/`: skills locais como onboard, regras, audit e como-funciona.
- `memoria/context/`: perfil e operação preenchidos pelo usuário.
- `memoria/memory/`: índice e memórias curadas.
- `memoria/references/`: frameworks, voz, nichos e doutrinas.
- `memoria/projects/`: projetos e clientes.
- `memoria/decisions/log.md`: decisões e motivos.
- `memoria/archives/`: material arquivado.

## Fronteira produto x dado

Use `MANIFESTO-UPDATE.md` como fonte única antes de mexer em update.

- Produto: docs, instaladores, vitrine, `_claude_global/`, referências genéricas e skills do pacote.
- Dado do usuário: contexto preenchido, voz, nichos, decisões, memórias, projetos, handoffs,
  credenciais e qualquer arquivo sensível.

Regra prática: se o `/onboard` ou o uso real preencheu, preserve.

## Regra para reorganizar

Não mova arquivo físico só para deixar a árvore mais bonita. Mover só vale quando os quatro pontos
abaixo ficam atualizados e testados:

- instaladores;
- `INSTALAR-AGENTE.md`;
- `MANIFESTO-UPDATE.md`;
- skill `/atualizar`.

Na dúvida, crie um mapa ou índice. Movimento de pasta vem depois de validação.
