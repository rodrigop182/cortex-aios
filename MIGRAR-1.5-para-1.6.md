# Migrar do CORTEX 1.5 para 1.6 — roteiro pro agente

> **Para o Claude Code (o agente).** Você está levando o CORTEX do seu usuário da versão **1.5**
> pra **1.6**. Siga À RISCA, em ordem, em português simples. **Regra de ouro: backup ANTES de tocar
> em qualquer coisa; nunca apague nem sobrescreva dado do usuário (memória, voz, projetos).** A 1.6
> NÃO muda dado nenhum — só acrescenta o loop de qualidade da memória e melhora hooks/skills.

## O que a 1.6 traz (e por isso precisa migrar)

- Hooks NOVOS: `registra_uso_memoria.py` (mede qual regra é usada) e `poda_por_evidencia.py`
  reescrito (3 camadas, sob demanda). Mais o `_eficacia-regras.log` (veredito de eficácia).
- Hooks ATUALIZADOS: `captura_regra.py` e `captura_feedback.py` (guard anti-envelope),
  `guarda_tamanho_memoria.py`.
- `settings.json` ganha a entrada `PostToolUse:Read` (chama o `registra_uso_memoria.py`).
- Skills atualizadas: `fecha-sessao`, `catch-up-aprendizado`, `audit`, `continuar-sessao`,
  `handoff/scripts/detectar_handoff.py`.

## Passo 0 — Backup (OBRIGATÓRIO)

Copie (não mova) pra `~/.claude/_backup-cortex-migra-1.6-<data-hora>/`: `settings.json` e as pastas
`hooks/` e `skills/`. Se o usuário versiona o CORTEX em git, isso fica fora do git (passo do
caminho A cuida do `.gitignore`; no manual, não comite a pasta de backup).

## Caminho A — atalho (se o usuário guardou a pasta-fonte do zip)

Se existe a pasta-fonte da instalação (o espelho com `_claude_global/` e `memoria/` dentro), use o
`atualizar.py` **da versão 1.6** (o do pacote novo, que já sabe fazer deploy):

```
python <zip-1.6>/_claude_global/skills/atualizar/scripts/atualizar.py \
  --instalado "<pasta-fonte-guardada>" --novo "<zip-1.6-descompactado>" \
  --claude-dir "<caminho de ~/.claude>" --cortex-dir "<pasta CORTEX>" --dry-run
```

Confira o plano; rode de novo trocando `--dry-run` por `--yes`. O script atualiza a pasta-fonte e
faz o deploy pros lugares vivos, preservando o que você já resolveu. **Depois, resolva os itens de
"AJUSTE MANUAL" que ele listar** (em geral: placeholders dos hooks novos e a seção `hooks` do
`settings.json` — ver Passo 3 e 4 abaixo). Pule pro Passo 5.

## Caminho B — manual (sempre funciona)

Use se não houver pasta-fonte guardada. Trabalhe a partir do `<zip-1.6>` descompactado.

### Passo 1 — copiar os hooks

Copie do `<zip-1.6>/_claude_global/hooks/` pra `~/.claude/hooks/` (sobrescrevendo os de mesmo nome,
já que você fez backup): `registra_uso_memoria.py`, `poda_por_evidencia.py`, `captura_regra.py`,
`captura_feedback.py`, `guarda_tamanho_memoria.py`. **NÃO copie** a pasta `{{CAMINHO_MEMORIA}}/`
(é seed de dado, não vai pra `hooks/`).

### Passo 2 — copiar as skills atualizadas

Copie do `<zip-1.6>` pros lugares vivos, sobrescrevendo: as pastas das skills `fecha-sessao`,
`catch-up-aprendizado`, `continuar-sessao` (de `_claude_global/skills/`) e o
`handoff/scripts/detectar_handoff.py`. A skill `audit` fica na pasta CORTEX
(`<CORTEX>/.claude/skills/audit/`): copie o `SKILL.md` novo de `<zip-1.6>/memoria/.claude/skills/audit/`.

### Passo 3 — resolver `{{CAMINHO_MEMORIA}}` nos hooks novos

Nos arquivos `registra_uso_memoria.py` e `poda_por_evidencia.py` (e confira os outros do passo 1),
troque `{{CAMINHO_MEMORIA}}` pelo caminho REAL da pasta `memory/` do usuário — o mesmo que já está
nos hooks 1.5 que funcionam (ex: `~/.claude/projects/<id>/memory`). Confirme com:
`grep -rl "{{CAMINHO_MEMORIA}}" ~/.claude/hooks/` — não pode sobrar nenhum.

### Passo 4 — adicionar `PostToolUse:Read` ao `settings.json`

No `~/.claude/settings.json`, dentro de `"hooks"`, acrescente (sem apagar o que já existe), trocando
`{{CAMINHO_CLAUDE}}` pelo caminho real de `~/.claude`:

```json
    "PostToolUse": [
      {
        "matcher": "Read",
        "hooks": [
          { "type": "command", "command": "python {{CAMINHO_CLAUDE}}/hooks/registra_uso_memoria.py" }
        ]
      }
    ]
```

Se já houver um bloco `"PostToolUse"`, só acrescente a entrada de matcher `"Read"` à lista dele.

## Passo 5 — verificar

- `grep -rl "{{" ~/.claude/hooks/ ~/.claude/settings.json` não lista nada (fora do `CLAUDE.md`).
- `python -B ~/.claude/hooks/poda_por_evidencia.py` roda e imprime um relatório (provavelmente
  "modo conservador", porque a instrumentação de uso ainda é nova — normal).
- Diga ao usuário pra dar **`/clear`** (hooks e skills recarregam; o cérebro pega na próxima sessão).

## Se algo der errado

Tudo que você sobrescreveu está no backup do Passo 0 — restaure de lá. Os hooks falham em silêncio
(nunca travam o turno), então um placeholder esquecido não quebra a sessão, só desliga aquele pedaço
do loop de aprendizado até você resolver.
