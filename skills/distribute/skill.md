---
name: distribute
description: 'Use when the user wants to publish an article to multiple platforms at once. Triggers: "publish article", "distribute to platforms", "send to devto and hashnode", "cross-post", "publish everywhere", "distribute my post".'
---

Read `.agents/content-context.md` first (if it exists).

## Purpose

Orchestrate the full publishing workflow: QA — publish each platform — update state.

## State tracking

Check `.content-ops-state.json` (in article's directory) for in-progress publishes.
If article was partially published, skip completed platforms and resume.

```json
{
  "article-slug": {
    "devto": "published",
    "hashnode": "failed",
    "twitter": "pending"
  }
}
```

## Process

1. Run content-qa skill first. If failures: stop and ask user to fix.
2. Ask: Which platforms? (dev.to, Hashnode, Twitter/X, HN, or all)
3. For each platform in order:
   a. Show dry-run preview
   b. Ask for confirmation
   c. Run publish command
   d. Update state file
4. After all platforms: report summary table

```
Platform  | Status  | URL
----------|---------|-----
dev.to    | OK      | https://dev.to/...
Hashnode  | OK      | https://hashnode.dev/...
Twitter/X | OK      | https://x.com/...
HN        | Link    | https://news.ycombinator.com/submitlink?...
```

## Notes

- Always dry-run first, confirm per platform — never batch-post without human review
- Twitter/X posts last (most volatile platform)
- HN is always human-in-loop (submitlink, not automated post)
- If a platform fails: update state file as "failed", continue with next platform
- User can re-run distribute to resume from failed platforms
