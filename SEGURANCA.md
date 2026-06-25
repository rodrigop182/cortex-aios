# Segurança e privacidade do CORTEX

O CORTEX é markdown no seu PC. Sem servidor, sem nuvem, sem telemetria: seu contexto não sai da
sua máquina, a não ser que VOCÊ sincronize (e aí, só em repo privado). Mesmo assim, há regras pra
não vazar dado sensível.

## REGRA ESTRITA (inviolável)

**Chave de API, senha, token, credencial e DADO FINANCEIRO vivem SÓ no seu PC. NUNCA vão pra
memória, pro repositório de sync, nem pra lugar nenhum fora da sua máquina.** Não há exceção. Na
dúvida, o CORTEX NÃO sobe. Isso é garantido por defesa em camadas:

1. **O CORTEX (comportamento):** nunca grava segredo na memória, nunca sugere versionar segredo.
2. **`.gitignore` (em `memoria/` e na raiz):** barra por NOME de arquivo (`.env`, `*credential*`,
   `*token*`, `*.key`, `*financeiro*`, `*extrato*`, etc.) antes de qualquer commit. Esta é a trava
   forte e automática: arquivo com esses nomes nunca entra no git.
3. **Hook `sync_push.py` (trava final, por CONTEÚDO):** antes de cada push, varre os arquivos que
   subiriam por padrões reais de segredo (API key, `AKIA…`, `ghp_…`, `sk-…`, `BEGIN PRIVATE KEY`,
   `password=`, cartão de 16 dígitos, marcadores de conta/agência) E por qualquer `<private>` que
   tenha sobrado. Achou um? ABORTA o push inteiro e avisa. Nada vaza.
4. **Tag `<private>`:** trecho marcado é a sua zona morta. O CORTEX não destila o que está ali, e o
   `sync_push.py` aborta o push se um `<private>` chegar a um arquivo versionado.
5. **Aprovação humana:** comando que apaga/sobrescreve pede confirmação; o push é seu, sob seu olho.

Se você precisa que o CORTEX saiba de algo sensível pra trabalhar, envolva em `<private>`: ele usa
na sessão, mas nunca guarda nem sincroniza.

## Tag `<private>` (não vai pra memória nem pra sync)

Marque qualquer trecho que NUNCA deve ser guardado na memória, destilado, nem versionado:

```
<private>
senha do cliente: ...
chave de API: ...
</private>
```

O CORTEX ignora o que está entre `<private>` na hora de destilar/gravar. Use pra segredo, dado
de cliente, qualquer coisa sensível.

## Regras de segurança embutidas (regra R8)

- **Nunca** pôr segredo (chave, senha, token, webhook) em arquivo versionado.
- **Dado de CLIENTE é sensível como segredo.** Material dos seus clientes não vai pra sync nem pra
  memória sem você decidir conscientemente; na dúvida, marque com `<private>` ou mantenha só local.
  Você é o responsável pelo tratamento desse dado (ver `PRIVACIDADE.md`).
- **Aprovação** antes de comando que apaga/sobrescreve arquivo. O hook `guarda_seguranca.py`
  bloqueia o destrutivo óbvio (`rm -rf`, `Remove-Item -Recurse -Force`).
- **Sync da memória só em repo PRIVADO.** O `.gitignore` do template já barra `.env`, credenciais,
  e os arquivos pessoais preenchidos pelo `/onboard`.
- **Skip permissions desligado por padrão.** Bypass é pontual, só quando você autoriza.

## O que NUNCA é versionado (já no .gitignore)

`.env`, `*credentials*`, `*secret*`, `*token*`, `*.key`, `*.pem`, os arquivos pessoais de
`context/`, `voz.md`, `nicho-*.md`, `decisions/log.md`, `projects/*`, e os logs de sessão.

## Antes de devolver uma melhoria

Se você for devolver uma skill ou regra pra quem te passou o CORTEX, use `/contribuir`: ele limpa
o seu pessoal (nome, cliente, voz, segredo) automaticamente antes de empacotar. Confira o pacote
gerado antes de enviar: nada seu deve estar nele.

## Privacidade por design

- **Local-first:** tudo no seu PC. Sem conta, sem servidor do CORTEX.
- **Legível:** toda memória é markdown que você abre e lê. Nada de caixa-preta.
- **Reversível:** qualquer regra ou memória, você desliga/apaga (`/regras`, editar o arquivo).
