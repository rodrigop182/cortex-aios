# Critério de esforço ao mexer no CORTEX — quando ir leve, quando ir pesado

Existe porque eu (Opus) me impunha cerimônia pesada em TUDO (auditoria adversarial + teste isolado +
porte + zip + log), inclusive em ajuste de Markdown. O {{USUARIO}}go cobrou em 2026-06-23: "a auditoria
adversarial tem que ser só quando muito necessário, não pode ser o que mais gasta tempo e token; tu
entende melhor que eu quando disparar, então tu define o critério". Este é o critério. Vale pro
CORTEX (vivo e produto). Companheiro: `ARQUITETURA.md`.

---

## A pergunta-mãe: isso vai pra TERCEIRO/PRODUÇÃO ou fica no vivo do {{USUARIO}}go?

O custo de errar é o que decide o esforço. Não o fato de "ser código" nem de "ser do CORTEX".

### FAIXA LEVE — fazer direto, sem cerimônia
Ajuste no vivo do {{USUARIO}}go que ele revê na hora e é trivial de desfazer:
- Editar regra, memória, CLAUDE.md, guia, texto, ponteiro do MEMORY.md.
- Mudança de description de skill (uma ou poucas), ajuste de conteúdo Markdown.
- Conserto pequeno e apontado.
→ **Faço e sigo.** Sem subagente, sem teste isolado, sem auditoria. No máximo um backup datado se
  for sobrescrever volume. A revisão é o próprio {{USUARIO}}go lendo o resultado.

### FAIXA MÉDIA — testar, mas sozinho (sem auditoria adversarial)
Código/hook/script que roda no vivo mas que EU consigo verificar rodando:
- Hook novo ou alterado, script Python, lógica com casos de borda.
- → **Escrevo, testo eu mesmo** (rodar com inputs reais, casos de borda, encoding, exit code,
  compile). Backup antes. **NÃO disparo auditoria adversarial** se o teste fechou e a superfície é
  pequena. Meu próprio teste rodado já é a verificação.

### FAIXA PESADA — teste isolado + porte + auditoria adversarial
Só quando o custo de errar é alto E o erro é difícil de ver só relendo:
- Vai pro PRODUTO distribuível (template/zip que o amigo instala e eu não acompanho).
- Toca o instalador, o settings, placeholder, sync — coisa que quebra silenciosa na casa do outro.
- Mudança ampla e cruzada (muitos arquivos, muitas interações, fácil introduzir regressão invisível).
→ Aí sim: backup, teste em HOME isolado quando grava em ~/.claude, e **auditoria adversarial**.

---

## O GATILHO da auditoria adversarial (o que o {{USUARIO}}go cobrou)

Auditoria adversarial = um SEGUNDO agente (≠ quem fez) tenta REPROVAR. É a ferramenta mais cara em
tempo e token. **Default é NÃO rodar.** Disparo SÓ se passar neste teste de duas portas:

**Porta 1 — o custo de errar é alto?** (pelo menos um)
- Vai pra terceiro/produção e eu não vou ver o erro acontecer.
- Toca segurança, credencial, instalador, sync, dado financeiro.
- Um bug aqui faz o {{USUARIO}}go abrir algo quebrado / mostrar pro cliente errado.

**Porta 2 — o erro é difícil de pegar só com meu próprio teste/releitura?**
- Lógica com casos de borda que eu posso não ter imaginado.
- Cruza muitos arquivos/efeitos; regressão invisível provável.
- Eu sou a parte interessada (escrevi e quero que passe) num julgamento de qualidade subjetivo.

**Passou nas DUAS portas → rodo.** Passou em uma só → meu próprio teste basta. Nenhuma → faço direto.

### NÃO disparar auditoria adversarial quando:
- É edição de conteúdo/Markdown/regra/memória (releitura minha resolve).
- A mudança é pequena, apontada, e meu teste rodado já fechou verde.
- É algo que o {{USUARIO}}go revê na hora de qualquer jeito.
- Eu já rodei uma auditoria nesta cadeia e a 2ª seria sobre superfície menor (foi o caso das
  descriptions em 23/06: a 2ª auditoria do dia rendeu pouco — 2 colisões pequenas que eu teria pego
  relendo. Lição: não encadear auditoria por reflexo).

### Quando rodar, rodar BARATO:
- 1 subagente no tier certo (Sonnet pra análise com nuance, não Opus), não um leque.
- Escopo cravado e específico ("ache bug que quebra em produção"), não "audita tudo".
- Uma rodada, não loop.

---

## Regra de ouro
Calibrar pelo CUSTO DE ERRAR, não pelo "é do CORTEX então é sério". O alvo do {{USUARIO}}go é VELOCIDADE
(tem plano máximo, o que aperta é turno e contexto, não o dinheiro do token). Cerimônia que não muda
o resultado final é desperdício de turno dele. Quando em dúvida entre leve e médio: leve. Entre médio
e pesado: médio, a não ser que as duas portas da auditoria estejam abertas.
