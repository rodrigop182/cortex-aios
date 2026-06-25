# SECURITY — modelo de ameaça e diligência do CORTEX

Este documento é honesto sobre o que o CORTEX protege, o que NÃO protege, e os riscos que
você assume ao usá-lo. Segurança do dia a dia (segredo, tag `<private>`, sync) está em
`SEGURANCA.md`; aqui é o modelo de ameaça e a parte de dependências.

## Modelo de ameaça (premissas)

O CORTEX foi desenhado para um cenário **local-first, single-user, agente semi-confiável**:
- Roda na SUA máquina, com markdown que você lê e edita. Sem servidor do CORTEX.
- Você confia no Claude Code (o agente) o suficiente pra deixá-lo ler/editar seus arquivos.
- O risco principal que o CORTEX mitiga é **vazamento acidental** de segredo/dado sensível
  para um repositório de sync, e **comando destrutivo por acidente**.

## O que o CORTEX NÃO protege (limites reais)

- **Agente mal-intencionado ou prompt injection.** Os hooks barram o destrutivo óbvio, mas não
  são uma sandbox. Se o agente for induzido a algo malicioso, o CORTEX não é a última defesa.
- **Supply chain de plugins/dependências.** Software de terceiro roda com os mesmos privilégios.
  Veja a política de update abaixo.
- **Rede hostil** (ex: WiFi compartilhado). Não trafegue segredo nessas redes; recrie credencial
  no local.
- **Conteúdo enviado a serviços de IA.** O Claude Code envia o que você digita à Anthropic para
  funcionar. Isso é inerente à ferramenta, não algo que o CORTEX intercepta.

## Dependências de terceiro (risco assumido)

- **Claude Code (Anthropic)** — base do sistema. Conteúdo de sessão vai à API da Anthropic.

## Política de update de dependências (diligência)

- **Pinar versão.** Prefira instalar versão fixa de dependência de terceiro, não `latest`.
- **autoUpdate desligado.** Marketplaces de plugin podem ter `autoUpdate: true`.
  Deixe `false`: um update do mantenedor entraria e rodaria com seus hooks sem revisão. Confira o
  changelog/diff antes de subir de versão.
- **Conferir o que mudou.** Após instalar/atualizar dependência que toca `~/.claude/settings.json`,
  faça um diff contra backup pra confirmar que seus hooks sobreviveram.

## Como reportar um problema de segurança

Por ser sistema pessoal, não há canal formal. Se você distribuiu pra alguém e essa pessoa achar
um problema, peça que relate em privado a você (não em issue pública), pra você corrigir antes de
expor. Nunca cole segredo real num relato.
