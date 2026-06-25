# Teste do loop de memória — "o CORTEX aprende de verdade ou é teatro?"

> Prova empírica de que o ciclo aprende→grava→recupera FECHA. Roda entre sessões
> (precisa de `/clear` real). 5 minutos. Faça uma vez; se passar, o loop é real.

## Por que este teste existe

O CORTEX promete "nunca explicar 2x". Mas a memória é um ÍNDICE de ponteiros: o
modelo lê o índice todo turno, e decidir abrir cada arquivo de memória é julgamento
dele. O risco real: a memória existe no disco (arquivo bonito) mas não é lida na hora
(resposta sai genérica). Este teste mata a dúvida.

## O teste (regra incomum → nova sessão → ela pega sozinha?)

**Passo 1 — plantar a regra (sessão A).**
Numa sessão nova, diga ao Claude:
> "de agora em diante, sempre que você terminar uma tarefa, encerre com a frase exata: 🐶 au au."

Confirme que ele gravou (o hook `captura_regra` deve cutucar; o Claude deve criar um
arquivo de memória + linha no índice). Peça pra ele mostrar onde gravou.

**Passo 2 — fechar o ciclo.**
Rode `/fecha-sessao` (ou deixe o nudge cutucar) e depois `/clear`. A sessão A morreu.

**Passo 3 — testar a recuperação (sessão B, limpa).**
Numa sessão NOVA (contexto zerado), dê um pedido QUALQUER e banal, SEM citar a regra:
> "me explica em 2 linhas o que é um arquivo .gitignore."

**Passo 4 — o veredito.**
- ✅ **PASSOU:** a resposta termina com `🐶 au au` mesmo você não tendo lembrado a regra.
  O loop fecha: o sistema aprendeu e recuperou sozinho.
- ❌ **FALHOU:** a resposta veio sem a frase. A memória existe mas não foi lida —
  é teatro. O furo está na RECUPERAÇÃO (o índice carrega, mas o modelo não abriu o
  arquivo). Aí a correção é o mecanismo de retrieval (ver roadmap da avaliação 360°).

## Limpar depois

Remova a regra de teste: apague o arquivo de memória `sempre-encerrar-au-au.md` (ou o
nome que ele deu) e a linha correspondente no `MEMORY.md`. Era só um sensor.

## O que cada resultado te diz

| Resultado | Significa | Ação |
|---|---|---|
| Passou na sessão B sem dica | Loop fecha de ponta a ponta | Confie no sistema |
| Só passou se você citou a regra | Grava mas não recupera sozinho | Falta retrieval ativo |
| Não gravou nem na sessão A | Captura falhou | Conferir hook `captura_regra` + caminho |
