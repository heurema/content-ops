#!/usr/bin/env python3
"""Score an article against a stylometric voice baseline for drift detection.

Usage:
    python3 tools/voice_drift.py <article.md> --baseline <path.json> [--format json|text]

Outputs a drift report with z-scores, anomalies, and an overall drift_score (0-100).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from shared.env import load as _load_env; _load_env()
from shared.article import parse_article
from voice_baseline import compute_features, FEATURE_NAMES

# ---------------------------------------------------------------------------
# Anomaly notes
# ---------------------------------------------------------------------------

_ANOMALY_NOTES: dict[str, dict[str, str]] = {
    "sentence_length_mean": {
        "high": "sentences longer than usual",
        "low": "sentences shorter than usual",
    },
    "sentence_length_std": {
        "high": "sentence length more variable than usual",
        "low": "sentence length less variable than usual",
    },
    "ttr": {
        "high": "vocabulary more diverse than usual",
        "low": "vocabulary less diverse than usual",
    },
    "paragraph_count": {
        "high": "more paragraphs than usual",
        "low": "fewer paragraphs than usual",
    },
    "avg_paragraph_length": {
        "high": "paragraphs longer than usual",
        "low": "paragraphs shorter than usual",
    },
    "punctuation_rate": {
        "high": "more commas per sentence than usual",
        "low": "fewer commas per sentence than usual",
    },
    "function_word_ratio": {
        "high": "higher function word ratio than usual",
        "low": "lower function word ratio than usual",
    },
}


def _note(feature: str, z_score: float) -> str:
    direction = "high" if z_score > 0 else "low"
    return _ANOMALY_NOTES.get(feature, {}).get(direction, "unusual value")

# ---------------------------------------------------------------------------
# Core drift computation
# ---------------------------------------------------------------------------

def compute_drift(article_features: dict[str, float], baseline: dict) -> dict:
    """Compute z-scores, anomalies, drift_score and drift_level."""
    baseline_features = baseline.get("features", {})

    z_scores: dict[str, float] = {}
    anomalies: list[dict] = []

    for name in FEATURE_NAMES:
        if name not in article_features or name not in baseline_features:
            continue
        bfeat = baseline_features[name]
        b_mean = bfeat.get("mean", 0.0)
        b_std = bfeat.get("std", 0.0)
        value = article_features[name]

        if b_std == 0.0:
            # Cannot compute meaningful z-score — skip
            continue

        z = (value - b_mean) / b_std
        z_scores[name] = z

        if abs(z) > 2.0:
            anomalies.append({
                "feature": name,
                "value": round(value, 6),
                "baseline_mean": round(b_mean, 6),
                "z_score": round(z, 4),
                "note": _note(name, z),
            })

    # drift_score: mean of |z| * 10, clamped to 0-100
    if z_scores:
        mean_abs_z = sum(abs(z) for z in z_scores.values()) / len(z_scores)
        drift_score = min(100, max(0, round(mean_abs_z * 10)))
    else:
        drift_score = 0

    if drift_score < 30:
        drift_level = "low"
    elif drift_score <= 50:
        drift_level = "medium"
    else:
        drift_level = "high"

    return {
        "drift_score": drift_score,
        "drift_level": drift_level,
        "anomalies": anomalies,
    }

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Score an article against a voice baseline for drift detection"
    )
    parser.add_argument("article", help="Path to Markdown article")
    parser.add_argument("--baseline", required=True, help="Path to baseline JSON file")
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="json",
        help="Output format (default: json)",
    )
    args = parser.parse_args(argv)

    baseline_path = Path(args.baseline)
    if not baseline_path.exists():
        result = {
            "drift_score": None,
            "drift_level": "unknown",
            "anomalies": [],
            "error": "baseline not found",
        }
        print(json.dumps(result, indent=2))
        sys.exit(0)

    try:
        baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        result = {
            "drift_score": None,
            "drift_level": "unknown",
            "anomalies": [],
            "error": f"failed to load baseline: {exc}",
        }
        print(json.dumps(result, indent=2))
        sys.exit(1)

    article = parse_article(args.article)
    features = compute_features(article.body)

    if features is None:
        result = {
            "drift_score": None,
            "drift_level": "unknown",
            "anomalies": [],
            "error": "article body is empty",
        }
        print(json.dumps(result, indent=2))
        sys.exit(0)

    report = compute_drift(features, baseline)

    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        lines = [
            f"Voice drift — {args.article}",
            f"drift_score : {report['drift_score']}/100",
            f"drift_level : {report['drift_level']}",
        ]
        if report["anomalies"]:
            lines.append("anomalies:")
            for a in report["anomalies"]:
                lines.append(
                    f"  {a['feature']}: value={a['value']}, "
                    f"baseline_mean={a['baseline_mean']}, "
                    f"z={a['z_score']} — {a['note']}"
                )
        else:
            lines.append("anomalies: none")
        print("\n".join(lines))


if __name__ == "__main__":
    main()
