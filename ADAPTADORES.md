# Adaptadores por runtime

O CORTEX é um núcleo de context engineering em Markdown, com automações quando o runtime permite.

## Níveis de suporte

| Nível | O que significa | Exemplo de capacidade |
|---|---|---|
| Full | O agente lê arquivos, roda shell e suporta hooks ou comandos equivalentes | aprendizado automático, auditoria, segurança, atualização |
| Médio | O agente lê regras/projetos e roda comandos, mas sem hooks confiáveis | núcleo de contexto + scripts manuais |
| Básico | O agente lê um arquivo de instruções do projeto | regras e memória sob demanda, sem automação |

## Claude Code

Nível: Full.

Use o pacote completo: `CLAUDE.md`, skills, hooks, `/onboard`, `/audit`, `/destilar-sessoes`,
`/atualizar` e segurança por hook.

## Codex CLI ou extensão no VSCode

Nível: Médio.

Use `AGENTS.md` como porta de entrada, a pasta `memoria/` como cérebro externo e os scripts locais
quando precisar. A instalação copia `memoria/AGENTS.md` para a raiz da pasta CORTEX, então abrir
`C:\CORTEX` ou `~/CORTEX` no Codex já carrega a orientação certa.

Onde não houver hook, rode a destilação ou auditoria manualmente. Para atualizar com Codex, use
`ATUALIZAR-COM-CODEX.md`: dry-run primeiro, aplicação só depois de conferir preservação de
`context/`, `memory/`, `projects/` e `decisions/`.

## Cursor, Cline, Windsurf e agentes similares

Nível: Básico a médio, conforme a ferramenta.

O núcleo portável é:

- arquivo de instruções do projeto;
- `memoria/README.md`;
- `memoria/memory/MEMORY.md`;
- `memoria/references/`;
- `memoria/projects/`;
- scripts locais quando o agente puder rodar shell.

Se a ferramenta tiver rules por pasta, a melhor adaptação é mapear:

- regras globais para o arquivo principal de instruções;
- regras de projeto para a pasta do projeto;
- referências pesadas para leitura sob demanda.

## Limites da promessa

- Chat puro sem acesso a arquivos não roda o CORTEX completo.
- Runtime sem shell não fecha loop de verificação.
- Runtime sem hooks depende de comando manual para destilar e medir.

## Regra de produto

O CORTEX deve sempre degradar com honestidade:

1. Full quando há hooks, shell e leitura de arquivos.
2. Médio quando há shell e leitura de arquivos.
3. Básico quando só há regras de projeto.

O usuário nunca deve achar que comprou automação que o runtime dele não suporta.
