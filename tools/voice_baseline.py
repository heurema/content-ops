#!/usr/bin/env python3
"""Build a stylometric voice baseline from a corpus of Markdown articles.

Usage:
    python3 tools/voice_baseline.py <directory_or_glob> [--output path.json]

Outputs JSON with mean+std for each feature across all parsed articles.
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from shared.env import load as _load_env; _load_env()
from shared.article import parse_article

# ---------------------------------------------------------------------------
# Function word list (~50 English function words)
# ---------------------------------------------------------------------------

FUNCTION_WORDS = frozenset({
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "shall",
    "should", "may", "might", "can", "could", "must", "of", "in", "to",
    "for", "with", "on", "at", "by", "from", "as", "into", "about",
    "between", "through", "this", "that", "it", "not", "or", "and",
    "but", "if", "so", "yet",
})

# ---------------------------------------------------------------------------
# Markdown stripping
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
# Feature computation
# ---------------------------------------------------------------------------

def _compute_std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    return math.sqrt(variance)


def compute_features(body: str) -> dict[str, float] | None:
    """Compute stylometric features from article body. Returns None if body is empty."""
    plain = _strip_markdown(body).strip()
    if not plain:
        return None

    # Sentences: split on [.!?] followed by whitespace or end of string
    sentence_parts = re.split(r"[.!?]+(?:\s+|\n|$)", plain)
    sentences = [s.strip() for s in sentence_parts if s.strip()]

    sentence_word_counts = [len(s.split()) for s in sentences]
    if sentence_word_counts:
        sentence_length_mean = sum(sentence_word_counts) / len(sentence_word_counts)
        sentence_length_std = _compute_std([float(c) for c in sentence_word_counts])
    else:
        sentence_length_mean = 0.0
        sentence_length_std = 0.0

    # Paragraphs: split on double newline
    paragraph_parts = re.split(r"\n{2,}", plain)
    paragraphs = [p.strip() for p in paragraph_parts if p.strip()]
    paragraph_count = len(paragraphs)
    if paragraphs:
        avg_paragraph_length = sum(len(p.split()) for p in paragraphs) / len(paragraphs)
    else:
        avg_paragraph_length = 0.0

    # Words: lowercase alpha tokens
    all_words = re.findall(r"[a-z]+", plain.lower())
    total_words = len(all_words)

    if total_words > 0:
        ttr = len(set(all_words)) / total_words
        function_word_ratio = sum(1 for w in all_words if w in FUNCTION_WORDS) / total_words
    else:
        ttr = 0.0
        function_word_ratio = 0.0

    # Punctuation rate: commas per sentence
    comma_count = plain.count(",")
    punctuation_rate = comma_count / len(sentences) if sentences else 0.0

    return {
        "sentence_length_mean": sentence_length_mean,
        "sentence_length_std": sentence_length_std,
        "ttr": ttr,
        "paragraph_count": float(paragraph_count),
        "avg_paragraph_length": avg_paragraph_length,
        "punctuation_rate": punctuation_rate,
        "function_word_ratio": function_word_ratio,
    }

# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

FEATURE_NAMES = [
    "sentence_length_mean",
    "sentence_length_std",
    "ttr",
    "paragraph_count",
    "avg_paragraph_length",
    "punctuation_rate",
    "function_word_ratio",
]


def aggregate_features(per_file: list[dict[str, float]]) -> dict[str, dict[str, float]]:
    """Aggregate per-file feature dicts into {feature: {mean, std}}."""
    result: dict[str, dict[str, float]] = {}
    for name in FEATURE_NAMES:
        values = [f[name] for f in per_file if name in f]
        if values:
            mean = sum(values) / len(values)
            std = _compute_std(values)
        else:
            mean = 0.0
            std = 0.0
        result[name] = {"mean": round(mean, 6), "std": round(std, 6)}
    return result

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Build a stylometric voice baseline from a corpus of Markdown articles"
    )
    parser.add_argument(
        "source",
        help="Directory of .md files or glob pattern (e.g. posts/**/*.md)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Write JSON to this path (default: stdout)",
    )
    args = parser.parse_args(argv)

    # Resolve source: directory → glob all .md, otherwise treat as glob pattern
    source_path = Path(args.source)
    if source_path.is_dir():
        md_files = sorted(source_path.glob("*.md"))
        source_directory = str(source_path.resolve())
    else:
        md_files = [Path(p) for p in sorted(glob.glob(args.source, recursive=True))]
        source_directory = args.source

    per_file_features: list[dict[str, float]] = []
    skipped = 0

    for md_path in md_files:
        try:
            article = parse_article(str(md_path))
            if not article.body or not article.body.strip():
                skipped += 1
                continue
            features = compute_features(article.body)
            if features is None:
                skipped += 1
                continue
            per_file_features.append(features)
        except Exception:
            skipped += 1
            continue

    aggregated = aggregate_features(per_file_features)

    output = {
        "features": aggregated,
        "corpus_size": len(per_file_features),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_directory": source_directory,
    }

    json_str = json.dumps(output, indent=2)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json_str, encoding="utf-8")
        print(f"Baseline written to {args.output} ({len(per_file_features)} files, {skipped} skipped)")
    else:
        print(json_str)


if __name__ == "__main__":
    main()
