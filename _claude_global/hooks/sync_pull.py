#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_pull.py  —  Hook de SessionStart do CORTEX.

Puxa o que outra maquina enviou pro repo privado, ANTES de comecar a sessao, pra
voce sempre trabalhar com o contexto mais recente. Silencioso e falha-segura: se
nao houver repo, ou der erro de rede, nao trava o inicio da sessao.

CONFIGURE: ajuste REPO pro caminho do REPOSITORIO GIT de sync (a pasta que tem .git/).
Esse caminho e DIFERENTE da pasta de memoria dos hooks de aprendizado
(precompact_flush.py, nudge_destilacao.py): aqueles apontam pra pasta memory/ da memoria
do projeto; este aqui aponta pro repo git de sincronizacao entre maquinas.
"""
import subprocess
import sys
from pathlib import Path

# CONFIGURE: caminho do REPOSITORIO GIT de sync (a pasta que contem .git/).
# Diferente do {{CAMINHO_MEMORIA}} dos hooks de aprendizado — esse e o repo git de sync.
REPO = Path(r"{{REPO_SYNC}}")


def main():
    if not (REPO / ".git").exists():
        return  # sync nao configurado: nada a fazer, segue a vida
    try:
        subprocess.run(
            ["git", "pull", "--rebase", "--autostash", "--quiet"],
            cwd=str(REPO), timeout=30,
            capture_output=True, text=True,
        )
    except Exception:
        pass  # falha segura: nunca travar o inicio da sessao por causa de sync


if __name__ == "__main__":
    main()
    sys.exit(0)
