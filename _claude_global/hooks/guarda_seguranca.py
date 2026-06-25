#!/usr/bin/env python3
"""
Guarda de segurança (PreToolUse) do CORTEX OS.

Intercepta comandos de Bash/PowerShell ANTES de rodar e BLOQUEIA o destrutivo óbvio.
Filosofia (do vídeo de boas práticas de agentes): tudo que o agente pode tocar, assuma
que ele vai tocar, mesmo sem você pedir. Esta é uma rede de proteção contra ACIDENTE e
erro de interpretação, NÃO um cofre contra agente mal-intencionado (burlar com
script em 2 passos é possível; cobrir todo loophole é impossível).

Calibragem padrão: bloquear só o destrutivo óbvio, deixar o resto passar.
Retorno: exit 0 = libera; exit 2 = BLOQUEIA (o Claude para e avisa o operador).
"""
import json
import re
import sys

# Padrões que BLOQUEIAM. Cada um: (regex, motivo mostrado ao operador).
PADROES_BLOQUEIO = [
    # Remoção recursiva ampla (rm -rf, Remove-Item -Recurse -Force)
    (r"\brm\s+(-[a-zA-Z]*r[a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*r|-rf|-fr)\b",
     "rm recursivo e forçado: pode apagar pasta inteira."),
    (r"Remove-Item\b.*-Recurse\b.*-Force|Remove-Item\b.*-Force\b.*-Recurse",
     "Remove-Item -Recurse -Force: pode apagar pasta inteira."),
    # Git destrutivo de histórico/trabalho
    (r"\bgit\s+push\b.*(--force\b|-f\b|--force-with-lease\b)",
     "git push forçado: reescreve histórico remoto."),
    (r"\bgit\s+reset\s+--hard\b",
     "git reset --hard: descarta trabalho local não commitado."),
    (r"\bgit\s+clean\s+-[a-zA-Z]*f",
     "git clean -f: apaga arquivos não rastreados."),
    # Push não autorizado (o operador publica quando manda explicitamente)
    (r"\bgit\s+push\b(?!.*--dry-run)",
     "git push: o operador só publica quando manda explicitamente."),
    # Leitura de segredo + envio para fora (exfiltração acidental)
    (r"(curl|wget|Invoke-WebRequest|Invoke-RestMethod)\b.*(\.env|secret|token|password|senha|credential|api[_-]?key)",
     "requisição externa tocando arquivo de segredo: risco de vazamento."),
    (r"(cat|type|Get-Content)\b.*\.env\b.*\|(.*)(curl|wget|nc|Invoke-)",
     "lendo .env e mandando para fora: risco de vazamento."),
    # Sobrescrever disco / formatar (raro, mas catastrófico)
    (r"\b(mkfs|dd\s+if=.*of=/dev/|format\s+[a-zA-Z]:)\b",
     "operação de disco de baixo nível: catastrófico."),
]


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        # Sem payload legível: não bloqueia (não travar o trabalho por erro de parsing).
        sys.exit(0)

    tool = payload.get("tool_name", "")
    if tool not in ("Bash", "PowerShell"):
        sys.exit(0)

    comando = (payload.get("tool_input", {}) or {}).get("command", "")
    if not comando:
        sys.exit(0)

    for regex, motivo in PADROES_BLOQUEIO:
        if re.search(regex, comando, re.IGNORECASE):
            print(
                "BLOQUEADO pela guarda de segurança do CORTEX OS.\n"
                f"Motivo: {motivo}\n"
                f"Comando: {comando}\n"
                "Se for intencional, o operador pode rodar manualmente ou pedir bypass pontual.",
                file=sys.stderr,
            )
            sys.exit(2)  # exit 2 = bloqueia e devolve a mensagem ao Claude

    sys.exit(0)


if __name__ == "__main__":
    main()
