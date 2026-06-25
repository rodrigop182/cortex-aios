---
name: regras
description: Lista, explica, liga e desliga as regras base do CORTEX OS. Use quando o operador disser "quais são as regras", "mostra as regras", "lista o que você segue", "desliga a regra X", "não quero que você faça Y", "remove essa regra", "ativa de novo a regra", ou "/regras". Nunca remove regra sem o operador entender o que ela faz.
---

## O que esta skill faz

Dá ao operador controle visível e reversível sobre as **regras base** do CORTEX (o bloco
`=== REGRAS BASE ===` no `CLAUDE.md` global). Ele pode listar, entender e ligar/desligar
qualquer regra — mas a skill garante que ele **conheça** a regra antes de removê-la.

É a materialização do princípio 6 (transparência sobre autonomia): nada do que governa o
comportamento do sistema fica escondido ou imutável no escuro.

## Princípio inegociável

**Conhecer antes de remover.** Se o operador pedir pra desligar uma regra que ele claramente
não leu, mostre o que ela faz e o efeito de desligá-la ANTES de aplicar. Confirmação explícita
antes de qualquer edição no `CLAUDE.md`.

A regra "Cérebro fino" (fora do bloco de regras base) **não é removível** — é o que mantém o
sistema funcionando. Se pedirem pra tirar, explique o porquê e recuse com gentileza.

## Onde as regras moram

- O **núcleo** (`~/.claude/CLAUDE.md`) tem só o resumo das regras críticas sempre ativas. As 15
  regras DETALHADAS, com IDs `[R1]..[R15]`, moram em `references/regras-completas.md` (lido sob
  demanda). Pra explicar/listar uma regra, leia esse arquivo. Pra LIGAR/DESLIGAR, edite lá (e, se
  for uma das que também vivem no núcleo, ajuste o resumo do núcleo junto).
- Uma regra **desligada** não é apagada: vira um comentário marcado, pra poder religar.
  Formato de regra desligada:
  ```
  <!-- [R4] DESLIGADA por {{NOME}} em {data}: motivo {motivo} -->
  <!-- texto original da regra preservado aqui -->
  ```
- Uma regra **desligada** não é apagada: vira um comentário marcado, pra poder religar.
  Formato de regra desligada:
  ```
  <!-- [R4] DESLIGADA por {{NOME}} em {data} — motivo: {motivo} -->
  <!-- texto original da regra preservado aqui -->
  ```

## Execução

### "Quais são as regras?" / "/regras" (listar)

Leia o bloco de regras base do `CLAUDE.md`. Imprima uma tabela curta:

```
Regras base do seu CORTEX (use /regras desligar R4 pra mexer):

✅ [R1] Conselho, não autoridade — eu sugiro, você decide.
✅ [R2] Radar de processo — ofereço atalho quando vejo trabalho repetitivo.
✅ [R3] Planejar, delegar, verificar — plano antes, teste depois.
✅ [R4] Mudança cirúrgica — mexo só no pedido, nada de brinde.
... (todas)
⛔ [R7] DESLIGADA — aprender e não repetir (desligada em {data})

Pra entender qualquer uma: "/regras explica R3".
Pra desligar/religar: "/regras desligar R4" ou "/regras ligar R7".
```

Use ✅ pra ativa, ⛔ pra desligada.

### "Explica a regra R3" (entender)

Mostre o texto completo da regra + o que muda no seu comportamento quando ela está ligada vs.
desligada. Uma frase de cada. Sem enrolar.

### "Desliga a regra R4" (remover)

1. Se houver sinal de que ele não leu a regra, mostre o que ela faz primeiro.
2. Diga o efeito concreto de desligar: *"Sem a R4 eu posso retocar coisas adjacentes ao que
   você pediu sem avisar. Tem certeza?"*
3. Com confirmação, edite o `CLAUDE.md`: comente a regra no formato de "regra desligada"
   acima, com data e motivo (pergunte o motivo em uma linha; opcional).
4. Registre em `decisions/log.md`: "Desligou [R4] em {data} — motivo: {motivo}".
5. Confirme em uma linha.

### "Liga de novo a R7" (religar)

Descomente a regra, remova o marcador de desligada, registre no log, confirme.

### "Cria uma regra nova" (adicionar)

O operador pode adicionar uma regra própria. Pegue o texto, dê o próximo ID livre, insira no
bloco de regras base no formato `**[Rn] Título.** texto`. Registre no log. Lembre que regra
nova engorda o cérebro fino — se for conhecimento e não comportamento, sugira `references/`.

## Regras de implementação

1. **Nunca edita o `CLAUDE.md` sem confirmação explícita.**
2. **Desligar = comentar, não apagar.** Sempre reversível.
3. **Toda mudança vai pro `decisions/log.md`** (transparência).
4. **A regra "Cérebro fino" não é removível.** Explique e recuse.
5. **{{IDIOMA}}, padrões editoriais da casa** em todo texto gerado.
