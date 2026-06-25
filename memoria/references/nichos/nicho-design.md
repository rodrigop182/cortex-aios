# Nicho: Design / Criação Visual

## Vocabulário e contexto

- **Design system** — conjunto de tokens (cor, tipografia, espaçamento), componentes e regras que garantem consistência entre telas
- **Token** — valor nomeado e reutilizável do design system (ex: `color-primary`, `spacing-md`)
- **Hierarquia visual** — ordem de importância dos elementos na tela, comunicada por tamanho, peso, contraste e posição
- **Wireframe** — estrutura esquemática sem estilo, focada em layout e fluxo
- **Handoff** — entrega do design pro time de desenvolvimento, com specs e assets exportados
- **Breakpoint** — ponto de largura onde o layout muda de comportamento (mobile, tablet, desktop)
- **Contraste de acessibilidade** — relação de luminância entre texto e fundo; mínimo WCAG AA é 4.5:1 pra texto normal
- **Drift de consistência** — quando elementos visuais vão divergindo do design system ao longo do projeto sem percepção

## Regras extras deste nicho

**[N1] Decisão antes de estética.** Antes de discutir cor ou tipografia, confirmar objetivo da peça, público e contexto de uso. Estética sem decisão vira preferência pessoal, difícil de defender ou iterar.

**[N2] Nunca sugerir "moderno" ou "clean" como direção.** Esses termos não descrevem nada acionável. Traduzir sempre em escolhas concretas: tipografia sem serifa com kerning apertado, paleta de dois tons com contraste alto, espaçamento generoso entre blocos.

**[N3] Ancorar no design system existente.** Se o projeto tem sistema de cores e tipos definido, qualquer sugestão nova parte de dentro desse sistema. Introduzir cor fora do sistema exige justificativa explícita e registro no sistema.

**[N4] Nunca entregar peça sem checar os três breakpoints.** Desktop bonito que quebra no mobile é entrega incompleta. Mobile é o breakpoint prioritário em qualquer projeto voltado ao consumidor.

**[N5] Combater drift ativamente.** Ao revisar ou gerar componente novo, comparar com os existentes e apontar divergências de token antes de dar como pronto.

**[N6] Acessibilidade não é opcional.** Verificar contraste de texto e estado de foco em qualquer componente interativo. Registrar se algum elemento fica abaixo do WCAG AA.

## Atalhos e fluxos típicos

**Diagnóstico de hierarquia:** receber print ou descrição de tela e mapear onde a hierarquia visual está fraca (elementos de mesma importância com peso visual igual, CTA que não se destaca, excesso de focos de atenção).

**Sugestão de direção criativa:** dado briefing com objetivo, público e referências, devolver três direções distintas em palavras: cada uma com paleta de papel (primária/secundária/fundo/texto), tipografia e tom visual. O usuário escolhe antes de qualquer execução.

**Revisão de consistência:** receber lista de componentes ou telas e apontar onde há divergência de token, espaçamento ou tipografia em relação ao design system documentado.

**Briefing de asset:** dado o contexto de uso (banner de rede social, capa de e-book, thumbnail), montar spec de formato (dimensões, resolução, formato de arquivo) e orientações de composição.

**Checklist de handoff:** montar lista de verificação antes da entrega ao dev (componentes nomeados, tokens referenciados, estados de interação documentados, assets exportados nos formatos corretos).

## Skills sugeridas pra instalar

- **Skill de direção criativa** — gera três direções visuais distintas em palavras a partir de briefing, pra escolha antes da execução
- **Skill de revisão de consistência** — compara componentes com o design system e lista divergências por severidade
- **Skill de wireframe** — monta estrutura de tela em texto ou HTML esquemático focado em layout e fluxo
- **Skill de checklist de handoff** — gera lista de verificação pré-entrega com itens específicos do projeto
- **Skill de diagnóstico de hierarquia** — analisa composição e aponta problemas de foco, peso e contraste

## Armadilhas conhecidas

- **Proposta única de estética:** apresentar uma só direção visual e pedir aprovação coloca o cliente em modo de ajuste, não de escolha. Leque de opções distintas chega mais rápido em resultado bom.
- **Ignorar o sistema existente:** sugerir nova cor ou tipo sem verificar se o design system já resolve. Cada exceção ao sistema acumula drift e custo de manutenção.
- **Confundir wireframe com design:** o cliente pede "como ficaria essa tela" e recebe wireframe fidelidade baixa sem aviso. Alinhar fidelidade esperada antes de entregar.
- **Desktop-first em produto mobile:** projetar a experiência completa no desktop e adaptar pro mobile no final. Mobile-first descobre os problemas de conteúdo e hierarquia cedo, quando são baratos de resolver.
