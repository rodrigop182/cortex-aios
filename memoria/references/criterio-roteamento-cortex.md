# Critério de roteamento: vivo do {{USUARIO}}go vs. CORTEX distribuível

Toda regra, comportamento ou melhoria que entra no sistema precisa ser roteada antes de gravar.
A pergunta-mãe: **isso serve só ao {{USUARIO}}go, ou serve a qualquer agente CORTEX?**

---

## Vai SÓ pro vivo do {{USUARIO}}go (`{{CAMINHO_CORTEX}}\` + `memory/`)

Critério: tem dado pessoal, depende do contexto dele, ou é preferência sua que não generaliza.

- Dado pessoal: nome, clientes, projetos, caminhos reais (`{{CAMINHO_CORTEX}}\...`)
- Preferência de nicho: regras específicas de landing, CSS, identidade V3 (`#FF4002`)
- Fluxo de trabalho particular: como ele lida com Leo, João, o estúdio
- Voz/tom dele: minúsculas, sem acentos no coloquial, abreviações
- Memória de projeto: estado de frentes ativas, decisões passadas, clientes
- Regra que o {{USUARIO}}go cobrou explicitamente como "só pra mim"

→ Grava em `memory/`, `CLAUDE.md` do projeto, ou ficha do cliente. Não toca o template.

---

## Vai pro CORTEX distribuível (`_template_aios\`)

Critério: **qualquer pessoa com um CORTEX se beneficiaria disso**, independente de nicho, projeto ou voz.

Perguntas de filtro (basta 1 ser "sim"):
1. Um agente CORTEX de dev, escritor ou gestor usaria essa regra do mesmo jeito?
2. Ela melhora a qualidade do raciocínio/entrega do agente, não só do {{USUARIO}}go?
3. Resolve um problema universal de AIOS (loop de aprendizado, elevação de resultado, root cause)?
4. Seria uma das primeiras coisas que qualquer novo usuário precisaria saber?

Exemplos que passam no filtro:
- Root cause fix (corrigir + fechar a causa — qualquer agente comete erro)
- Nomear padrão técnico (qualquer operador se beneficia do léxico)
- Modo elevação / `melhore` (qualquer agente entrega resultado fraco às vezes)
- Não mostrar v1 crua (universal)
- Entrevistar antes de executar (universal)

→ Porta pro template **sem dado pessoal**: trocar caminho real por placeholder, remover nome/cliente/nicho específico. Regra/comportamento fica, contexto pessoal fica pra trás.

---

## Casos de borda

**Regra que nasceu num nicho mas generaliza:** porta pro template com linguagem genérica.
Ex: "tá fraco + print = diagnóstico com léxico técnico" nasceu em CSS de landing, mas o método
(nomear defeito com termo da área + descartar v1 + referência de elite) serve pra qualquer entregável.
→ Template recebe o método genérico; o vivo do {{USUARIO}}go mantém a versão com detalhe de CSS/design.

**Regra comportamental sobre o {{USUARIO}}go especificamente:** fica no vivo.
Ex: "ele é perfeccionista, empurrar com prazo + entregável" é sobre ELE, não sobre todo operador.

**Dúvida real:** perguntar ao {{USUARIO}}go antes de portar. Não assumir universal.

---

## Como usar

Ao gravar qualquer regra nova (manual, `/fecha-sessao`, destilação automática):
1. Passar pelo filtro acima
2. Se universal: gravar no vivo E portar pro template na mesma operação (não acumular dívida)
3. Se pessoal: só no vivo
4. Registrar decisão de porte em `decisions/log.md` se for não-óbvio

Ponteiro no MEMORY.md + 1 linha no `playbook-atualizar-otimizar-cortex.md` (seção "O que porta").
