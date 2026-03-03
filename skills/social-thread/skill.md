---
name: social-thread
description: 'Use when the user wants to promote an article on social media. Triggers: "Twitter thread", "LinkedIn post", "social variants", "tweetstorm from article", "social media post", "share on Twitter".'
---

Read `.agents/content-context.md` first (if it exists).

## Purpose

Generate platform-specific social variants from a finished article. One article — multiple formats.

## Variants

### Twitter/X thread (default)

Generate 6-8 tweets:
- Tweet 1: Hook — specific claim or number that makes people want to read
- Tweets 2-6: One insight per tweet (not summaries — standalone value)
- Tweet 7: Pushback — what this approach won't solve
- Tweet 8: CTA + link

Each tweet: max 280 chars. Verify length before showing.

### LinkedIn post

Single post, 150-300 words:
- Open with a concrete result or observation (no "I'm excited to share")
- 3-5 paragraphs, each short
- Link in first comment (algorithm buries links in post body)
- 3-5 hashtags at end

### Bluesky / Mastodon

Same as Twitter thread but shorter hook, skip the pushback tweet.

## Process

1. Ask: Which platforms? (Twitter/X, LinkedIn, Bluesky, all)
2. Read the article.
3. Generate variants.
4. Show previews, ask for edits.
5. If Twitter/X selected: offer to run `/publish-twitter` after approval.
