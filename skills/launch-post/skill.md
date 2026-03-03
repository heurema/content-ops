---
name: launch-post
description: 'Use when the user wants to announce a product launch or new feature. Triggers: "HN Show post", "announce feature", "product launch post", "announce on HN", "write launch announcement", "post on HN".'
---

Read `.agents/content-context.md` first (if it exists).

## Purpose

Write launch announcements for developer channels. Different channels need different framing.

## Templates

### Show HN (Hacker News)

Format: `Show HN: <what it does in plain English>`

Rules:
- Under 80 chars
- No adjectives ("powerful", "simple", "amazing")
- Describe the thing, not your feelings about it
- Examples: "Show HN: A CLI that cross-posts Markdown articles to dev.to and Hashnode"

Body (comment on your own submission):
- What problem it solves (1 sentence)
- How it works (2-3 sentences, technical)
- What you'd love feedback on (specific)
- Link to repo

### Reddit (r/programming, r/ClaudeAI)

- Title: factual, not promotional
- Body: context + link (self posts or link posts depending on subreddit)
- Note: Reddit API requires pre-existing credentials (see `docs/setup.md`)

### Email announcement (newsletter)

- Subject: specific benefit, not "exciting news"
- Body: what changed + why it matters + one call to action

## Process

1. Ask: Which channel? (HN, Reddit, email, all)
2. Ask: What are you launching? (feature, new version, new project)
3. Generate draft for each selected channel.
4. For HN: offer to run `/publish-hn` to generate the submitlink.
