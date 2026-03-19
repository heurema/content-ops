---
name: launch-post
description: 'Use when the user wants to announce a product launch or new feature. Triggers: "HN Show post", "announce feature", "product launch post", "announce on HN", "write launch announcement", "post on HN", "Product Hunt post", "IndieHackers post", "GitHub launch".'
---

Read `.agents/content-context.md` first (if it exists).

## Purpose

Write launch announcements for developer channels. Different channels need different framing.

## Templates

### Show HN (Hacker News)

Title formula: `Show HN: [Product Name] – [One-sentence value proposition]`

Rules:
- Under 80 chars
- No adjectives ("powerful", "simple", "amazing")
- Describe the thing, not your feelings about it
- Show HN is ONLY for things people can run/try — blog posts and pure announcements are off-topic
- Post Tue–Thu, 8–10 AM PT for best visibility
- Leave a substantive first comment within 5 minutes of submission

Body structure (first comment on your own submission):
1. Who you are (1 sentence, relevant background only)
2. What it does (1 sentence, plain English)
3. Problem it solves (1-2 sentences, concrete)
4. Backstory — why you built it
5. Technical approach (2-3 sentences)
6. How it differs from alternatives
7. Specific ask for feedback

After approval: offer to run `/publish-hn` to generate the submitlink.

### Product Hunt

Tagline: ~60 chars, action-oriented, no superlatives.
Formula: `[Product] – [Verb] [Outcome] for [Audience]`
Example: `content-ops – Cross-post Markdown articles to dev.to and Hashnode`

Maker comment (≤800 chars):
1. What changed / what you built
2. Why it matters
3. Where to start
4. CTA (upvote, try it, share feedback)

Timing: post Tue–Thu at 12:01 AM PST (leaderboard resets at midnight PST).
Pre-launch: 2–4 weeks of teaser content; aim for 300+ waitlist before launch day.

### Reddit

Subreddit tiers:
- Permissive (self-promo OK): r/SideProject, r/IMadeThis, r/AlphaAndBetaUsers
- Cautious (add value first): r/SaaS, r/Entrepreneur
- No direct promo: r/programming, r/webdev — use their Showoff Saturday threads instead

Rules:
- 90/10 rule: 90% genuine participation, 10% promotional
- Frame as "war story" or "lessons learned", not a product announcement
- Put the link in the first comment, not the post body
- Title: factual, not promotional

### IndieHackers

Headline formula: `[Specific number] + [Transformation] + [Timeframe]`
Example: `$1,200 MRR in 90 days building in public — what worked and what didn't`

- Journey posts with specific revenue or growth numbers
- 750–1,500 words; include honest failures alongside wins
- Converts at 12–24% (vs PH's 1–3%), but requires 90+ days of community presence before posting

### GitHub

- Social preview image: 1280×640 px
- Up to 20 repo tags — choose terms your audience actually searches
- Submit to relevant `awesome-*` lists
- GitHub Releases: full changelogs with migration notes, not just version bumps

### "I built X" article (dev.to / Hashnode)

Title: specific and descriptive, no clickbait.

Body structure:
1. Problem (concrete — what broke, what was missing)
2. Approach (why this solution, what you tried first)
3. Technical details (enough for a developer to reproduce it)
4. What you learned
5. Link + repo

Set `canonical_url` to your own domain when cross-posting. Publish on your domain first, then cross-post.

### Email announcement (newsletter)

- Subject: specific benefit, not "exciting news"
- Body: what changed → why it matters → one call to action

## Process

1. Ask: Which channel(s)? (Show HN, Product Hunt, Reddit, IndieHackers, GitHub, "I built X" article, email, all)
2. Ask: What are you launching? (feature, new version, new project)
3. Generate draft for each selected channel.
4. Show previews, ask for edits.
5. For Show HN: offer to run `/publish-hn` to generate the submitlink.
