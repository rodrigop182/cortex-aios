# Auto-manutenção da memória — como o CORTEX cresce sem estourar

> Desenho de arquitetura nascido da pergunta do {{USUARIO}}go (23/06): "a própria premissa do
> CORTEX faz ele crescer naturalmente, tem que ter um jeito de manter abaixo do limite".
> É o paradoxo central do produto. Este arquivo é o desenho da FASE 5 (a executar com
> gate humano, não no improviso). Casa com [[cortex-3-loops-auto-desenvolvimento]] (M3/M4),
> [[sem-rag-gap-e-qualidade]] e [[evitar-retrabalho-correcao-repetida]].

## STATUS — CONSTRUÍDA em 2026-06-23 (vivo + template)
Os 3 mecanismos existem e foram auditados (subagente adversarial). A consolidação do índice já rodou
(MEMORY.md 23.2→18.4KB). Hooks: `guarda_tamanho_memoria.py` (detector de família, LIMIAR=22),
`registra_uso_memoria.py` (instrumentação, PostToolUse:Read), `poda_por_evidencia.py` (sob demanda,
gate). FALTA, no tempo: (a) a instrumentação coletar ~30 dias antes da 1ª poda confiável (trava
conservadora ativa); (b) ligar a `poda_por_evidencia` ao gatilho AUTOMÁTICO (vigia de inatividade /
catch-up) — hoje é só sob demanda. Decisões em `decisions/log.md` (2026-06-23 FASE 5).

## O paradoxo
"Aprende todo dia + nunca esquece" + índice fino lido todo turno (teto ~24.4KB de
carregamento do Claude Code) = o índice estoura e VOLTA a esquecer (trunca silencioso).
A promessa se autossabota sem um mecanismo de auto-manutenção. Avisar (guarda de tamanho)
não basta: a entrada é constante, então o equilíbrio tem que ser ESTRUTURAL, não manual.

## Por que NÃO é "apagar pra caber"
Apagar pra caber faz o sistema perder regra viva sem o operador ver — fere o princípio
de não mutar memória no escuro. A solução é mudar a FORMA do crescimento, não cortar.

## Os 3 mecanismos (juntos = crescimento sublinear)

### 1. Índice guarda ponteiros, não conhecimento (já vale hoje)
Conhecimento novo vira ARQUIVO (cresce ilimitado); no índice entra 1 linha. Necessário,
mas sozinho ainda cresce LINEAR com o nº de regras. Insuficiente.

### 2. Consolidação, não acumulação (A CHAVE que faltava)
Quando entram N regras do MESMO tema (ex: 5 sobre QA visual), elas NÃO viram N linhas no
índice — viram 1 ARQUIVO-TÓPICO que as absorve + 1 linha no índice. O índice cresce com o
nº de TEMAS (finito: design, QA, voz, git, vídeo, copy...), não de REGRAS (infinito, mas
moram FORA do índice). Resultado: a enésima regra de design não adiciona linha nenhuma ao
índice — só engorda o arquivo `design.md`. É isto que torna o crescimento SUBLINEAR.
- Gatilho de consolidação: quando uma família do índice passa de ~K entradas (ex: 8), o
  sistema propõe fundir as entradas daquele tema num arquivo-tópico e deixar 1 ponteiro.
- A fusão preserva cada regra (move pro arquivo), nunca apaga; só troca N linhas por 1.

### 3. Poda por evidência (ataca a torneira aberta)
Regra que nunca foi usada/citada em X tempo (ou contradiz outra mais nova) é candidata a
sair. Exige instrumentação: marcar quando uma regra foi REALMENTE aplicada (citada numa
resposta, carregada sob demanda, evitou um retrabalho). Sem medir uso, poda é chute.
- Sinais de uso: arquivo aberto/citado em sessão; regra referenciada na destilação; match
  com correção repetida resolvida.
- Gate: poda nunca é silenciosa — log auditável do que saiu + porquê, e (no começo)
  confirmação humana antes de remover. Reversível (move pra `archives/`, não deleta).

## Ordem de construção (FASE 5)
1. Instrumentar USO (sem isso, nada de poda confiável). Hook/registro leve de "regra X
   foi tocada nesta sessão".
2. Consolidação assistida: detector de família inchada → propõe fusão → eu executo com
   julgamento → 1 linha pro {{USUARIO}}go.
3. Poda por evidência: regra sem uso há X + log + gate → move pra archives.
4. Só quando 1-3 provarem que não comem regra viva: subir o nível de automação.

## Princípio que fica
O índice fino não escala por ser PEQUENO — escala por separar TEMA (finito, no índice) de
REGRA (infinita, no arquivo). Consolidar o vivo vem antes de podar o morto.
