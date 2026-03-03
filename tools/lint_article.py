#!/usr/bin/env python3
"""Lint a Markdown article for common issues before publishing.

Usage:
    python3 lint_article.py <article.md> [--strict]

Exit codes:
    0 — no issues (or only warnings in non-strict mode)
    1 — errors found (always fails on errors; in strict mode also fails on warnings)

Checks:
    ERROR  — em dashes (—): AI generation signal, fails publishing
    ERROR  — description > 160 chars: truncated by dev.to / Hashnode
    ERROR  — missing required frontmatter: title, description, tags, date
    WARNING — en dashes (–) in prose: less common but still suspicious
    WARNING — tags with hyphens: will break dev.to
    WARNING — description > 150 chars: approaching limit
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from shared.article import parse_article


# ---------------------------------------------------------------------------
# Check functions — each returns list of (level, message) tuples
# ---------------------------------------------------------------------------

def check_em_dashes(body: str) -> list[tuple[str, str]]:
    """Detect em dashes outside code blocks."""
    issues = []
    # Strip fenced code blocks before checking
    clean = re.sub(r"```.*?```", "", body, flags=re.DOTALL)
    clean = re.sub(r"`[^`]+`", "", clean)
    count = clean.count("—")
    if count:
        lines = [
            i + 1
            for i, line in enumerate(body.splitlines())
            if "—" in line and not line.strip().startswith("```")
        ]
        issues.append((
            "ERROR",
            f"Em dash (—) found {count}× on lines {lines} — replace with ' - '"
        ))
    return issues


def check_en_dashes(body: str) -> list[tuple[str, str]]:
    """Detect en dashes outside code blocks (suspicious but softer)."""
    clean = re.sub(r"```.*?```", "", body, flags=re.DOTALL)
    clean = re.sub(r"`[^`]+`", "", clean)
    count = clean.count("–")
    if count:
        return [("WARNING", f"En dash (–) found {count}× — consider replacing with '-'")]
    return []


def check_description_length(description: str) -> list[tuple[str, str]]:
    issues = []
    n = len(description)
    if n > 160:
        issues.append(("ERROR", f"Description {n} chars (max 160) — will be truncated"))
    elif n > 150:
        issues.append(("WARNING", f"Description {n} chars — approaching 160 limit"))
    return issues


def check_required_frontmatter(article) -> list[tuple[str, str]]:
    issues = []
    if not article.title:
        issues.append(("ERROR", "Missing frontmatter: title"))
    if not article.description:
        issues.append(("ERROR", "Missing frontmatter: description"))
    if not article.tags:
        issues.append(("ERROR", "Missing frontmatter: tags"))
    if not article.date:
        issues.append(("WARNING", "Missing frontmatter: date"))
    return issues


def check_tag_format(tags: list[str]) -> list[tuple[str, str]]:
    issues = []
    bad = [t for t in tags if "-" in t]
    if bad:
        issues.append((
            "WARNING",
            f"Tags with hyphens will break dev.to: {bad} — use alphanumeric only"
        ))
    return issues


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def lint(path: str, strict: bool = False) -> int:
    article = parse_article(path)
    body = Path(path).read_text(encoding="utf-8")

    all_issues: list[tuple[str, str]] = []
    all_issues += check_required_frontmatter(article)
    all_issues += check_em_dashes(body)
    all_issues += check_en_dashes(body)
    all_issues += check_description_length(article.description or "")
    all_issues += check_tag_format(article.tags)

    errors = [(lvl, msg) for lvl, msg in all_issues if lvl == "ERROR"]
    warnings = [(lvl, msg) for lvl, msg in all_issues if lvl == "WARNING"]

    if not all_issues:
        print(f"OK  {path}")
        return 0

    for lvl, msg in errors + warnings:
        prefix = "ERR " if lvl == "ERROR" else "WARN"
        print(f"{prefix}  {msg}")

    if errors or (strict and warnings):
        print(f"\nFAIL  {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1

    print(f"\nOK (with {len(warnings)} warning(s))")
    return 0


def main(argv: list[str] | None = None) -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Lint article before publishing")
    parser.add_argument("article", help="Path to Markdown article")
    parser.add_argument("--strict", action="store_true", help="Fail on warnings too")
    args = parser.parse_args(argv)
    sys.exit(lint(args.article, strict=args.strict))


if __name__ == "__main__":
    main()
