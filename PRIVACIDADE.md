# PRIVACIDADE — tratamento de dados no CORTEX

Nota honesta sobre quais dados o CORTEX guarda, onde moram, o que sai da máquina e como apagar.
Mesmo sendo um sistema pessoal, isto importa porque o CORTEX pode guardar dado de CLIENTES seus.

## Categorias de dado guardadas

- **Perfil do usuário** — quem você é, como trabalha, preferências. Mora em `context/`, `memory/`
  e no núcleo. É o coração do sistema (contextualização).
- **Dado de cliente** — informação dos projetos/clientes que você atende. Mora em `projects/` e
  pastas de cliente. **Sensível**: pode incluir material de terceiros.
- **Dado financeiro** — extrato, fatura, valor de proposta, saldo. **Nunca deve ser versionado.**

## O que sai da máquina, e para onde

- **Para a Anthropic (sempre):** o conteúdo que você digita ao Claude Code vai à API da Anthropic
  pra o sistema funcionar. Inerente à ferramenta.
- **Para o repositório de sync (se você configurar):** o sync espelha parte de `~/.claude` e da
  pasta de memória para um repo git **privado**. O que sobe vs o que fica só local está definido
  no `MANIFESTO-UPDATE.md` e nos `.gitignore`.

## O que NUNCA sai (zona morta)

- Segredo (chave, token, senha, credencial) — barrado por `.gitignore` (nome) e pela trava de
  conteúdo do `sync_push.py`.
- Dado financeiro e qualquer trecho marcado com `<private>...</private>` — o `sync_push.py` aborta
  o push se um `<private>` chegar a um arquivo versionado.

## Você é o controlador do dado de cliente

Se o CORTEX guarda dado de clientes seus, **a responsabilidade pelo tratamento é sua**, não do
CORTEX nem da Anthropic. Antes de sincronizar, considere se você tem o consentimento necessário.
Na dúvida, marque com `<private>` ou mantenha só no local.

## Retenção e exclusão

- **Memória é markdown editável.** Pra apagar o que o sistema sabe, edite/apague o arquivo.
- **Histórico no git de sync.** Apagar um arquivo não apaga o histórico: para remover de vez,
  use `git filter-repo` (ou recrie o repo). Lembre que segredo que já subiu deve ser ROTACIONADO,
  não só removido.
