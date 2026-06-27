# Retroatividade operacional do CORTEX

Uso: antes de declarar pronta uma mudanca que altera regra, caminho, nome, marca, identidade, asset, automacao, template ou comportamento do CORTEX.
Escopo: CORTEX instalado, projetos, automacoes e template distribuivel.
Gatilho: "isso vale para o que ja fizemos?", "mudar logo", "trocar nome de pasta", "caminho antigo", "feature nova", "link quebrado", "retroativo".
Nao usar para: ajuste pequeno que so afeta um arquivo isolado e nao deixa referencia futura.

## Regra central

Mudanca nova so esta pronta quando responde o que acontece com o passado.

Saidas possiveis:

- `aplicar agora`: atualizar os lugares antigos afetados no mesmo turno.
- `manter compatibilidade`: deixar alias, redirecionamento, ponteiro, README ou caminho antigo funcionando.
- `marcar stale`: registrar que um artefato antigo ficou desatualizado e precisa regenerar quando voltar a ser usado.
- `criar migracao`: abrir item com dono, criterio de pronto e sensor.
- `nao aplica`: justificar por que a mudanca so vale daqui para frente.

## Exemplos

- Logotipo: fonte e templates vivos mudam; exports antigos precisam regenerar ou ser marcados como stale.
- Caminho/pasta: buscar referencias antigas, atualizar links e manter alias quando possivel.
- Feature nova: testar em dados antigos ou criar migracao controlada.

## Sensor minimo

- `rg` por nome, caminho, cor, slug ou arquivo antigo.
- `Test-Path` para caminhos principais.
- screenshot ou build quando identidade visual muda.
- dry-run quando mover, renomear ou reescrever muitos arquivos.

## Criterio de pronto

- a mudanca declarou se aplica ao passado;
- o retroativo pequeno foi corrigido;
- o retroativo grande virou migracao com dono, criterio e sensor;
- o que ficou antigo esta marcado ou continua compativel.
