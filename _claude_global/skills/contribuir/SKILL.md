---
name: contribuir
description: Empacota uma skill ou regra sua, limpa de dado pessoal, pra devolver a quem te passou o CORTEX. Use quando disser "quero contribuir", "mandar essa skill de volta", "devolver melhoria pro CORTEX", ou "/contribuir". NAO porta nada pro produto: so empacota pra voce enviar; quem mantem a versao decide se entra.
---

# Contribuir — devolver uma melhoria pra quem te passou o CORTEX

O CORTEX que voce usa veio de alguem (quem mantem e distribui a sua versao). Se voce criou uma
skill ou regra boa e generica, pode devolver pra essa pessoa, e ela pode entrar na proxima versao
que todo mundo recebe. Esta skill empacota a sua contribuicao num formato limpo e padrao, pronta
pra enviar. Ela nunca porta nada direto: a decisao de admitir e sempre de quem mantem o produto.

## Passo 1: O que voce quer contribuir?

Pergunte (uma escolha):
- Uma **skill** sua (uma pasta em `~/.claude/skills/`): pergunte qual.
- Uma **regra** ou **referencia** (um texto, um jeito de trabalhar, um fluxo).

## Passo 2: Limpe o que e SEU antes de empacotar (o cuidado central)

Uma contribuicao boa e generica: serve pra qualquer usuario. Antes de empacotar, varra o conteudo
e tire o que e pessoal seu, com a regua do onboard ao contrario:
- Seu nome, apelidos, @ → generico ou removido
- Nomes de cliente, pessoas, projetos seus → removidos ou `{{CLIENTE_EXEMPLO}}`
- Cor/token da sua marca, sua voz, seu nicho especifico → removidos ou `{{...}}`
- Caminhos absolutos do seu PC → `{{PASTA_RAIZ}}` / `{{CAMINHO_MEMORIA}}`
- Qualquer segredo, dado financeiro, numero real → removido

Se o conteudo tem dado pessoal demais entranhado (nao da pra generalizar limpo), avise:
"isso esta muito colado no seu contexto pra virar contribuicao; melhor reescrever generico antes".

## Passo 3: Empacote num formato padrao

Crie a pasta `contribuicoes-enviar/contribuicao-<slug>-<AAAA-MM-DD>/` com:

- `MANIFESTO.md` (o cartao da contribuicao):
  ```
  tipo: skill | regra | referencia
  titulo: <nome curto>
  autor: <seu nome ou @, opcional>
  data: AAAA-MM-DD
  resolve: <que problema resolve, quando usar — 1-2 linhas>
  ```
- O conteudo: a pasta da skill copiada (ja limpa), ou o texto em `conteudo.md` (regra/referencia).

## Passo 4: Entregue

Diga ao usuario: "Pronto. Manda a pasta (ou um zip dela) `<caminho>` pra quem te passou o CORTEX,
por onde for mais facil (mensagem, email, drive). Quem mantem a versao avalia e decide se entra no
produto. Voce nao precisa de acesso ao repo dela."

## Regras de implementacao

1. **Nunca porta direto.** Esta skill so empacota; quem admite no produto e quem mantem a versao.
2. **Limpeza de dado pessoal e obrigatoria.** Na duvida, avisa, nao empacota as cegas.
3. **Padroes editoriais da casa** em todo texto gerado.
