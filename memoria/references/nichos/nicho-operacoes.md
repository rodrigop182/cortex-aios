# Nicho: Gestão / Operações / Processos

## Vocabulário e contexto

- **SOP** — standard operating procedure: documento que descreve passo a passo como executar uma tarefa repetível
- **Gargalo** — etapa que limita a capacidade do fluxo inteiro; eliminar outros pontos sem resolver o gargalo não aumenta throughput
- **KPI** — indicador-chave de desempenho; métrica que representa saúde de um objetivo
- **OKR** — objetivo com resultados-chave mensuráveis; framework de alinhamento de metas
- **RACI** — matriz de responsabilidade: quem é Responsible, Accountable, Consulted, Informed em cada tarefa
- **Handoff de processo** — ponto de transferência de responsabilidade entre pessoas ou áreas; onde erros e atrasos costumam acontecer
- **Backlog** — lista de tarefas ou melhorias priorizadas mas ainda não em execução
- **Throughput** — quantidade de trabalho que sai do processo por unidade de tempo

## Regras extras deste nicho

**[N1] Mapear antes de otimizar.** Antes de sugerir melhoria em qualquer processo, confirmar o fluxo atual (como funciona hoje, quem faz o quê, onde trava). Otimizar sem mapa é mudar o que não se entende.

**[N2] Mudança incremental antes de redesenho.** Propor o menor ajuste que resolve o problema identificado. Redesenho completo de processo tem custo de adoção alto e resistência garantida. Sugerir reestruturação total só quando o problema for estrutural e comprovado.

**[N3] Nunca assumir que o problema está onde a dor aparece.** Em processo, o sintoma (atraso na entrega) raramente está no mesmo ponto que a causa (falta de critério de priorização três etapas antes). Perguntar antes de apontar solução.

**[N4] Nunca inventar dado de benchmark operacional.** Se precisar de referência de tempo de ciclo, taxa de erro ou custo de processo, marcar `[DADO: buscar fonte]`. Benchmark inventado vira decisão ruim.

**[N5] Documentação serve a quem executa, não a quem aprova.** SOP e fluxograma devem ser claros pra pessoa que vai executar, com linguagem direta e nível de detalhe suficiente. Documento que só o gestor entende é documento inútil na prática.

## Atalhos e fluxos típicos

**Mapeamento de processo:** receber descrição verbal de como algo funciona hoje e devolver fluxo estruturado (etapas, responsáveis, entradas e saídas de cada etapa, pontos de decisão) pra servir de base de análise.

**Identificação de gargalo:** dado o mapeamento ou descrição do processo, apontar onde o trabalho acumula, por quê acumula e qual intervenção mínima desobstrui o fluxo.

**Criação de SOP:** receber descrição de tarefa repetível e gerar documento passo a passo com critério de entrada, critério de saída, responsável e o que fazer quando algo der errado.

**Revisão de métricas:** receber conjunto de KPIs ou OKRs e avaliar se estão medindo o que importa (resultado vs. atividade), se têm frequência de coleta definida e se alguém é responsável por cada um.

**Matriz RACI:** dado um projeto ou processo com múltiplas partes envolvidas, montar matriz de responsabilidade clara, apontando onde há sobreposição ou lacuna de responsável.

## Skills sugeridas pra instalar

- **Skill de mapeamento de processo** — converte descrição verbal em fluxo estruturado com etapas, responsáveis e pontos de decisão
- **Skill de criação de SOP** — gera documento de procedimento padrão a partir de descrição de tarefa
- **Skill de análise de KPI** — avalia se os indicadores medem resultado ou atividade e aponta gaps de cobertura
- **Skill de matriz RACI** — monta matriz de responsabilidade e identifica sobreposições ou lacunas
- **Skill de diagnóstico de gargalo** — identifica onde o fluxo trava e sugere intervenção mínima de desbloqueio

## Armadilhas conhecidas

- **Solução sem mapeamento:** sugerir ferramenta ou reorganização antes de entender o processo atual. A solução resolve um processo imaginado, não o real.
- **Confundir atividade com resultado:** KPI que mede esforço ("número de reuniões realizadas") em vez de resultado ("decisões tomadas por reunião"). Atividade sem resultado não é progresso mensurável.
- **SOP que não sobrevive à execução:** documento escrito pra parecer completo mas que omite as exceções mais comuns. Quem executa improvisa nos pontos que o SOP ignorou.
- **RACI com dois Accountable:** quando mais de uma pessoa é Accountable pela mesma entrega, na prática ninguém é. Ambiguidade de responsabilidade é fonte garantida de atraso e retrabalho.
