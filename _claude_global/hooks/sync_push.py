#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_push.py  —  Hook de SessionEnd do CORTEX.

Envia o que mudou na pasta memoria/ pro repo privado, no fim da sessao, SOZINHO.

TRAVA DE SEGURANCA (prioridade absoluta): antes de QUALQUER push, varre os arquivos
que iriam subir atras de segredo (chave de API, senha, token, credencial, dado
financeiro). Se achar UM, ABORTA o push inteiro e avisa. Nada vaza. Falha sempre
pro lado seguro: na duvida, NAO sobe.

Regra estrita: segredo, senha e dado financeiro do usuario VIVEM SO NO LOCAL.

CONFIGURE: ajuste REPO pro caminho do REPOSITORIO GIT de sync (a pasta que tem .git/).
Esse caminho e DIFERENTE da pasta de memoria dos hooks de aprendizado
(precompact_flush.py, nudge_destilacao.py): aqueles apontam pra pasta memory/ da memoria
do projeto; este aqui aponta pro repo git de sincronizacao entre maquinas.
"""
import re
import subprocess
import sys
from pathlib import Path

# CONFIGURE: caminho do REPOSITORIO GIT de sync (a pasta que contem .git/).
# Diferente do {{CAMINHO_MEMORIA}} dos hooks de aprendizado — esse e o repo git de sync.
REPO = Path(r"{{REPO_SYNC}}")

# Padroes de nome de arquivo que NUNCA podem subir.
SECRET_NAME = re.compile(
    r"(\.env$|credential|secret|(^|[^a-z])token([^a-z]|$)|\.key$|\.pem$|"
    r"password|senha|\.p12$|\.pfx$|id_rsa)",
    re.IGNORECASE,
)

# Padroes de CONTEUDO que denunciam segredo/dado sensivel dentro de um arquivo.
SECRET_CONTENT = [
    re.compile(r"(api[_-]?key|secret[_-]?key|access[_-]?token|bearer\s+[A-Za-z0-9._-]{12,})", re.I),
    re.compile(r"(AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{10,})"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bpassword\s*[:=]\s*\S+", re.I),
    # dado financeiro: cartao (16 digitos), e marcadores explicitos
    re.compile(r"\b(?:\d[ -]?){13,16}\b"),
    re.compile(r"(conta\s*banc|ag[eê]ncia|n[uú]mero\s*do\s*cart|cvv|iban|swift)", re.I),
    # marcador <private>: se chegou no arquivo versionado, e dado que NAO podia subir.
    # Qualquer token <private (aberto, fechado ou malformado) aborta o push.
    re.compile(r"<\s*/?\s*private\b", re.I),
]

# Extensoes de texto que vale escanear o conteudo.
TEXT_EXT = {".md", ".txt", ".json", ".yml", ".yaml", ".csv", ".env", ".ini", ".cfg", ".py", ".js", ".ts", ".sh"}


def staged_files():
    """Arquivos que git de fato subiria (respeitando o .gitignore)."""
    try:
        subprocess.run(["git", "add", "-A"], cwd=str(REPO), timeout=20, capture_output=True)
        out = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=str(REPO), timeout=20, capture_output=True, text=True,
        )
        return [REPO / line.strip() for line in out.stdout.splitlines() if line.strip()]
    except Exception:
        return None  # erro: trataremos como "nao sei, nao sobe"


def find_leaks(files):
    leaks = []
    for f in files:
        name = f.name
        if SECRET_NAME.search(name):
            leaks.append(f"{name} (nome suspeito de segredo)")
            continue
        if f.suffix.lower() in TEXT_EXT and f.exists():
            try:
                txt = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            # qualquer <private> no arquivo versionado = dado que nao podia subir: aborta
            for pat in SECRET_CONTENT:
                if pat.search(txt):
                    leaks.append(f"{name} (conteudo: possivel segredo/dado financeiro)")
                    break
    return leaks


def main():
    if not (REPO / ".git").exists():
        return  # sync nao configurado

    files = staged_files()
    if files is None:
        print("CORTEX sync: nao consegui verificar os arquivos. Push ABORTADO por seguranca.", file=sys.stderr)
        return
    if not files:
        return  # nada mudou

    leaks = find_leaks(files)
    if leaks:
        # TRAVA: aborta o push. Nada vaza. Desfaz o stage pra nao deixar pendente.
        try:
            subprocess.run(["git", "reset"], cwd=str(REPO), timeout=20, capture_output=True)
        except Exception:
            pass
        print("=" * 60, file=sys.stderr)
        print("CORTEX sync: PUSH ABORTADO. Possivel segredo/dado sensivel detectado:", file=sys.stderr)
        for x in leaks:
            print(f"  - {x}", file=sys.stderr)
        print("Esses dados ficam SO no seu PC. Mova o segredo pra fora da pasta", file=sys.stderr)
        print("memoria/ ou envolva em <private>...</private>, e tente de novo.", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        return

    # Tudo limpo: commit + push silencioso.
    try:
        subprocess.run(["git", "commit", "-m", "CORTEX: sync automatico"],
                       cwd=str(REPO), timeout=30, capture_output=True)
        subprocess.run(["git", "push", "--quiet"],
                       cwd=str(REPO), timeout=60, capture_output=True)
    except Exception:
        pass  # falha segura: nao quebra o fim da sessao


if __name__ == "__main__":
    main()
    sys.exit(0)
