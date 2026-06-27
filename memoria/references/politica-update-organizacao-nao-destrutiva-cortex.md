---
name: politica-update-organizacao-nao-destrutiva-cortex
description: Atualizacoes de organizacao do CORTEX devem ser aditivas e preservar pastas livres de usuarios existentes
metadata:
  type: reference
  tags:
    - cortex
    - update
    - template
    - compatibilidade
    - organizacao
---

# Politica de update organizacional nao destrutivo

Uso: antes de portar uma reorganizacao para o template distribuivel, mexer no `/atualizar`, criar nova taxonomia de pastas ou alterar docs de instalacao.

## Regra central

Usuario novo recebe a estrutura recomendada.

Usuario existente preserva a estrutura que ja criou.

Atualizacao de produto pode adicionar mapas, READMEs, regras de busca, aliases e ferramentas de migracao opcional. Ela nao deve mover, renomear, apagar ou esconder pastas livres do usuario.

Na duvida, caminho desconhecido e dado do usuario.

## Contrato para usuario existente

Durante update, a organizacao nova entra como camada de orientacao:

- docs novas explicam onde colocar coisas a partir de agora;
- indices ajudam o agente a encontrar o que ja existe;
- pastas novas so sao criadas quando nao colidem e quando forem parte do produto;
- migracao fisica fica opcional, com dry-run, backup e confirmacao;
- pastas customizadas continuam validas e aparecem como legado ou local customizado;
- o agente pode sugerir reorganizacao, mas nao aplica sem pedido explicito.

O update nunca transforma uma instalacao viva em instalacao nova.

## Modo legado

Uma instalacao entra em modo legado quando:

- ja tem `VERSION`, `MANIFESTO-UPDATE.md` ou memoria preenchida;
- tem pastas fora da taxonomia atual;
- tem arquivos em `projects/`, `context/`, `memory/`, `decisions/` ou `references/` que nao vieram do pacote novo;
- o usuario aponta uma pasta CORTEX existente como destino.

No modo legado:

1. nao mover nada automaticamente;
2. dry-run deve listar "pastas customizadas preservadas";
3. docs novas entram sem apagar mapas antigos;
4. agente usa busca por indices e `rg`, incluindo pastas customizadas;
5. se a reorganizacao for util, oferecer plano opcional em lote separado.

## Migracao fisica opcional

Reorganizacao fisica so pode acontecer em comando separado do update comum.

Requisitos:

- dry-run mostrando origem e destino de cada item;
- backup antes;
- manifesto de movimentacao;
- confirmacao explicita do usuario;
- teste depois em hooks, skills, MEMORY, paths e busca;
- plano de rollback.

Sem esses itens, a melhoria fica em docs, indices e regras de criacao futura.

## Implicacao para o template

O template deve separar:

- `instalar`: cria a estrutura recomendada para usuario novo;
- `atualizar`: troca produto e preserva estrutura existente;
- `organizar`: fluxo opcional e assistido para quem quiser migrar pastas antigas.

`MANIFESTO-UPDATE.md` deve dizer explicitamente que caminhos desconhecidos e pastas livres sao preservados.

## Checklist de pronto

- O dry-run mostra o que escreve, remove e preserva.
- Pastas desconhecidas aparecem como preservadas, nao como erro.
- A taxonomia nova esta em docs e indices, nao aplicada por forca.
- Usuario antigo consegue continuar usando a pasta como antes.
- Usuario novo entende o caminho recomendado.
- Qualquer migracao fisica e opcional, separada e reversivel.

**Why:** usuarios existentes ja criam pastas livremente dentro do CORTEX; update de produto nao pode atrapalhar uma instalacao viva.

**How to apply:** ao portar organizacao para o distribuivel, atualizar docs, manifesto e script de update com vies de preservacao.
