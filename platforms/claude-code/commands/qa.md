---
name: qa
description: Run deterministic content QA on an article. 4-layer check — structural, editorial (Vale), platform-fit, style metrics. Returns JSON report with composite score and pass/review/block decision.
---

Run the 4-layer content QA pipeline on `$ARTICLE_PATH`.

## Steps

1. Run:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/tools/content_qa.py "$ARTICLE_PATH" --format text
   ```
2. Show the output to the user.
3. Check exit code:
   - `0` — **pass**: article is ready to publish
   - `1` — **review**: show issues, ask user whether to proceed or fix first
   - `2` — **block**: hard failures found, must fix before publishing

4. If the user wants JSON output for programmatic use:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/tools/content_qa.py "$ARTICLE_PATH" --format json
   ```

## What it checks

| Layer | Check | Tool |
|-------|-------|------|
| A — Structural | Required frontmatter, markdown formatting | markdownlint |
| B — Editorial | Prose quality, AI-pattern detection | Vale + ContentOps rules |
| C — Platform fit | Title/description/tag limits per platform | Hardcoded limits |
| D — Style metrics | TTR, sentence variance, trigrams, punctuation | Stdlib analysis |

## Composite score

Score 0-100 based on weighted penalties from all layers. Decision thresholds:
- **>= 85** → pass (auto-publishable)
- **70-84** → review (manual check recommended)
- **< 70 or hard failures** → block (must fix)

## Notes

- Vale and markdownlint are optional — if not installed, those layers are skipped gracefully.
- Use `--strict` to promote review decisions to block.
- Run this before every publish. The `/distribute` command runs it automatically.
