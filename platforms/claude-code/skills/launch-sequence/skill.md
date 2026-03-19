---
name: launch-sequence
description: 'Use when the user wants to plan and execute a multi-platform launch. Triggers: "launch plan", "launch sequence", "launch checklist", "multi-platform launch", "coordinate launch", "launch timeline".'
---

Read `.agents/content-context.md` first (if it exists).

## Purpose

Orchestrate a multi-platform launch across three tiers: a short spike, community seeding, and long-tail distribution. Each tier has different mechanics, timing, and content formats.

## Three-Tier Framework

| Tier | Channels | Window | Goal |
|------|----------|--------|------|
| Spike | Product Hunt, Show HN, BetaList | 24–72 h | Burst visibility, initial users |
| Community | IndieHackers, Reddit, Twitter #buildinpublic | Weeks 1–4 | Qualified audience, trust |
| Long-tail | dev.to / Hashnode, directories, awesome-* lists | Months–years | Compounding organic traffic |

Do not treat all three tiers as simultaneous. Spike content burns fast; long-tail content compounds slowly.

## Recommended Timeline

| Day | Action |
|-----|--------|
| -14 | Publish teaser on Twitter/Bluesky, open waitlist, start IH presence |
| -7  | "I'm building X" post on IndieHackers, Reddit r/SideProject |
| -3  | BetaList submission (7-day lead time); finalize PH assets (social preview, maker comment) |
| 0   | Product Hunt at 12:01 AM PST; Show HN at 8–10 AM PT (same day or next) |
| +1  | Reply to all PH and HN comments; post Twitter/Bluesky launch thread |
| +3  | "I built X" article on dev.to / Hashnode (link back to PH/HN threads) |
| +7  | Post-mortem / lessons-learned post on IndieHackers with real numbers |
| +14 | Submit to directories (BetaPage, Uneed, Lobste.rs, etc.) |
| +28 | Submit to awesome-* lists; write SEO-targeted follow-up article |

## Per-Platform Checklist

**Product Hunt**
- [ ] Social preview image (1200×630 px)
- [ ] Tagline ≤60 chars, no superlatives
- [ ] Maker comment drafted (≤800 chars)
- [ ] 300+ waitlist / supporters ready to upvote at launch

**Show HN**
- [ ] Thing is live and runnable (Show HN rejects pure announcements)
- [ ] Title ≤80 chars, plain English
- [ ] First comment written and ready to paste within 5 min of submission

**IndieHackers**
- [ ] 90+ days of community participation before launch post
- [ ] Real numbers (revenue, users, growth)
- [ ] 750–1,500 words, includes failures

**Reddit**
- [ ] Correct subreddit tier identified (permissive / cautious / Showoff Saturday)
- [ ] Link goes in first comment, not post body
- [ ] War-story framing, not announcement framing

**dev.to / Hashnode**
- [ ] `canonical_url` set to own domain
- [ ] Published on own domain first
- [ ] Tags relevant and within platform limits

**GitHub**
- [ ] Social preview image set (1280×640 px)
- [ ] Up to 20 tags applied
- [ ] GitHub Release with full changelog published

## Process

1. Ask: What are you launching? (product, feature, version — include URL if live)
2. Ask: Which tiers? (Spike only, Community only, Full sequence)
3. Ask: Launch date (to back-calculate the timeline).
4. Generate a timeline table customized to their dates.
5. For each platform in the plan, call the relevant skill:
   - Content drafts → `launch-post` skill
   - Social threads → `social-thread` skill
6. Track completion: update `.content-ops-state.json` with platform statuses.
7. After launch day: prompt for post-mortem numbers (PH rank, HN points, signups) to feed the IH lessons post.

## Notes

- Never post Spike content and Community content on the same day — pace it
- IH and Reddit require community presence before the launch post pays off; start early
- Long-tail directories have cumulative value but low single-day impact — do not skip them
- Show HN and PH on the same day is high-risk (splits attention); 24 h apart is safer
