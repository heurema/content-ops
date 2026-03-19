---
name: social-thread
description: 'Use when the user wants to promote an article on social media. Triggers: "Twitter thread", "LinkedIn post", "Bluesky post", "Mastodon toot", "LinkedIn carousel", "social variants", "tweetstorm from article", "social media post", "share on Twitter".'
---

Read `.agents/content-context.md` first (if it exists).

## Purpose

Generate platform-specific social variants from a finished article. One article — multiple formats.

## Variants

### Twitter/X thread (default)

Generate 8-12 tweets, numbered (1/, 2/, …):
- Tweet 1: Hook — pick one formula:
  - Bold contrarian claim ("Everyone does X. X is wrong.")
  - Specific promise with outcome ("How I did X in Y days — 3 things that mattered")
  - Story teaser ("Six months ago I almost shut this down.")
  - Surprising statistic ("X% of developers have never done Y.")
  - Question-based gap ("Why does X work when Y doesn't?")
- Tweets 2-9: One insight per tweet (not summaries — standalone value)
- Tweet 10: Pushback — what this approach won't solve
- Tweet 11-12: CTA + link (2026: X algorithm boosts external article links)

Each tweet: max 280 chars. Verify length before showing.

### LinkedIn post

Single post, up to 3000 chars:
- Open with a concrete result or observation (no "I'm excited to share")
- 3-5 paragraphs, each short
- No link in body — put link in first comment (algorithm penalty for links in post body)
- 3-5 hashtags at end
- Vertical images get 32% reach boost — note this when relevant

**Carousel option** (if article has a clear how-to or list structure): 6-9 slides, captions <100 chars each. Structure: Hook → Problem → Solution → How-to → Result → CTA.

### Bluesky

5-10 posts, numbered (1/7, 2/7, …):
- 300 chars per post (URLs count as 22 chars)
- Anti-corporate, direct tone — no hype
- Skip aggressive CTA; end with a low-key pointer to the article
- Same insight-per-post structure as Twitter, adapted in tone

After approval: offer to run `/publish-bluesky`.

### Mastodon

Single post or short thread (instance default: 500 chars/toot):
- Plain text only — no formatting tricks
- Tone: community-first, not broadcast
- Add content warning (`CW:`) for sensitive or political topics — cultural norm on most instances
- Hashtags at end; check instance-specific communities for relevant tags

After approval: offer to run `/publish-mastodon`.

## Process

1. Ask: Which platforms? (Twitter/X, LinkedIn, Bluesky, Mastodon, all)
2. Read the article.
3. Generate variants for selected platforms.
4. Show previews, ask for edits.
5. If Twitter/X selected: offer to run `/publish-twitter` after approval.
6. If LinkedIn selected: offer to run `/publish-linkedin` after approval.
7. If Bluesky selected: offer to run `/publish-bluesky` after approval.
8. If Mastodon selected: offer to run `/publish-mastodon` after approval.
