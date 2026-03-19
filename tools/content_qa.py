#!/usr/bin/env python3
"""Unified 4-layer content QA for Markdown articles.

Layers:
  A — Structural  : markdownlint-cli2 + frontmatter required fields
  B — Editorial   : Vale (prose linter)
  C — Platform fit: per-platform field limits
  D — Style metrics: deterministic, stdlib-only

Usage:
    python3 content_qa.py <article.md> [--format json|text] [--strict]

Exit codes:
    0 — pass
    1 — review
    2 — block
"""
from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from shared.env import load as _load_env; _load_env()
from shared.article import parse_article

_VOICE_BASELINE_PATH = Path.home() / ".config" / "content-ops" / "voice-baseline.json"
_QA_HISTORY_PATH = Path.home() / ".config" / "content-ops" / "qa-history.jsonl"


def _log_telemetry(report: dict, article_path: str, body: str) -> None:
    """Append one JSON line to qa-history.jsonl. Never crashes — QA output takes priority."""
    try:
        path = _QA_HISTORY_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        slug = Path(article_path).stem
        word_count = len(body.split())
        entry = {
            "timestamp": report["timestamp"],
            "file": report["file"],
            "slug": slug,
            "word_count": word_count,
            "score": report["score"],
            "decision": report["decision"],
            "vale_errors": report["layers"]["editorial"]["vale_errors"],
            "vale_warnings": report["layers"]["editorial"]["vale_warnings"],
            "ai_pattern_hits": report["layers"]["editorial"]["ai_pattern_hits"],
            "voice_drift_score": report["layers"]["style"].get("voice_drift_score"),
            "platform_failures": report["layers"]["platform_fit"]["failure_count"],
        }
        with open(path, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass  # telemetry must never break QA

# ---------------------------------------------------------------------------
# Platform limits
# ---------------------------------------------------------------------------

PLATFORM_LIMITS: dict[str, dict[str, Any]] = {
    "devto": {
        "title": 128,
        "description": 160,
        "tags": 4,
    },
    "hashnode": {
        "title": 100,
        "description": 250,
        "tags": 5,
    },
    "twitter": {
        "description": 280,
    },
    "bluesky": {
        "description": 300,
    },
}

REQUIRED_FRONTMATTER = ["title", "description", "tags", "date"]

# ---------------------------------------------------------------------------
# Markdown stripping (for style metrics)
# ---------------------------------------------------------------------------

def _strip_markdown(text: str) -> str:
    """Remove markdown syntax, leaving plain prose."""
    # Fenced code blocks
    text = re.sub(r"```[\s\S]*?```", "", text)
    # Inline code
    text = re.sub(r"`[^`\n]+`", "", text)
    # Images
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    # Links — keep link text
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    # Reference-style links
    text = re.sub(r"\[[^\]]*\]\[[^\]]*\]", "", text)
    # Headings
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # Bold / italic
    text = re.sub(r"\*{1,3}([^*\n]+)\*{1,3}", r"\1", text)
    text = re.sub(r"_{1,3}([^_\n]+)_{1,3}", r"\1", text)
    # Horizontal rules
    text = re.sub(r"^[-*_]{3,}\s*$", "", text, flags=re.MULTILINE)
    # HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    # Blockquote markers
    text = re.sub(r"^>\s?", "", text, flags=re.MULTILINE)
    # List bullets
    text = re.sub(r"^[\s]*[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^[\s]*\d+\.\s+", "", text, flags=re.MULTILINE)
    return text

# ---------------------------------------------------------------------------
# Layer A — Structural
# ---------------------------------------------------------------------------

def run_layer_a(article_path: str, article: Any) -> dict[str, Any]:
    """Run markdownlint and check required frontmatter fields."""
    # Required frontmatter
    missing_fields: list[str] = []
    fm = article.frontmatter
    for field in REQUIRED_FRONTMATTER:
        val = fm.get(field)
        if not val and field == "tags":
            val = article.tags
        if not val:
            missing_fields.append(field)

    # markdownlint
    markdownlint_errors = 0
    markdownlint_raw: list[dict] = []
    markdownlint_skipped = False

    binary = shutil.which("markdownlint-cli2") or shutil.which("markdownlint")
    if binary is None:
        markdownlint_skipped = True
    else:
        try:
            result = subprocess.run(
                [binary, "--formatter", "json", article_path],
                capture_output=True,
                text=True,
                timeout=30,
            )
            output = result.stdout or result.stderr
            try:
                data = json.loads(output)
                if isinstance(data, list):
                    markdownlint_raw = data
                    markdownlint_errors = sum(
                        len(item.get("errors", [])) if isinstance(item, dict) else 1
                        for item in data
                    )
                elif isinstance(data, dict):
                    # Some versions output {file: [errors]}
                    for errs in data.values():
                        if isinstance(errs, list):
                            markdownlint_errors += len(errs)
                            markdownlint_raw.extend(errs)
            except (json.JSONDecodeError, TypeError):
                # Non-JSON output — count non-empty lines as errors
                lines = [l for l in output.splitlines() if l.strip()]
                markdownlint_errors = len(lines)
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            markdownlint_skipped = True

    return {
        "missing_frontmatter": missing_fields,
        "markdownlint_errors": markdownlint_errors,
        "markdownlint_skipped": markdownlint_skipped,
        "markdownlint_raw": markdownlint_raw,
    }

# ---------------------------------------------------------------------------
# Layer B — Editorial (Vale)
# ---------------------------------------------------------------------------

def run_layer_b(article_path: str) -> dict[str, Any]:
    """Run Vale and parse JSON output."""
    vale_errors = 0
    vale_warnings = 0
    vale_suggestions = 0
    ai_pattern_hits = 0
    vale_skipped = False
    vale_raw: dict = {}

    binary = shutil.which("vale")
    if binary is None:
        vale_skipped = True
    else:
        try:
            result = subprocess.run(
                [binary, "--output=JSON", article_path],
                capture_output=True,
                text=True,
                timeout=60,
            )
            output = result.stdout or ""
            try:
                data = json.loads(output)
                vale_raw = data
                # data is {filepath: [alerts]}
                for alerts in data.values():
                    if not isinstance(alerts, list):
                        continue
                    for alert in alerts:
                        severity = alert.get("Severity", "").lower()
                        if severity == "error":
                            vale_errors += 1
                        elif severity == "warning":
                            vale_warnings += 1
                        elif severity == "suggestion":
                            vale_suggestions += 1
                        # Count ContentOps rule hits
                        rule = alert.get("Check", "")
                        if "ContentOps" in rule or "contentops" in rule.lower():
                            ai_pattern_hits += 1
            except (json.JSONDecodeError, TypeError, AttributeError):
                pass
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            vale_skipped = True

    return {
        "vale_errors": vale_errors,
        "vale_warnings": vale_warnings,
        "vale_suggestions": vale_suggestions,
        "ai_pattern_hits": ai_pattern_hits,
        "vale_skipped": vale_skipped,
        "vale_raw": vale_raw,
    }

# ---------------------------------------------------------------------------
# Layer C — Platform fit
# ---------------------------------------------------------------------------

def run_layer_c(article: Any) -> dict[str, Any]:
    """Check per-platform field limits."""
    failures: list[dict[str, Any]] = []

    title_len = len(article.title or "")
    desc_len = len(article.description or "")
    tag_count = len(article.tags or [])

    # devto
    if title_len > PLATFORM_LIMITS["devto"]["title"]:
        failures.append({
            "platform": "devto",
            "field": "title",
            "limit": PLATFORM_LIMITS["devto"]["title"],
            "actual": title_len,
        })
    if desc_len > PLATFORM_LIMITS["devto"]["description"]:
        failures.append({
            "platform": "devto",
            "field": "description",
            "limit": PLATFORM_LIMITS["devto"]["description"],
            "actual": desc_len,
        })
    if tag_count > PLATFORM_LIMITS["devto"]["tags"]:
        failures.append({
            "platform": "devto",
            "field": "tags",
            "limit": PLATFORM_LIMITS["devto"]["tags"],
            "actual": tag_count,
        })

    # hashnode
    if title_len > PLATFORM_LIMITS["hashnode"]["title"]:
        failures.append({
            "platform": "hashnode",
            "field": "title",
            "limit": PLATFORM_LIMITS["hashnode"]["title"],
            "actual": title_len,
        })
    if desc_len > PLATFORM_LIMITS["hashnode"]["description"]:
        failures.append({
            "platform": "hashnode",
            "field": "description",
            "limit": PLATFORM_LIMITS["hashnode"]["description"],
            "actual": desc_len,
        })
    if tag_count > PLATFORM_LIMITS["hashnode"]["tags"]:
        failures.append({
            "platform": "hashnode",
            "field": "tags",
            "limit": PLATFORM_LIMITS["hashnode"]["tags"],
            "actual": tag_count,
        })

    # twitter — description used as thread hook
    if desc_len > PLATFORM_LIMITS["twitter"]["description"]:
        failures.append({
            "platform": "twitter",
            "field": "description",
            "limit": PLATFORM_LIMITS["twitter"]["description"],
            "actual": desc_len,
        })

    # bluesky
    if desc_len > PLATFORM_LIMITS["bluesky"]["description"]:
        failures.append({
            "platform": "bluesky",
            "field": "description",
            "limit": PLATFORM_LIMITS["bluesky"]["description"],
            "actual": desc_len,
        })

    return {
        "failures": failures,
        "failure_count": len(failures),
    }

# ---------------------------------------------------------------------------
# Layer D — Style metrics (stdlib only)
# ---------------------------------------------------------------------------

def _split_sentences(text: str) -> list[str]:
    """Split plain text into sentences on [.!?] followed by space or newline."""
    parts = re.split(r"[.!?]+(?:\s+|\n|$)", text)
    return [p.strip() for p in parts if p.strip()]


def _split_paragraphs(text: str) -> list[str]:
    """Split on double newline."""
    parts = re.split(r"\n{2,}", text)
    return [p.strip() for p in parts if p.strip()]


def _word_tokens(text: str) -> list[str]:
    """Lowercase alpha-only tokens."""
    return re.findall(r"[a-z]+", text.lower())


def _compute_std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    return math.sqrt(variance)


def _compute_trigrams(tokens: list[str]) -> list[tuple[str, str, str]]:
    if len(tokens) < 3:
        return []
    return [(tokens[i], tokens[i + 1], tokens[i + 2]) for i in range(len(tokens) - 2)]


def run_layer_d(body: str) -> dict[str, Any]:
    """Compute deterministic style metrics."""
    plain = _strip_markdown(body)

    sentences = _split_sentences(plain)
    sentence_lengths = [len(s.split()) for s in sentences]

    if sentence_lengths:
        sentence_length_mean = sum(sentence_lengths) / len(sentence_lengths)
        sentence_length_std = _compute_std([float(x) for x in sentence_lengths])
    else:
        sentence_length_mean = 0.0
        sentence_length_std = 0.0

    paragraphs = _split_paragraphs(plain)
    paragraph_word_counts = [len(p.split()) for p in paragraphs]
    if len(paragraph_word_counts) >= 2:
        mean_p = sum(paragraph_word_counts) / len(paragraph_word_counts)
        paragraph_length_variance = sum(
            (c - mean_p) ** 2 for c in paragraph_word_counts
        ) / len(paragraph_word_counts)
    else:
        paragraph_length_variance = 0.0

    tokens = _word_tokens(plain)
    if tokens:
        ttr = len(set(tokens)) / len(tokens)
    else:
        ttr = 0.0

    trigrams = _compute_trigrams(tokens)
    trigram_counts = Counter(trigrams)
    repeated_trigrams = sum(1 for count in trigram_counts.values() if count >= 3)

    # Punctuation ratio: commas per sentence
    comma_count = plain.count(",")
    punctuation_ratio = comma_count / len(sentences) if sentences else 0.0

    # AI-risk heuristic
    if ttr > 0.5 and sentence_length_std > 5:
        ai_risk = "low"
    elif ttr < 0.35:
        ai_risk = "high"
    else:
        ai_risk = "medium"

    return {
        "sentence_length_mean": round(sentence_length_mean, 2),
        "sentence_length_std": round(sentence_length_std, 2),
        "paragraph_length_variance": round(paragraph_length_variance, 2),
        "ttr": round(ttr, 4),
        "repeated_trigrams": repeated_trigrams,
        "punctuation_ratio": round(punctuation_ratio, 2),
        "ai_risk": ai_risk,
    }

# ---------------------------------------------------------------------------
# Composite score + decision
# ---------------------------------------------------------------------------

def run_voice_drift(article_body: str) -> dict[str, Any]:
    """Run voice drift analysis if baseline exists. Returns drift info or nulls."""
    null_result: dict[str, Any] = {"voice_drift_score": None, "drift_level": None, "drift_anomalies": []}
    if not _VOICE_BASELINE_PATH.exists():
        return null_result
    try:
        import json as _json
        from voice_baseline import compute_features
        from voice_drift import compute_drift
        baseline = _json.loads(_VOICE_BASELINE_PATH.read_text(encoding="utf-8"))
        features = compute_features(article_body)
        if features is None:
            return null_result
        drift = compute_drift(features, baseline)
        return {
            "voice_drift_score": drift["drift_score"],
            "drift_level": drift["drift_level"],
            "drift_anomalies": drift["anomalies"],
        }
    except Exception:
        return null_result


def compute_score(layer_a: dict, layer_b: dict, layer_c: dict, layer_d: dict, drift: dict | None = None) -> int:
    score = 100

    score -= layer_b["vale_errors"] * 10
    score -= layer_b["vale_warnings"] * 3
    score -= layer_b["vale_suggestions"] * 1

    score -= layer_a["markdownlint_errors"] * 5

    score -= layer_c["failure_count"] * 5

    ai_risk = layer_d["ai_risk"]
    if ai_risk == "medium":
        score -= 5
    elif ai_risk == "high":
        score -= 15

    if drift is not None and drift.get("drift_level"):
        drift_level = drift["drift_level"]
        if drift_level == "high":
            score -= 15
        elif drift_level == "medium":
            score -= 5

    return max(0, min(100, score))


def determine_hard_failures(layer_a: dict, layer_b: dict) -> list[str]:
    failures: list[str] = []
    for field in layer_a["missing_frontmatter"]:
        failures.append(f"missing_frontmatter:{field}")
    if layer_b["vale_errors"] > 0:
        failures.append(f"vale_errors:{layer_b['vale_errors']}")
    return failures


def determine_decision(score: int, hard_failures: list[str]) -> str:
    if hard_failures:
        return "block"
    if score < 85:
        return "review"
    return "pass"

# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def build_report(
    article_path: str,
    article: Any,
    layer_a: dict,
    layer_b: dict,
    layer_c: dict,
    layer_d: dict,
) -> dict[str, Any]:
    drift = run_voice_drift(article.body)
    score = compute_score(layer_a, layer_b, layer_c, layer_d, drift=drift)
    hard_failures = determine_hard_failures(layer_a, layer_b)
    decision = determine_decision(score, hard_failures)

    style_metrics = dict(layer_d)
    style_metrics["voice_drift_score"] = drift["voice_drift_score"]
    style_metrics["drift_anomalies"] = drift["drift_anomalies"]

    return {
        "file": article_path,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "score": score,
        "hard_failures": hard_failures,
        "layers": {
            "structural": {
                "missing_frontmatter": layer_a["missing_frontmatter"],
                "markdownlint_errors": layer_a["markdownlint_errors"],
                "markdownlint_skipped": layer_a["markdownlint_skipped"],
            },
            "editorial": {
                "vale_errors": layer_b["vale_errors"],
                "vale_warnings": layer_b["vale_warnings"],
                "vale_suggestions": layer_b["vale_suggestions"],
                "ai_pattern_hits": layer_b["ai_pattern_hits"],
                "vale_skipped": layer_b["vale_skipped"],
            },
            "platform_fit": {
                "failures": layer_c["failures"],
                "failure_count": layer_c["failure_count"],
            },
            "style": style_metrics,
        },
    }


def format_text(report: dict[str, Any]) -> str:
    lines = [
        f"Content QA — {report['file']}",
        f"Decision : {report['decision'].upper()}",
        f"Score    : {report['score']}/100",
    ]
    if report["hard_failures"]:
        lines.append(f"Hard failures: {', '.join(report['hard_failures'])}")

    s = report["layers"]["structural"]
    lines.append("\n[A] Structural")
    if s["missing_frontmatter"]:
        lines.append(f"  Missing frontmatter: {', '.join(s['missing_frontmatter'])}")
    if s["markdownlint_skipped"]:
        lines.append("  markdownlint: skipped (not installed)")
    else:
        lines.append(f"  markdownlint errors: {s['markdownlint_errors']}")

    e = report["layers"]["editorial"]
    lines.append("\n[B] Editorial")
    if e["vale_skipped"]:
        lines.append("  vale: skipped (not installed)")
    else:
        lines.append(
            f"  vale: {e['vale_errors']} errors, {e['vale_warnings']} warnings, "
            f"{e['vale_suggestions']} suggestions, {e['ai_pattern_hits']} AI hits"
        )

    p = report["layers"]["platform_fit"]
    lines.append("\n[C] Platform fit")
    if p["failure_count"] == 0:
        lines.append("  All platforms: OK")
    else:
        for f in p["failures"]:
            lines.append(
                f"  {f['platform']}.{f['field']}: {f['actual']} > {f['limit']}"
            )

    st = report["layers"]["style"]
    lines.append("\n[D] Style metrics")
    lines.append(f"  sentence_length_mean : {st['sentence_length_mean']}")
    lines.append(f"  sentence_length_std  : {st['sentence_length_std']}")
    lines.append(f"  ttr                  : {st['ttr']}")
    lines.append(f"  repeated_trigrams    : {st['repeated_trigrams']}")
    lines.append(f"  punctuation_ratio    : {st['punctuation_ratio']}")
    lines.append(f"  ai_risk              : {st['ai_risk']}")

    return "\n".join(lines)

# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="4-layer content QA: structural, editorial, platform fit, style"
    )
    parser.add_argument("file", help="Path to Markdown article")
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat 'review' as 'block'",
    )
    args = parser.parse_args(argv)

    article = parse_article(args.file)

    layer_a = run_layer_a(args.file, article)
    layer_b = run_layer_b(args.file)
    layer_c = run_layer_c(article)
    layer_d = run_layer_d(article.body)

    report = build_report(args.file, article, layer_a, layer_b, layer_c, layer_d)

    if args.strict and report["decision"] == "review":
        report["decision"] = "block"

    _log_telemetry(report, args.file, article.body)

    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(format_text(report))

    decision = report["decision"]
    if decision == "pass":
        sys.exit(0)
    elif decision == "review":
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()
