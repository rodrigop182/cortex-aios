# Politica de contexto, memoria e compactacao

Uso: sob demanda
Escopo: sistema
Gatilho: contexto pesado, memoria grande, link sem gatilho, compactacao automatica, jeito que o usuario fala
Nao usar para: tarefa sem relacao com contexto, memoria, hook ou retrieval

## Regra mae

O CORTEX nao tenta carregar tudo. Ele opera em quatro camadas:

1. boot minimo;
2. gatilho pela fala real do usuario;
3. ponteiro pequeno para o arquivo certo;
4. leitura sob demanda so quando a tarefa pedir.

Se uma informacao existe, mas nao tem gatilho no jeito que o usuario fala, ela ainda nao esta pronta.

## Personalizacao

O template distribuivel leva o mecanismo, nao o jeito de fala de quem criou o template.

| Camada | O que entra |
| --- | --- |
| Template | exemplos genericos, placeholders e checklist de teste |
| CORTEX instalado | aliases reais do usuario, descobertos no uso e no onboarding |
| Nunca portar | cliente, giria, caminho local ou preferencia pessoal de outro usuario |

O criterio pratico para abrir, buscar ou ignorar arquivos fica em `references/criterio-acesso-contexto-cortex.md`.

## Politica de boot

- `SessionStart` nao injeta contexto comum.
- Excecao: alerta urgente e acionavel, como conflito de sync ou bloqueio de seguranca.
- Handoff existente, referencia nova e tamanho de memoria sao informacoes consultaveis, nao contexto de todo turno.
- `UserPromptSubmit` pode injetar no maximo 1 ponteiro pequeno por tema, nunca conteudo pesado.

## Orcamento util de contexto

- Criterio inicial do CORTEX: area util de 250k tokens por janela antes de handoff.
- Se o operador medir outro limite saudavel para seu plano/modelo, ajustar este numero e o alerta.
- O limite tecnico maior do modelo nao e meta de uso operacional.
- Todo custo fixo deve ser proporcional a area util, nao ao teto tecnico.
- Conteudo grande so entra por leitura deliberada, com arquivo certo e motivo claro.

## Politica do MEMORY.md

- Meta operacional: ficar entre 12KB e 16KB.
- Alerta de produto: 18KB.
- Reparar antes de continuar crescendo: 20KB.
- O limite tecnico de cerca de 24.4KB e emergencia, nao meta.
- Entrada nova no indice: 1 linha ou consolidacao em familia existente.
- Regra procedural de skill vai para o `SKILL.md`, nao para o `MEMORY.md`.

## Politica de compactacao

- `autoCompactEnabled` fica desligado por padrao quando a superficie permitir.
- Primeiro alerta de contexto longo: 220k tokens, deixando margem antes da area util de 250k.
- O caminho preferido para sessao longa e `/handoff` + sessao nova.
- `/compact` e recurso manual ou ultimo recurso.
- `PreCompact` existe so como cinto de seguranca.

## Criterio de pronto

- frase natural do usuario puxa o ponteiro certo;
- boot nao carrega lista de handoff, memoria, referencia ou status;
- `MEMORY.md` fica abaixo de 16KB sem perder arquivo duravel;
- compactacao vira excecao controlada.
