---
name: sync
description: Configura e gerencia a sincronização do CORTEX entre dispositivos via repositório GitHub PRIVADO, pra seu contexto te seguir entre máquinas. Use quando o operador disser "sincronizar entre dispositivos", "usar em outro PC", "configurar sync", "meu contexto em outra máquina", "/sync", ou aceitar a oferta de sync no onboard. NÃO é backup local nem exportação de dados.
---

## O que esta skill faz

Deixa o CORTEX te seguir entre dispositivos: a pasta `memoria/` (seu contexto, regras, perfil)
vive num repositório GitHub PRIVADO; cada máquina puxa no início e envia no fim da sessão. Você
trabalha igual em qualquer PC.

## Regra de ouro (segurança, inegociável)

- **Repo SEMPRE privado.** Nunca público. Seu contexto pessoal não vai pra internet aberta.
- **Nunca versionar segredo.** Chave, senha, token, `.env`, credencial: barrados pelo
  `.gitignore` e pela trava do hook de sync. Trecho em `<private>` também não sobe.
- Se a trava detectar um segredo prestes a subir, ela ABORTA o push e avisa. Falha segura.

## Configurar (1x por conta)

### Passo 1: Criar o repo privado

Oriente o operador (ou faça, com o `gh` CLI dele):
```bash
# com GitHub CLI:
gh repo create meu-cortex --private

# ou manual: crie um repo PRIVADO em github.com (marque "Private"), sem README
```

### Passo 2: Ligar a pasta memoria/ ao repo

Na PASTA_RAIZ/memoria do operador:
```bash
cd SUA_PASTA_RAIZ/memoria
git init
git remote add origin <url-do-repo-privado>
# confirme que o .gitignore do CORTEX está presente (barra segredo e dado pessoal)
git add .
git commit -m "CORTEX: primeiro sync"
git branch -M main
git push -u origin main
```

### Passo 3: Ligar os hooks de sync (opcional, recomendado)

No `settings.json`, ative os hooks de sync (já vêm no `settings.json` do template, comentados):
- **SessionStart:** `git pull --rebase` (puxa o que a outra máquina enviou)
- **SessionEnd:** trava anti-segredo + `git add/commit/push` (envia o que mudou)

Assim você nunca digita git: o CORTEX sincroniza sozinho. Detalhe em `settings.LEIA-ME.md`.

## Usar em OUTRO dispositivo

Na segunda máquina, instale o CORTEX normalmente, depois:
```bash
cd SUA_PASTA_RAIZ
git clone <url-do-repo-privado> memoria
```
Pronto: o contexto, regras e perfil já estão lá. Os hooks mantêm as duas em dia.

## Regras de operação (evitar conflito)

1. **Pull antes de começar, push ao terminar.** Os hooks fazem isso. Se rodar manual, mesma ordem.
2. **Duas máquinas abertas ao mesmo tempo:** cada uma faz `git pull --rebase` antes de enviar,
   pra não sobrescrever a outra. O hook de SessionStart já puxa.
3. **Conflito de merge:** raro (você cura à mão). Se acontecer, o CORTEX avisa e ajuda a resolver
   o arquivo, nunca sobrescreve cegamente.
4. **Nunca commitar no meio de uma sessão** sem necessidade: deixa o push pro fim (SessionEnd),
   pra não subir estado pela metade.

## Se o operador NÃO usa vários dispositivos

Pule. O sync é opcional. O CORTEX funciona 100% local sem nunca tocar em git.

## Regras de implementação

1. **Repo privado, sem exceção.** Se o operador criar público, alerte e recuse seguir até privar.
2. **Trava anti-segredo sempre ativa.** Nunca empurrar push que contém segredo.
3. **Falha segura.** Erro de sync nunca trava o trabalho nem sobe coisa quebrada.
4. **Padrões editoriais da casa.** No idioma do operador.
