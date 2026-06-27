# Guardrails de autoevolucao do CORTEX

Uso: sob demanda
Escopo: sistema
Gatilho: melhorar o CORTEX, vibecoding do CORTEX, mudanca em memoria, hook, skill, settings ou template
Nao usar para: entrega sem mudanca no sistema

## Risco central

O CORTEX pode piorar quando o agente edita o proprio sistema por sensacao, sem teste, sem fronteira e sem revisao humana.

## Controles

| Risco | Controle |
| --- | --- |
| Regra demais | consolidar por tema, nao somar linha infinita no indice |
| Gatilho amplo | testar prompt positivo e negativo |
| Contaminacao pessoal | template leva mecanismo, instalado recebe aliases do usuario |
| Hook falante | `SessionStart` so alerta urgencia real |
| Drift entre agentes | declarar alvo antes de editar |
| Compactacao como muleta | preferir handoff curado e sessao nova |
| Sem retroatividade | declarar se aplica ao passado, mantem compatibilidade, marca stale ou cria migracao |
| Task esquecida | toda task relevante precisa de gatilho natural e sensor |
| Edicao invisivel | diff pequeno e registro de decisao |
| Sem rollback | backup quando tocar configuracao viva |
| Spam no terminal | trabalhar em lote, ocultar detalhe bruto e fechar com resumo |

## Permitido sem nova decisao

- adicionar alias de retrieval para arquivo ja existente;
- corrigir bug claro em hook com teste local;
- mover regra solta para arquivo-topico mantendo ponteiro;
- reduzir contexto automatico removendo aviso nao urgente;
- atualizar doc compartilhada para refletir decisao ja tomada.

## Exige confirmacao do usuario

- apagar memoria, skill, hook ou decisao;
- mudar sync, git, seguranca, modelo ou custo;
- ligar auto-compact, auto-push, auto-merge ou auto-poda;
- criar automacao que escreve sozinha em memoria;
- portar preferencia pessoal de um usuario para o template.

## Protocolo

1. Declarar alvo: compartilhado, agente, template ou nao portar.
2. Fazer patch minimo.
3. Testar gatilho positivo, negativo e frase parecida.
4. Medir impacto quando tocar boot, retrieval ou `MEMORY.md`.
5. Declarar impacto retroativo quando tocar regra, caminho, nome, asset, automacao ou template.
6. Registrar decisao quando mudar governanca.
7. Em terminal, relatar por resumo. Mostrar diff/log completo so sob pedido.
