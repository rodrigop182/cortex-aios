# Gatilhos operacionais do CORTEX

Uso: quando uma task, sensor, script ou automacao operacional for criada.
Escopo: agentes, cockpit, scripts e template distribuivel.
Gatilho: "nao vou lembrar de usar", "isso era para acionar sozinho", "task", "comando manual", "gatilho predefinido".
Nao usar para: comando destrutivo, publicacao, push, apagamento ou migracao fisica sem confirmacao.

## Regra central

Task manual e fallback. O caminho principal e gatilho natural no agente.

Toda task operacional relevante precisa declarar:

- `gatilho de fala`: frases do usuario que devem acionar a checagem.
- `sensor`: script, busca, checklist, screenshot ou teste que roda.
- `auto`: se pode rodar sozinho ou se precisa perguntar.
- `fallback manual`: nome da task no VS Code ou comando equivalente.
- `saida esperada`: o que o agente deve fazer com o resultado.

## Nivel de automacao

- Sensor read-only: pode rodar sozinho.
- Escrita leve append-only: so com intencao clara.
- Mudanca em arquivo vivo: fazer com diff e verificacao.
- Irreversivel ou grande: perguntar antes.

## Criterio de pronto

Uma task esta pronta quando:

- aparece como fallback manual ou comando documentado;
- tem gatilho natural documentado;
- o agente sabe quando rodar sem o usuario lembrar;
- comando foi testado;
- risco de escrita/destruicao esta bloqueado.
