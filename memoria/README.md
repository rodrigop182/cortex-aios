# Seu AIOS — memória do cérebro

Esta pasta é a **memória de longo prazo** do seu assistente de IA pessoal (AIOS).

> **O cérebro (as regras, quem é você, como trabalhar) NÃO mora aqui.** Ele mora no
> `CLAUDE.md` GLOBAL deste PC (`~/.claude/CLAUDE.md`), que carrega em toda sessão, em qualquer
> pasta. Por isso o cérebro está sempre ativo quando você abre sua pasta de trabalho. Esta
> pasta guarda os DADOS que o cérebro lê sob demanda (decisões, contexto, referências).
> Editar o cérebro = editar o global, não criar outro CLAUDE.md aqui (evita dois arquivos
> divergindo).

## A ideia em uma frase

Um assistente de IA que não te reexplica todo dia: lembra quem você é, como você escreve, no
que você foca, e aprende com cada erro pra não repetir. Três pilares:

1. **Cérebro fino** — o `CLAUDE.md` é um índice curto lido todo turno. Conteúdo pesado mora
   aqui na memória e é lido só quando precisa.
2. **Memória em dois níveis** — o que é sempre necessário fica no prompt; o resto fica
   buscável sob demanda.
3. **Loop de aprendizado que fecha sozinho** — erros viram regras, decisões ficam
   registradas, e a destilação do dia roda sem você digitar comando.

## Onde cada regra mora

Não basta TER a regra: o que importa é ONDE ela carrega. Cada regra vai pro destino que a faz
aparecer só quando é relevante, pra o cérebro fino não inchar:

- **Específica de um projeto/cliente** → o `CLAUDE.md` daquele projeto (carrega só quando você
  trabalha nele).
- **Específica de uma skill/fluxo** → o corpo da skill (`SKILL.md` ou `references/`), carrega só
  quando a skill aciona. Nunca no índice global.
- **Geral, transversal** (jeito de trabalhar, método de execução) → o cérebro (`CLAUDE.md`
  global), que carrega todo turno.

Por quê: o cérebro é lido todo turno; enchê-lo de regra contextual (de um projeto, de um tipo de
tarefa) dilui o sinal e queima contexto à toa. Ao gravar QUALQUER regra, pergunte primeiro "onde
isso carrega?" e mande pro destino certo, não despeje tudo no índice.

## Como começar (Dia 1)

1. Instale o template (veja `INSTALAR.md` na raiz do pacote).
2. Preencha `intake.md` (7 perguntas) — ou rode `/onboard` pra ele te entrevistar.
3. Rode `/onboard`. Ele monta seu `context/`, sua `voz.md`, seu `connections.md` e completa
   seu `CLAUDE.md`.
4. Teste: peça "me pergunta — no que eu devo focar essa semana?". Esse é o momento "uau".

## Ritual

- **Toda semana:** `/audit` (nota do setup pelos 6 princípios) e `/level-up` (1 alavanca → 1
  artefato enviado).
- **Antes de tarefa de mais de um passo:** `/plan`, e `/grill-me` pra pressionar o plano.
- **Fim do dia / fim de sessão longa:** `/fecha-sessao` destila o que aprendeu em regras.
- **Decisão relevante:** registre em `decisions/log.md`.

## Os frameworks

- **6 princípios de AIOS** (a régua) — `references/principios-aios.md`. Base do `/audit`.
- **Protocolos de execução** — `references/protocolo-execucao.md`, `references/regras-completas.md`
  e `references/tiers-de-modelo.md`.

## Estrutura

```
memoria/                   (a memória; o cérebro mora em ~/.claude/CLAUDE.md)
├── intake.md           suas 7 respostas (fonte do /onboard)
├── connections.md      o que o sistema alcança
├── context/            sobre você, sua operação, prioridades
├── references/         frameworks, voz, padrões, doutrinas
├── projects/           clientes e projetos (isolados um do outro)
├── decisions/log.md    decisões e o porquê (append-only)
├── archives/           coisa velha (mover, não apagar)
└── .claude/skills/     onboard, regras, como-funciona, audit, level-up, plan, grill-me
```

## Crédito

Arquitetura CORTEX OS: cérebro fino, memória em dois níveis, capacidades sob demanda e loop de
aprendizado auditável.
