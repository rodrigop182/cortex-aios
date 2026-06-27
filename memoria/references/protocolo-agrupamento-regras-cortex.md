---
name: protocolo-agrupamento-regras-cortex
description: Como regras novas sao classificadas, agrupadas e fundidas ao longo do tempo sem inflar o indice
metadata:
  type: reference
  tags:
    - cortex
    - regras
    - memoria
    - consolidacao
    - context-engineering
---

# Protocolo de agrupamento de regras do CORTEX

Uso: antes de gravar regra nova, consolidar `MEMORY.md`, processar `_fila-regras.md`, destilar sessao ou desenhar automacao de captura.

## Regra central

Regra nova nao deve virar arquivo solto por reflexo.

Ela primeiro vira um sinal classificado. Depois entra em uma familia existente, cria familia nova ou atualiza uma skill/ficha. O indice cresce por familias, nao por cada frase aprendida.

Classificacao nao e retrieval amplo.

Palavras como `sempre`, `nunca` e `quando` ajudam a organizar e auditar regras, mas nao autorizam o agente a carregar todas as regras que usam a mesma palavra. Na hora de responder um pedido, o agente busca por dominio, gatilho especifico e arquivo-familia provavel. O operador verbal so refina a faixa lida depois que o dominio ja foi escolhido.

## Padroes verbais

Classificar operadores como sinal de logica:

- `sempre`, `obrigatorio`: P1 obrigacao;
- `nunca`, `proibido`, `nao pode`: P0 bloqueio;
- `antes de`: preflight;
- `quando`, `ao`, `se`: gatilho condicional;
- `depois de`: postflight;
- `preferir`, `default`: preferencia;
- `salvo`, `exceto`: excecao;
- `na duvida`: criterio de desempate.

## Dois eixos obrigatorios

Toda regra capturada recebe:

1. **Dominio:** onde ela governa, como seguranca, git, memoria, update, design, copy, cliente, skill ou comportamento universal.
2. **Operador:** como ela governa, como bloqueio, obrigacao, preflight, condicional, postflight, preferencia ou excecao.

## Registro minimo

```yaml
slug: regra-curta
dominio: memoria-contexto
operador: sempre
forca: P1
gatilho: quando surgir aprendizado duravel
acao: agrupar no arquivo-topico antes de criar entrada solta
excecao: se for dado de cliente, fica na ficha do cliente
evidencia: frase ou situacao que originou a regra
status: candidata | ativa | fundida | substituida | arquivada
alvo: vivo | distribuivel | ambos | nao-portar
```

Sem gatilho, acao e excecao, a regra ainda e rascunho.

## Fluxo

1. Capturar bruto: frase, origem e evidencia curta.
2. Normalizar: `gatilho -> acao -> excecao`.
3. Classificar: dominio, operador, forca e alvo.
4. Deduplicar: buscar regra parecida por slug, dominio, operador e palavras do gatilho.
5. Fundir: atualizar arquivo-familia ou destino local.
6. Promover: dar peso maior se P0/P1, erro repetido ou regra universal.

## Retrieval por faixas, nao por palavra comum

Ao usar regras agrupadas numa tarefa real:

1. Escolher o dominio primeiro.
2. Ler indice ou cabeca do arquivo-familia.
3. Buscar dentro do arquivo por termos do pedido, objeto, caminho, cliente, ferramenta e gatilho especifico.
4. Usar operador (`sempre`, `nunca`, `antes de`) apenas para achar a subsecao certa.
5. Abrir a menor faixa: heading, regra candidata e excecoes imediatas.
6. Escalar para regras vizinhas ou arquivo inteiro so se houver conflito ou risco real.

Exemplo: o pedido "atualiza sem quebrar CORTEX antigo" nao busca `sempre` global. Ele vai para `update-template`, abre a politica de update, busca `instalacao existente`, `pasta livre`, `migracao fisica` e so le esses blocos.

## Estrutura de arquivo-familia

```md
# Regras de <familia>

Uso:
Gatilhos:
Nao usar para:

## P0, nunca
## P1, sempre
## Antes de agir
## Quando acontecer X
## Defaults e preferencias
## Excecoes
## Regras fundidas
## Evidencias curtas
```

## Gatilhos de consolidacao

Consolidar quando:

- uma familia no indice passa de 8 ponteiros;
- existem 3 regras com mesmo dominio e operador;
- existem 2 regras que comecam com o mesmo padrao verbal;
- o usuario diz que ja pediu isso antes;
- o agente encontra regra solta na raiz de `memoria/`;
- `MEMORY.md` cresce com entradas individuais que poderiam ser topico.

## Criterio de pronto

- Regra nova encontra familia antes de criar arquivo.
- `MEMORY.md` aponta para familias, nao para cada microcorrecao.
- `rg "sempre|nunca|antes de|quando"` ajuda a auditar operadores, nao a carregar contexto de tarefa.
- Regra P0/P1 tem gatilho, acao e excecao.
- Agente abre faixas especificas do arquivo-familia ate chegar no contexto necessario.
- Regra velha fundida continua recuperavel.

**Why:** regras recorrentes usam padroes verbais e devem se agrupar por classificacao em vez de virarem memoria solta.

**How to apply:** toda captura de regra, destilacao, consolidacao de `MEMORY.md` e melhoria distribuivel deve passar por dominio + operador + dedup.
