---
name: estrategia-retrieval-md-cortex
description: Como o CORTEX usa arquivos Markdown grandes sem ler tudo por reflexo
metadata:
  type: reference
  tags:
    - cortex
    - retrieval
    - markdown
    - contexto
---

# Estrategia de retrieval em Markdown no CORTEX

Uso: antes de criar, organizar ou consultar muitos `.md` em `memoria/`, `wiki/`, `projects/`, `references/` ou pastas quentes.

## Regra central

Markdown escala bem quando funciona como biblioteca indexada. Markdown vira custo quando cada pergunta obriga leitura integral.

O desenho certo do CORTEX e:

1. indice curto aponta a rota;
2. `rg` acha termo, data, slug, tag ou heading;
3. agente abre o menor trecho suficiente;
4. leitura integral fica como fallback consciente;
5. arquivo quente ganha resumo local.

## Como escrever um `.md` consultavel

Todo arquivo duravel deve facilitar busca futura:

- frontmatter quando o arquivo for regra, referencia, wiki ou projeto quente;
- `name` em kebab-case;
- `description` de 1 linha, pensada para decisao de relevancia;
- `metadata.type` quando fizer sentido: `reference`, `project`, `wiki`, `decision`, `feedback`;
- `tags` quando houver mais de um eixo de busca;
- headings estaveis, curtos e especificos;
- secoes pequenas, com uma ideia por bloco;
- exemplos nomeados com termos que o usuario usaria falando.

Arquivos grandes precisam de sumario no topo ou indice por headings. Se o arquivo vira fonte recorrente, criar `.cortex/SUMMARY.md` na pasta ou um `README.md` de 1 linha por arquivo.

## Como o agente deve buscar

Ordem padrao:

1. `MEMORY.md`, `README.md` ou mapa da pasta para achar a rota provavel.
2. `rg` por termos naturais, datas, cliente, projeto, slug, tag e heading.
3. Abrir o arquivo candidato pelo trecho relevante, nao a pasta inteira.
4. Ler o arquivo inteiro somente se ele for pequeno, canonico ou se o risco justificar.
5. Se o mesmo caminho voltar 3 ou mais vezes, criar ou atualizar resumo local.

Comando mental: "qual e o menor contexto que muda a proxima acao?"

## Busca em instalacao antiga

A taxonomia nova e rota preferida, nao rota unica. Em instalacao existente:

- procurar primeiro nos indices e READMEs;
- incluir aliases e pastas customizadas registradas;
- preservar pasta livre como dado do usuario;
- criar README ou SUMMARY quando uma pasta customizada virar quente;
- nunca mover arquivo antigo so para caber na taxonomia nova.

## Checklist de pronto

- A pasta tem README, SUMMARY ou indice quando ja tem muitos arquivos.
- O arquivo novo tem `description` que ajuda retrieval.
- Os headings sao pesquisaveis com palavras reais do usuario.
- `MEMORY.md` guarda ponteiro curto, nao corpo de referencia.
- Busca textual ignora artefatos pesados por padrao.

**Why:** CORTEX pode ter muitos `.md` sem obrigar o agente a ler biblioteca inteira por reflexo.

**How to apply:** ao criar base grande de Markdown, organizar pasta quente, responder pergunta de memoria ou mexer em retrieval do CORTEX.
