---
name: salvar-referencia
description: "Salva material que o operador jogou pra aprender (PDF, link, imagem, vídeo, áudio, YouTube, site) e destila pro lugar certo. Aciona por INTENÇÃO explícita: 'salva essa ref', 'aprende com isso', 'guarda esse material', 'processa essa pasta', ou quando auditoria apontar arquivo novo. NAO aciona quando operador só MENCIONA referência em conversa — exige que ele esteja MANDANDO algo pra guardar. NAO caça ref na web nem destila sessão de trabalho (fecha-sessao)."
---

# Ingerir referência

Fecha o loop "operador joga referência → o sistema entende e aprende com ela". A pasta
`{{PASTA_REFERENCIAS}}` funciona como um arquivo de furtos: este é o processo de garimpar
cada furto novo e guardar o que vale. Roda como SUBAGENTE quando há folga: não vira assunto
do chat principal (manutenção de memória é backstage, nunca o protagonista da conversa).

## Quando roda

- Manutencao/auditoria identificou arquivo novo na pasta de referencias.
- O operador cola um LINK ou arquivo de referência no chat (processa na hora, sem esperar o hook).
- Ele pede direto: "ingere essa referência", "processa a pasta de referências".

## Autonomia (nível: auto, com freio na regra)

- **Referência consultável** (resumo/acervo que o agente consulta depois): GRAVA sozinho. É reversível.
  - Geral (técnica, princípio, método aplicável ao trabalho do operador) → `{{CAMINHO_MEMORIA}}/references/<slug>.md`.
  - De projeto/cliente específico → pasta do projeto ou a memória daquele projeto. Nunca jogar no global o que é de um contexto específico.
- **Regra de trabalho** (muda como criamos SEMPRE, mexe em CLAUDE.md ou memória de regra): NÃO grava
  sozinho. Destila a proposta e devolve ao operador para aprovação. Irreversível confirma antes de gravar.

## Passo a passo

### 1. Achar o que ingerir
- Pasta: ler `{{PASTA_REFERENCIAS}}/_ingeridos.md` e varrer `{{PASTA_REFERENCIAS}}`; o que não
  está no manifesto e não é infra (`README.md`, `_*`, `.*`) é novo.
- Chat: o link/arquivo que o operador colou é o alvo.

### 2. Compreender (com o multimodal)
Escolher a ferramenta pelo tipo:

| Tipo | Como compreender |
|---|---|
| PDF | `pdftotext -layout arquivo.pdf -` (texto). Em PDF muito visual, também tentar `pdftoppm -png -r 100 arquivo.pdf out` e ler os PNGs com o Read; se `pdftoppm` faltar, ficar no texto. |
| .txt / .md | Read direto. |
| imagem (.png/.jpg/.jpeg/.webp/.gif) | Read multimodal (ver a imagem de fato). |
| vídeo (.mp4/.mov/.mkv/.webm) | extrair frames `ffmpeg -i v.mp4 -vf fps=1/5 frame_%03d.png` e Read nos frames + transcrever áudio com faster-whisper se disponível. |
| áudio (.ogg/.m4a/.wav/.mp3) | transcrever com faster-whisper local se disponível. |
| link YouTube/Short | baixar a transcrição (legenda automática via yt-dlp ou skill equivalente) → ler o .txt. |
| link de site/artigo | WebFetch (extrair o conteúdo). |

### 3. Extrair o que importa
Não copiar tudo: pegar o que vale ser reutilizado. Para cada referência, capturar:
- a IDEIA/decisão por trás (o pensamento, não só a aparência);
- o que dá para aplicar no trabalho habitual do operador;
- com o que já casa na memória existente (linkar se relevante).

### 4. Rotear o destino

A regra central: **a referência vai pro destino que a faz carregar só quando relevante.**

- É princípio/técnica GERAL de uma área que já tem guia de referência (`references/guia-*.md`)?
  → NÃO criar arquivo solto: incorporar a regra ao guia correspondente (adicionar/refinar a regra
  + ajustar o checklist) e logar em `decisions/log.md`. É assim que os guias melhoram com o tempo.
- É princípio/técnica GERAL sem guia próprio ainda? → referência global em `{{CAMINHO_MEMORIA}}/references/`.
- É de um cliente/projeto específico? → pasta/memória daquele projeto.
- Sugere mudar COMO trabalhamos sempre? → proposta de regra (não gravar; devolver ao operador).

### 5. Gravar e fechar
- Gravar a referência consultável no destino escolhido (criar/editar; não sobrescrever regra
  existente sem aprovação do operador).
- Atualizar `{{PASTA_REFERENCIAS}}/_ingeridos.md` (linha: arquivo/link, data, tipo, destino).
- Housekeeping: mídia pesada (vídeo/áudio) pode ser movida pra fora do repositório de memória
  e virar apenas catálogo; apagar arquivos temporários de frames/download.
- No máximo 1 linha discreta ao operador se algo foi gravado; proposta de regra, sim, mostrar.

## Não confundir

- Caçar referência nova na web (galerias, premiações, artigos) → outra skill ou busca manual.
- Destilar o aprendizado de uma SESSÃO de trabalho → `fecha-sessao`.
- Esta skill é sobre material que o OPERADOR TROUXE como referência.
