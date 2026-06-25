# Plano, peso e custo — como o CORTEX gasta seus tokens

> **Status:** o produto-foco do CORTEX é o cérebro COMPLETO (geral), pensado pra quem não tem
> aperto de token agora. O cérebro enxuto (LITE) existe e funciona, mas é uma otimização que será
> LAPIDADA depois que o geral estiver redondo. Se você tem folga de tokens, use o completo; o LITE
> é pra mais adiante, pra quem precisar.


A regra de ouro do CORTEX: **o plano é o teto, o peso da tarefa é o gasto.** Seu plano de IA
define quanto o CORTEX PODE puxar; o que ele REALMENTE gasta segue a tarefa. Tarefa simples é
leve em qualquer plano. A folga de um plano maior só aparece em tarefa complexa, e vira
qualidade, não desperdício.

## A matriz (o que decide o gasto)

| | **Tarefa SIMPLES** (troca/acha algo, fato) | **Tarefa COMPLEXA** (cria/refaz, decisão, vários passos) |
|---|---|---|
| **Plano ~$20 (teto baixo)** | Mínimo: núcleo só (~650 tok no cérebro enxuto), sem puxar memória/nicho | Puxa o essencial, verificação frugal (1 passe) |
| **Plano ~$100 (teto alto)** | **Igual ao $20**: mínimo. Nunca queimo seus tokens no trivial | Aproveita a folga em QUALIDADE: grill-me, subagente verificador, re-teste |

O ponto-chave: a linha "simples" é **igual nos dois planos**. Ter $100 não faz "troca essa cor"
custar mais. A diferença entre planos só existe na coluna "complexa".

## Por que isso funciona

O que pesa num assistente não é "saber muito", é carregar muito em todo turno. O CORTEX carrega um
núcleo mínimo sempre, e puxa o resto (regras detalhadas, nicho, memória, verificação) só quando a
tarefa pede. Então:
- **Tarefa simples:** roda no núcleo. Barata em qualquer plano.
- **Tarefa complexa:** puxa contexto e verificação até o teto do plano. O $100 capricha mais na
  confiança do resultado; o $20 entrega sólido, só mais enxuto na checagem.

## Os dois cérebros (consequência do plano)

O plano define qual cérebro você instala, mas os dois sabem e fazem as MESMAS coisas:

| | Cérebro enxuto (~$20) | Cérebro completo (~$100) |
|---|---|---|
| Arquivo | `CLAUDE-LITE.md` | `CLAUDE.md` |
| Núcleo por turno | 63 linhas | 86 linhas |
| Regras, skills, memória | Todas iguais | Todas iguais |
| Verificação em tarefa complexa | Frugal | Caprichada (folga vira qualidade) |
| Loop de aprendizado | Manual (`/fecha-sessao`) | Automático (hooks) |

**O enxuto NÃO corta capacidade:** mesmas skills, mesmas regras, mesmo one-shot, mesmo leque de
opções. Corta verbosidade, leitura proativa e automação de hooks. Tudo reversível.

## Instalar e trocar

```bash
# plano básico (~$20): cérebro enxuto (execute da raiz do pacote)
cp lite/CLAUDE-LITE.md   ~/.claude/CLAUDE.md
# plano folgado (~$100): cérebro completo
cp _claude_global/CLAUDE.md   ~/.claude/CLAUDE.md
```

Trocar a qualquer hora: copie o outro por cima. Sua `memoria/` e o `intake.md` continuam valendo,
só o cérebro troca de tamanho. Pode pedir "muda pro cérebro enxuto" e eu faço.

## Economia que vale em qualquer plano

- Trocou de assunto? `/clear`. Contexto velho atrapalha e custa.
- Tarefa simples: peça resposta direta, sem plano longo.
- Nicho e referências: lidos só quando a tarefa exige, nunca "por garantia".
- Calibre o esforço pelo PESO da tarefa, não pelo modelo aberto nem pelo tamanho do plano.
