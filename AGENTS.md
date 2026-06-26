# CORTEX OS para Codex

Este arquivo é um ponteiro para quem abre a pasta do pacote no Codex.

O arquivo que deve existir na pasta CORTEX instalada é:

```text
memoria/AGENTS.md
```

Na instalação, o conteúdo de `memoria/` é copiado flat para `C:\CORTEX` ou `~/CORTEX`, então o Codex
enxerga `AGENTS.md` direto na raiz da pasta viva.

Para usar no Codex:

1. abra a pasta CORTEX instalada;
2. confirme que existe `AGENTS.md`;
3. peça tarefas normalmente;
4. rode fechamento e atualização manualmente quando precisar, porque Codex não usa os hooks do
   Claude Code do mesmo jeito.

Detalhes em `ATUALIZAR-COM-CODEX.md` e `ADAPTADORES.md`.
