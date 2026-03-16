---
name: publish-linkedin
description: Publish a Markdown article to LinkedIn as a ugcPost link share. Reads YAML frontmatter for title, description, canonical_url. Writes back linkedin_post_id and linkedin_post_url after publish.
---

Publish the article at `$ARTICLE_PATH` to LinkedIn.

## Steps

1. Check that `LINKEDIN_ACCESS_TOKEN` and `LINKEDIN_PERSON_URN` are set in the environment.
2. Run in dry-run mode first to preview the payload:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/tools/publish_linkedin.py "$ARTICLE_PATH" --dry-run
   ```
3. Show the user the ugcPost payload and ask for confirmation.
4. If confirmed, publish with:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/tools/publish_linkedin.py "$ARTICLE_PATH" --confirm
   ```
5. Report the LinkedIn post URL from the output.

## Notes

- Uses LinkedIn ugcPosts API (self-service, not Partner Program).
- OAuth 2.0 token must be obtained manually and stored as `LINKEDIN_ACCESS_TOKEN`.
- `LINKEDIN_PERSON_URN` format: `urn:li:person:AbCdEfGhIj` (find in LinkedIn API dashboard).
- If `LINKEDIN_ACCESS_TOKEN` or `LINKEDIN_PERSON_URN` is not set, redirect the user to `docs/setup.md`.
