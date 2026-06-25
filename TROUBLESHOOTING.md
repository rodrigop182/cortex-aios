# Solução de problemas — CORTEX OS

Os erros mais comuns na instalação e no dia a dia, com a causa e o conserto. Se o seu não está
aqui, rode `/como-funciona` ou abra o `INSTALAR.md` de novo.

---

## Instalação

### A memória/skills sumiram, ou o CORTEX "esquece" tudo às vezes

Quase sempre é **pasta errada**: você abriu o VSCode numa pasta que não é a do CORTEX. O Claude
Code guarda memória e skills **por pasta** — abriu outra, ele não acha nem o que aprendeu nem as
skills (`/onboard`, `/regras`...). Conserto: abra o VSCode **SEMPRE** na pasta CORTEX (`C:\CORTEX`
no Windows, `~/CORTEX` no Mac/Linux). Lá dentro tem o `_ABRA-ESTA-PASTA-NO-VSCODE.md` lembrando.
No VSCode, fixe ela em **Arquivo > Adicionar Pasta ao Espaço de Trabalho** e salve o workspace.

### As skills do sistema (/onboard, /regras) não aparecem no Mac/Linux

Se você instalou **na mão** com `cp -r memoria/* ...`, o `*` do bash pula arquivos ocultos e a
pasta `.claude/skills/` (onde moram as skills do motor) fica de fora. Use `cp -r memoria/. ...`
(com o ponto), ou rode o `instalar.sh`, que já faz certo.

### "Ele não me conhece" / responde genérico depois do /onboard

Provável placeholder `{{...}}` que sobrou sem trocar. Rode:

- **Mac/Linux:** `grep -rl "{{" ~/.claude/CLAUDE.md ~/.claude/hooks ~/.claude/settings.json`
- **Windows (PowerShell):** `Get-ChildItem "$env:USERPROFILE\.claude\CLAUDE.md","$env:USERPROFILE\.claude\settings.json","$env:USERPROFILE\.claude\hooks" -Recurse -File | Select-String "{{" -List | Select-Object Path`

Se listar algum arquivo, troque o `{{CAMINHO_MEMORIA}}` / `{{CAMINHO_CLAUDE}}` pelo caminho real e
re-rode `/onboard`.

### Uma skill/hook/CLAUDE.md meu sumiu depois de instalar

O instalador faz **backup antes de sobrescrever** — skills, agents, hooks, o `CLAUDE.md` e os
arquivos de memória que colidiram. Procure em `~/.claude/_backup-cortex-<data>/` (a data é a do
momento da instalação). Seu arquivo original está lá; copie de volta o que precisar.

### O hook não dispara (nada acontece no fim/início da sessão)

1. Confira se ele está registrado no `~/.claude/settings.json` (compare com
   `_claude_global/settings.json` do pacote — você precisa **mesclar**, não sobrescrever o seu).
2. Confira o caminho no comando: deve ser `python <caminho-real>/hooks/<nome>.py`, sem
   `{{CAMINHO_CLAUDE}}` sobrando.
3. Teste o hook na mão: `python ~/.claude/hooks/<nome>.py` — se ele erra, o erro aparece aí.
4. Precisa de **Python 3** no PATH. Cheque com `python --version` (ou `python3 --version`).

### "settings.json inválido" / Claude Code não carrega os hooks

O arquivo pode estar salvo com **BOM** (marca de ordem de bytes) no começo, o que quebra o parser.
Reabra e salve como **UTF-8 sem BOM**. No PowerShell, ao gerar um settings use
`Out-File -Encoding utf8` (não `utf8BOM`).

---

## Sync entre máquinas (opcional)

### O push foi abortado: "possível segredo/dado sensível detectado"

É a trava de segurança funcionando. Um arquivo que ia subir tem cara de segredo (chave, token,
senha, dado financeiro) **ou** sobrou um bloco `<private>` no conteúdo. Conserto:

- Mova o segredo pra **fora** da pasta `memoria/`, ou
- Envolva o trecho sensível em `<private>...</private>` (com a tag fechada), e tente de novo.

Lembre: dado em `<private>` é zona morta — nunca sincroniza. Se você esqueceu de **fechar** a tag
(`</private>`), o push aborta de propósito; feche e repita.

### Não uso duas máquinas — como desligo o sync?

Remova as entradas `sync_push.py` e `sync_pull.py` do seu `~/.claude/settings.json`. O resto do
sistema funciona sem elas.

---

## Segurança

### A guarda bloqueou meu comando de apagar pasta

O hook `guarda_seguranca.py` bloqueia `rm -rf` e `Remove-Item -Recurse -Force` nos dois shells —
mesmo com aprovação no pop-up. É de propósito: evita apagar pasta inteira por acidente. Pra apagar
de verdade, faça arquivo-a-arquivo (`find ... -delete` + `rmdir`) ou desligue o hook
temporariamente no `settings.json`.

---

## Atualização

### "Vou perder meu contexto se atualizar?"

Não. A skill `/atualizar` troca só a camada **PRODUTO** (skills, núcleo, refs genéricas) e preserva
o **DADO** (memória, voz, nicho, contexto, projetos). A fronteira está em `MANIFESTO-UPDATE.md`. Na
dúvida, ela trata o caminho como DADO (preserva). Veja o `CHANGELOG.md` da versão de destino antes.
