# Brief do subagente CONSOLIDADOR (tier-2)

Um unico subagente, depois que TODOS os extratores devolveram. Dedupa e organiza os achados
num documento de sintese enxuto. Ele tambem so LE e PROPOE: nao escreve em memoria.

---

Voce recebe N blocos de achados (saida dos extratores, cada um cobrindo um lote cronologico de
sessoes) MAIS uma copia da memoria JA existente do operador (o MEMORY.md e os arquivos que ele
apontar). Sua tarefa: fundir tudo num so documento `SINTESE.md`, enxuto, sem repeticao.

## Regras de fusao

1. **Dedup.** Mesmo achado em varios lotes vira UM bullet. Some o sinal ("apareceu em 5 lotes")
   se for util pra curadoria pesar.
2. **Recente vence antigo.** Se dois lotes se contradizem, a versao do lote MAIS RECENTE
   (cronologico) prevalece; anote a antiga como "(superado em [lote recente])". A curva de
   maturidade existe pra isso.
3. **Cruzar com a memoria existente.** Para cada achado, marcar:
   - `[JA EXISTE]` se ja ha memoria que cobre -> a curadoria vai ATUALIZAR, nao criar.
   - `[NOVO]` se nao ha nada parecido.
   - `[CONTRADIZ: <arquivo>]` se contraria uma memoria atual -> a curadoria decide.
4. **Sem dado sensivel.** Reconferir: nenhuma cifra, credencial ou segredo entrou. Bloco
   `<private>` nao existe.

## Estrutura do SINTESE.md

```
# SINTESE — catch-up [datas] (gerado em [data])
> [N] sessoes, [M] lotes. ZERO dado sensivel.

## 1. Voz do operador
[vocabulario/tom dedupado + 10-15 verbatim representativos]

## 2. Curva inexperiente -> maduro
[erros que ja venceram vs jeito atual; o que NAO repetir]

## 3. Fatos sobre o operador
[bullets, cada um marcado JA EXISTE / NOVO / CONTRADIZ]

## 4. Preferencias de processo
[bullets, cada um marcado JA EXISTE / NOVO / CONTRADIZ]

## 5. Candidatos a regra (pra curadoria decidir)
[os achados que parecem merecer virar/atualizar memoria, ja roteados:
 - procedural (conserta uma skill) vs semantico (vira memoria)
 - atualizar memoria X vs criar arquivo novo]
```

Mantenha curto. A sintese e insumo de DECISAO, nao o produto final. A curadoria (tier-1) le isto
e decide o que grava.
