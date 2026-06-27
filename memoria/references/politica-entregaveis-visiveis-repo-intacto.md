# Politica de entregaveis visiveis e repo intacto

Uso: antes de gerar, salvar, mover ou organizar entrega, render, pacote, imagem, video, zip, PDF pesado, print de QA ou arquivo final dentro do CORTEX.
Escopo: raiz, projetos, repo e contexto.
Gatilho: "entrega", "output", "arquivo pesado", "zip", "render", "print", "quero ver no CORTEX", "nao lotar repo".

## Regra central

Entregavel com dono fica dentro da pasta do dono, visivel no editor, mas fora do repo e fora do contexto automatico.

`<CORTEX_ROOT>` e a pasta CORTEX escolhida pelo usuario, com default `C:\CORTEX`.

O CORTEX nao esconde a producao em uma pasta externa sem contexto. Ele organiza a producao perto do projeto e protege o repo por convencao de pastas, `.gitignore` e manifesto leve.

## Arvore de destino

1. Tem cliente/projeto de trabalho? `<CORTEX_ROOT>/projects/<projeto>/_entregas/` ou pasta de projeto equivalente criada pelo usuario.
2. E marca/empresa do operador? Usar a pasta de operacao definida no setup, com `_entregas/`.
3. E produto proprio? `<CORTEX_ROOT>/produtos/<produto>/_entregas/`, se existir essa categoria.
4. E ferramenta interna? `<CORTEX_ROOT>/ferramentas/<ferramenta>/_entregas/` ou `_prints/` se for QA.
5. Nao tem dono claro ainda? `<CORTEX_ROOT>/_local/quarentena/` ate triar.
6. E saida transversal sem projeto? `<CORTEX_ROOT>/_local/saidas/geradas/`.

`memory/` e `projects/` guardam estado textual, plano, registro e indice. Nao guardam pacote pesado.

## Pastas locais padrao dentro de qualquer projeto

| Pasta | Uso |
| --- | --- |
| `_entregas/` | arquivos finais, zips, PDFs pesados, pacotes para cliente/comprador |
| `_renders/` | videos, exports, renders e builds pesados |
| `_prints/` | screenshots, QA visual e evidencias |
| `_downloads/` | midia baixada ou insumos externos |
| `_assets-pesados/` | fonte pesada necessaria para o projeto, mas fora do repo |
| `_referencias-binarias/` | referencias de midia/design que nao devem virar contexto bruto |
| `_tmp/` | trabalho descartavel local |

Cada pasta pesada pode ter `README.md`, `MANIFESTO.md`, `MANIFEST.md`, `_manifest.json` ou `index.md` leve e versionavel. O arquivo pesado fica ignorado.

## Sempre

- Resolver `<CORTEX_ROOT>` antes de montar caminho.
- Guardar entregaveis pesados dentro da pasta do projeto quando eles forem parte operacional daquele projeto.
- Proteger o git antes de colocar arquivo pesado dentro de um repo.
- Criar manifesto leve ao lado dos arquivos pesados.
- Registrar em `projects/` apenas resumo textual, decisoes, status, caminhos e lacunas.
- Abrir midia/binario somente quando a tarefa pedir ou quando o manifesto indicar que aquele arquivo muda a proxima acao.
- Preferir metadados antes do arquivo bruto: nome, extensao, tamanho, duracao, resolucao, data, checksum e manifesto.

## Nunca

- Nunca colocar arquivo pesado diretamente em `memory/`, `projects/`, `references/` ou indice canonico.
- Nunca transformar memoria em deposito de PDF, video, ZIP, PSD, banco, backup, imagem bruta ou render final.
- Nunca fazer busca recursiva que leia conteudo de binarios/midia sem filtro.
- Nunca abrir video, audio, imagem, PDF grande, ZIP ou arquivo de design so para "entender o projeto" se houver manifesto ou indice leve suficiente.
- Nunca versionar entregaveis pesados por acidente.
- Nunca usar `.gitignore` como licenca para despejar lixo no projeto. Entregavel pesado precisa ter dono, motivo e manifesto.

## Protocolo para agentes

1. Ler o indice leve do projeto.
2. Ler `MANIFESTO.md`, `MANIFEST.md` ou `_manifest.json` se existir.
3. Verificar git status se a acao puder afetar repo.
4. Abrir midia/binario so se for necessario para a tarefa atual.
5. Ao criar entrega pesada, criar ou atualizar manifesto leve.
6. Ao finalizar, reportar caminho do entregavel e protecao git verificada.

## Criterio de pronto

- Entrega pesada esta no lugar certo.
- Editor consegue enxergar a pasta.
- Git continua limpo ou com mudancas esperadas.
- Memoria contem so ponteiro leve.
- Agente futuro sabe quando abrir o arquivo bruto.
