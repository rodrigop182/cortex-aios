# Portar skill pra outro CORTEX — guia

Quando você quiser passar uma skill (ou guia de lastro) do seu CORTEX pra o CORTEX de outra
pessoa, NÃO copie o arquivo cru. Um skill do seu ambiente está cheio de coisas que só existem no
seu sistema: caminhos absolutos, links de memória que apontam pro seu cérebro, arquivos de lastro
locais. No CORTEX do outro, viram referência morta.

A skill portada precisa ser autossuficiente.

## Como fazer (5 passos)

1. **Caminhos absolutos → relativos ao kit de destino.**
   Troque qualquer caminho absoluto (ex: `/Users/voce/.claude/skills/minha-skill/guias/x.md`) por
   caminho relativo à pasta que você vai entregar (ex: `./references/x.md` ou `../guias/x.md`).

2. **Links de memória (`[[nome-da-memoria]]`) → frase inline.**
   A outra pessoa não tem aquela memória. Para cada `[[link]]`, converta o conteúdo daquela memória
   em 1 frase de princípio que fique explícita no próprio arquivo da skill. Sem o link, sem depender
   do cérebro alheio.

3. **Empacotar os arquivos de lastro junto.**
   Se a skill cita guias, léxicos ou fontes que vivem em `references/`, inclua esses arquivos na
   pasta do kit que você está entregando. Skill sem lastro entregável não funciona no destino.

4. **Incluir um `LEIA-PRIMEIRO.md` na raiz do kit.**
   Deve conter: o que é a skill, como instalar (copiar pra `.claude/skills/` mantendo subpasta
   `references/` se existir), como usar (qual frase dispara, qual o output esperado), e aviso sobre
   os caminhos relativos.

5. **Entregar com um prompt pronto.**
   Escreva a primeira mensagem que a pessoa deve colar pra o Claude dela ao usar a skill pela
   primeira vez. Reduz fricção e garante que o contexto certo está presente.

## Regra de escopo em repo de terceiro

Se você está entregando via repositório compartilhado com outra pessoa (qualquer repo que não é
só seu), só toque dentro da pasta acordada. Nunca escreva fora dela ao preparar o kit.

## Relação com a skill `/contribuir`

Este fluxo casa com a skill `/contribuir`: ao contribuir com uma skill de volta ao template
genérico, os mesmos princípios se aplicam. Caminhos relativos, memória inline, lastro empacotado.
