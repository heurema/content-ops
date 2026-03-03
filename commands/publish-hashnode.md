---
name: publish-hashnode
description: Publish a Markdown article to Hashnode. Uses GraphQL publishPost mutation. Writes back hashnode_id and hashnode_url after publish.
---

Publish the article at `$ARTICLE_PATH` to Hashnode.

## Steps

1. Check that `HASHNODE_TOKEN` and `HASHNODE_PUBLICATION_ID` are set.
2. Dry-run preview:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/tools/publish_hashnode.py "$ARTICLE_PATH" --dry-run
   ```
3. Show GraphQL variables to user, ask for confirmation.
4. Publish:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/tools/publish_hashnode.py "$ARTICLE_PATH" --confirm
   ```
5. Report the Hashnode post URL.

## Notes

- Tags are converted to `{name, slug}` objects required by Hashnode API.
- If tag slug doesn't exist on Hashnode, the API creates it.
- Missing env vars: redirect to `docs/setup.md`.
