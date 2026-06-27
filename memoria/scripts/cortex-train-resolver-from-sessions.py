#!/usr/bin/env python3
"""Gera candidatos de aliases/evals para o Context Resolver a partir de sessoes.

Treino offline/backstage: le JSONL recentes, extrai so falas do usuario e produz
um artefato revisavel. Nao altera indices automaticamente.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path


HOME = Path.home()
CLAUDE_PROJECTS = HOME / ".claude" / "projects"
CODEX_SESSIONS = HOME / ".codex" / "sessions"
SCRIPT = Path(__file__).resolve()
MEMORIA = SCRIPT.parents[1]
OUT_DIR = MEMORIA / "indexes" / "training"
OUT_FILE = OUT_DIR / "resolver-session-candidates.json"


DOMAIN_PATTERNS = {
    "backstage-governanca": [
        "poluir meu chat",
        "poluindo meu chat",
        "ruido",
        "ruido de regras",
        "manutencao de regras",
        "backstage",
        "frisando regras",
        "aprimorar a cada dia",
        "custo beneficio de contexto",
    ],
    "memoria-contexto": [
        "context resolver",
        "resolver",
        "context engineering",
        "bootstrap",
        "inchaço",
        "inchaco",
        "nunca",
        "sempre",
        "tags",
        "retroativo",
        "contexto",
        "memoria",
    ],
    "destilacao-resolver": [
        "alimentar o resolver",
        "treinar resolver",
        "treinar context resolver",
        "json das sessoes",
        "pegar tudo",
        "sessoes antigas",
        "forma mais eficiente",
        "abandono destilar",
        "abandonar destilar",
    ],
    "update-template": [
        "atualizar",
        "update",
        "usuario antigo",
        "cortex antigo",
        "preservar",
        "nao apagar",
        "migracao",
    ],
    "orquestracao-fanout": [
        "fan out",
        "fan-out",
        "dispare",
        "subagente",
        "multiagent",
        "multiagente",
        "em paralelo",
    ],
    "orquestracao-operacao": [
        "portabilidade",
        "compativel",
        "plataformas",
        "claude",
        "codex",
        "cursor",
        "cline",
        "agents",
        "claude md",
    ],
    "design-premium-lp": [
        "landing",
        "lp-creator",
        "ta fraco",
        "generico",
        "hero",
        "design",
    ],
    "cliente-projeto": [
        "cliente",
        "cliente",
        "projeto do cliente",
        "identidade do cliente",
        "design system do cliente",
        "identidade do cliente",
    ],
    "git-seguranca": [
        "commit",
        "git",
        "github",
        "push",
        "branch",
    ],
    "repo-intacto-entregaveis": [
        "repo",
        "zip",
        "render",
        "print",
        "arquivo pesado",
        "gitignore",
    ],
    "seguranca-operacao": [
        "credencial",
        "token",
        "hook",
        "settings",
        "apagar memoria",
        "seguranca",
    ],
}


EXPECT = {
    "backstage-governanca": {
        "rules": ["backstage-nao-polui-chat", "gate-custo-beneficio-contexto"],
        "slices": ["backstage-mvp::regra-central", "backstage-mvp::gate-custo-beneficio"],
    },
    "memoria-contexto": {
        "rules": ["operador-nao-e-dominio", "bootstrap-linha-precisa-evitar-erro"],
        "slices": ["context-engineering::camadas", "acesso-contexto::escada"],
    },
    "destilacao-resolver": {
        "rules": ["resolver-treino-por-mapas-evals"],
        "slices": ["resolver-treino::pipeline-eficiente"],
    },
    "update-template": {
        "rules": ["update-preservar-usuario-antigo", "update-modo-legado-preserva-customizacao"],
        "slices": ["update-politica::regra-central", "update-politica::modo-legado"],
    },
    "orquestracao-fanout": {
        "rules": ["fanout-travado"],
        "slices": ["fanout::trava"],
    },
    "orquestracao-operacao": {
        "rules": ["paridade-multiagente"],
        "slices": ["paridade-multiagente::regra-mae"],
    },
    "design-premium-lp": {
        "rules": [],
        "slices": ["design-senior::regra-central", "anti-slop::lexico"],
    },
    "cliente-projeto": {
        "rules": ["identidade-projeto-sem-default"],
        "slices": ["cliente-projeto::identidade-do-projeto"],
    },
    "git-seguranca": {
        "rules": ["git-operacao-cirurgica"],
        "slices": ["git-seguranca::regra-vs-skill"],
    },
    "repo-intacto-entregaveis": {
        "rules": ["repo-intacto-entregaveis"],
        "slices": ["repo-intacto::regra-central"],
    },
    "seguranca-operacao": {
        "rules": ["autoevolucao-seguranca-stop"],
        "slices": ["guardrails-autoevolucao::parada-operador"],
    },
}


def normalize(text: str) -> str:
    text = text.lower()
    text = text.replace("—", "-").replace("–", "-")
    return re.sub(r"\s+", " ", text).strip()


def redact(text: str) -> str:
    text = re.sub(r"<private>.*?</private>", "[private]", text, flags=re.I | re.S)
    text = re.sub(r"\b\d{2,}\b", "[num]", text)
    text = re.sub(r"(?i)(token|senha|password|api[_ -]?key)\s*[:=]\s*\S+", r"\1=[redacted]", text)
    return text


def flatten_content(value) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts = []
        for item in value:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                if item.get("type") in {"text", "input_text", "output_text"}:
                    parts.append(str(item.get("text") or ""))
                elif "content" in item:
                    parts.append(flatten_content(item.get("content")))
        return "\n".join(p for p in parts if p)
    if isinstance(value, dict):
        return flatten_content(value.get("content") or value.get("text"))
    return ""


def extract_user_text(obj: dict) -> str:
    msg = obj.get("message")
    if isinstance(msg, dict) and msg.get("role") == "user":
        return flatten_content(msg.get("content"))

    payload = obj.get("payload")
    if isinstance(payload, dict):
        if payload.get("role") == "user":
            return flatten_content(payload.get("content"))
        if payload.get("type") == "message" and payload.get("role") == "user":
            return flatten_content(payload.get("content"))
        if payload.get("type") in {"input_text", "user_message"}:
            return flatten_content(payload.get("text") or payload.get("content"))

    if obj.get("type") == "user":
        return flatten_content(obj.get("text") or obj.get("content"))
    return ""


def is_noise(text: str) -> bool:
    norm = normalize(text)
    if not norm:
        return True
    path_like_hits = len(re.findall(r"(?:[a-z]:\\|/users/|/c/|\\users\\|\\cortex\\|\\.claude\\|\\.codex\\)", norm))
    file_ext_hits = len(re.findall(r"\.(?:md|json|jsonl|html|css|js|py|png|jpg|mp4|mov|zip|toml|yaml|yml)\b", norm))
    code_markers = len(re.findall(r"\b(?:const|function|import|export|return|class|def|from|var|let)\b|[{}</>;]", norm))
    noise_fragments = [
        "file state is current",
        "has been updated successfully",
        "<environment_context>",
        "<codex_internal_context",
        "<command-message>",
        "# agents.md instructions",
        "base directory for this skill:",
        "base_instructions",
        "session_meta",
        "tool_calls",
        "function_call_output",
        "pretooluse:",
        "hook error:",
        "perfil compacto",
        "the user opened the file",
        "<system-reminder>",
        "<local-command-stdout>",
        "launching skill:",
        "this session is being continued from a previous conversation",
        "invalid_request_error",
        "você é 1 agente de uma frota",
        "voce e 1 agente de uma frota",
        "the server returned http",
        "shell cwd was reset",
        "temporary-screenshots/",
        "<tool_use_error>",
        "<persisted-output>",
        "you are optimizing a skill description",
        "claude code settings.json validation failed",
        "checking mcp server health",
        "requested permissions to edit",
        "whisper_print_timings",
        "cloning into",
        "fatal: unable to access",
        "page.screenshot:",
        "node:internal/process",
        "triggeruncaughtexception",
        "output too large",
        "full output saved to:",
        "download webpage",
        "extracting url:",
        "tool_use",
        "tool result",
    ]
    if any(fragment in norm for fragment in noise_fragments):
        return True
    if norm.startswith(("the file c:", "the file /", "o arquivo c:", "--- name:", "# /continuar", "# handoff")):
        return True
    if re.match(r"^\d+\s+", norm) or norm.startswith("[num]"):
        return True
    if norm.startswith(("{\"type\":\"error\"", "set model to ", "total [num]", "name kb", "pronto:", "const ", "/*")):
        return True
    if path_like_hits >= 3 or file_ext_hits >= 8:
        return True
    if code_markers >= 30 and len(norm) > 350:
        return True
    if len(norm) > 240 and len(re.findall(r"\\|/|{|}|;|<|>", norm)) > len(norm) * 0.08:
        return True
    return False


def iter_jsonl(path: Path):
    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue
    except OSError:
        return


def session_roots(all_projects: bool) -> list[Path]:
    roots: list[Path] = []
    if all_projects and CLAUDE_PROJECTS.exists():
        roots.extend(p for p in CLAUDE_PROJECTS.iterdir() if p.is_dir())
    else:
        roots.extend([
            CLAUDE_PROJECTS / "c--CORTEX",
        ])
    return roots


def session_files(days: int, older_than_days: int | None, all_projects: bool, max_files: int | None) -> list[Path]:
    now = datetime.now().timestamp()
    newer_cutoff = now - days * 86400 if days > 0 else None
    older_cutoff = now - older_than_days * 86400 if older_than_days is not None else None
    roots = session_roots(all_projects)
    files: list[Path] = []
    for root in roots:
        if root.exists():
            files.extend(root.glob("*.jsonl"))
    if CODEX_SESSIONS.exists():
        files.extend(CODEX_SESSIONS.rglob("*.jsonl"))

    selected = []
    seen = set()
    for path in files:
        key = str(path.resolve()).lower()
        if key in seen:
            continue
        seen.add(key)
        try:
            mtime = path.stat().st_mtime
        except OSError:
            continue
        if older_cutoff is not None:
            if mtime > older_cutoff:
                continue
        elif newer_cutoff is not None and mtime < newer_cutoff:
            continue
        selected.append(path)

    selected = sorted(selected, key=lambda p: p.stat().st_mtime, reverse=True)
    if max_files is not None:
        selected = selected[:max_files]
    return selected


def evidence_source(path: Path) -> dict:
    try:
        raw = str(path.resolve()).lower()
    except OSError:
        raw = str(path).lower()
    kind = "codex-session" if ".codex" in raw else "claude-session" if ".claude" in raw else "session"
    return {
        "kind": kind,
        "id": hashlib.sha1(raw.encode("utf-8", errors="replace")).hexdigest()[:12],
    }


def classify(text: str) -> tuple[str, list[str], int]:
    norm = normalize(text)
    scores = {}
    hits_by_domain = {}
    for domain, patterns in DOMAIN_PATTERNS.items():
        hits = [p for p in patterns if p in norm]
        if hits:
            scores[domain] = len(hits)
            hits_by_domain[domain] = hits
    if not scores:
        return "", [], 0
    domain = max(scores, key=scores.get)
    return domain, hits_by_domain[domain], scores[domain]


def make_aliases(text: str, hits: list[str]) -> list[str]:
    norm = normalize(text)
    aliases = set(hits)
    chunks = re.split(r"[?.!,;\n]", norm)
    for chunk in chunks:
        chunk = chunk.strip()
        if 12 <= len(chunk) <= 90 and any(h in chunk for h in hits):
            aliases.add(chunk)
    return sorted(aliases, key=lambda s: (len(s), s))[:8]


def train(days: int, max_candidates: int, older_than_days: int | None, all_projects: bool, max_files: int | None) -> dict:
    candidates = {}
    counters = Counter()
    scanned = 0
    user_messages = 0

    for path in session_files(days, older_than_days, all_projects, max_files):
        scanned += 1
        for obj in iter_jsonl(path):
            text = redact(extract_user_text(obj))
            if not text or len(text) < 8 or is_noise(text):
                continue
            user_messages += 1
            domain, hits, score = classify(text)
            if not domain:
                continue
            counters[domain] += 1
            query = normalize(text)
            if len(query) > 180:
                query = query[:177].rsplit(" ", 1)[0] + "..."
            key = (domain, query)
            if key in candidates:
                candidates[key]["frequency"] += 1
                continue
            expected = EXPECT.get(domain, {"rules": [], "slices": []})
            candidates[key] = {
                "domain_guess": domain,
                "phrase": query,
                "aliases": make_aliases(text, hits),
                "negative_aliases": [],
                "eval_query": query,
                "expect_domain": domain,
                "expect_rules": expected["rules"][:1],
                "expect_slices": expected["slices"][:1],
                "evidence_source": evidence_source(path),
                "confidence": "high" if score >= 2 else "medium",
                "frequency": 1,
                "cost_benefit": "revisar antes de promover; candidato veio de fala real dos ultimos dias",
            }

    ranked = sorted(
        candidates.values(),
        key=lambda x: (x["frequency"], len(x["aliases"]), x["confidence"] == "high"),
        reverse=True,
    )[:max_candidates]
    return {
        "source": "claude-and-codex-sessions",
        "generated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "session_window_days": days,
        "older_than_days": older_than_days,
        "all_projects": all_projects,
        "max_files": max_files,
        "files_scanned": scanned,
        "user_messages_seen": user_messages,
        "domain_counts": dict(counters.most_common()),
        "candidates": ranked,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=10)
    parser.add_argument("--older-than-days", type=int)
    parser.add_argument("--all-projects", action="store_true")
    parser.add_argument("--max-files", type=int)
    parser.add_argument("--max-candidates", type=int, default=80)
    parser.add_argument("--out", default=str(OUT_FILE))
    args = parser.parse_args(argv)

    data = train(args.days, args.max_candidates, args.older_than_days, args.all_projects, args.max_files)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": True,
        "out": str(out),
        "files_scanned": data["files_scanned"],
        "user_messages_seen": data["user_messages_seen"],
        "candidates": len(data["candidates"]),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
