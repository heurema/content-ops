#!/usr/bin/env python3
"""QA history viewer for content-ops.

Reads ~/.config/content-ops/qa-history.jsonl and prints summary statistics.

Usage:
    python3 tools/qa_history.py [--last N] [--format json|text]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from shared.env import load as _load_env; _load_env()

_QA_HISTORY_PATH = Path.home() / ".config" / "content-ops" / "qa-history.jsonl"


def load_history() -> list[dict]:
    """Read all entries from qa-history.jsonl. Returns empty list if file absent."""
    if not _QA_HISTORY_PATH.exists():
        return []
    entries = []
    with open(_QA_HISTORY_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return entries


def build_summary(entries: list[dict], last_n: int = 5) -> dict:
    total = len(entries)
    pass_count = sum(1 for e in entries if e.get("decision") == "pass")
    review_count = sum(1 for e in entries if e.get("decision") == "review")
    block_count = sum(1 for e in entries if e.get("decision") == "block")

    scores = [e["score"] for e in entries if isinstance(e.get("score"), (int, float))]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0

    recent = entries[-last_n:] if last_n > 0 else entries
    recent = list(reversed(recent))

    ai_hits = sum(1 for e in entries if (e.get("ai_pattern_hits") or 0) > 0)
    drift_high = sum(
        1 for e in entries
        if isinstance(e.get("voice_drift_score"), (int, float)) and e["voice_drift_score"] > 0.5
    )
    vale_errs = sum(1 for e in entries if (e.get("vale_errors") or 0) > 0)

    def pct(n: int) -> str:
        return f"{round(n / total * 100)}%" if total > 0 else "0%"

    return {
        "total": total,
        "pass": pass_count,
        "review": review_count,
        "block": block_count,
        "pass_pct": pct(pass_count),
        "review_pct": pct(review_count),
        "block_pct": pct(block_count),
        "average_score": avg_score,
        "recent": recent,
        "issues": {
            "ai_pattern_hits_gt0": {"count": ai_hits, "pct": pct(ai_hits)},
            "voice_drift_high": {"count": drift_high, "pct": pct(drift_high)},
            "vale_errors_gt0": {"count": vale_errs, "pct": pct(vale_errs)},
        },
    }


def format_text(summary: dict) -> str:
    total = summary["total"]
    lines = [
        "QA History Summary",
        "==================",
        f"Total runs:     {total}",
        f"Pass:           {summary['pass']} ({summary['pass_pct']})",
        f"Review:         {summary['review']} ({summary['review_pct']})",
        f"Block:          {summary['block']} ({summary['block_pct']})",
        f"Average score:  {summary['average_score']}",
    ]

    recent = summary["recent"]
    if recent:
        lines.append(f"\nLast {len(recent)} runs:")
        for e in recent:
            ts = e.get("timestamp", "")[:10] if e.get("timestamp") else "unknown"
            fname = Path(e.get("file", "")).name if e.get("file") else e.get("slug", "?")
            score = e.get("score", "?")
            decision = e.get("decision", "?")
            lines.append(f"  {ts} {fname:<30} score={score}  {decision}")

    issues = summary["issues"]
    lines.append("\nTop issues:")
    lines.append(f"  ai_pattern_hits > 0:  {issues['ai_pattern_hits_gt0']['count']} runs ({issues['ai_pattern_hits_gt0']['pct']})")
    lines.append(f"  voice_drift high:     {issues['voice_drift_high']['count']} runs ({issues['voice_drift_high']['pct']})")
    lines.append(f"  vale_errors > 0:      {issues['vale_errors_gt0']['count']} runs ({issues['vale_errors_gt0']['pct']})")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="QA history summary")
    parser.add_argument(
        "--last",
        type=int,
        default=5,
        metavar="N",
        help="Show last N entries in the runs section (default: 5)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="text",
        help="Output format (default: text)",
    )
    args = parser.parse_args(argv)

    entries = load_history()
    summary = build_summary(entries, last_n=args.last)

    if args.format == "json":
        print(json.dumps(summary, indent=2))
    else:
        print(format_text(summary))


if __name__ == "__main__":
    main()
