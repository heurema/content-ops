---
name: publish-hn
description: Generate a Hacker News submitlink URL for an article. Checks Algolia for duplicates. human-in-loop — no auth required, no API posting.
---

Generate a Hacker News submit URL for the article at `$ARTICLE_PATH`.

## Steps

1. Run:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/tools/publish_hn.py "$ARTICLE_PATH"
   ```
2. Show the user the submitlink URL and any duplicate warnings.
3. If no duplicates: guide the user to open the URL in their browser.
4. Suggest title refinements:
   - Technical tool/project → prefix "Show HN: "
   - Blog post/essay → use article title as-is
   - Avoid: "I built X" (sounds spammy), all-caps, clickbait

## Notes

- HN submission is always human-in-loop — no automated posting.
- Best posting times: weekday mornings US Eastern.
- Don't submit the same URL twice — Algolia check helps avoid this.
