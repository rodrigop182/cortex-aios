---
name: atualizar
description: Atualiza o CORTEX OS pra uma versao nova trocando SO a camada de produto (skills, nucleo, refs genericas) e PRESERVANDO o dado do usuario (memoria, voz, nicho, contexto, projetos). Usar quando o usuario disser "atualiza o CORTEX", "chegou versao nova", "como atualizo sem perder meu contexto", ou apontar um zip/pasta novo do CORTEX. NAO reinstala do zero (e instalar.ps1/sh) nem mexe na memoria do usuario.
---

# /atualizar — trocar o produto sem perder o contexto

O usuario usou o CORTEX por um tempo e acumulou DADO (memoria aprendida, voz preenchida, nicho,
projetos). Agora chegou uma versao nova do produto. Esta skill troca **so a camada de produto**
(skills, nucleo, referencias genericas, hooks) e **nao toca em nada que o usuario preencheu**.

A fronteira produto vs dado mora no `MANIFESTO-UPDATE.md` (fonte unica da verdade). O script
`scripts/atualizar.py` le o manifesto, faz backup e aplica.

## Antes de rodar (sempre confirmar)

1. **Onde esta o CORTEX instalado** (a raiz, ex: a pasta que tem `_claude_global/` e `memoria/`).
2. **Onde esta a versao nova** (zip ja descompactado numa pasta; o usuario aponta).
   - Se ele tem so o `.zip`, descompacte primeiro pra uma pasta temporaria.

## Fluxo (mostrar antes de aplicar, sempre)

1. **Dry-run primeiro** (nunca pular): roda o script com `--dry-run` e MOSTRA o plano ao usuario:
   o que vai criar, o que ficou pendente de merge manual, o que seria removido so por lista explicita,
   e a confirmacao de que o dado fica intocado.

   ```
   python <skill>/scripts/atualizar.py --instalado "<raiz-instalada>" --novo "<raiz-nova>" --dry-run
   ```

2. **O usuario confere e aprova.** Se houver arquivo de produto que ele editou a mao, o script
   avisa; o backup garante reversao, mas vale alertar antes de aplicar.

3. **Aplicar** com `--yes` (so depois do OK dele):

   ```
   python <skill>/scripts/atualizar.py --instalado "<raiz-instalada>" --novo "<raiz-nova>" --yes
   ```

   O script faz backup da raiz inteira em `_backup-update-<versao>-<data>/` ANTES de tocar em nada.

## Deploy pros lugares vivos (`--claude-dir` / `--cortex-dir`)

Atualizar a pasta-fonte (o espelho do zip que o usuario guardou) NAO atualiza sozinho os
hooks/skills que o Claude Code de fato carrega em `~/.claude` e na pasta CORTEX. Pra fechar esse
gap, passe os destinos vivos (rode com `--dry-run` primeiro, sempre):

```
python <skill>/scripts/atualizar.py --instalado "<raiz-fonte>" --novo "<raiz-nova>" \
  --claude-dir "<caminho de ~/.claude>" --cortex-dir "<pasta CORTEX>" --dry-run
```

O deploy e NAO-DESTRUTIVO e nunca quebra o que o usuario ja configurou:
- arquivo SEM placeholder: atualiza direto (backup datado antes).
- arquivo com placeholder JA resolvido e logica igual: PRESERVA (nao toca, nao re-introduz `{{...}}`).
- arquivo com logica nova, ou hook NOVO configuravel: copia e MARCA pra AJUSTE MANUAL — voce (o
  agente) resolve os `{{...}}` que ele listar, do mesmo jeito que na instalacao.
- `settings.json`: nunca sobrescrito automatico (pode ter hooks do usuario mesclados) — vem na lista
  de ajuste manual pra voce re-mesclar so a secao `hooks`.

Se o destino e um repo git (ex CORTEX versionado no GitHub), o script poe os backups/cache no
`.gitignore` sozinho, pra nao sujar o git. Depois do deploy, resolva os itens de AJUSTE MANUAL que
ele listar e oriente o usuario a dar `/clear` (o `CLAUDE.md` novo so pega na proxima sessao).

## O que a skill garante

- **Dado do usuario intocado:** memoria (`memoria/memory/**`), voz, nicho, contexto, decisoes,
  projetos preenchidos, handoffs. O script nem le esses caminhos pra escrever.
- **Produto trocado pela versao nova:** skills, `CLAUDE.md`, `lite/CLAUDE-LITE.md`, settings, hooks,
  refs genericas, docs. Arquivo de produto que sumiu na versao nova e preservado por padrao.
  Remocao so acontece se o caminho estiver em `REMOVER_PRODUTO` e o operador usar flag explicita.
  Arquivo existente diferente fica preservado e a versao nova vai para `_update-pendente/`, salvo
  quando houver permissao explicita de sobrescrita.
- **Backup sempre:** da pra reverter restaurando da pasta `_backup-update-*`.
- **Versao:** o `VERSION` instalado passa a ser o da versao nova. Downgrade pede `--yes`.

## Armadilhas

- Se o usuario aponta o MESMO diretorio como instalado e novo, o script aborta.
- Se a versao nova nao traz `MANIFESTO-UPDATE.md`, o script aborta (nao da pra saber a fronteira).
- Nicho/voz que vierem no zip novo sao IGNORADOS (sao dado): nunca sobrescrevem o do usuario.
- Esta skill NAO e a primeira instalacao (isso e `instalar.ps1`/`instalar.sh`). Aqui ja existe
  CORTEX rodando com dado.

## Verificacao final

1. Rodei o dry-run e mostrei o plano antes de aplicar?
2. O usuario aprovou?
3. Confirmei pra ele que o dado ficou intocado e onde esta o backup?
4. O `VERSION` instalado bate com o da versao nova?
