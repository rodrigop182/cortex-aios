# Fluxo de roteamento do aprendizado — onde cada coisa mora (padrão do CORTEX)

> Criado 22/06/2026 porque o roteamento estava na intuição e ficava inconsistente (hooks longos no
> índice fino, memória às vezes em `memory/` às vezes em `references/` sem critério). Este doc é a
> REGRA que eu e os subagentes seguimos pra todo aprendizado novo. Carrega sob demanda (não todo turno).

## O mapa real das pastas (confirmado no disco 22/06)

| Lugar | O que mora | Carrega quando |
|---|---|---|
| `~/.claude/CLAUDE.md` (global) | O CÉREBRO: quem é o {{USUARIO}}go (curto), como trabalhar, PONTEIROS | TODO turno (fino de propósito) |
| `~/.claude/projects/c--Projetos/memory/` + `MEMORY.md` | AUTO-MEMÓRIA: regras de feedback, preferências, voz, estado. 1 fato por arquivo. `MEMORY.md` = índice | `MEMORY.md` TODO turno; os arquivos sob demanda |
| `{{CAMINHO_MEMORIA}}\references/` | Conhecimento PESADO: guias de nicho, frameworks, doutrinas, este doc | sob demanda (link explícito) |
| `{{CAMINHO_MEMORIA}}\decisions/log.md` | Decisões datadas + porquê (append-only, episódico) | sob demanda |
| `{{CAMINHO_MEMORIA}}\context/` | Sobre o {{USUARIO}}go/operação/prioridades (pesado) | sob demanda |
| `{{CAMINHO_MEMORIA}}\projects/` | Ficha de cada cliente/projeto, isolada | sob demanda |
| pasta do PROJETO (`clientes/x/`, `estudio/site/`) | STATUS.md do projeto (onde paramos) | quando abre o projeto |

ARMADILHA confirmada: existe `{{CAMINHO_MEMORIA}}\memory\` (VAZIO) e a auto-memória real em
`~/.claude/.../memory/`. Não confundir. A auto-memória real é a do `~/.claude`. A vazia é resíduo.

## A REGRA DE ROTEAMENTO (qual pasta pra qual aprendizado)

Pergunte, nesta ordem:

1. **É JEITO DE FAZER (workflow, passo-a-passo)?** → conserta/cria uma **SKILL**, não memória solta.
   (corpo da skill carrega só quando aciona; ver [[auto-melhoria-skills]] do CLAUDE.md)
2. **É DECISÃO DATADA com porquê** (escolhi X em vez de Y em tal dia)? → `decisions/log.md`, 1 entrada.
3. **É REGRA/PREFERÊNCIA/VOZ durável e CURTA** (cabe em ~15-20 linhas)? → arquivo em `memory/`
   (auto-memória), `type: feedback`, + 1 LINHA de ponteiro no `MEMORY.md`.
4. **É CONHECIMENTO PESADO** (guia, framework, doutrina, tabela, >~25 linhas)? → arquivo em
   `memoria/references/` + 1 linha de ponteiro no lugar que o invoca (CLAUDE.md ou MEMORY.md).
5. **É SOBRE UM PROJETO/CLIENTE específico?** → ficha em `memoria/projects/` ou CLAUDE.md do cliente.
6. **É ESTADO de projeto (onde paramos)?** → STATUS.md na pasta do projeto (gerado automático).

## A LEI DO ÍNDICE FINO (a que eu violei e estou consertando)

O `MEMORY.md` e o CLAUDE.md carregam TODO TURNO. A partir de ~200-250k de contexto o modelo fica
burro. Logo, no índice:
- **Hook de 1 linha, NUNCA um parágrafo.** Formato: `- [Título](arquivo.md) — gancho de 1 frase.`
- O hook diz só o SUFICIENTE pra decidir relevância. O conteúdo mora no arquivo, não no índice.
- Se o hook passou de 1 linha (2 frases longas), está errado: cortar pro essencial.
- Regra contextual (só vale num caso) NÃO entra no índice: vai pro destino que a faz carregar só
  quando relevante (skill, CLAUDE.md de cliente). Ver [[regra-mora-onde-carrega]].

## LINKAR LIBERALMENTE (o que faltava)

Todo arquivo de memória novo deve LINKAR os relacionados com `[[nome-do-slug]]`. Link que ainda não
existe é OK (marca o que falta escrever). Sem links, o cérebro vira ilhas e eu re-descubro tudo.
Ao gravar: olhar 2-3 memórias vizinhas e cruzar referências nos dois sentidos.

## CURADORIA ANTES DE GRAVAR (não criar duplicata — o erro clássico)

1. **Dedup:** já existe arquivo do tema? ATUALIZA ele, não cria outro. (eu criei a regra
   anti-retrabalho 2x uma vez — é o sintoma de pular este passo).
2. **Contradição:** fato novo derruba velho? Reescreve o velho pro estado atual, 1 linha do que mudou.
3. **Poda:** memória que aponta arquivo/fluxo morto → apaga e tira do índice. (perguntar antes se não é minha)

## CHECKLIST ao gravar um aprendizado (rodar mentalmente, é rápido)

- [ ] Roteei pela pergunta certa (1-6 acima)? Não joguei tudo em `memory/` por preguiça?
- [ ] Se foi pro índice: hook tem 1 linha só?
- [ ] Conhecimento pesado ficou em `references/` com ponteiro, não inflado no índice?
- [ ] Linkei `[[ ]]` as memórias vizinhas?
- [ ] Conferi dedup (não duplico arquivo existente)?

Casa com [[criterio-relevancia-destilacao]], [[evitar-retrabalho-correcao-repetida]],
[[cortex-evolui-todo-dia]] (a destilação diária aplica este fluxo) e a seção "Cérebro fino" do CLAUDE.md.
