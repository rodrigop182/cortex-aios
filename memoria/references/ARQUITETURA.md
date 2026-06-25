# ARQUITETURA do CORTEX — mapa pra mexer sem redescobrir

Lido SOB DEMANDA (não todo turno) antes de mexer na estrutura do CORTEX: hook, skill, settings,
porte vivo↔template, zip. Existe pra eu não gastar 4 buscas redescobrindo onde mora cada coisa toda
vez. Se ao mexer eu achar que este mapa diverge do disco, CORRIJO este arquivo no mesmo passo (o
`/audit` também confere). Última varredura real: 2026-06-23.

> Companheiro: `criterio-esforco-cortex.md` (quando ir leve vs. pesado, quando disparar auditoria
> adversarial). Leia os dois juntos antes de uma mexida de peso.

---

## 1. As três raízes (não confundir)

| Raiz | O que é | Quando carrega |
|---|---|---|
| `C:\Users\{{USUARIO}}\.claude\` | Instalação global do Claude Code: hooks, skills, settings, CLAUDE.md global | Toda sessão, qualquer pasta |
| `{{CAMINHO_MEMORIA}}\` | **Pasta CORTEX** (o cérebro de longo prazo): references, context, decisions, projects | Ao abrir `{{CAMINHO_CORTEX}}` |
| `C:\Users\{{USUARIO}}\.claude\projects\c--Projetos\memory\` | **Memória persistente** por-projeto: MEMORY.md + ~140 .md + logs backstage | Ao trabalhar dentro do projeto |

Erro clássico meu: tratar "memória" como uma coisa só. São TRÊS. `{{CAMINHO_MEMORIA}}` (template)
aponta pra a 3ª (`projects/.../memory`), NÃO pra a 2ª (`memoria/`). A pasta `references/` mora na 2ª.

---

## 2. Hooks (onde ficam, o que fazem, em que evento)

Vivo: `C:\Users\{{USUARIO}}\.claude\hooks\*.py`. Registro: `~/.claude/settings.json` → `hooks`.

| Evento | Hooks (na ordem) |
|---|---|
| **PreToolUse** Bash/PowerShell | `guarda_seguranca.py` (bloqueia destrutivo, exit 2) |
| **PreToolUse** Write/Edit | `snapshot_memoria.py`, `guardiao_escrita.py` |
| **PostToolUse** Read | `registra_uso_memoria.py` |
| **UserPromptSubmit** | `hook_contexto.py`, `roteia_cliente.py`, `retrieval_topico.py`, `captura_regra.py`, `captura_feedback.py` |
| **SessionStart** | `nudge_destilacao.py`, `nudge_referencias.py`, `guarda_tamanho_memoria.py`, git pull (shell inline) |
| **PreCompact** auto | `precompact_flush.py` |
| **SessionEnd** | `auto_sync_cerebro.py`, `registrar_sessao.py` (skill fecha-sessao) |

Papel de cada (1 linha): segurança bloqueia rm-rf/push-f · snapshot/guardiao protegem escrita ·
registra_uso mede leitura · hook_contexto avisa ~250k · roteia_cliente injeta ficha de cliente
citado · retrieval_topico injeta guia/regra por tópico · captura_regra/feedback logam sinais ·
nudges avisam fila · guarda_tamanho mede MEMORY.md · precompact_flush marca antes de compactar ·
auto_sync espelha ~/.claude→memoria/dot-claude e faz push · registrar_sessao destila a sessão.

**Padrão técnico OBRIGATÓRIO de hook novo** (aprendido na dor, 23/06):
- **stdin em UTF-8 explícito:** `sys.stdin.buffer.read().decode("utf-8")`. O default Windows é cp1252
  e quebra acento ("conversão"→"conversÃ£o").
- **stdout em UTF-8 explícito:** `sys.stdout.reconfigure(encoding="utf-8")` (quebra em ↔/emoji senão).
- **Falha silenciosa:** `try/except` genérico, exit 0, nunca polui o turno. Só `guarda_seguranca` usa exit 2.
- **Lê JSON do stdin** (campo `prompt`, `cwd`, etc.), escreve em LOG ou stdout, nunca em arquivo de trabalho.
- **Match de texto:** por palavra inteira (`(?<!\w)…(?!\w)`) e SEM acento (normaliza NFKD) pra casar
  o que o {{USUARIO}}go digita com acento contra keyword sem acento.

---

## 3. Skills (onde ficam)

- **Globais:** `~/.claude/skills/*` (~64). Carregam em qualquer pasta. Só a `description:` + `name`
  são injetadas todo turno (custam token sempre); o corpo do SKILL.md carrega sob demanda.
- **Escopadas por pasta:** `memoria/.claude/skills/*` (ex: onboard, audit, plan, grill-me,
  level-up, ingerir, novo-cliente) — só carregam ao trabalhar sob `memoria/`.
- Regra de description enxuta: `references/compressao-description-skill.md`.

---

## 4. References (a biblioteca pesada) — `memoria/references/*.md`

Onde mora o conhecimento atemporal. ~41 arquivos. Famílias: frameworks (3ms, principios-aios,
karpathy), **13 guias de nicho** (`guia-*.md` + `ref-design-fcc.md`, cada um com `## Checklist` no
fim), voz/design-system, processo (playbook, fluxo-roteamento, manutencao-backstage), aprendizado
(como-o-sistema-aprende, auto-*, loop-*). Índice dos guias: `_indice-guias-nicho.md`.

O `retrieval_topico.py` injeta daqui por tópico (guia → só o `## Checklist`; regra curta → inteira).

---

## 5. Template (o produto) — `{{CAMINHO_CORTEX}}\_template_aios\` + `{{CAMINHO_CORTEX}}\CORTEX-OS.zip`

```
_template_aios/
├── _claude_global/      → vai pra ~/.claude (CLAUDE.md, settings.json, hooks/, skills/, agents/)
├── memoria/             → vai FLAT pra a pasta CORTEX do amigo (references/, nichos/, context/ vazio…)
│   └── references/nichos/ → 6 nichos consolidados (design/dev/escrita/marketing/operacoes/vendas)
├── lite/                → variante enxuta (CLAUDE-LITE.md)
├── _claude_skills/      → VAZIO (placeholder)
└── docs de instalação   → INSTALAR-AGENTE.md, INSTALAR.md, MANIFESTO-UPDATE.md, CHANGELOG, VERSION
```

Zip = espelho da raiz do template (excluindo `__pycache__`/`.pyc`/`.git`/testes). VERSION atual: ver `VERSION`.

### Placeholders (resolvidos na instalação — NUNCA versionar resolvido)
| Placeholder | Resolve pra | Onde |
|---|---|---|
| `{{CAMINHO_CLAUDE}}` | `~/.claude` | settings.json, hooks, instalar.ps1 — CRÍTICO |
| `{{CAMINHO_MEMORIA}}` | `~/.claude/projects/<proj>/memory` | hooks de aprendizado — CRÍTICO |
| `{{PASTA_CORTEX}}` | a pasta CORTEX de trabalho (onde mora `references/`) | `retrieval_topico.py` — desde 1.6.2 |
| `{{PASTA_REFERENCIAS}}` | pasta de ingestão de refs | `nudge_referencias.py` — opcional |
| `{{REPO_SYNC}}` | repo git de sync multi-máquina | sync_pull/push — opcional |
| `{{NOME}}`, `{{NICHO}}`, `{{NORTE}}`, `{{IDIOMA}}`, `{{PLANO}}`… | identidade do operador | CLAUDE.md, onboard — preenchidos no /onboard |

---

## 6. DIVERGÊNCIAS vivo ↔ template (o "imposto de tradução" — a causa nº2 da lentidão)

Toda feature paga isso DUAS vezes. O que difere:

| Dimensão | Vivo ({{USUARIO}}go) | Template (amigo) |
|---|---|---|
| **Guias de nicho** | 13 `guia-*.md` granulares, cada um com `## Checklist` | 6 `nichos/nicho-*.md` consolidados, com `## Regras extras` (SEM checklist) |
| **FCC / design-system** | tem `ref-design-fcc.md` | NÃO tem (é da identidade do {{USUARIO}}go) |
| **Caminhos** | hardcoded `{{CAMINHO_MEMORIA}}` | placeholder `{{...}}` |
| **Hooks só do vivo** | `roteia_cliente.py`, `auto_sync_cerebro.py` | NÃO portar sem decidir arquitetura do amigo |
| **Sync** | `auto_sync_cerebro` (espelha ~/.claude do {{USUARIO}}go) | `sync_pull/push` via `{{REPO_SYNC}}` (genérico) |
| **Pessoa** | "{{USUARIO}}go" | "operador", "você" |

### Porte vivo→template, o checklist (pra não quebrar)
1. **Adaptar, não copiar.** Se a estrutura difere (guia vs nicho), reescrever o MAPA/caminho pro lado
   do template, não colar o do vivo.
2. **Caminho vira placeholder.** Trocar `{{CAMINHO_MEMORIA}}` por `{{PASTA_CORTEX}}`/`{{CAMINHO_MEMORIA}}`.
3. **Despessoalizar.** "{{USUARIO}}go" → "operador"; tirar nome de cliente, FCC, dado pessoal.
4. **Registrar hook novo** no `settings.json` do template com `{{CAMINHO_CLAUDE}}` E documentar
   qualquer placeholder novo no `INSTALAR-AGENTE.md`.
5. **NUNCA sobrescrever DADO** do amigo no /atualizar: `context/`, `decisions/`, `memory/`,
   `projects/`, nichos customizados, hooks/skills customizados. Ver `MANIFESTO-UPDATE.md`.
6. **Regenerar zip** excluindo `__pycache__`/`.pyc`/testes; bumpar VERSION + CHANGELOG.
7. **Validar empacotamento:** placeholder ainda literal (não resolvido), 0 pyc, 0 vazamento de dado
   pessoal, settings registra o hook, VERSION certo.

---

## 7. Rede de segurança (não há git em ~/.claude nem {{CAMINHO_CORTEX}})

Antes de tocar arquivo de estrutura: **backup datado manual** (`_backup-<o-que>-AAAAMMDD-HHMMSS`).
O `auto_sync_cerebro` versiona ~/.claude em `memoria/dot-claude` no SessionEnd, mas isso é espelho,
não rede de desfazer mid-session.

---

## 8. Onde escrever cada coisa (roteamento)

| O quê | Onde |
|---|---|
| Regra de como trabalhar com o {{USUARIO}}go | `MEMORY.md` + arquivo em `projects/.../memory/` |
| Conhecimento atemporal / framework / guia | `memoria/references/` |
| Skill (procedural) | `~/.claude/skills/` ou `memoria/.claude/skills/` |
| Decisão e porquê | `memoria/decisions/log.md` (append, mais recente no topo) |
| Estado de projeto | `context/` ou memória `status:` |
| Backstage (feedback/regra/sessão) | logs em `projects/.../memory/_*.log` (automático) |
