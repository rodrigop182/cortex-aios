# Armadilhas técnicas — referência

Conhecimento acumulado sobre comportamentos inesperados de ferramentas no ambiente do CORTEX.
Não é comportamento do agente: é leitura de referência, puxada sob demanda quando o erro aparece.

---

## Bash tool: `:` e `/` em argumentos git (Windows)

O Bash tool no Claude Code interpreta `:` e `/` em argumentos como separadores de caminho ou
redirecionamento do shell. Isso quebra silenciosamente (ou com erro de parse) comandos git que
usam essa notação.

**Exemplo problemático:**

```bash
# NÃO funciona via Bash tool no Windows:
git show origin/nome-da-branch:caminho/arquivo.html
```

O Bash tool corrompe o argumento antes de o git processar, resultando em erro ou arquivo errado.

**Solução:** para qualquer comando git com `:` no argumento (leitura de arquivo de branch, `HEAD:path`,
`branch:path`), use o **PowerShell tool** em vez do Bash tool:

```powershell
# Funciona corretamente via PowerShell:
git show origin/nome-da-branch:caminho/arquivo.html
```

Vale pra qualquer argumento git que contenha `:` seguido de caminho: `HEAD:arquivo`,
`sha:arquivo`, `branch:pasta/arquivo`. A regra é simples: git com `:` no arg vai pelo PowerShell.

---

## Python no Windows: encoding e BOM

Scripts Python que abrem arquivos no Windows caem em `cp1252` por padrão, quebrando em caracteres
acentuados/especiais. Sempre declarar `encoding='utf-8'` nos `open()`.

Ao ler stdin JSON em Python (ex: recebendo output de PowerShell), usar `utf-8-sig` em vez de `utf-8`
puro — remove nativamente o BOM (Byte Order Mark) que shells Windows injetam antes do JSON. Sem
isso, `json.loads()` quebra silenciosamente.

PowerShell 5.1 `Get-Content`/`Set-Content` corrompe UTF-8 (mojibake em caracteres especiais);
prefira `Copy-Item` ou resolva via Python para preservar encoding.

---

## Python no Windows: caminhos em strings

Placeholder ou caminho Windows em string Python normal quebra com `SyntaxError unicodeescape`
(`\U` de `\Users` é interpretado como sequência de escape). Sempre usar raw string (`r''`) ou
escape duplo. Validar com `compileall` resolvido (não apenas `py_compile` pontual).

---

## Operações atômicas em arquivo (race conditions)

Em scripts de poda/log com possível concorrência, nunca fazer delete + write separado. Usar
arquivo temporário + `os.replace()` (operação atômica no Windows/Unix) para evitar corrupção
parcial e race conditions.

---

## CLI `claude -p` via subprocess: timeout

`claude -p` via subprocess sofre timeout em pipelines grandes. Migrar para o SDK Python
(`import anthropic`) elimina overhead de processo e resolve timeouts definitivamente.

---

## MCP servers: carregamento e configuração

MCP servers só carregam na sessão seguinte após ativação — sempre pedir reinício do Claude Code
antes de testar ferramentas novas.

Configurar via `.mcp.json` ou seção MCP específica em settings — não diretamente em
`~/.claude/settings.json` global. Usar `/mcp` command ou CLI para diagnosticar quais estão ativos.

Ao configurar, sempre ler o arquivo de settings atual antes de editar — nunca substituir o arquivo
inteiro, sempre fazer merge com as configurações existentes.

---

## Playwright: processos órfãos no Windows

Playwright/Chromium deixa processos órfãos acumulados após múltiplos testes. Ao ver
`ERR_NO_BUFFER_SPACE` no Windows, matar todos os processos python em background antes de re-rodar.
Não esperar resolução automática.

Screenshots Playwright: aguardar `networkidle` ANTES de inspecionar DOM em webapp dinâmica;
em HTML estático, ler arquivo direto.

---

## Comparação de versão semântica

Nunca comparar via string (`1.10 < 1.9` alfabeticamente). Sempre parsear em tupla de inteiros
`(1, 10, 0)` ou usar biblioteca semver — comparação string bloqueia upgrades legítimos.

---

## Troca de modelo mid-session

Trocar de modelo dentro de uma sessão (mesmo em menos de 5 min) causa cache miss no novo modelo.
Em sessão grande, o custo do miss pode superar a economia de usar modelo mais barato. Preferir
deixar a conversa no modelo atual ou fazer handoff/clear entre tarefas antes de trocar.
