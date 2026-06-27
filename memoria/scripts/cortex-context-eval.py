#!/usr/bin/env python3
"""Eval local do Context Resolver.

Zero dependencia externa. Serve como smoke test para evitar que alias amplo
puxe dominio errado e injete contexto sem custo-beneficio.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve()
MEMORIA = SCRIPT.parents[1]
RESOLVER_PATH = SCRIPT.with_name("cortex-context-resolver.py")
CASES_PATH = MEMORIA / "indexes" / "eval-cases.json"


def load_resolver():
    spec = importlib.util.spec_from_file_location("cortex_context_resolver", RESOLVER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"nao consegui carregar {RESOLVER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_cases():
    resolver = load_resolver()
    data = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    results = []
    for case in data.get("cases", []):
        needs_text = case.get("max_text_chars") is not None
        got = resolver.resolve_query(case["query"], include_text=needs_text)
        got_slice_list = got.get("slices", [])
        got_slices = {s["id"] for s in got_slice_list}
        got_rules = {r["id"] for r in got.get("rules", [])}
        missing = [s for s in case.get("expect_slices", []) if s not in got_slices]
        missing_rules = [r for r in case.get("expect_rules", []) if r not in got_rules]
        forbidden_domain_hit = got.get("domain") in set(case.get("forbid_domains", []))
        expected_client = case.get("expect_client")
        got_client = (got.get("client") or {}).get("slug")
        client_mismatch = expected_client is not None and got_client != expected_client
        if "expect_has_claude" in case:
            has_claude_mismatch = (got.get("client") or {}).get("has_claude") != case["expect_has_claude"]
        else:
            has_claude_mismatch = False
        expected_project = case.get("expect_project")
        got_project = (got.get("project") or {}).get("slug")
        project_mismatch = expected_project is not None and got_project != expected_project
        expected_confidence = case.get("expect_confidence")
        confidence_mismatch = expected_confidence is not None and got.get("confidence") != expected_confidence
        expected_warnings = case.get("expect_warnings", [])
        got_warnings = got.get("warnings", [])
        missing_warnings = [
            warning for warning in expected_warnings if not any(warning in got for got in got_warnings)
        ]
        max_slices = case.get("max_slices")
        too_many_slices = max_slices is not None and len(got_slice_list) > max_slices
        text_chars = sum(len(t.get("text", "")) for t in got.get("texts", [])) if needs_text else None
        text_too_large = (
            case.get("max_text_chars") is not None
            and text_chars is not None
            and text_chars > case["max_text_chars"]
        )
        ok = (
            got.get("domain") == case.get("expect_domain")
            and not missing
            and not missing_rules
            and not forbidden_domain_hit
            and not client_mismatch
            and not has_claude_mismatch
            and not project_mismatch
            and not confidence_mismatch
            and not missing_warnings
            and not too_many_slices
            and not text_too_large
        )
        results.append(
            {
                "id": case["id"],
                "ok": ok,
                "query": case["query"],
                "expect_domain": case.get("expect_domain"),
                "got_domain": got.get("domain"),
                "missing_slices": missing,
                "missing_rules": missing_rules,
                "forbidden_domain_hit": forbidden_domain_hit,
                "expect_client": expected_client,
                "got_client": got_client,
                "client_mismatch": client_mismatch,
                "has_claude_mismatch": has_claude_mismatch,
                "expect_project": expected_project,
                "got_project": got_project,
                "project_mismatch": project_mismatch,
                "expect_confidence": expected_confidence,
                "got_confidence": got.get("confidence"),
                "confidence_mismatch": confidence_mismatch,
                "missing_warnings": missing_warnings,
                "slice_count": len(got_slice_list),
                "max_slices": max_slices,
                "text_chars": text_chars,
                "max_text_chars": case.get("max_text_chars"),
                "too_many_slices": too_many_slices,
                "text_too_large": text_too_large,
            }
        )
    return results


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    results = run_cases()
    ok = all(r["ok"] for r in results)
    if args.json:
        print(json.dumps({"ok": ok, "results": results}, ensure_ascii=False, indent=2))
    else:
        for r in results:
            status = "OK" if r["ok"] else "FAIL"
            print(f"{status} {r['id']}: {r['got_domain']}")
            if not r["ok"]:
                print(f"  expected domain: {r['expect_domain']}")
                print(f"  missing slices: {r['missing_slices']}")
                print(f"  missing rules: {r['missing_rules']}")
                print(f"  client: {r['got_client']} / {r['expect_client']}")
                print(f"  project: {r['got_project']} / {r['expect_project']}")
                print(f"  confidence: {r['got_confidence']} / {r['expect_confidence']}")
                print(f"  missing warnings: {r['missing_warnings']}")
                print(f"  slice count: {r['slice_count']} / {r['max_slices']}")
                print(f"  text chars: {r['text_chars']} / {r['max_text_chars']}")
        print(f"\nsummary: {'OK' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
