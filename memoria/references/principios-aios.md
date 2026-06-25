# Princípios de um AIOS pessoal (com lastro) — a régua do sistema

> Substitui os "4 Cs" (Context/Connections/Capabilities/Cadence) do Nate Herk como a régua do
> sistema. Por quê: os 4 Cs são mnemônico de criador de conteúdo, sem lastro de engenharia — bom pra
> didática, fraco como medida. Estes princípios vêm da doc da Anthropic e dos dois maiores frameworks
> open-source de 2026 (OpenClaw, Hermes). Lastro em [[benchmark-openclaw-hermes]]. Não é um acrônimo
> novo de propósito: é o que a engenharia séria exige, não uma sigla pra decorar.

## Os 6 princípios (o que faz um AIOS pessoal funcionar de verdade)

### 1. Cérebro fino, no teto
O arquivo lido todo turno (CLAUDE.md) é alto sinal e curto. Anthropic: 80-120 linhas; o modelo segue
~150-200 instruções e o sistema já gasta ~50. OpenClaw/Hermes impõem TETO DE TAMANHO de propósito —
"força curadoria, não acumulação". **Teste:** o CLAUDE.md cabe no teto? Conhecimento pesado está FORA
(em arquivo lido sob demanda), com só um ponteiro no índice?

### 2. Memória em dois níveis
Curada e enxuta no prompt (markdown, lida todo turno) vs. volumosa e buscável fora do prompt (lida só
quando precisa). O índice fino aponta; o depósito guarda. **Teste:** existe separação clara entre o
que carrega sempre e o que carrega sob demanda? A memória persistente tem entradas vivas e curadas?

### 3. Regras negativas tão fortes quanto as positivas
"Nunca commitar segredo", "nunca em-dash", "nunca [comportamento indesejado específico do operador]".
Sem regra negativa explícita, o modelo escolhe o padrão mais comum que conhece — que não é o seu.
**Teste:** os erros caros estão gravados como proibição explícita, não só como preferência?

### 4. Capacidade carregada sob demanda (progressive disclosure)
Skills no formato SKILL.md, das quais só o nome+resumo entra no contexto; o corpo carrega quando o
gatilho casa. Mantém o custo plano independente de quantas skills existem. Subagentes isolam contexto
e devolvem só o resultado. **Teste:** as skills carregam só quando acionadas? Trabalho de pesquisa/
volume vai pra subagente em vez de inchar a sessão principal?

### 5. O loop de aprendizado FECHA sozinho
O ponto onde quase todo AIOS pessoal falha. Aprender não pode depender de lembrar de acionar. Os
frameworks sérios disparam destilação automática: nudge periódico (Hermes, a cada N turnos) e
flush antes de perder contexto (OpenClaw/Hermes, Pre-Compaction). Curadoria com regra: dedup, fato
novo derruba velho, poda o stale. **Teste:** o aprendizado do dia é gravado SEM o operador digitar
comando? Erro repetido vira regra automaticamente?

### 6. Transparência sobre autonomia
Memória explícita, auditável, humano cura o que importa. O agente NÃO reescreve as próprias regras
sozinho sem o operador ver (é onde o Hermes erra para certos casos de uso). "O OS sugere, o operador
decide." **Teste:** toda mudança de regra/memória é visível e revisável? Nada muta no escuro?

## Como isto mapeia (e melhora) os 4 Cs

- **Context** (4 Cs) → vira princípios 1+2+3. Mais preciso: separa "fino no teto" de "dois níveis" de
  "regra negativa", que os 4 Cs amontoavam num bloco só.
- **Connections** → NÃO é um pilar de qualidade do cérebro; é uma capacidade. Vai pra dentro do
  princípio 4 (o que o sistema alcança é uma capacidade carregada quando precisa).
- **Capabilities** → princípio 4.
- **Cadence** → vira o princípio 5, mas afiado: não basta "ter hook recorrente"; o teste é se o LOOP
  DE APRENDIZADO fecha sozinho. Cadence media presença de ritual; o princípio 5 mede se ele aprende.
- **Falta nos 4 Cs:** o princípio 6 (transparência) não existia na régua antiga. É o que separa a
  abordagem conservadora (OpenClaw) da abordagem de maior risco (Hermes).

## Uso
Esta é a régua do `/audit`. Régua também de qualquer decisão de arquitetura do OS: antes de adicionar
peça, perguntar qual princípio ela serve e se fere o 1 (incha o cérebro) ou o 6 (muta no escuro).
