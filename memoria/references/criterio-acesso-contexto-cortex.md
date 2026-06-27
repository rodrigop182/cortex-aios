# Criterio de acesso ao contexto do CORTEX

Uso: antes de abrir arquivos grandes, navegar a pasta CORTEX, mexer em retrieval ou responder sobre memoria/contexto
Escopo: sistema
Gatilho: "quando acessar contexto", "pasta CORTEX", "custo de token pra abrir arquivo", "mandei @arquivo", "biblioteca roteavel"
Nao usar para: tarefa simples com arquivo ja apontado e pequeno

## Regra central

A pasta CORTEX e a biblioteca viva da operacao. No template, ela e a raiz instalada pelo usuario, por padrao `C:\CORTEX` ou a pasta escolhida no setup.

Essa raiz agregadora deve ser facil de acessar, mas nao deve ser injetada por garantia.

O criterio correto e: acessar o menor contexto que muda a proxima acao.

## Escopo indexavel

Por padrao, o CORTEX indexa e consulta texto e codigo:

- markdown, txt, csv, json, yaml, toml;
- codigo e scripts;
- fichas, summaries, decisions, references, wiki, projects, scripts e codigo dentro da raiz agregadora.

Midia e arquivos pesados ficam fora do caminho automatico:

- video, audio, imagem, PSD, ZIP, binarios, exports e renders;
- so consultar quando o usuario apontar o arquivo ou a tarefa exigir, como transcrever video, otimizar imagem ou revisar asset;
- nesses casos, usar ferramenta especifica e nao transformar o arquivo pesado em contexto bruto.

## Escada de acesso

| Nivel | Acao | Quando usar | Custo esperado |
| --- | --- | --- | --- |
| 0 | Nao acessar | pedido generico, resposta simples, tarefa que nao depende de memoria local | zero |
| 1 | Usar ponteiro | retrieval achou arquivo provavel, mas a resposta ainda pode seguir sem detalhe | baixo |
| 2 | Buscar com `rg` | nao sei qual arquivo governa, ou o tema pode estar em varias pastas | baixo a medio |
| 3 | Ler secao ou cabeca | arquivo medio/grande, preciso confirmar regra, status ou fonte | medio controlado |
| 4 | Ler arquivo inteiro | arquivo pequeno ou fonte canônica indispensavel para nao errar | medio a alto |
| 5 | Criar summary | mesmo arquivo/projeto voltou 3+ vezes ou esta virando frente quente | investimento |

## Quando vale abrir contexto

Abrir contexto quando pelo menos um for verdadeiro:

- o usuario aponta `@arquivo`, caminho, cliente, projeto ou frente;
- existe risco de identidade vazar entre projetos;
- a resposta depende de decisao anterior, regra duravel, ficha de cliente ou estado local;
- a tarefa pede continuidade: "retoma", "como combinamos", "o que falta", "estado";
- o custo de errar e maior que o custo de ler;
- a leitura vai reduzir perguntas ou retrabalho na mesma janela.

## Quando nao vale abrir

Nao abrir contexto quando:

- a resposta e conceitual e nao depende do historico do operador;
- o pedido e mecanico e o arquivo alvo ja esta aberto ou claro;
- a memoria so daria "mais seguranca" sem mudar a acao;
- o arquivo provavel e grande e a pergunta pode ser respondida com busca pontual;
- o prompt e de baixa consequencia e uma suposicao reversivel resolve.

## Orcamento por area util

Area util inicial da operacao: 250k tokens por janela antes de handoff, salvo medicao local diferente.

Regra pratica:

- contexto automatico precisa ser minimo;
- retrieval injeta ponteiro, nao conteudo;
- leitura grande precisa ter motivo explicito;
- se a janela ja esta longa, preferir handoff ou summary curto a abrir mais doutrina;
- o custo deve ser pago pela tarefa que se beneficia dele, nao por todo turno.

## Roteamento das pastas

| Pergunta | Primeiro lugar |
| --- | --- |
| "Como devo agir?" | `memory/MEMORY.md` e regras curtas |
| "Qual doutrina governa?" | `references/` |
| "O que aconteceu/foi aprendido?" | `wiki/`, quando existir |
| "Qual estado do projeto?" | `projects/` ou ficha do cliente |
| "Por que decidimos isso?" | `decisions/log.md` |
| "Como o CORTEX funciona?" | `references/ARQUITETURA.md` |
| "Qual arquivo exato?" | `rg` na raiz CORTEX, filtrando texto/codigo, depois leitura pequena |
| "Qual midia usar/transcrever/otimizar?" | caminho apontado pelo usuario + ferramenta especifica |

## Uso de internet

Se a fonte local nao cobrir o criterio, padrao, biblioteca, API ou benchmark atual, buscar fonte externa atualizada. A internet complementa o CORTEX, nao substitui a memoria local. Para assunto instavel ou tecnico atual, verificar fonte oficial/primaria antes de cravar.

## Se o usuario mandou `@arquivo`

Ler antes de produzir quando:

- o arquivo e fonte do pedido;
- o usuario pediu para usar aquele arquivo;
- o arquivo define restricao, identidade, briefing ou criterio.

Se o arquivo for grande:

1. ler cabeca/sumario primeiro, quando existir;
2. buscar termos do pedido dentro dele;
3. ler so a secao relevante;
4. ler inteiro apenas se for fonte canônica e o risco justificar.

## Criterio de pronto

O acesso ao CORTEX esta correto quando:

- o agente encontra o arquivo certo sem despejar pasta inteira no contexto;
- prompt comum nao puxa doutrina pesada;
- prompt de memoria/contexto puxa esta regra ou a politica de contexto;
- leitura grande vira decisao consciente;
- arquivos quentes ganham summary para a proxima janela.
