# Como o sistema aprende (o ponto do AIOS pessoal)

O cérebro global só tem o ponteiro. Aqui está o detalhe. O motivo deste sistema existir: parar de
reexplicar as coisas todo dia, e aprender com cada erro pra não repetir. Na prática:

- **Memória persistente.** Fato durável sobre o operador, a operação ou as preferências vai
  pra memória (`{{CAMINHO_MEMORIA}}/memory/` + `MEMORY.md`) ou pro `context/`, não fica só na
  conversa. Da próxima vez o OS já sabe, o operador não repete.
- **Onboarding é semente, não retrato eterno.** O que foi preenchido no dia 1 serve como base de
  partida. Uso real, entregas, mudança de foco e repetição observada têm mais peso que a intenção
  antiga. Se o comportamento atual contradiz o onboard, o certo é atualizar o arquivo vivo, não
  continuar obedecendo a fotografia velha.
- **Decisão registrada.** Toda escolha relevante vai pro `decisions/log.md` com o porquê. O
  sistema nunca "esquece" o que foi combinado.
- **Erro vira correção gravada — e causa fechada (root cause fix).** Quando o OS erra e o operador
  corrige, dois passos obrigatórios: (1) corrigir o retroativo, (2) perguntar "o que gerou esse
  erro?" e gravar a causa como regra — não como correção pontual. Correção sem causa-raiz é
  remendo; causa-raiz virada em regra é vacina. Causa não clara → registrar como pergunta aberta
  em `decisions/log.md`. Falha é dado, não desastre.
- **Skill que falha, skill que melhora.** Skill ou script que deu problema e foi resolvido ganha
  a correção dentro de si (regra nova na seção "Aprendizados", referência, ID fixo). Roda de novo
  já curado. O COMO disso (quando disparar, correção procedural conserta a skill em vez de virar
  memória solta) está em `auto-melhoria-skills.md`; o mapa de como as
  skills se ligam, colidem e desatualizam está em `grafo-de-skills.md`.
- **Cérebro que cresce sem inchar.** Conhecimento novo entra como arquivo ligado (em `references/`
  ou no segundo cérebro), com 1 linha de ponteiro no global. Nunca despejar conteúdo no cérebro
  (ver regra "Cérebro fino" no CLAUDE.md global).

Regra de ouro: se o OS percebe que o operador está corrigindo a mesma coisa 2 ou 3 vezes, para e
grava, em vez de fazer o operador repetir uma quarta. A skill `aprender-do-dia` destila as sessões
do dia nesses lugares automaticamente.
