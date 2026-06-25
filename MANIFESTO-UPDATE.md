# Manifesto de atualização — CORTEX OS

Define a fronteira **PRODUTO** (atualizável pela skill `/atualizar`) vs **DADO DO USUÁRIO**
(preservado, nunca tocado). O script `atualizar.py` lê este arquivo como fonte única da verdade.

A regra-mãe: **o que o `/onboard` ou o uso preenchem é DADO; o resto é PRODUTO.** Na dúvida,
um caminho é DADO (preservar é o lado seguro do erro).

## PRODUTO (a skill substitui pela versão nova)

Caminhos relativos à raiz do CORTEX instalado. Globs permitidos.

```
VERSION
README.md
INSTALAR.md
INSTALAR-AGENTE.md
COMECE-AQUI.txt
SEGURANCA.md
lite/MODO-LITE.md
lite/CLAUDE-LITE.md
MANIFESTO-UPDATE.md
CHANGELOG.md
TROUBLESHOOTING.md
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
memoria/references/3ms-framework.md
memoria/references/auto-melhoria-skills.md
memoria/references/como-o-sistema-aprende.md
memoria/references/grafo-de-skills.md
memoria/references/karpathy-4-principios.md
memoria/references/otimizacoes-processo.md
memoria/references/principios-aios.md
memoria/references/protocolo-execucao.md
memoria/references/regras-completas.md
memoria/references/skill-description-eficiente.md
memoria/references/tiers-de-modelo.md
memoria/references/ciclo-de-contexto.md
memoria/references/skills-catalogo/**
memoria/regras-base.md
memoria/intake.md
memoria/README.md
memoria/connections.md
memoria/projects/README.md
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
memoria/projects/*.md
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

1. **Backup primeiro:** copiar a raiz instalada inteira pra `_backup-update-<versao-antiga>-<data>/`
   antes de tocar em qualquer coisa. Sem backup, não atualiza.
2. **Só substitui PRODUTO:** para cada caminho de PRODUTO presente no zip novo, sobrescreve o
   instalado. Arquivo de produto que sumiu na versão nova é removido do instalado (limpeza).
3. **Nunca toca DADO:** nenhum caminho de DADO é lido, copiado ou apagado. Se o zip novo trouxer
   um arquivo de DADO (ex: `nicho-exemplo.md`), ele é IGNORADO (não sobrescreve o do usuário).
4. **Conflito de produto editado à mão:** se um arquivo de PRODUTO foi alterado pelo usuário
   (difere do esperado da versão antiga), o script avisa e guarda a versão dele no backup, mas
   aplica a nova mesmo assim (produto é do CORTEX). O backup garante reversão.
5. **VERSION manda:** ao fim, o `VERSION` do instalado vira o do zip novo. Se a versão do zip for
   menor ou igual à instalada, o script avisa e pede confirmação (downgrade/reinstalação).
