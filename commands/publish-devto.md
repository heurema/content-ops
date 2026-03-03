---
name: publish-devto
description: Publish a Markdown article to dev.to. Reads YAML frontmatter for title, description, tags, canonical_url. Writes back devto_id and devto_url after publish.
---

Publish the article at `$ARTICLE_PATH` to dev.to.

## Steps

1. Check that `DEVTO_API_KEY` is set in the environment.
2. Run in dry-run mode first to preview the payload:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/tools/publish_devto.py "$ARTICLE_PATH" --dry-run
   ```
3. Show the user the payload and ask for confirmation.
4. If confirmed, publish with:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/tools/publish_devto.py "$ARTICLE_PATH" --confirm
   ```
5. Report the dev.to URL from the output.

## Notes

- Dev.to enforces max 4 tags — extra tags are silently truncated.
- If `devto_id` already exists in frontmatter, uses PUT (update) instead of POST (create).
- If `DEVTO_API_KEY` is not set, redirect the user to `docs/setup.md`.
