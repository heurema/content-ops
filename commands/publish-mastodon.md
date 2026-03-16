---
name: publish-mastodon
description: Publish a Markdown article to Mastodon as a status post. Reads YAML frontmatter for title, description, tags, canonical_url. Writes back mastodon_post_id and mastodon_post_url after publish.
---

Publish the article at `$ARTICLE_PATH` to Mastodon.

## Steps

1. Check that `MASTODON_ACCESS_TOKEN` and `MASTODON_INSTANCE_URL` are set in the environment.
2. Run in dry-run mode first to preview the status:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/tools/publish_mastodon.py "$ARTICLE_PATH" --dry-run
   ```
3. Show the user the status text and character count, then ask for confirmation.
4. If confirmed, publish with:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/tools/publish_mastodon.py "$ARTICLE_PATH" --confirm
   ```
5. Report the Mastodon post URL from the output.

## Notes

- Mastodon enforces a 500 character limit per status (default; some instances differ).
- Status is formatted as: title + description + hashtags + canonical URL.
- If text exceeds 500 characters, description is dropped, then title is truncated.
- Token must be obtained manually via your Mastodon instance OAuth settings.
- If `MASTODON_ACCESS_TOKEN` or `MASTODON_INSTANCE_URL` is not set, redirect the user to `docs/setup.md`.
