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
from shared.env import load as _load_env; _load_env()
from shared.article import parse_article


# ---------------------------------------------------------------------------
# Check functions — each returns list of (level, message) tuples
# ---------------------------------------------------------------------------

def _line_has_dash_outside_code(line: str, char: str) -> bool:
    """Return True if char appears in line outside inline code spans."""
    if line.strip().startswith("```"):
        return False
    # Remove inline code spans before checking
    line_clean = re.sub(r"`[^`\n]+`", "", line)
    return char in line_clean


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
            if _line_has_dash_outside_code(line, "—")
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
    # Tags with spaces will be slugified to hyphens by publish_devto — catch early
    spaced = [t for t in tags if " " in t and t not in bad]
    if spaced:
        issues.append((
            "WARNING",
            f"Tags with spaces will become hyphenated after slugify (breaks dev.to): {spaced}"
        ))
    return issues


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def fix_dashes(path: str) -> int:
    """Replace em/en dashes outside code blocks in-place. Returns count of fixes."""
    text = Path(path).read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    fixed = []
    count = 0
    in_fence = False
    for line in lines:
        if line.strip().startswith("```"):
            in_fence = not in_fence
        if in_fence or line.strip().startswith("```"):
            fixed.append(line)
            continue
        # Replace outside inline code: temporarily mask inline code, fix, restore
        segments = re.split(r"(`[^`\n]+`)", line)
        new_segments = []
        for seg in segments:
            if seg.startswith("`") and seg.endswith("`"):
                new_segments.append(seg)  # inline code: leave as-is
            else:
                orig = seg
                seg = seg.replace("—", " - ").replace("–", "-")
                if seg != orig:
                    count += len([c for c in orig if c in "—–"])
                new_segments.append(seg)
        fixed.append("".join(new_segments))
    if count:
        Path(path).write_text("".join(fixed), encoding="utf-8")
    return count


def lint(path: str, strict: bool = False) -> int:
    article = parse_article(path)
    # Use article.body to avoid re-reading the file (TOCTOU)
    body = article.body

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
    parser.add_argument("--fix", action="store_true", help="Auto-fix em/en dashes in-place")
    args = parser.parse_args(argv)
    if args.fix:
        n = fix_dashes(args.article)
        if n:
            print(f"Fixed {n} dash(es) in {args.article} — re-linting...")
        else:
            print("No dashes to fix.")
    sys.exit(lint(args.article, strict=args.strict))


if __name__ == "__main__":
    main()
