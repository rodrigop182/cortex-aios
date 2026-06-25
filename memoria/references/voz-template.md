---
name: voz-template
description: Sinais de voz do operador — como ele sinaliza correção, aprovação e execução. Populado no /onboard e refinado com o tempo.
---

# Voz do operador — sinais que o sistema reconhece

Preenchido no /onboard. Refinado automaticamente pelo /destilar-sessoes conforme o sistema
aprende com as sessões reais.

## Registro conversacional

{{VOZ_DESCRICAO}}
Ex: direto, minúsculas, abrevia, encadeia ideias com vírgula — ou formal, pontuado, detalhado.

## Sinais universais (valem pra qualquer operador)

### Correção / feedback negativo
- CAPS em palavra isolada — urgência ou frustração. Ex: `ERRADO`, `NAO`
- "como assim" / "por que você fez X" — questionamento pós-erro; não quer explicação, quer correção
- Repetir o mesmo pedido pela segunda vez — o anterior não foi atendido direito

### Aprovação
- Monossilábico ("sim", "ok", "isso") + próximo pedido direto — aprovação tácita, pode seguir
- Ausência de objeção + novo pedido — aprovado, continua
- Elogio em CAPS ("MUITO BOM", "PERFEITO") — acertou algo, guardar o que fez

### Execução (imperativo direto)
- Verbo no imperativo sem contexto: "faz", "vai", "resolve", "instala" — executa, não pergunta
- "sim" em resposta a proposta — go, aplica
- Escopo por negação: define o que NÃO pode, não o que deve — respeitar o limite, decidir o resto

### Dúvida / co-criação
- "né?" / "faz sentido?" / "você acha?" — quer opinião, não execução
- "sei lá" / "tipo" no meio — pensando em voz alta, quer que eu preencha
- "aqui comigo" — quer co-criar, não receber monólogo

## Sinais específicos do operador

{{SINAIS_ESPECIFICOS}}
Ex: "po" no final = impaciência; "uê" = estranheza; ditado por voz = abreviações fonéticas.
Preencher conforme o operador for revelando o próprio padrão.

## Regras editoriais

{{REGRAS_EDITORIAIS}}
Ex: PT-BR, sem em-dash, sem clichê de IA. Ou: inglês, conciso, bullet points.

## Como o sistema aprende

O /destilar-sessoes extrai sinais de correção e aprovação das sessões reais e refina este
arquivo automaticamente. Quanto mais sessões, mais afinado fica o reconhecimento.
