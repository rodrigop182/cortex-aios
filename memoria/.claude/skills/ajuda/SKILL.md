---
name: ajuda
description: Pesquisa e recomenda a forma mais eficiente e barata de resolver um problema, priorizando open source e gratuito. Use quando o operador disser "como eu faço X", "preciso de uma ferramenta pra Y", "qual a melhor forma de Z", "tem algo grátis que faça isso", "me ajuda a resolver", "/ajuda", ou descrever uma dor sem saber a solução. NÃO é tutorial de ferramenta já escolhida; é a etapa de escolher o caminho certo.
---

## O que esta skill faz

O operador traz um problema ("preciso transcrever áudio", "quero agendar posts", "tenho que
juntar 200 PDFs"). A skill descobre a forma mais eficiente e barata de resolver, com viés forte
em **open source / gratuito**, e entrega um leque de 2-3 caminhos comparados + um veredito do
que fazer.

O ponto não é dar a primeira ferramenta que aparece. É achar o melhor **custo-benefício real**:
preço + esforço de setup + manutenção + curva de aprendizado, contra o que o operador já tem.

## Princípios (a ordem de preferência)

1. **Já existe e é grátis/open source?** Antes de construir qualquer coisa, ver se há app
   open source, CLI, ou ferramenta gratuita madura que já resolve. Quase sempre há.
2. **O operador já tem a capacidade?** Cheque o que já está conectado/instalado (skills do
   CORTEX, `connections.md`, ferramentas que ele já paga). A melhor solução pode ser algo que
   ele já tem e não sabe usar.
3. **Dá pra resolver com um script simples / a própria IA?** Se o problema é pequeno e
   recorrente, um script local ou uma skill nova (via `skill-creator`) pode ganhar de um SaaS.
4. **Só então, ferramenta paga.** E aí, a mais barata que resolve, com plano grátis se houver.

Viés explícito: **open source e gratuito primeiro**. Pago só entra no leque quando o ganho
justifica claramente, e sempre com a alternativa grátis ao lado pra comparação honesta.

## Execução

### Passo 1: Entender o problema (rápido)

Se o pedido já está claro, siga. Se faltar o essencial pra recomendar bem, pergunte no MÁXIMO
2-3 coisas que mudam a resposta:
- **Frequência:** uma vez só, ou recorrente? (uma vez → solução descartável; recorrente →
  vale automatizar)
- **Sistema/contexto:** onde roda (Windows/Mac/Linux/navegador)? Há restrição (offline, dado
  sensível que não pode subir pra nuvem)?
- **Volume e qualidade:** quantos itens, e o resultado precisa ser perfeito ou "bom o
  suficiente"?

Não interrogue. Se dá pra recomendar com o que tem, recomende.

### Passo 2: Checar o que já existe (na ordem dos princípios)

1. **Capacidade interna primeiro.** Veja se uma skill do CORTEX já resolve, ou se
   `connections.md` lista uma ferramenta que ele já tem. Se sim, essa é forte candidata.
2. **Pesquisar open source / grátis.** Use WebSearch pra achar as opções maduras (GitHub,
   alternativeto, awesome-lists, fóruns). Foque em: software open source, ferramentas com
   plano grátis real, CLIs, extensões. Cheque sinais de saúde (manutenção recente, adoção).
3. **Solução caseira.** Avalie se um script local ou uma skill nova (skill-creator) é mais
   simples que adotar uma ferramenta.

### Passo 3: Comparar por custo-benefício real

Monte 2-3 candidatos distintos (não 3 variações do mesmo). Pra cada um, pese:

| Critério | O que olhar |
|---|---|
| **Custo** | Grátis? Open source? Plano grátis com limite? Quanto custa se passar? |
| **Esforço de setup** | Instala e usa, ou precisa configurar/hospedar? |
| **Manutenção** | Mexe sozinho, ou exige cuidado contínuo? |
| **Curva** | O operador consegue usar hoje, ou tem aprendizado? |
| **Encaixe** | Resolve o problema REAL dele (volume, sistema, privacidade)? |

### Passo 4: Entregar o leque + veredito

Formato (curto, sem encher):

```
Pro seu problema (X), os caminhos:

1. [NOME] — open source / grátis
   Resolve assim: ...
   Custo: grátis · Setup: fácil · Curva: baixa
   Ponto fraco: ...

2. [NOME] — grátis com limite / ou script local
   Resolve assim: ...
   Custo: ... · Setup: ... · Curva: ...
   Ponto fraco: ...

3. [NOME] — pago (só se valer)
   ... (só incluir se o grátis não cobre bem)

VEREDITO: eu iria de [opção], porque [motivo ligado ao SEU caso: frequência/sistema/volume].
Quer que eu já [instale / monte o script / crie a skill / te guie no setup]?
```

O veredito é uma recomendação com motivo, não um "depende". Termine oferecendo o próximo passo
concreto (e, se for o caso, ofereça executar: instalar, escrever o script, criar a skill).

## Regras de implementação

1. **Open source / grátis primeiro, sempre.** Pago só com justificativa e com a alternativa
   grátis ao lado.
2. **Reconhecer app pronto antes de construir.** Não reinventar o que já existe maduro.
3. **Custo-benefício é mais que preço.** Inclua setup, manutenção e curva no peso.
4. **Leque de candidatos distintos**, não 3 sabores do mesmo.
5. **Veredito com motivo ligado ao caso dele**, e um próximo passo acionável.
6. **Pesquisa atual.** Use WebSearch; não recomende de memória ferramenta que pode ter mudado
   de preço ou morrido. Cheque se ainda é mantida.
7. **Sem inventar.** Se não achou opção boa, diga; não fabrique ferramenta ou preço.
8. **Padrões editoriais da casa** no idioma do operador, sem em-dash, sem clichê.
