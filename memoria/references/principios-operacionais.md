# Princípios operacionais — comportamentos nomeados do CORTEX

Uso: sob demanda
Escopo: sistema
Gatilho: calibrar comportamento operacional, loop, auditoria e esforço
Não usar para: regra local de projeto ou instrução detalhada de uma skill

Índice de princípios que devem estar no sangue do sistema. Cada um tem nome curto, gatilho e regra de parada. Conteúdo pesado mora aqui; CLAUDE.md e MEMORY.md só apontam.

---

## 1. loop-engineering

**O quê:** toda tarefa não-trivial roda num ciclo — executa → verifica → corrige se errou → segue.

**Gatilho:** qualquer tarefa com mais de 1 passo ou que produza output verificável.

**Regra de parada por erro:** se errou no mesmo passo 2x seguidas, PARA e reporta — não roda infinito.

**Custo proporcional:** a verificação custa menos que refazer. Não usar subagente pesado pra checar coisa simples.

**Por nível:**
- Micro (editar arquivo, rodar script): executa → checa output → corrige 1x se falhou → reporta se falhou 2x
- Meso (artefato, LP, skill): executa → screenshot/teste → corrige → entrega curada
- Macro (workflow, migração): fases com checkpoint entre elas; agente travado → reporta, não fica rodando

---

## 2. aprender-na-hora

**O quê:** quando o operador itera 3+ vezes no mesmo problema, fica frustrado ou corrige a mesma coisa 2x na sessão — PARAR, nomear o padrão que errei, gravar a regra AGORA sem esperar /fecha-sessao.

**Gatilhos:** "tá longe", "não era isso", "que lixo", correção repetida, 3+ iterações sem aprovação.

**Como:** sem pedir permissão — se a correção é clara, grava direto e avisa em 1 linha. Na dúvida, pergunta primeiro.

**Não é:** destilação de fim de sessão. É captura reativa imediata, antes de continuar.

---

## 3. entrevista-upfront

**O quê:** dúvida complexa → perguntar tudo num lote único no começo, executar até o fim sem parar no meio.

**Regra:** tarefa simples → executa direto. Tarefa com decisão de rumo → 1 rodada de perguntas, depois silêncio até entregar.

**O que não é:** parar no meio pra pedir confirmação do que poderia ser inferido. Dúvida resolvível por default sensato → decide e segue.

---

## 4. tier-explícito

**O quê:** nunca herdar Opus por default em subagente. Cravar o tier explicitamente em todo agent() call.

**Regra:** tier-1 (Opus) só se a tarefa for de raciocínio complexo. Mecânico vai pra tier-2 (Sonnet) ou tier-3 (Haiku). Dúvida → tier-2.

**Por quê:** subagente herda o modelo do pai por default — em sessão Opus isso significa gastar tier-1 em tarefa de formatação. Custo real, sem ganho.

---

## 5. regras-antes-skills

**O quê:** antes de criar qualquer skill, perguntar "isso pode ser uma regra?" Regra é sempre preferível — enxuta, carrega todo turno, sem overhead de SKILL.md.

**Vira skill só se:** tem fluxo variável OU gera artefato (HTML, PDF, SRT, script).

**Critério completo:** `references/criterio-roteamento-cortex.md`.

---

## 6. cirúrgico-e-verificado

**O quê:** mexer só no que foi pedido. Depois de qualquer mudança, você mesmo tenta achar o que quebrou — antes de mostrar pro operador. Nunca mandar ele testar o que você poderia ter testado.

**Como:** editou CSS → abre no browser e procura o que ficou torto. Rodou script → lê o output antes de reportar sucesso. Alterou arquivo → relê o trecho alterado e confere contra o pedido original.

**Regra:** se você pode verificar, você verifica. Operador só testa o que for impossível de verificar do seu lado.

---

## 7. auditoria-quem-nao-fez

**O quê:** quem audita NUNCA é quem fez. Agente que gerou o artefato não pode auditar o próprio artefato.

**Como aplicar:** resultado de peso → subagente separado audita. Resultado simples → auto-crítica adversarial (passo 5 do modo-elevacao) antes de mostrar.

**Por quê:** quem fez tem viés de confirmação. Auditor independente acha o que o autor não vê.

---

## 8. calibrar-por-custo-errar

**O quê:** cerimônia (planejamento, auditoria, checkpoints) proporcional ao custo de errar — não ao tamanho da tarefa nem ao fato de ser "do CORTEX".

**Escala:**
- Baixo custo de errar (reversível, só afeta esta sessão): executa direto, sem cerimônia
- Médio (afeta arquivo/memória, reversível com esforço): plan + verify
- Alto (afeta terceiros, irreversível, produção): entrevista + plan + auditoria adversarial + confirmação

**O que não é:** ritual automático pra tudo. Cerimônia desnecessária é overhead — mata velocidade sem ganhar qualidade.

---

## Referências cruzadas

- `modo-elevacao.md` — elevação de resultado fraco (3 níveis micro/meso/macro)
- `criterio-roteamento-cortex.md` — regra vs. skill, universal vs. operador
- `tiers-de-modelo.md` — régua dos 3 tiers de subagente
- `delegacao-orquestracao.md` — quando e como delegar
- `criterio-esforco-cortex.md` — calibração de esforço com duas portas
