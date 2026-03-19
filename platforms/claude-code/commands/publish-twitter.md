---
name: publish-twitter
description: Convert a Markdown article into a Twitter/X thread and post it. Generates 6-8 tweets, validates 280-char limit, posts with 1s delay between tweets.
---

Post the article at `$ARTICLE_PATH` as a Twitter/X thread.

## Steps

1. Check that all 4 X credentials are set: `X_API_KEY`, `X_API_KEY_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET`.
2. Generate and preview the thread:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/tools/publish_twitter.py "$ARTICLE_PATH" --dry-run
   ```
3. Show the numbered tweets to the user. Ask if they want to edit any tweets before posting.
4. If edits needed, modify the thread manually in the preview, then post:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/tools/publish_twitter.py "$ARTICLE_PATH" --confirm
   ```
5. Report the thread URL (first tweet URL).

## Platform Risk Warning

X API free tier (500 posts/month) is volatile. The `--dry-run` default is intentional.
If the API returns an error, check `docs/setup.md` for current tier status.
