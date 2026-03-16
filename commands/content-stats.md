---
name: content-stats
description: "Show engagement stats for a published article across all platforms."
---

Fetch and display engagement stats for the article at `$ARTICLE_PATH`.

## Steps

1. Run the stats tool:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/tools/stats_article.py "$ARTICLE_PATH"
   ```
2. Report the table to the user.
3. If any platforms show `(error)`, explain which env var may be missing.

## Notes

- Only platforms with a stored ID in frontmatter are queried (e.g. `devto_id`, `hashnode_id`, `twitter_thread_id`, `hn_story_id`, `mastodon_post_id`).
- Bluesky and LinkedIn stats are not available — will print a note.
- Use `--json` for machine-readable output:
  ```bash
  python3 ${CLAUDE_PLUGIN_ROOT}/tools/stats_article.py "$ARTICLE_PATH" --json
  ```
- Required env vars per platform:
  - dev.to: `DEVTO_API_KEY`
  - Twitter/X: `X_BEARER_TOKEN`
  - Mastodon: `MASTODON_INSTANCE_URL`
  - Hashnode, HN: no auth needed
