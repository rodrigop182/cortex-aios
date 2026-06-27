# Context-engineering do CORTEX

Uso: sob demanda
Escopo: sistema
Gatilho: "regras globais", "prioridade n1", "indice global", "context-engineering", "como carregar contexto"
Nao usar para: tarefa de cliente sem mudanca na arquitetura de contexto

## Regra central

Contexto prioritario nao e contexto grande. Prioridade N1 e a regra estar na camada certa, com peso certo e gatilho certo.

O CORTEX deve carregar sempre so o que governa sempre. O que governa as vezes fica em referencia com ponteiro. O que depende do jeito de falar do usuario entra como alias de retrieval.

O orcamento base e a area util configurada para a operacao, com padrao inicial de 250k tokens por janela. Tudo que entra automaticamente precisa se justificar contra esse teto pratico, mesmo quando o modelo aceita contexto tecnico maior.

## Camadas

| Camada | Funcao | O que entra | O que nao entra |
| --- | --- | --- | --- |
| P0 bootstrap | trava absoluta | seguranca, kill switch, identidade nao vazar, irreversivel pede OK | teoria, historico, exemplos longos |
| P1 bootstrap | padrao ativo | comportamento que deve disparar sozinho em turnos relevantes | detalhe operacional extenso |
| P2 ponteiro | referencia sob demanda | politica, criterio, metodologia, checklist | copia do conteudo pesado |
| Indice | navegacao | 1 linha por item | explicacao, excecao, lista grande |
| Retrieval | gatilho natural | aliases do usuario para o arquivo certo | conteudo do arquivo |
| Summary | continuidade local | estado quente de projeto/arquivo | doutrina global |

## Como decidir se algo entra no global

Uma regra entra no bootstrap se passar em pelo menos um criterio:

- bloqueia dano irreversivel;
- muda comportamento de toda tarefa relevante;
- evita erro recorrente ja observado;
- escolhe qual arquivo/agente/skill deve ser acionado;
- e curta o bastante para caber em 1 linha com ponteiro.

Se precisa de explicacao, exemplos ou excecoes, a explicacao vai para `references/`. O bootstrap fica com a regra curta e o caminho.

## Prioridade N1

Prioridade N1 nao significa "colocar tudo no global". Significa:

1. P0/P1 curto no bootstrap.
2. Ponteiro para a fonte detalhada.
3. Alias de fala natural no retrieval, se o usuario costuma pedir com outro vocabulario.
4. Teste com prompt positivo e negativo.
5. Registro em decision log quando muda governanca.

Sem esses cinco itens, a regra pode existir no disco, mas ainda nao governa bem.

## Criterio de compressao

- P0/P1: so regra que precisa governar o turno antes de qualquer ferramenta.
- P2: ponteiro para arquivo certo, sem carregar conteudo.
- P3: busca ou leitura deliberada quando a tarefa real pedir.
- Se uma informacao nao melhora a proxima acao dentro da area util configurada, ela nao entra automaticamente.

Detalhe operacional de quando abrir, buscar ou ignorar arquivos do CORTEX: `references/criterio-acesso-contexto-cortex.md`.

## Criterio de pronto

Uma mudanca de contexto esta pronta quando:

- o boot segue curto;
- a regra tem peso P0/P1/P2 claro;
- o arquivo detalhado existe;
- o retrieval acha pelo jeito real do usuario;
- o template recebeu so o mecanismo generico;
- a proxima sessao exige menos explicacao.
