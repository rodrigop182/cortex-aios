# CORTEX OS

Seu sistema operacional de contexto para IA agentica: memória estruturada, método de execução,
destilação de sessões e atualização segura em cima do agente que você já usa.

Comece pela experiência curta:

- [vitrine/index.html](vitrine/index.html): abra a vitrine estática do produto.
- [DEMO-5-MIN.md](DEMO-5-MIN.md): veja o CORTEX deixando de responder genérico e passando a operar com contexto.
- [ADAPTADORES.md](ADAPTADORES.md): entenda o que funciona em Claude Code, Codex, Cursor, Cline, Windsurf e similares.
- [INSTALAR-SEM-IA.md](INSTALAR-SEM-IA.md): instale sozinho, sem pedir para um agente mexer por você.
- [CONFIGURAR-SEM-IA.md](CONFIGURAR-SEM-IA.md): preencha o perfil manualmente, se não quiser rodar `/onboard`.
- [ATUALIZAR-SEM-IA.md](ATUALIZAR-SEM-IA.md): atualize sem agente, sempre com dry-run.
- [ATUALIZAR-COM-CODEX.md](ATUALIZAR-COM-CODEX.md): use Codex para atualizar preservando seus dados.
- [MAPA-DO-PACOTE.md](MAPA-DO-PACOTE.md): veja o papel de cada pasta antes de instalar ou reorganizar.

---

## Atualizar (para quem já tem instalado)

Cole no seu Claude Code:

```text
/atualizar --github-repo rodrigop182/cortex-aios --github-token SEU_TOKEN
```

O comando baixa a versão mais recente deste repo e atualiza só a camada de produto. Sua memória, voz e contexto ficam intocados.

Sem Claude Code, use [ATUALIZAR-SEM-IA.md](ATUALIZAR-SEM-IA.md). Com Codex, use
[ATUALIZAR-COM-CODEX.md](ATUALIZAR-COM-CODEX.md).

**Como criar o token:**

1. github.com → sua foto → Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token
2. Em "Repository access": Only select repositories → `rodrigop182/cortex-aios`
3. Em "Permissions": Contents → **Read-only**
4. Gere, copie e cole no comando acima

> **Para o Claude Code:** o motor de atualização é `_claude_global/skills/atualizar/scripts/atualizar.py`. Aceita `--github-repo` + `--github-token`, baixa o zipball do último release via API do GitHub, extrai e aplica preservando o dado do usuário. A fronteira produto/dado está em `MANIFESTO-UPDATE.md`.

---

## O que é

CORTEX OS é uma camada de contexto e memória pessoal para agentes de IA que trabalham dentro de
terminal, VSCode, IDE ou desktop app com acesso a arquivos. Ele diz pra IA quem você é, como você
trabalha, qual é a sua voz, seu nicho e as regras que ela deve seguir, antes de qualquer tarefa.

O resultado prático é "one prompt one shot": a IA já chega contextualizada, não precisa ser
reexplicada a cada conversa, e acerta a tarefa de primeira com mais frequência.

### O que o CORTEX faz

- Carrega seu perfil, regras e governança em todo turno (cérebro fino, lido sempre)
- Guarda o detalhe em arquivos separados, lidos só quando a tarefa pede
- Destila cada sessão em regras persistentes, pra não repetir o mesmo ajuste duas vezes
- Mede tendência de 1-shot quando a métrica está ativa
- Entrevista você no onboarding pra preencher o contexto com dados reais, não placeholders

### Limites do CORTEX

- Vector database e busca semântica ficam fora do escopo
- Chatbot com interface própria fica fora do escopo
- Histórico técnico bruto de sessões fica fora do escopo
- O CORTEX em si é markdown local, sem servidor nem telemetria próprios. (O Claude Code, que ele
  roda em cima, envia o que você digita à Anthropic pra funcionar. Detalhe em PRIVACIDADE.md.)

---

## Por que existe

A IA esquece quem você é a cada conversa.

Você abre uma sessão nova, reexplica o tom de voz, o nicho, o cliente, as preferências de
formatação. A resposta vem genérica. Você ajusta. Ela erra de novo na próxima sessão. O custo
disso aparece em tempo e em token gasto no contexto que deveria ser zero.

O CORTEX resolve isso tornando seu contexto um arquivo instalável. Uma vez configurado, ele
carrega automaticamente junto com o Claude Code. A IA sabe seu nome, como você gosta de trabalhar,
o que nunca deve fazer, e qual é o padrão do seu entregável, sem você repetir nada.

---

## Como funciona

Três pilares:

### 1. Núcleo mínimo lido todo turno

Um arquivo curto (`CLAUDE.md`) carregado em toda sessão. Guarda quem você é, ponteiros pro
restante, e as regras que nunca mudam. O restante (frameworks, referências, projetos) fica em
arquivos separados e é lido só quando a tarefa pede. A janela de contexto não enche à toa.

### 2. Memória curada com perfil compacto

Um índice de regras e decisões que crescem com o uso. Não é dump automático de histórico. É
curado: cada sessão destila o que mudou de verdade (um erro corrigido, uma preferência nova, uma
decisão registrada). O perfil compacto é o que a IA aprende sobre como trabalhar com você.

### 3. Loop de aprendizado

O `/fecha-sessao` (ou o hook automático equivalente) destila o dia em regras novas. Erros viram
correções gravadas. A mesma coisa corrigida duas vezes vira memória. Com o tempo, o sistema fica
mais preciso e a IA precisa de menos tentativas pra acertar.

---

## Instalação

Você pode instalar de três formas:

- com o próprio agente, seguindo [INSTALAR-AGENTE.md](INSTALAR-AGENTE.md);
- sem IA, seguindo [INSTALAR-SEM-IA.md](INSTALAR-SEM-IA.md);
- manualmente, seguindo [INSTALAR.md](INSTALAR.md).

### Mac/Linux/Git-Bash

```bash
git clone <url-deste-repo> cortex-os
cd cortex-os
bash instalar.sh
# instala em ~/CORTEX por padrão. Pra mudar o lugar: --destino ~/outra-pasta
# ou com opcoes:
bash instalar.sh --hooks
```

### Windows (PowerShell)

```powershell
git clone <url-deste-repo> cortex-os
cd cortex-os
.\instalar.ps1
# instala em C:\CORTEX por padrão. Pra mudar o lugar: -Destino "C:\outra-pasta"
# ou com opcoes:
.\instalar.ps1 -Hooks
```

Depois de instalar, abra o VSCode **SEMPRE na pasta CORTEX** (`C:\CORTEX` no Windows, `~/CORTEX`
no Mac/Linux). Abrir sempre a mesma pasta é o que faz a memória e as skills te seguirem. Com o
Claude Code aberto nela, rode:

```text
/onboard
```

A entrevista leva ~5 minutos e preenche os placeholders com seus dados reais. No fim, teste com:

```text
no que eu devo focar essa semana?
```

Se a resposta vier te conhecendo, o sistema está funcionando.

Se você não quiser usar `/onboard`, preencha os arquivos de contexto pelo guia
[CONFIGURAR-SEM-IA.md](CONFIGURAR-SEM-IA.md).

Para usar no Codex, abra a pasta CORTEX instalada. Ela traz `AGENTS.md` na raiz depois da instalação.

Para detalhes completos de instalação (estrutura de pastas, ajuste de hooks, ajuste de caminhos),
veja [INSTALAR.md](INSTALAR.md). Travou em algo? [TROUBLESHOOTING.md](TROUBLESHOOTING.md). O que
mudou em cada versão: [CHANGELOG.md](CHANGELOG.md).

---

## CORTEX vs alternativas

| | CORTEX OS | System prompt manual |
| --- | --- | --- |
| O que resolve | Contexto de trabalho: quem você é, voz, regras, nicho, governança | Instruções fixas sem estrutura |
| Tecnologia | Markdown curado, local-first | Texto livre |
| Curação | Manual (você controla o que entra) | Você faz tudo |
| One-shot | Sim (contexto chega pronto) | Depende da qualidade do prompt |
| Privacidade | Local, sem servidor, sem telemetria | Depende da plataforma |
| Aprende com uso | Sim (loop de destilação) | Não |
| Transparência | Total (markdown legível) | Total |

---

## Privacidade e segurança

O CORTEX é markdown no seu PC. Ele próprio não tem servidor, conta nem telemetria, e seu contexto
não sai da máquina pela mão do CORTEX a menos que você sincronize, e aí só em repositório privado.
Importante: o Claude Code (base do sistema) envia o que você digita à Anthropic pra funcionar.
O "local-first" é do CORTEX, não da stack inteira. Ver
[PRIVACIDADE.md](PRIVACIDADE.md).

Pontos principais:

- **Local-first:** tudo em arquivos que você abre e le. Nao ha caixa-preta.
- **Tag `<private>`:** qualquer trecho marcado assim fica fora da destilação e do versionamento.
- **Reversível:** qualquer regra ou memória, você desliga ou apaga via `/regras` ou editando o
  arquivo diretamente.
- **Hook de segurança:** o `guarda_seguranca.py` (instalado com `--hooks`) bloqueia comandos
  destrutivos óbvios antes de executar.
- **`.gitignore` com trava:** o template ja barra `.env`, credenciais, arquivos pessoais
  preenchidos pelo `/onboard`, e logs de sessao.

Criou uma skill ou regra boa e generica? Devolva pra quem te passou o CORTEX com `/contribuir`:
ele empacota a melhoria ja limpa do seu pessoal, e ela pode entrar na proxima versao que todo
mundo recebe.

Detalhes em [SEGURANCA.md](SEGURANCA.md).

Existe um modo LITE (cérebro mínimo pra plano básico) na pasta `lite/`; veja `lite/MODO-LITE.md`.

---

## Licença

O CORTEX OS é licenciado sob **MIT** (ver [LICENSE](LICENSE)): use, modifique e redistribua
livremente, com crédito e sem garantia. A licença cobre o conteúdo original do autor.

Partes com licenças próprias (ver [NOTICE.md](NOTICE.md) pra atribuições completas):

- **skill-creator:** da Anthropic, Apache 2.0. Licença em
  `_claude_global/skills/skill-creator/LICENSE.txt`.
- **Skills de documento (pdf, docx, pptx e similares):** proprietárias, NÃO vêm embutidas no
  repositório. Se instalam separado via `/plugin` quando disponível.

---

## Disclaimer

- **Sem afiliação à Anthropic.** O CORTEX OS é um projeto independente, sem afiliação,
  patrocinado nem endossado pela Anthropic. "Claude" e "Claude Code" são marcas da Anthropic.
- **Fornecido "como está", sem garantia.** Use por sua conta e risco (ver [LICENSE](LICENSE)).
- **Sem conselho profissional.** O CORTEX aconselha sobre trabalho, mas não substitui conselho
  financeiro, contábil, jurídico ou fiscal de um profissional.
- **Saída gerada por IA pode errar.** A IA pode inventar fato, número ou citação. Confira antes
  de publicar, enviar a cliente ou tomar decisão com base nela.
