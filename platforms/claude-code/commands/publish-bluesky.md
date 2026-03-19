---
name: publish-bluesky
description: Publish a Markdown article to Bluesky as a link-card post. Reads YAML frontmatter for title, description, tags, canonical_url. Writes back bluesky_post_id and bluesky_post_url after publish.
---

Publish the article at `$ARTICLE_PATH` to Bluesky.

## Steps

1. Check that `BLUESKY_HANDLE` and `BLUESKY_APP_PASSWORD` are set in the environment.
2. Run in dry-run mode first to preview the post:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/tools/publish_bluesky.py "$ARTICLE_PATH" --dry-run
   ```
3. Show the user the post text and grapheme count, then ask for confirmation.
4. If confirmed, publish with:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/tools/publish_bluesky.py "$ARTICLE_PATH" --confirm
   ```
5. Report the Bluesky post URL from the output.

## Notes

- Bluesky enforces a 300 grapheme limit per post.
- Phase 1: single link-card post only (no threads).
- Post is formatted as: title + description + hashtags + canonical URL.
- If text exceeds 300 graphemes, description is dropped, then title is truncated.
- If `BLUESKY_HANDLE` or `BLUESKY_APP_PASSWORD` is not set, redirect the user to `docs/setup.md`.
