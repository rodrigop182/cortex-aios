# Catálogo de skills — geral + por nicho

O CORTEX vem com as **skills do motor** (onboard, regras, audit, level-up, plan, grill-me,
handoff, fecha-sessao) e a **skill-creator** (Apache 2.0, embutida). Este catálogo é a curadoria
do que mais vale a pena ADICIONAR por cima, separado em **geral** (serve pra todo mundo) e
**por nicho**.

## Importante: licença (leia antes)

As skills oficiais da Anthropic para documentos (pdf, docx, pptx, xlsx) e várias outras são de
**licença proprietária** e **não podem ser redistribuídas** dentro deste pacote. Por isso o
catálogo NÃO embute essas skills: ele aponta de onde você as instala (elas já vêm gratuitas com
o seu Claude Code). A `skill-creator` é a exceção (Apache 2.0), e por isso é a única skill de
terceiros que vem embutida aqui.

Regra simples: **skill Apache/MIT** você pode receber embutida; **skill proprietária** você
instala da fonte oficial. O catálogo respeita isso.

## Como instalar uma skill do catálogo

As skills oficiais da Anthropic vêm com o Claude Code. Para ver e instalar:

```
# dentro do Claude Code:
/plugin            # abre o marketplace de plugins/skills
```

Ou copie manualmente uma pasta de skill pra `~/.claude/skills/<nome>/` (cada skill é uma pasta
com `SKILL.md`). Para criar uma skill SUA do zero, use a `skill-creator` (já incluída): diga
"cria uma skill que faz X".

## Pacote GERAL (recomendado pra todo mundo)

Skills de documento e utilitárias que servem em qualquer nicho. Veja `geral.md`.

## Pacotes por NICHO

Cada arquivo lista as skills que mais rendem naquela área:

- `nicho-dev.md` — desenvolvimento
- `nicho-marketing.md` — marketing / conteúdo
- `nicho-escrita.md` — escrita / redação
- `nicho-design.md` — design
- `nicho-vendas.md` — vendas / comercial
- `nicho-operacoes.md` — operações / gestão

> Estes catálogos descrevem CATEGORIAS de skill e apontam as oficiais por nome. Não é uma lista
> fechada: conforme a Anthropic e a comunidade lançam skills novas, atualize o catálogo (ou peça
> pra eu atualizar). O que você criar com a skill-creator também entra aqui.
