---
name: lint-article
description: Lint an article for publishing issues before sending to any platform. Deterministic checks — exits non-zero on errors.
---

Run deterministic checks on `$ARTICLE_PATH` before publishing.

## Steps

1. Run:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/tools/lint_article.py "$ARTICLE_PATH"
   ```
2. Show the output to the user.
3. If exit code is non-zero, **stop** — do not proceed to any publish command.
4. Fix errors before re-running lint.

## Checks performed

| Level | Check |
|-------|-------|
| ERROR | Em dashes (—) in prose — AI generation signal |
| ERROR | Description > 160 chars (truncated by platforms) |
| ERROR | Missing required frontmatter: title, description, tags |
| WARNING | En dashes (–) in prose |
| WARNING | Tags with hyphens (break dev.to) |
| WARNING | Description 151–160 chars (approaching limit) |

## Notes

- Code blocks are excluded from typography checks.
- `--strict` flag promotes warnings to errors.
- Run this before every publish, not just the first time.
