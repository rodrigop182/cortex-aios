# Estado da arte: 1-shot, memória e custo-benefício em agentes de IA (jun/2026)

Destilação de pesquisa externa (4 varreduras) pra calibrar o [[cortex-visao-produto]] e o
`projects/cortex-roadmap.md` contra o que sêniores fazem. Ler sob demanda, não todo turno.

## Achado central (4 frentes convergem)

O 1-shot NÃO vem da inteligência do modelo. Vem de: **(1) contexto enxuto + (2) verificação
externa + (3) memória que aprende e poda.** Lastro científico:
- **Context rot** (Chroma, 18 modelos incl. Opus 4): janela cheia PIORA a resposta, mesmo em 1M;
  morde ~300-400k. → gastar menos contexto é QUALIDADE, não só economia. Valida o "~250k dumbzone".
  https://www.trychroma.com/research/context-rot
- **Self-correction no vácuo PIORA** (ICLR 2024): modelo revisando a si mesmo regride. Auditar só
  funciona com check externo (teste/build/screenshot) ou outro contexto.
  https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00713/125177
- **Teto de ~150-200 instruções** que o modelo segue com confiança (system prompt do CC já gasta
  ~50). Cérebro fino é limite físico, não estética.

## O que sêniores fazem pra acertar de primeira

1. Separar pesquisar → planejar → executar (plano em artefato versionado). Anthropic mediu: sobe
   acerto de ~1/3 pra ~2/3 em tarefa complexa. https://code.claude.com/docs/en/best-practices
2. Dar ao agente um CHECK que ele roda (teste/build/screenshot) e mandar iterar até passar — fecha o
   loop sem o humano virar o verificador.
3. Prompt específico ancorado em EXEMPLO canônico ("faça igual ao arquivo X") > descrever do zero.
4. Entrevista antes → vira SPEC.md → executar em SESSÃO NOVA (contexto limpo = melhor 1-shot).
   Spec-driven reduz erro até 50%. https://arxiv.org/html/2602.00180v1
5. CLAUDE.md enxuto com o "porquê" de cada regra; podar o que o modelo já cumpre sozinho.
   https://www.humanlayer.dev/blog/writing-a-good-claude-md
6. Progressive disclosure (skill/arquivo sob demanda) + just-in-time retrieval (ponteiro, não valor).
   https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
7. Subagente pra pesquisa em leque (devolve resumo ~1-2k tok); NÃO pra tarefa de 1 passo (overhead
   compõe). Encadear vai por arquivo, não por agentes conversando.
8. Gestão agressiva de contexto: /clear entre tarefas; 2 correções na mesma coisa = contexto poluído
   → /clear + reprompt melhor. Manter janela em 40-60%.
9. Frequent Intentional Compaction (HumanLayer): cada fase produz artefato .md compactado que é o
   input da próxima. https://www.humanlayer.dev/blog/advanced-context-engineering
10. Memorizar preferências após cada sessão (anti-retrabalho). É a alavanca nº1 do 1-shot no tempo.

## Loops de verificação (planejar→executar→auditar→validar)

- **Evaluator-Optimizer** (Anthropic "Building Effective Agents"): um gera, OUTRA chamada avalia, em
  loop. Auditoria é chamada separada (subagente) que vê só entregável + critério.
  https://www.anthropic.com/research/building-effective-agents
- **Reflexion** (NeurIPS 2023): erro vira texto na memória episódica e volta na próxima tentativa.
  91% vs 80% no HumanEval. O ganho vem do evaluator externo + reflexão escrita virar input.
  https://arxiv.org/abs/2303.11366
- **Stop hook determinístico** (3 camadas: PostToolUse linta, Stop pergunta completude, Stop command
  roda teste/build e exit 2 BLOQUEIA o fim até passar). Cuidado: CC solta após 8 bloqueios, checar
  `stop_hook_active`. https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
- **Revisor adversarial em contexto novo** (vê só o diff + critério). Instruir a sinalizar só gap de
  correção/requisito, senão over-engineering.
- **Anti-loop-infinito:** cap de iterações (10-15), detector de repetição de tool, completion check.
  Sem progresso em 2-3 voltas → para e pergunta (pop-up), não insiste no escuro.
- **Mostrar evidência, não afirmar sucesso:** entrega = output do check / screenshot, não "ficou bom".

## Error log / lições aprendidas (gravar erro e não repetir)

Forma dominante = arquivo .md (`learnings.md`) que acumula lições; próxima execução lê antes de agir.
Curadoria-chave: gravar só o NÃO-óbvio e reutilizável (senão incha e o agente ignora). Dois níveis:
**efêmero** (dentro da tarefa, alimenta o retry) → se recorre, vira **regra persistente**. NÃO usar
RAG; a literatura é texto + curadoria. (Casa com [[sem-rag-gap-e-qualidade]].)

## Custo-benefício / token

- **Prompt caching:** cache read = 10% do preço base (90% economia em prefixo estável). NÃO editar a
  base estável no meio da sessão (invalida o cache dali pra frente). Conteúdo volátil DEPOIS do
  estável. https://claude.com/blog/prompt-caching
- **Model routing por NATUREZA da tarefa:** Haiku=mecânico/varredura, Sonnet=braçal, Opus=decisão/
  design/voz/memória (NUNCA descer estes). Routing corta 50-80%. HAL: mais reasoning muitas vezes
  PIORA acurácia → calibrar effort pela tarefa. https://arxiv.org/abs/2510.11977
- **Métrica certa = $/tarefa concluída** (% resolved + custo médio), não $/token. Pro CORTEX, análogo
  é "iterações + contexto até o entregável passar no critério". Ler com /context e contagem de turnos.
- **Compactar cedo** (proativo, sessão saudável), não no estouro.

## Produtos comparados (e onde o CORTEX já ganha)

| Sistema | Tem poda/medição? | CORTEX vs ele |
|---|---|---|
| CLAUDE.md / AGENTS.md | Não (manual) | CORTEX já é índice fino + ponteiros (faz melhor) |
| Cline Memory Bank | Não (confessa, terceiriza p/ auto-compact) | CORTEX poda ativa (à frente) |
| Cursor Rules (.mdc) | Não; revisão trimestral manual | Roubar: carregar regra por GLOB de arquivo |
| Windsurf Rules+Memories | Memória auto efêmera local | Roubar: FAIXA de memória volátil que expira |
| Copilot custom instructions | Não; `applyTo` por glob | Mesma ideia de escopo por caminho |
| Anthropic memory tool | SIM: versionamento, limites, "dreaming", read_only | Roubar: consolidação periódica + read_only em references/ |

## Qualidades de vida a roubar (ranqueadas)

1. **Medir eficácia de regra + podar por evidência** — ninguém faz; é onde o CORTEX vira estado da arte.
2. **Dreaming / consolidação periódica** — funde memórias fragmentadas, reescreve, aposenta o velho.
3. **Carregar regra por glob de caminho** — regra de .tsx só entra quando toca .tsx (anti-bloat barato).
4. **Faixa de memória efêmera/volátil** — rascunho que expira, não pressiona a curadoria.
5. **`read_only` em references/** — protege referência canônica + fecha vetor de envenenamento de memória.
6. **Error log efêmero da tarefa** (Reflexion) — o loop quente que falta entre as sessões.

## Erros a EVITAR (que os produtos cometem)

- Estrutura fixa que incha sem freio (Cline). Confiar que o humano poda "no julgamento" (ninguém poda).
- Regra de estilo na memória (linter/hook faz melhor, barato, determinístico).
- Empilhar acima de ~150-200 instruções / ~50% da janela (obediência cai, "meio" é esquecido).
- Memória gravável + input não confiável = envenenamento (cautela ao destilar conteúdo externo direto).
- Regras geradas por LLM sem gate de dedup/contradição (Meta-Policy Reflexion confessa o problema).

## Fontes-âncora
- Anthropic best practices: https://code.claude.com/docs/en/best-practices
- Context engineering: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Building effective agents: https://www.anthropic.com/research/building-effective-agents
- Harnesses longos: https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
- HumanLayer ACE: https://www.humanlayer.dev/blog/advanced-context-engineering
- Context rot: https://www.trychroma.com/research/context-rot
- Reflexion: https://arxiv.org/abs/2303.11366 | SSGM: arXiv 2603.11768 | Meta-Policy Reflexion: 2509.03990
- Prompt caching: https://claude.com/blog/prompt-caching | HAL: https://arxiv.org/abs/2510.11977
