# Demo em 5 minutos

Objetivo: provar que o CORTEX transforma um agente genérico em um operador com memória, método e
padrão de qualidade.

## Antes de começar

Você precisa ter:

- CORTEX instalado;
- VSCode, terminal ou desktop app com agente de IA aberto na pasta do CORTEX;
- onboarding concluído com `/onboard`.

Se ainda não instalou, comece por `COMECE-AQUI.txt`.

## O teste

Cole este pedido no seu agente:

```text
Tenho várias ideias e projetos soltos. Olhe meu CORTEX, entenda meu contexto e me diga qual é o próximo passo mais importante. Não me dê uma lista genérica: quero uma recomendação com motivo, risco e primeira ação concreta.
```

## O que uma boa resposta deve mostrar

- Usa seu perfil e suas prioridades, não conselhos genéricos.
- Cita arquivos ou áreas do CORTEX que sustentam a recomendação.
- Faz uma recomendação principal, com motivo e trade-off.
- Aponta a primeira ação concreta.
- Pergunta só o que realmente bloqueia.

## Segundo teste: memória que evita repetição

Corrija a resposta com uma regra clara:

```text
Regra: quando eu pedir prioridade, sempre separe caixa agora de produto próprio, e recomende uma ação que aproxime os dois quando possível.
```

Depois, em uma nova conversa, peça:

```text
Qual é minha prioridade desta semana?
```

O efeito esperado: o agente usa a nova regra sem você explicar de novo.

## Terceiro teste: auditoria do sistema

Rode:

```text
/audit
```

O efeito esperado: o CORTEX mostra a saúde do sistema pelos princípios de contexto, memória, regras,
capacidades, aprendizado e transparência. Se houver métrica de 1-shot, ela aparece como prova de
redução de retrabalho.

## Por que isso impressiona

Um prompt manual responde bem uma vez. O CORTEX melhora o ambiente inteiro: contexto, memória,
roteamento, segurança, atualização e aprendizado entre sessões.

## Se a demo falhar

- Rode `/onboard` de novo e preencha melhor seu perfil.
- Abra o projeto sempre na mesma pasta CORTEX.
- Rode `/audit` e corrija o maior buraco estrutural.
- Verifique `TROUBLESHOOTING.md`.
