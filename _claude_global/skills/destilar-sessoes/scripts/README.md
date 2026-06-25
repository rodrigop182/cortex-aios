# Scripts do destilar-sessoes

Pipeline de destilacao de sessoes do Claude Code em conhecimento duravel e narrativas de projeto.
Todos os scripts usam o SDK Python da Anthropic (Haiku por padrao — barato e rapido).

---

## Scripts

### extrai.py

**O que faz:** Le os arquivos `.jsonl` de historico de sessoes do Claude Code e gera `.txt`
enxutos em `_catchup/enxutos/`. Etapa 1 do pipeline — sem chamada de modelo, so parsing.

**Uso:**
```
python extrai.py [--sessoes DIR] [--out DIR] [--desde DATA]
```

Nao requer configuracao de projetos ou caminhos de memoria.

---

### sintetiza.py

**O que faz:** Le os `.txt` de `_catchup/enxutos/`, agrupa em lotes por projeto/tema,
chama o Haiku pra extrair REGRAS abstratas por conceito e salva artigos em `<wiki>/`.
Tambem regenera o `index.md` do wiki. Padrao Karpathy: conhecimento por conceito, nao por sessao.

**Uso:**
```
python sintetiza.py [--enxutos DIR] --wiki PASTA_WIKI [--dry-run]
```

`--wiki` e obrigatorio: aponta pra `{{CAMINHO_MEMORIA}}/wiki` (ou o equivalente no seu CORTEX).

**O que configurar antes de usar:**

1. `PROJETOS` — lista de `(slug, [keywords])` para classificar sessoes por projeto.
   Ordem importa: primeiro match vence. Ultimo item pode ser `("geral", [])` como fallback.

2. `CONCEITOS` — categorias de conhecimento que o extrator vai usar. Os defaults cobrem
   a maioria dos casos; ajuste so se seu CORTEX rastrear dominios muito diferentes.

3. `TEMPLATE_FILA` (opcional) — caminho para um arquivo `.md` onde achados `cortex-geral`
   sao enfileirados. Default e `None` (desabilitado). Defina como string de caminho se quiser.

4. `RETRIEVAL_MAPA_PATH` / `RETRIEVAL_RUIDO_PATH` (opcional) — caminhos para o hook
   `retrieval_topico.py` e o arquivo de relatorio de ruido. Default e `None` (desabilitado).
   Defina so se voce usa o hook de retrieval por topico.

---

### narra.py

**O que faz:** Le os `.txt` de `_catchup/enxutos/`, classifica por projeto e gera uma
NARRATIVA CRONOLOGICA em markdown por projeto — o que foi feito, o que foi descartado,
o que ficou. Diferente do `sintetiza.py` (que extrai regras), este script conta a historia
do projeto. Saida: `<out>/<slug>-narrativa.md`.

**Uso:**
```
python narra.py [--enxutos DIR] [--out DIR] [--dry-run] [--projeto SLUG]
```

`--out` aponta para `{{CAMINHO_MEMORIA}}/projects` por default.
`--projeto` processa so um projeto especifico (util pra rodar manualmente).

**O que configurar antes de usar:**

1. `PROJETOS` — mesmo formato do `sintetiza.py`. Sessoes que nao casam com nenhum
   projeto sao IGNORADAS (narra.py nao tem fallback "geral" — narrativa sem projeto e ruido).

2. `NOMES_DISPLAY` — dict `{slug: "Nome Legivel"}` para o cabecalho da narrativa.
   Adicione uma entrada por slug em `PROJETOS`.

3. `DEFAULT_OUT` — caminho default de saida. Substitua `{{CAMINHO_MEMORIA}}` pelo
   caminho real da sua pasta de memoria.

---

## Como configurar PROJETOS (sintetiza.py e narra.py)

```python
PROJETOS = [
    ("meu-cliente",  ["nome-do-cliente", "apelido", "produto"]),
    ("site-proprio", ["site proprio", "landing", "portfolio"]),
    ("cortex",       ["cortex", "catch-up", "catchup", "destilacao"]),
    ("geral",        []),  # fallback — so no sintetiza.py; no narra.py omita
]
```

- O `slug` vira nome do arquivo de saida.
- As keywords sao testadas em lowercase contra o conteudo do enxuto.
- Primeiro match vence — coloque os mais especificos antes.

## Como substituir os placeholders

| Placeholder | O que colocar |
|---|---|
| `{{CAMINHO_MEMORIA}}` | Caminho absoluto da sua pasta de memoria (ex: `C:/MeuCortex/memoria`) |
| `{{PASTA_CLAUDE}}` | Caminho da pasta `.claude` do usuario (ex: `C:/Users/meu-user/.claude`) |
| `{{NOME_OPERADOR}}` | Seu nome (ex: `Maria Silva`) |
| `{{DESCRICAO_OPERADOR}}` | Sua descricao profissional (ex: `dev + designer que trabalha com SaaS`) |

Os placeholders nos prompts do `sintetiza.py` e `narra.py` contextualizam o Haiku
sobre quem e o operador. Substituir melhora a qualidade da extracao, mas nao e obrigatorio
para o pipeline funcionar.

---

## Ordem de execucao

```
extrai.py  →  sintetiza.py  →  narra.py (opcional)
             └→ wiki/<conceito>.md      └→ projects/<slug>-narrativa.md
             └→ wiki/index.md
```

O `narra.py` pode rodar independente do `sintetiza.py` — ambos leem os mesmos enxutos.
