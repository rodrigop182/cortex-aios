#!/usr/bin/env python3
"""Cria manifest de markdowns do CORTEX para retrieval barato.

O manifest guarda metadados, nao conteudo bruto. Ele ajuda o resolver a saber
onde procurar antes de abrir arquivos grandes.
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


SCRIPT = Path(__file__).resolve()
MEMORIA = SCRIPT.parents[1]
CORTEX = MEMORIA.parent
INDEXES = MEMORIA / "indexes"
PATHS_INDEX = INDEXES / "paths.json"
DEFAULT_OUT = INDEXES / "md-manifest.json"

DEFAULT_IGNORE_GLOBS = [
    ".git/**",
    "**/.git/**",
    "_local/**",
    "**/_local/**",
    "**/_renders/**",
    "**/_downloads/**",
    "**/_assets-pesados/**",
    "**/_tmp/**",
    "**/node_modules/**",
    "**/__pycache__/**",
    "**/.venv/**",
    "**/venv/**",
    ".mcp.json",
    "**/.mcp.json",
    "**/mcp.json",
    "connections.md",
    "**/connections.md",
    "**/.env",
    "**/.atividade/**",
    "**/.historico/**",
    "_arquivadas/**",
    "**/_arquivadas/**",
    "**/skills-arquivadas/**",
    "**/history.jsonl",
    "**/sessions/**",
    "**/session-env/**",
    "**/shell-snapshots/**",
    "**/handoff-session/**",
    "**/*backup*/**",
    "**/*bak*/**",
    "**/*.bak",
    "**/*.bak-*",
    "**/*credentials*.md",
    "**/*credential*.md",
    "**/*secret*.md",
    "**/*token*.md",
    "**/*cookie*.md",
    "**/*cookies*.md",
    "**/*session*.md",
    "memoria/briefs/**",
    "memoria/indexes/training/**",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def rel_posix(path: Path) -> str:
    return path.relative_to(CORTEX).as_posix()


def load_ignore_globs() -> list[str]:
    globs = list(DEFAULT_IGNORE_GLOBS)
    if PATHS_INDEX.exists():
        try:
            data = json.loads(PATHS_INDEX.read_text(encoding="utf-8"))
            globs.extend(data.get("ignore_globs", []))
        except json.JSONDecodeError:
            pass
    return sorted(set(g for g in globs if g))


def ignored(rel: str, globs: list[str]) -> bool:
    return any(fnmatch.fnmatch(rel, pattern) for pattern in globs)


def blocked_manifest_path(rel: str) -> bool:
    """Deny versioned retrieval metadata for sensitive or noisy areas."""
    parts = rel.split("/")
    lower = rel.lower()
    if lower.startswith("clientes/"):
        return not (len(parts) == 3 and parts[2] == "CLAUDE.md")
    if "handoff-session" in parts:
        return True
    if any(part in {".atividade", ".historico", "sessions", "session-env", "shell-snapshots"} for part in parts):
        return True
    sensitive_terms = ("credential", "credentials", "secret", "token", "cookie", "cookies", "session")
    return any(term in lower for term in sensitive_terms)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def parse_frontmatter(lines: list[str]) -> dict:
    if not lines or lines[0].strip() != "---":
        return {}
    end = None
    for i, line in enumerate(lines[1:80], start=1):
        if line.strip() == "---":
            end = i
            break
    if end is None:
        return {}

    out: dict[str, str] = {}
    for line in lines[1:end]:
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if match:
            out[match.group(1).lower()] = match.group(2).strip().strip('"')
    return out


def markdown_meta(path: Path) -> dict:
    text = read_text(path)
    lines = text.splitlines()
    frontmatter = parse_frontmatter(lines)
    headings = []
    h1 = ""
    for line in lines:
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if not match:
            continue
        level = len(match.group(1))
        title = match.group(2).strip()
        if level == 1 and not h1:
            h1 = title
        headings.append({"level": level, "text": title})
        if len(headings) >= 24:
            break

    stat = path.stat()
    digest = hashlib.sha1(text.encode("utf-8", errors="replace")).hexdigest()[:12]
    rel = rel_posix(path)
    return {
        "path": rel,
        "size_bytes": stat.st_size,
        "mtime": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).astimezone().isoformat(timespec="seconds"),
        "sha1_12": digest,
        "name": frontmatter.get("name", ""),
        "description": frontmatter.get("description", ""),
        "h1": h1,
        "headings": headings,
        "top_level": rel.split("/", 1)[0],
    }


def build_manifest(root: Path, globs: list[str]) -> dict:
    files = []
    skipped = Counter()
    for path in sorted(root.rglob("*.md")):
        try:
            rel = rel_posix(path)
        except ValueError:
            continue
        if ignored(rel, globs):
            skipped["ignored_glob"] += 1
            continue
        if blocked_manifest_path(rel):
            skipped["blocked_manifest_path"] += 1
            continue
        try:
            files.append(markdown_meta(path))
        except OSError:
            skipped["read_error"] += 1

    by_top_level = Counter(item["top_level"] for item in files)
    return {
        "version": 1,
        "generated_at": now_iso(),
        "root": CORTEX.as_posix(),
        "files_total": len(files),
        "total_bytes": sum(item["size_bytes"] for item in files),
        "by_top_level": dict(sorted(by_top_level.items())),
        "skipped": dict(skipped),
        "ignore_globs": globs,
        "deny_policy": "no secrets, sessions, handoffs, backups, history or client docs beyond clientes/*/CLAUDE.md",
        "files": files,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args(argv)

    globs = load_ignore_globs()
    manifest = build_manifest(CORTEX, globs)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": True,
        "out": str(out),
        "files_total": manifest["files_total"],
        "total_bytes": manifest["total_bytes"],
        "by_top_level": manifest["by_top_level"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
