# Manifesto de atualização - CORTEX OS

Define a fronteira **PRODUTO** (atualizável pela skill `/atualizar`) vs **DADO DO USUÁRIO**
(preservado, nunca tocado). O script `atualizar.py` lê este arquivo como fonte única da verdade.

A regra-mãe: **o que o `/onboard` ou o uso preenchem é DADO; o resto é PRODUTO.** Na dúvida,
um caminho é DADO (preservar é o lado seguro do erro).

## PRODUTO (a skill substitui pela versão nova)

Caminhos relativos à raiz do CORTEX instalado. Globs permitidos.

```
VERSION
AGENTS.md
README.md
MAPA-DO-PACOTE.md
INSTALAR.md
INSTALAR-AGENTE.md
INSTALAR-SEM-IA.md
CONFIGURAR-SEM-IA.md
ATUALIZAR-SEM-IA.md
ATUALIZAR-COM-CODEX.md
COMECE-AQUI.txt
SEGURANCA.md
lite/MODO-LITE.md
lite/CLAUDE-LITE.md
MANIFESTO-UPDATE.md
CHANGELOG.md
TROUBLESHOOTING.md
vitrine/**
instalar.ps1
instalar.sh
atualizar.ps1
atualizar.sh
_claude_global/CLAUDE.md
_claude_global/settings.json
_claude_global/settings.LEIA-ME.md
_claude_global/hooks/**
_claude_global/agents/**
_claude_global/skills/**
memoria/references/auto-melhoria-skills.md
memoria/references/como-o-sistema-aprende.md
memoria/references/grafo-de-skills.md
memoria/references/otimizacoes-processo.md
memoria/references/principios-aios.md
memoria/references/principios-operacionais.md
memoria/references/protocolo-execucao.md
memoria/references/regras-completas.md
memoria/references/skill-description-eficiente.md
memoria/references/tiers-de-modelo.md
memoria/references/ciclo-de-contexto.md
memoria/references/ARQUITETURA.md
memoria/references/criterio-roteamento-cortex.md
memoria/references/fluxo-roteamento-aprendizado.md
memoria/references/controle-torneiras-token.md
memoria/references/context-engineering-cortex.md
memoria/references/criterio-acesso-contexto-cortex.md
memoria/references/guardrails-autoevolucao-cortex.md
memoria/references/lexico-operacional-cortex.md
memoria/references/padrao-markdown-agentes.md
memoria/references/paridade-multiagente-cortex.md
memoria/references/politica-entregaveis-visiveis-repo-intacto.md
memoria/references/politica-update-organizacao-nao-destrutiva-cortex.md
memoria/references/estrategia-retrieval-md-cortex.md
memoria/references/protocolo-agrupamento-regras-cortex.md
memoria/references/protocolo-auto-melhoria-continua-cortex.md
memoria/references/skills-catalogo/**
memoria/regras-base.md
memoria/intake.md
memoria/AGENTS.md
memoria/README.md
memoria/connections.md
memoria/projects/README.md
```

## REMOVER_PRODUTO (opcional; só com confirmação explícita)

Lista de arquivos de produto que uma versão nova autoriza remover quando, e somente quando, o
operador rodar o script com permissão explícita de remoção. Deixe vazio por padrão.

```
```

## DADO DO USUÁRIO (nunca tocar; preservar exatamente como está)

```
memoria/context/sobre-mim.md
memoria/context/sobre-operacao.md
memoria/context/prioridades.md
memoria/references/voz.md
memoria/references/nicho-*.md
memoria/references/nichos/**
memoria/decisions/log.md
memoria/memory/**
memoria/projects/**
memoria/archives/**
**/handoff-session/handoff-*.md
**/_sessions-pendentes.log
**/_pendencias-abertas.md
.env
*credential*
*secret*
*token*
*financeiro*
*.key
*.pem
```

## SEGREDO BLINDADO (nunca sai da máquina, nem pro seu próprio repo)

> Seção documental (o `/atualizar` não a lê; a proteção no update vem da lista DADO acima). Aqui só
> explica o que o `/sync` barra, pra você entender a fronteira.

O resto do DADO (contexto, voz, memória, decisões, projetos) é seu e **sincroniza normalmente**
pelo `/sync` se você usa o CORTEX em mais de uma máquina: é o ponto do sync, levar o seu cérebro
de um PC pro outro pelo seu repo privado.

O SEGREDO é a exceção: **nunca sobe, nem pro seu próprio repo**. São os arquivos de credencial e
dado financeiro já listados em DADO DO USUÁRIO (`.env`, `*credential*`, `*secret*`, `*token*`,
`*financeiro*`, `*.key`, `*.pem`). O `/sync` aborta o push se achar qualquer um (varre nome E
conteúdo), e todo trecho `<private>...</private>` é zona morta: não sincroniza nem vira memória.

## Regras do update (o script obedece)

0. **Organizacao nova e aditiva:** a taxonomia nova vale como default para instalacao limpa. Em
   instalacao existente, update nao move, renomeia, apaga ou esconde pasta livre do usuario. Pasta
   desconhecida e dado do usuario por padrao.
0. **Migracao fisica e fluxo separado:** reorganizar arquivos existentes exige mapa antigo -> novo,
   dry-run, backup, manifesto de movimentacao e confirmacao explicita. Sem mapa, o script preserva.
1. **Backup primeiro:** copiar a raiz instalada inteira pra `_backup-update-<versao-antiga>-<data>/`
   antes de tocar em qualquer coisa. Sem backup, não atualiza.
2. **Só substitui PRODUTO:** para cada caminho de PRODUTO presente no zip novo, sobrescreve o
   instalado. Arquivo que existia no instalado e não veio na versão nova é preservado por padrão.
   Remoção só acontece se o caminho estiver em `REMOVER_PRODUTO` e o operador habilitar a remoção
   explicitamente no script.
3. **Nunca toca DADO:** nenhum caminho de DADO é lido, copiado ou apagado. Se o zip novo trouxer
   um arquivo de DADO (ex: `nicho-exemplo.md`), ele é IGNORADO (não sobrescreve o do usuário).
4. **Conflito de produto editado à mão:** se um arquivo de PRODUTO foi alterado pelo usuário
   (difere do esperado da versão antiga), o script avisa, guarda a versão dele no backup e manda a
   versão nova para merge manual por padrão. Sobrescrita direta só com permissão explícita.
5. **VERSION manda:** ao fim, o `VERSION` do instalado vira o do zip novo. Se a versão do zip for
   menor ou igual à instalada, o script avisa e pede confirmação (downgrade/reinstalação).
