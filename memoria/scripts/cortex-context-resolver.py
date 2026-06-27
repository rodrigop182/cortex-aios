#!/usr/bin/env python3
"""Resolve consultas do CORTEX para pequenos slices de contexto.

Ferramenta sob demanda: nao injeta nada no boot. O objetivo e escolher dominio,
regra e heading provavel antes de qualquer leitura grande.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

SCRIPT = Path(__file__).resolve()
if SCRIPT.parents[1].name.lower() == "memoria":
    # Package/source layout: <template>/memoria/scripts/*.py
    MEMORIA = SCRIPT.parents[1]
    CORTEX = MEMORIA.parent
else:
    # Installed layout: <CORTEX>/scripts/*.py after memoria/ is copied flat.
    MEMORIA = SCRIPT.parents[1]
    CORTEX = MEMORIA
INDEXES = MEMORIA / "indexes"
MD_MANIFEST = INDEXES / "md-manifest.json"
DEFAULT_MAX_SLICES = 3
DEFAULT_MAX_CONTEXT_CHARS = 4800
MIN_USEFUL_SLICE_CHARS = 600
QUERY_STOPWORDS = {
    "agora",
    "como",
    "com",
    "da",
    "de",
    "do",
    "dos",
    "e",
    "em",
    "isso",
    "me",
    "na",
    "no",
    "o",
    "onde",
    "para",
    "por",
    "pra",
    "que",
    "sem",
    "um",
    "uma",
}
GENERIC_PROJECT_ALIASES = {
    "design system",
    "logo",
    "projetos",
    "site",
    "videos",
}
MANIFEST_PENALTY_PARTS = {
    ".atividade",
    ".historico",
    "handoff-session",
    "sessions",
    "session-env",
    "shell-snapshots",
}
MANIFEST_PENALTY_TERMS = (
    "backup",
    ".bak",
    "cookie",
    "credential",
    "credentials",
    "history",
    "secret",
    "session",
    "token",
)


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.translate(str.maketrans({
        "—": "-",
        "–": "-",
        "‑": "-",
        "−": "-",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
    }))
    return text.lower()


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_manifest() -> dict:
    if not MD_MANIFEST.exists():
        return {"files": []}
    return load_json(MD_MANIFEST)


def load_indexes():
    return {
        "paths": load_json(INDEXES / "paths.json"),
        "rules": load_json(INDEXES / "rules.json"),
        "slices": load_json(INDEXES / "context-slices.json"),
    }


def score_terms(query_norm: str, terms) -> int:
    score = 0
    for term in terms or []:
        t = normalize(term)
        if not t:
            continue
        if re.search(rf"(?<![a-z0-9]){re.escape(t)}(?![a-z0-9])", query_norm):
            score += 3 if " " in t else 1
    return score


def path_for_json(path: Path) -> str:
    return path.relative_to(CORTEX).as_posix()


def resolve_repo_path(rel: str) -> Path:
    rel = (rel or "").replace("\\", "/")
    direct = CORTEX / rel
    if direct.exists():
        return direct
    if rel.startswith("memoria/"):
        flat = MEMORIA / rel.removeprefix("memoria/")
        if flat.exists():
            return flat
    return direct


def first_heading(path: Path) -> str:
    if not path.exists():
        return ""
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if heading_level(line):
            return line.strip()
    return ""


def heading_text(path: Path) -> str:
    heading = first_heading(path)
    return re.sub(r"^#+\s*", "", heading).strip()


def aliases_from_client_file(path: Path) -> list[str]:
    if not path.exists():
        return []
    text = "\n".join(path.read_text(encoding="utf-8", errors="replace").splitlines()[:30])
    aliases = []
    for match in re.finditer(r"aliases:\s*(.*?)(?:-->|$)", text, flags=re.IGNORECASE):
        aliases.extend(part.strip() for part in match.group(1).split(","))
    return [a for a in aliases if a]


def aliases_from_folder(folder: Path) -> list[str]:
    aliases = {
        folder.name,
        folder.name.replace("-", " "),
        folder.name.replace("_", " "),
    }
    aliases.update(part for part in re.split(r"[-_\s]+", folder.name) if len(part) >= 3)
    return [a for a in aliases if a and not a.startswith("_")]


def direct_projects(folder: Path) -> list[dict]:
    projects = []
    for child in sorted(folder.iterdir()):
        if child.is_dir() and not child.name.startswith("_"):
            if child.name == "projetos":
                for nested in sorted(child.iterdir()):
                    if nested.is_dir() and not nested.name.startswith("_"):
                        projects.append(
                            {
                                "slug": nested.name,
                                "path": nested,
                                "aliases": aliases_from_folder(nested),
                            }
                        )
                continue
            projects.append(
                {
                    "slug": child.name,
                    "path": child,
                    "aliases": aliases_from_folder(child),
                }
            )
            nested_base = child / "projetos"
            if nested_base.exists():
                for nested in sorted(nested_base.iterdir()):
                    if nested.is_dir() and not nested.name.startswith("_"):
                        projects.append(
                            {
                                "slug": nested.name,
                                "path": nested,
                                "aliases": aliases_from_folder(nested),
                            }
                        )
    return projects


def build_client_registry() -> list[dict]:
    base = CORTEX / "clientes"
    if not base.exists():
        return []
    clients = []
    for folder in sorted(base.iterdir()):
        if not folder.is_dir() or folder.name.startswith("_"):
            continue
        ficha = folder / "CLAUDE.md"
        aliases = set(aliases_from_folder(folder))
        if ficha.exists():
            aliases.update(aliases_from_client_file(ficha))
            heading = heading_text(ficha)
            if heading:
                aliases.add(heading)
        projects = direct_projects(folder)
        clients.append(
            {
                "slug": folder.name,
                "folder": folder,
                "path": ficha,
                "has_claude": ficha.exists(),
                "heading": first_heading(ficha) if ficha.exists() else "",
                "aliases": sorted(aliases),
                "projects": projects,
            }
        )
    return clients


def iter_clients() -> list[dict]:
    return build_client_registry()


def client_hits(query: str) -> list[dict]:
    q = normalize(query)
    wants_site = any(score_terms(q, [term]) for term in ("site", "pagina", "landing"))
    hits = []
    for client in iter_clients():
        matched_aliases = [
            alias
            for alias in client["aliases"]
            if score_terms(q, [alias])
        ]
        client_score = score_terms(q, matched_aliases)
        matched_projects = []
        project_score = 0
        if client_score:
            for project in client["projects"]:
                matched = [
                    alias
                    for alias in project["aliases"]
                    if normalize(alias) not in GENERIC_PROJECT_ALIASES and score_terms(q, [alias])
                ]
                if wants_site and score_terms(normalize(project["slug"]), ["site"]):
                    matched.append(project["slug"])
                if matched:
                    matched_projects.append(
                        {
                            "slug": project["slug"],
                            "path": path_for_json(project["path"]),
                            "matched_aliases": matched,
                        }
                    )
                    project_score += score_terms(q, matched) + 4
        score = client_score + project_score
        if score:
            item = dict(client)
            item["score"] = score
            item["matched_aliases"] = matched_aliases
            item["matched_projects"] = matched_projects
            hits.append(item)
    return sorted(hits, key=lambda item: item["score"], reverse=True)


def rank_domains(query: str, indexes) -> list[dict]:
    q = normalize(query)
    scores: dict[str, dict] = {}
    domains = indexes["paths"].get("domains", {})

    for name, spec in domains.items():
        score = score_terms(q, spec.get("aliases", []))
        score -= score_terms(q, spec.get("negative_aliases", [])) * 2
        scores[name] = {"domain": name, "score": score, "reasons": []}
        if score:
            scores[name]["reasons"].append("domain aliases")

    for rule in indexes["rules"].get("rules", []):
        name = rule.get("domain")
        if name not in scores:
            continue
        s = score_terms(q, rule.get("aliases", []))
        s += score_terms(q, [rule.get("trigger", ""), rule.get("action", "")])
        if s:
            scores[name]["score"] += s
            scores[name]["reasons"].append(f"rule:{rule.get('id')}")

    for item in indexes["slices"].get("slices", []):
        name = item.get("domain")
        if name not in scores:
            continue
        s = score_terms(q, item.get("aliases", []))
        if s:
            scores[name]["score"] += s
            scores[name]["reasons"].append(f"slice:{item.get('id')}")

    clients = client_hits(query)
    if clients and "cliente-projeto" in scores:
        scores["cliente-projeto"]["score"] += clients[0]["score"] + 6
        scores["cliente-projeto"]["reasons"].append(f"client:{clients[0]['slug']}")

    ranked = sorted(scores.values(), key=lambda x: x["score"], reverse=True)
    return [r for r in ranked if r["score"] > 0]


def rank_rules(query: str, domain: str, indexes) -> list[dict]:
    q = normalize(query)
    out = []
    for rule in indexes["rules"].get("rules", []):
        if rule.get("domain") != domain:
            continue
        score = score_terms(q, rule.get("aliases", []))
        score += score_terms(q, [rule.get("trigger", ""), rule.get("action", "")])
        if score:
            out.append({"id": rule.get("id"), "score": score, "rule": rule})
    return sorted(out, key=lambda x: x["score"], reverse=True)


def rule_by_id(rule_id: str, indexes) -> dict | None:
    for rule in indexes["rules"].get("rules", []):
        if rule.get("id") == rule_id:
            return rule
    return None


def ensure_rule(ranked_rules: list[dict], rule_id: str, indexes) -> list[dict]:
    if any(item["id"] == rule_id for item in ranked_rules):
        return ranked_rules
    rule = rule_by_id(rule_id, indexes)
    if not rule:
        return ranked_rules
    return [{"id": rule_id, "score": 1, "rule": rule}] + ranked_rules


def rank_slices(query: str, domain: str, indexes) -> list[dict]:
    q = normalize(query)
    out = []
    for item in indexes["slices"].get("slices", []):
        if item.get("domain") != domain:
            continue
        score = score_terms(q, item.get("aliases", []))
        score += score_terms(q, [item.get("heading", ""), item.get("path", "")])
        if score:
            out.append({"id": item.get("id"), "score": score, "slice": item})
    if domain == "cliente-projeto":
        for client in client_hits(query):
            if not client["has_claude"]:
                continue
            out.append(
                {
                    "id": f"cliente::{client['slug']}::ficha",
                    "score": client["score"] + 20,
                    "slice": {
                        "id": f"cliente::{client['slug']}::ficha",
                        "domain": "cliente-projeto",
                        "path": path_for_json(client["path"]),
                        "heading": client["heading"],
                        "aliases": client["aliases"],
                        "max_chars": 3600,
                        "dynamic": True,
                    },
                }
            )
    return sorted(out, key=lambda x: x["score"], reverse=True)


def useful_query_pattern(query: str) -> str:
    words = []
    for word in re.findall(r"[a-z0-9][a-z0-9-]{2,}", normalize(query)):
        if word not in QUERY_STOPWORDS and word not in words:
            words.append(word)
    return "|".join(words[:6]) or re.escape(query[:40])


def query_tokens(query: str) -> list[str]:
    out = []
    for word in re.findall(r"[a-z0-9][a-z0-9-]{2,}", normalize(query)):
        if word not in QUERY_STOPWORDS and word not in out:
            out.append(word)
    return out[:12]


def manifest_text(item: dict) -> str:
    headings = " ".join(h.get("text", "") for h in item.get("headings", [])[:12])
    return normalize(" ".join([
        item.get("path", ""),
        item.get("name", ""),
        item.get("description", ""),
        item.get("h1", ""),
        headings,
    ]))


def rank_manifest_hits(query: str, limit: int = 5) -> list[dict]:
    manifest = load_manifest()
    tokens = query_tokens(query)
    if not tokens:
        return []
    ranked = []
    for item in manifest.get("files", []):
        haystack = manifest_text(item)
        score = 0
        for token in tokens:
            if re.search(rf"(?<![a-z0-9]){re.escape(token)}(?![a-z0-9])", haystack):
                score += 3 if token in normalize(item.get("path", "")) else 1
        rel = normalize(item.get("path", ""))
        parts = set(rel.split("/"))
        if parts & MANIFEST_PENALTY_PARTS or any(term in rel for term in MANIFEST_PENALTY_TERMS):
            score -= 8
        if score:
            ranked.append({
                "path": item.get("path"),
                "h1": item.get("h1"),
                "description": item.get("description"),
                "score": score,
            })
    ranked.sort(key=lambda item: (item["score"], item["path"] or ""), reverse=True)
    return ranked[:limit]


def rg_hint(query: str, domain: str, indexes) -> str:
    files = indexes["paths"].get("domains", {}).get(domain, {}).get("files", [])
    concrete_files = [f for f in files if "*" not in f]
    if not concrete_files:
        concrete_files = ["memoria", "clientes", "estudio", "produtos"]
    return f"rg -n \"{useful_query_pattern(query)}\" " + " ".join(
        f'"{path}"' for path in concrete_files[:6]
    )


def secondary_domains(query: str, primary_domain: str, indexes) -> list[str]:
    out = []
    for item in rank_domains(query, indexes):
        domain = item["domain"]
        if domain != primary_domain and domain not in out:
            out.append(domain)
    return out[:3]


def client_context(query: str) -> dict | None:
    hits = client_hits(query)
    if not hits:
        return None
    hit = hits[0]
    project = hit["matched_projects"][0] if hit.get("matched_projects") else None
    return {
        "slug": hit["slug"],
        "path": path_for_json(hit["folder"]),
        "has_claude": hit["has_claude"],
        "claude_path": path_for_json(hit["path"]) if hit["has_claude"] else None,
        "matched_aliases": hit.get("matched_aliases", [])[:6],
        "project": project,
    }


def safe_int(value, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def select_slices(
    ranked_slices: list[dict],
    max_slices: int = DEFAULT_MAX_SLICES,
    max_context_chars: int = DEFAULT_MAX_CONTEXT_CHARS,
) -> list[dict]:
    """Pick the strongest slices without letting context grow silently."""
    selected = []
    used_chars = 0
    max_slices = max(1, max_slices)
    max_context_chars = max(MIN_USEFUL_SLICE_CHARS, max_context_chars)

    for item in ranked_slices:
        if len(selected) >= max_slices:
            break
        remaining = max_context_chars - used_chars
        if remaining <= 0:
            break

        declared_limit = safe_int(item["slice"].get("max_chars"), 2500)
        char_limit = min(declared_limit, remaining)
        if selected and char_limit < MIN_USEFUL_SLICE_CHARS:
            continue

        picked = dict(item)
        picked["char_limit"] = char_limit
        selected.append(picked)
        used_chars += char_limit
    return selected


def heading_level(line: str) -> int | None:
    m = re.match(r"^(#{1,6})\s+", line)
    return len(m.group(1)) if m else None


def extract_heading(path: Path, heading: str, max_chars: int) -> str:
    if not path.exists():
        return ""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    wanted = normalize(heading.strip())
    start = None
    level = None
    for i, line in enumerate(lines):
        if normalize(line.strip()) == wanted:
            start = i
            level = heading_level(line) or 6
            break
    if start is None:
        text = "\n".join(lines[:80])
        return text[:max_chars]
    end = len(lines)
    for j in range(start + 1, len(lines)):
        lvl = heading_level(lines[j])
        if lvl is not None and lvl <= level:
            end = j
            break
    return "\n".join(lines[start:end])[:max_chars]


def resolve_query(
    query: str,
    include_text: bool = False,
    max_slices: int = DEFAULT_MAX_SLICES,
    max_context_chars: int = DEFAULT_MAX_CONTEXT_CHARS,
) -> dict:
    indexes = load_indexes()
    domains = rank_domains(query, indexes)
    domain = domains[0]["domain"] if domains else "unknown"
    client = client_context(query)
    rules = rank_rules(query, domain, indexes)
    if domain == "cliente-projeto":
        rules = ensure_rule(rules, "identidade-projeto-sem-default", indexes)
    slices = rank_slices(query, domain, indexes)
    selected = select_slices(slices, max_slices, max_context_chars)
    search_hint = "" if selected else rg_hint(query, domain, indexes)
    warnings = []
    if client and not client["has_claude"]:
        warnings.append("cliente sem CLAUDE.md; pedir ou criar ficha antes de front-end/copy")

    result = {
        "query": query,
        "domain": domain,
        "confidence": "high" if domains and domains[0]["score"] >= 6 else ("medium" if domains else "low"),
        "domain_reasons": domains[0].get("reasons", []) if domains else [],
        "secondary_domains": secondary_domains(query, domain, indexes) if domains else [],
        "rules": [
            {
                "id": r["id"],
                "strength": r["rule"].get("strength"),
                "trigger": r["rule"].get("trigger"),
                "action": r["rule"].get("action"),
                "source": r["rule"].get("source", {}),
            }
            for r in rules[:3]
        ],
        "slices": [
            {
                "id": s["id"],
                "path": s["slice"].get("path"),
                "heading": s["slice"].get("heading"),
                "max_chars": s.get("char_limit", s["slice"].get("max_chars")),
                "reason": "alias + dominio + termo especifico",
            }
            for s in selected
        ],
        "read_policy": "slice-only",
        "context_budget": {
            "max_slices": max(1, max_slices),
            "max_total_chars": max(MIN_USEFUL_SLICE_CHARS, max_context_chars),
            "allocated_chars": sum(s.get("char_limit", 0) for s in selected),
        },
        "manifest_hits": rank_manifest_hits(query),
        "search_hint": search_hint,
        "warnings": warnings,
    }
    if client:
        result["client"] = {k: v for k, v in client.items() if k != "project"}
        if client.get("project"):
            result["project"] = client["project"]

    if include_text:
        texts = []
        for s in selected:
            spec = s["slice"]
            path = resolve_repo_path(spec.get("path", ""))
            texts.append(
                {
                    "id": spec.get("id"),
                    "text": extract_heading(
                        path,
                        spec.get("heading", ""),
                        safe_int(s.get("char_limit"), int(spec.get("max_chars", 2500))),
                    ),
                }
            )
        result["texts"] = texts
    return result


def slugify(text: str) -> str:
    text = normalize(text)
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text[:64] or "tarefa"


def build_brief(query: str, result: dict) -> str:
    now = datetime.now().isoformat(timespec="seconds")
    lines = [
        f"# brief-contexto - {slugify(query)}",
        "",
        f"Gerado em: {now}",
        f"Tarefa: {query}",
        f"Dominio: {result['domain']} ({result['confidence']})",
        "",
        "## Contexto minimo",
    ]
    if result.get("slices"):
        for item in result["slices"]:
            lines.append(f"- Ler slice: `{item['path']}` :: `{item['heading']}`")
        budget = result.get("context_budget", {})
        if budget.get("allocated_chars"):
            lines.append(f"- Orcamento de leitura: ate {budget['allocated_chars']} chars no total.")
    else:
        lines.append("- Nenhum slice especifico encontrado. Usar busca pontual com `rg` antes de abrir arquivo grande.")
        if result.get("search_hint"):
            lines.append(f"- Busca sugerida: `{result['search_hint']}`")

    lines.extend(["", "## Regras aplicaveis"])
    if result.get("rules"):
        for item in result["rules"]:
            source = item.get("source", {})
            lines.append(f"- `{item['id']}` [{item.get('strength')}]")
            lines.append(f"  Trigger: {item.get('trigger')}")
            lines.append(f"  Acao: {item.get('action')}")
            if source:
                lines.append(f"  Fonte: `{source.get('path')}` :: `{source.get('heading')}`")
    else:
        lines.append("- Nenhuma regra especifica ranqueada.")

    lines.extend([
        "",
        "## Checklist de execucao",
        "- Abrir somente os arquivos acima antes de procurar contexto extra.",
        "- Se o slice nao resolver, usar `rg` no dominio provavel antes de ler arquivo inteiro.",
        "- Nao promover regra para bootstrap sem passar no gate: remover esta linha faria o agente errar em muitos turnos?",
        "- Registrar aprendizado novo no backstage se for manutencao de contexto, sem poluir o chat principal.",
        "",
        "## Saida esperada",
        "- Executar a tarefa principal usando o menor contexto suficiente.",
        "- Ao final, dizer o que mudou e quais validacoes passaram.",
    ])
    return "\n".join(lines) + "\n"


def write_brief(
    query: str,
    out: str | None = None,
    max_slices: int = DEFAULT_MAX_SLICES,
    max_context_chars: int = DEFAULT_MAX_CONTEXT_CHARS,
) -> Path:
    result = resolve_query(
        query,
        include_text=False,
        max_slices=max_slices,
        max_context_chars=max_context_chars,
    )
    if out:
        path = Path(out)
    else:
        brief_dir = MEMORIA / "briefs"
        path = brief_dir / f"brief-contexto-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{slugify(query)}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_brief(query, result), encoding="utf-8")
    return path


def validate_indexes() -> int:
    indexes = load_indexes()
    errors = []
    for name in ("paths", "rules", "slices"):
        if "version" not in indexes[name]:
            errors.append(f"{name}: sem version")
    domains = set(indexes["paths"].get("domains", {}))
    seen_rules = set()
    seen_slices = set()
    for item in indexes["slices"].get("slices", []):
        item_id = item.get("id")
        if item_id in seen_slices:
            errors.append(f"slice duplicado: {item_id}")
        seen_slices.add(item_id)
        if item.get("domain") not in domains:
            errors.append(f"slice {item_id}: domain desconhecido: {item.get('domain')}")
        rel = item.get("path", "")
        if not resolve_repo_path(rel).exists():
            errors.append(f"slice {item_id}: arquivo nao existe: {rel}")
    for rule in indexes["rules"].get("rules", []):
        rule_id = rule.get("id")
        if rule_id in seen_rules:
            errors.append(f"rule duplicada: {rule_id}")
        seen_rules.add(rule_id)
        if rule.get("domain") not in domains:
            errors.append(f"rule {rule_id}: domain desconhecido: {rule.get('domain')}")
        src = rule.get("source", {}).get("path", "")
        if src and not resolve_repo_path(src).exists():
            errors.append(f"rule {rule_id}: source nao existe: {src}")
    for client in build_client_registry():
        if not client["slug"]:
            errors.append("cliente sem slug detectado")
            continue
        if not client["folder"].exists():
            errors.append(f"cliente {client['slug']}: pasta nao existe")
        if client["has_claude"] and not client["path"].exists():
            errors.append(f"cliente {client['slug']}: CLAUDE.md marcado mas ausente")
    if errors:
        print(json.dumps({"ok": False, "errors": errors}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps({"ok": True}, ensure_ascii=False, indent=2))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_resolve = sub.add_parser("resolve")
    p_resolve.add_argument("query")
    p_resolve.add_argument("--json", action="store_true")
    p_resolve.add_argument("--text", action="store_true")
    p_resolve.add_argument("--max-slices", type=int, default=DEFAULT_MAX_SLICES)
    p_resolve.add_argument("--max-context-chars", type=int, default=DEFAULT_MAX_CONTEXT_CHARS)

    p_explain = sub.add_parser("explain")
    p_explain.add_argument("query")

    p_brief = sub.add_parser("brief")
    p_brief.add_argument("query")
    p_brief.add_argument("--out", default="")
    p_brief.add_argument("--print", action="store_true")
    p_brief.add_argument("--max-slices", type=int, default=DEFAULT_MAX_SLICES)
    p_brief.add_argument("--max-context-chars", type=int, default=DEFAULT_MAX_CONTEXT_CHARS)

    sub.add_parser("validate-indexes")

    args = parser.parse_args(argv)
    if args.cmd == "validate-indexes":
        return validate_indexes()
    if args.cmd == "resolve":
        result = resolve_query(
            args.query,
            include_text=args.text,
            max_slices=args.max_slices,
            max_context_chars=args.max_context_chars,
        )
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"domain: {result['domain']} ({result['confidence']})")
            for s in result["slices"]:
                print(f"- {s['id']} -> {s['path']} :: {s['heading']}")
        return 0
    if args.cmd == "explain":
        result = resolve_query(args.query, include_text=False)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "brief":
        path = write_brief(
            args.query,
            args.out or None,
            max_slices=args.max_slices,
            max_context_chars=args.max_context_chars,
        )
        print(str(path))
        if args.print:
            print(path.read_text(encoding="utf-8"))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
