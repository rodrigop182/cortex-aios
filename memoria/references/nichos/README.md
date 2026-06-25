# Pacotes de nicho — a variável de upgrade do CORTEX

O CORTEX é genérico de fábrica. O **pacote de nicho** é o que o sintoniza na SUA área: regras
extras, vocabulário, atalhos e skills sugeridas que só fazem sentido pro seu trabalho.

## Como funciona

1. No `/onboard`, você diz seu nicho (ou diga "ativa meu nicho" a qualquer momento).
2. O sistema cria/copia `references/nicho-{seu-nicho}.md` a partir de um dos exemplos aqui
   (ou monta um do zero entrevistando você).
3. O `CLAUDE.md` ganha a variável `{{NICHO}}` preenchida e um ponteiro pro arquivo. O cérebro
   continua fino: o pacote é lido **sob demanda**, não todo turno.

## Nichos de exemplo já prontos (copie e ajuste)

- `nicho-dev.md` — desenvolvimento de software
- `nicho-marketing.md` — marketing / conteúdo / growth
- `nicho-escrita.md` — escrita / redação / copy
- `nicho-design.md` — design / criação visual
- `nicho-vendas.md` — vendas / comercial / prospecção
- `nicho-operacoes.md` — gestão / operações / processos

Não achou o seu? Diga "monta o pacote do meu nicho" e o `/onboard` entrevista e cria.

## Anatomia de um pacote de nicho

Todo pacote segue o mesmo molde (veja qualquer exemplo):

```
# Nicho: {nome}

## Vocabulário e contexto
(termos da área que eu devo entender sem você explicar)

## Regras extras deste nicho
(o que fazer e o que NUNCA fazer, específico da área — viram regras [N1], [N2]...)

## Atalhos e fluxos típicos
(as tarefas recorrentes da área e como eu ajudo em cada)

## Skills sugeridas pra instalar
(quais skills do ecossistema fazem sentido pra este nicho)

## Armadilhas conhecidas
(erros comuns da área que eu devo evitar)
```

As regras de nicho (`[N1]`, `[N2]`...) também são gerenciáveis com `/regras` — você liga e
desliga como as regras base.
