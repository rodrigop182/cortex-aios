# Criterio de explicitacao, peso e retroativo do CORTEX

Uso: sob demanda
Escopo: sistema
Gatilho: quando uma regra "ja existia", mas estava implicita, fraca, enterrada ou mal roteada
Nao usar para: detalhe local de projeto sem valor sistemico

Regra-mae: **regra so esta pronta quando esta explicita, com o peso certo, acionavel na hora certa e reconciliada com o retroativo relevante.**

Se eu descubro uma boa regra so depois do erro, ou digo "isso ja existia, mas nao estava explicito", o trabalho ainda nao terminou.

## O problema nomeado

Erro comum do CORTEX:

- a regra existe em algum arquivo pesado;
- mas nao tem nome forte;
- nao tem gatilho claro;
- nao tem ponteiro no bootstrap certo;
- nao rebaixa ou substitui a versao implicita antiga;
- nao dispara revisao retroativa nos lugares que continuam contradizendo a regra.

Resultado: a regra "existe", mas nao governa.

## Teste de pronto para qualquer regra nova

Toda regra nova ou consolidada precisa passar nestas 5 portas:

1. **Explicita**
   - da para apontar a frase exata da regra?
   - o nome dela e encontravel por `rg`?
   - o agente consegue cita-la sem reinterpretar?

2. **Acionavel**
   - ela diz quando usar?
   - ela diz quando nao usar?
   - ela diz o que fazer quando o gatilho acontecer?

3. **Pesada o bastante**
   - ela mora na camada certa?
   - ha ponteiro no bootstrap ou no indice certo?
   - o custo de ignora-la justifica mais destaque?

4. **Sem concorrente implicito**
   - existe texto velho, mais fraco ou contraditorio ainda guiando comportamento?
   - existe duplicata que dilui a regra?
   - existe versao "bonita", mas menos operacional, competindo com a versao boa?

5. **Retroativo reconciliado**
   - os arquivos quentes que dependem dela foram revisados?
   - as fichas, skills, ganchos, templates ou docs que ainda encarnam a regra velha foram corrigidos?
   - a decisao foi registrada se o porte nao for obvio?

6. **Multiagente quando for CORTEX**
   - o alvo foi declarado: compartilhado, Claude Code, Codex, Cursor/Cline portatil ou nao portar?
   - Claude Code e Codex receberam ponteiro ou patch quando a regra afeta os dois?
   - o que for portatil para Cursor/Cline ficou em markdown, script neutro ou referencia compartilhada?

Se uma dessas portas falhou, a regra ainda nao esta pronta.

## Matriz de peso

| Tipo de regra | Onde precisa aparecer | Peso minimo |
| --- | --- | --- |
| comportamento universal do sistema | `references/` + ponteiro curto em `CLAUDE.md` ou `AGENTS.md` + decisao se nao for obvio | alto |
| regra de roteamento ou memoria | `references/` + lugar que dispara o uso | alto |
| regra de projeto ou cliente | ficha do projeto/cliente + summary se estiver quente | medio |
| detalhe de skill | `SKILL.md` ou glossario local | medio |
| preferencia verbal pessoal | memoria curta ou lexico central, se cruzar superficies | medio ou baixo |
| melhoria do CORTEX multiagente | `references/` + ponteiros Claude/Codex + template/espelho se distribuivel | alto |

## Pergunta de peso

Antes de encerrar uma consolidacao, perguntar:

**se essa regra faltar amanha, onde o sistema erra de novo?**

Resposta:

- erra em varias superficies -> precisa de peso sistemico;
- erra so numa skill ou cliente -> peso local basta;
- erra pouco, mas custa caro quando erra -> destacar mais do que o volume sugeriria.

## Gatilho obrigatorio de promocao

Promover uma regra para peso maior quando qualquer item abaixo for verdadeiro:

- eu disse "isso ja existia, mas nao estava explicito";
- o operador corrigiu a mesma coisa 2x;
- a regra ficou escondida em arquivo pesado e nao disparou no fluxo real;
- o erro reapareceu em outra superficie;
- a regra mudou decisao, nao so redacao;
- a regra altera como onboard, ficha, memoria, skill ou update devem ser mantidos.

## Protocolo retroativo de reconciliacao

Quando uma regra sobe de nivel, rodar este sweep curto:

1. **Nomear a regra**
   - criar um nome tecnico simples e buscavel.

2. **Fixar a fonte canonica**
   - escolher 1 arquivo principal onde o detalhe mora.

3. **Dar peso**
   - adicionar ponteiro curto no bootstrap, indice ou skill que precisa dispara-la.

4. **Cacar concorrentes**
   - procurar duplicata, versao fraca, texto implicito ou trecho contraditorio.

5. **Corrigir o retroativo relevante**
   - ajustar os arquivos quentes que ainda operam pela regra velha.

6. **Registrar a decisao**
   - `decisions/log.md` quando o porte, escopo ou motivo nao forem obvios.

7. **Portar entre agentes**
   - aplicar em Claude Code e Codex quando fizer sentido;
   - deixar Cursor/Cline cobertos pelo que for portatil;
   - registrar `nao portar` com motivo quando a capacidade for exclusiva.

## Escopo minimo do sweep retroativo

Nao varrer o mundo inteiro. Revisar primeiro:

- o arquivo canonico do tema;
- o bootstrap que deveria apontar para ele;
- a skill, ficha ou template que mais sofrem com esse erro;
- o template distribuivel, se a regra for universal.

## Anti-padroes

- "depois a gente porta"
- "a regra ja existe em algum lugar"
- "isso ficou implicito no exemplo"
- "resolvi no arquivo novo, mas deixei o antigo competindo"
- "gravei a memoria, mas nao aumentei o peso"
- "corrigi daqui pra frente, mas nao reconciliei o retroativo"

## Checklist de auditoria

- [ ] A regra esta escrita em frase direta?
- [ ] Tem `Uso`, `Gatilho` e `Nao usar para` quando for referencia?
- [ ] Esta na camada certa?
- [ ] Tem ponteiro na camada que realmente dispara o comportamento?
- [ ] Existe versao antiga competindo com ela?
- [ ] Fiz sweep retroativo curto nos lugares quentes?
- [ ] Registrei a decisao se precisava?
- [ ] Declarei o alvo multiagente e portei para Claude Code/Codex quando fazia sentido?

## Criterio de pronto

Esta regra esta funcionando quando:

1. eu nao preciso mais dizer "ja existia, mas estava implicito";
2. o bootstrap puxa a regra na hora certa;
3. o detalhe mora em um lugar so;
4. o retroativo quente foi reconciliado;
5. a regra volta a ser encontrada e aplicada sem depender da memoria da conversa.
