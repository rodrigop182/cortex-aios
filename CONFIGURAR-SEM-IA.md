# Configurar sem IA - CORTEX OS

Use este guia se você instalou o CORTEX e quer preencher o perfil manualmente, sem rodar `/onboard`.

O objetivo é sair do zero com o mínimo necessário para o agente reconhecer quem você é, como você
trabalha e qual foco deve respeitar.

## Onde mexer

Abra sempre a pasta CORTEX no VSCode.

Arquivos mínimos:

- `intake.md`;
- `context/sobre-mim.md`;
- `context/sobre-operacao.md`;
- `context/prioridades.md`.

Arquivos úteis depois:

- `connections.md`;
- `references/voz.md`;
- `projects/README.md`;
- `decisions/log.md`.

## Passo 1 - Preencha o intake

Abra `intake.md` e responda as 7 perguntas.

Use frases simples. Não tente escrever bonito. Quanto mais concreto, melhor.

Preencha principalmente:

- quem você é e o que entrega;
- 1 ou 2 textos reais seus;
- prioridades dos próximos 90 dias;
- como seu trabalho gera resultado;
- onde estão seus arquivos;
- tarefa repetitiva que mais toma tempo.

## Passo 2 - Preencha o perfil compacto

Abra `context/sobre-mim.md`.

Troque o placeholder por um texto curto neste formato:

```text
Sou [nome], trabalho com [área] e entrego [tipo de entrega] para [tipo de público].
Meu ponto forte é [ponto forte].
Minha dor principal hoje é [dor].
Quero que o CORTEX me ajude principalmente com [objetivo].
```

## Passo 3 - Preencha a operação

Abra `context/sobre-operacao.md`.

Use este formato:

```text
Meu trabalho hoje funciona assim:
- Entrada de demanda: [onde chegam pedidos]
- Entrega principal: [o que eu produzo]
- Ferramentas: [apps e pastas principais]
- Gargalo: [onde trava]
- Rotina: [como uma semana típica funciona]
```

## Passo 4 - Preencha as prioridades

Abra `context/prioridades.md`.

Escreva 2 ou 3 prioridades reais dos próximos 90 dias.

Boa prioridade:

- tem entrega observável;
- cabe em 90 dias;
- ajuda a decidir o que ignorar.

Exemplo:

```text
- Publicar uma primeira versão do portfólio.
- Fechar dois projetos com escopo claro.
- Transformar um serviço repetido em produto simples.
```

## Passo 5 - Diga onde estão as coisas

Abra `connections.md`.

Registre só ponteiros, sem senha:

- pasta principal de trabalho;
- Drive ou nuvem usada;
- ferramenta de tarefas;
- canais de comunicação;
- repositórios ou pastas de projeto.

Nunca coloque senha, token, extrato ou chave de API.

## Passo 6 - Crie o primeiro projeto

Dentro de `projects/`, crie uma pasta para um projeto real.

Exemplo:

```text
projects/meu-produto/README.md
```

Conteúdo mínimo:

```markdown
# Meu produto

## Objetivo
[o que este projeto precisa virar]

## Estado atual
[o que já existe]

## Próximo gate
[a próxima prova objetiva]
```

## Passo 7 - Teste

Abra o Claude Code na pasta CORTEX e pergunte:

```text
Leia meu contexto e me diga qual deve ser meu foco desta semana. Se faltar algo importante, pergunte só o essencial.
```

Se a resposta usar seus arquivos de contexto, está funcionando.

Se a resposta vier genérica, confira:

- VSCode está aberto na pasta CORTEX certa;
- `context/sobre-mim.md` não está vazio;
- `context/prioridades.md` tem prioridades reais;
- `.claude/skills/onboard/SKILL.md` existe na pasta CORTEX.

## Quando rodar o onboard depois

Você pode rodar `/onboard` mais tarde para refinar.

Antes disso, este guia já deixa o CORTEX utilizável.
