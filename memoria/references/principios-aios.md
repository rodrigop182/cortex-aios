# Princípios de um AIOS pessoal - régua do sistema

> Esta é a régua interna do CORTEX OS. Ela existe para avaliar se o sistema está leve, útil,
> auditável e capaz de aprender sem virar uma pasta inchada de instruções.

## Os 6 princípios (o que faz um AIOS pessoal funcionar de verdade)

### 1. Cérebro fino, no teto
O arquivo lido todo turno (`CLAUDE.md`) é alto sinal e curto. Ele guarda só identidade, regras
invioláveis e ponteiros. **Teste:** o `CLAUDE.md` cabe no teto? Conhecimento pesado está fora dele,
em arquivo lido sob demanda, com só um ponteiro no índice?

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
hooks precisam deixar rastro de sessão, avisar sobre pendência e preservar aprendizado antes de
trocas longas de contexto. Curadoria com regra: dedup, fato novo derruba velho, poda o stale.
**Teste:** o aprendizado do dia é gravado sem o operador lembrar de pedir? Erro repetido vira regra
persistente?

### 6. Transparência sobre autonomia
Memória explícita, auditável, humano cura o que importa. O agente NÃO reescreve as próprias regras
sozinho sem o operador ver. "O OS sugere, o operador decide." **Teste:** toda mudança de regra ou
memória é visível e revisável? Nada muta no escuro?

## Uso
Esta é a régua do `/audit`. Régua também de qualquer decisão de arquitetura do OS: antes de adicionar
peça, perguntar qual princípio ela serve e se fere o 1 (incha o cérebro) ou o 6 (muta no escuro).
