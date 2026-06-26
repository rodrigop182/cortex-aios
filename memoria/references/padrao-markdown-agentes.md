# Padrao de Markdown para agentes do CORTEX

Uso: sob demanda
Escopo: sistema
Gatilho: criar, editar ou refatorar `.md` do cerebro, indice, referencia ou summary
Nao usar para: conteudo de entrega ao cliente ou copy visivel de peca

Referencia para escrever `.md` como infra de contexto para agente, nao como documentacao corrida para humano.
Objetivo: maxima contextualizacao com o minimo de tokens.

## Principio central

O Markdown do CORTEX deve otimizar, nesta ordem:

1. roteamento correto
2. recuperacao rapida do bloco certo
3. leitura parcial por secao
4. baixo custo de contexto
5. legibilidade humana

## Regras praticas

- bootstrap aponta, nao despeja
- indice navega, nao ensina
- referencia resolve uma pergunta por secao
- tabela, checklist e matriz vencem prosa longa
- titulo deve ajudar busca por `rg`

## Estrutura preferida

```md
# Titulo

Uso: sob demanda
Escopo: sistema | projeto | skill
Gatilho: quando X
Nao usar para: Y

1 linha: para que serve.

## Quando usar
## Quando nao usar
## Regra
## Exemplos
## Arquivos relacionados
```

## Criterio de pronto

O padrao esta sendo seguido quando o agente acha a regra certa sem reler o arquivo inteiro.
