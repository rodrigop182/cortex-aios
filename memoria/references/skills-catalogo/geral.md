# Pacote geral (todo nicho)

Skills que servem pra qualquer pessoa, independente da área. Recomendadas como base antes de
adicionar o pacote do seu nicho.

> Skills com licença proprietária (Anthropic) não vêm embutidas no CORTEX. Você as instala pelo
> marketplace do Claude Code com `/plugin`. São gratuitas, só não redistribuíveis.

---

## Skills de documento (oficiais Anthropic, instalar via /plugin)

| Skill | Pra quê | Como obter |
|-------|---------|------------|
| `pdf` | Ler, criar, editar, mesclar e dividir PDFs; preencher formulários; extrair texto por OCR. Indispensável quando o cliente manda arquivo ou você precisa entregar em PDF fechado. | Via `/plugin` (proprietária Anthropic) |
| `docx` | Criar e editar documentos Word: relatórios, cartas, propostas, contratos. Útil quando o destinatário exige `.docx` editável em vez de PDF. | Via `/plugin` (proprietária Anthropic) |
| `pptx` | Criar e editar apresentações PowerPoint: slides, decks de proposta, relatórios visuais. Serve quando a entrega precisa ser em formato de slides editáveis. | Via `/plugin` (proprietária Anthropic) |
| `xlsx` | Criar e editar planilhas Excel com fórmulas, tabelas e gráficos. Para orçamentos, relatórios numéricos, controles financeiros e qualquer dado tabelado. | Via `/plugin` (proprietária Anthropic) |

---

## Skill de criação (embutida no CORTEX)

| Skill | Pra quê | Como obter |
|-------|---------|------------|
| `skill-creator` | Criar skills próprias do zero: você descreve o que quer automatizar, ela monta a skill, testa e instala. É o principal mecanismo de extensão do CORTEX. Licença Apache 2.0. | Já incluída no CORTEX |

---

## Categorias úteis gerais (criar com skill-creator ou buscar no marketplace)

As categorias abaixo não têm nome oficial conhecido. Se existir uma skill publicada, procure no
marketplace (`/plugin`). Se não encontrar, use a `skill-creator` pra montar uma.

| Categoria | O que faria | Sugestão |
|-----------|------------|---------|
| Captura e transcrição de conteúdo web | Acessar uma URL, extrair o texto principal e entregar como nota limpa ou resumo. Útil pra pesquisa, benchmarking e curadoria. | Criar com `skill-creator` ou buscar no marketplace |
| Pesquisa com múltiplas fontes | Fazer buscas em leque, cruzar fontes e sintetizar um relatório com referências. Para due diligence, pesquisa de mercado e verificação de fatos. | Criar com `skill-creator` ou buscar no marketplace |
| Agendamento e lembretes | Criar eventos no calendário, programar tarefas recorrentes ou enviar lembretes por integração. Depende das ferramentas que você já usa (Google Calendar, Notion, etc.). | Criar com `skill-creator` (requer integração MCP) |
| Teste de webapp | Abrir um navegador em modo headless, navegar nas páginas, tirar screenshots e reportar o que quebrou. Para quem desenvolve ou mantém sites. | Criar com `skill-creator` ou buscar no marketplace |
| Formatação e padronização de texto em lote | Aplicar regras de estilo (ortografia, tom, formato) a vários arquivos de uma vez. Para quem edita conteúdo em volume. | Criar com `skill-creator` |
| Geração de imagem por prompt | Descrever uma imagem e receber o arquivo gerado, integrando com ferramentas de geração (Replicate, Stability, etc.). | Buscar no marketplace ou criar com `skill-creator` (requer MCP de geração) |

---

## Como decidir o que instalar primeiro

1. Leia seu nicho (`nicho-*.md`) e veja quais skills aparecem com mais frequência.
2. Instale as oficiais pelo `/plugin` na ordem de uso esperado.
3. Para o que não existir pronto, descreva a automação que você quer e use a `skill-creator`.

> O catálogo não é fechado. Conforme a Anthropic e a comunidade lançam skills novas, atualize
> este arquivo ou peça ao CORTEX pra atualizar.
