---
title: "Content-Ops Enhancement Research: Multi-Platform Distribution & Promotion"
run_id: "20260316T073535Z-48111"
date: 2026-03-16
depth: medium
verification_status: unverified
completion_status: complete
agents: 4
sources: 40+
topic: "Content-ops plugin enhancement — similar tools, approaches, and resources for promoting developer projects across multiple platforms"
---

# Content-Ops Enhancement Research

## Executive Summary

Current content-ops supports 4 platforms: dev.to, Hashnode, Twitter/X, Hacker News (human-in-loop). Research identified **3 platforms with viable APIs** for immediate addition (Bluesky, Mastodon, LinkedIn), mapped **content adaptation rules** for 7 platform formats, documented **launch promotion workflows** across 6 communities, and found **analytics APIs** for all currently supported platforms.

## 1. New Platforms to Add

### Priority Additions (viable API, worth implementing)

#### Bluesky — RECOMMENDED FIRST
- **API**: Official, open, stable (AT Protocol)
- **Auth**: JWT via `com.atproto.server.createSession` (handle + app password). No OAuth needed.
- **Publish**: `com.atproto.repo.createRecord` with `app.bsky.feed.post` lexicon
- **Limit**: 300 graphemes per post. URLs = 22 chars. No native article support — threads or link cards.
- **Rate limit**: 5,000 points/hour (CREATE = 3 pts → ~1,666 posts/hour)
- **SDK**: `atproto` Python package (PyPI, updated Dec 2025)
- **Implementation**: Post title + short excerpt + canonical URL as external link card. Thread mode optional.
- **Effort**: Low — simplest auth of all platforms, well-documented SDK.

#### Mastodon — RECOMMENDED SECOND
- **API**: Official REST, well-documented
- **Auth**: OAuth 2.0 per-instance, `write:statuses` scope. Instance URL is user-configurable.
- **Publish**: `POST /api/v1/statuses`
- **Limit**: 500 chars default (instance-configurable). Plain text only (no markdown rendering).
- **Rate limit**: 30 POSTs per 30 minutes
- **Implementation**: Post title + excerpt + canonical URL. Very similar to Twitter/X publisher.
- **Effort**: Low-medium — similar to Twitter but instance URL must be configurable.

#### LinkedIn — RECOMMENDED THIRD
- **API**: Official self-service ("Share on LinkedIn" product)
- **Auth**: OAuth 2.0, `w_member_social` scope, 60-day access tokens (no refresh tokens!)
- **Publish**: ugcPosts API — text + article URL card (title + description + thumbnail). NOT full article body.
- **Rate limit**: 150 requests/day per member
- **Key limitation**: Token expires every 60 days — requires manual re-auth. The newer Posts API (richer content) requires LinkedIn Partner Program approval.
- **Implementation**: Post article excerpt + canonical URL as article card. Human-in-loop for token refresh.
- **Effort**: Medium — OAuth flow complexity, token expiry management.

### Skip (no viable API)

| Platform | Reason |
|----------|--------|
| Medium | API deprecated Jan 2025. Manual import only (medium.com/p/import with canonical URL). |
| Reddit | API requires pre-approval since Nov 2025 (Responsible Builder Policy). Write access scrutinized. Add as conditional feature if user has pre-existing PRAW credentials. |
| DZone | No API. Manual submission + 7-12 day editorial review. MVB program is editorial RSS, not programmable. |
| Substack | No official publishing API. Unofficial session-cookie tools support Notes only (not full posts). |
| Product Hunt | GraphQL API v2 has no public mutation for launches. Wrong use case (product launches ≠ article publishing). |
| Hacker Noon | No API. Manual submission + editorial review. |

## 2. Content Adaptation Strategies

### Per-Platform Format Rules

#### Twitter/X Threads (existing — needs improvement)
- **Optimal length**: 8-15 tweets (current 6-8 is below optimal)
- **Hook formulas**: bold contrarian claim, specific promise with outcome, story teaser, surprising statistic, question-based gap
- **Structure**: numbered tweets (1/, 2/), one idea per tweet, CTA + link as final tweet
- **2026 change**: X algorithm now actively boosts external article links (dev.to, Substack, personal blogs)
- **Action**: Upgrade thread generator from 6-8 to 8-12 tweets, add dedicated hook formula selection

#### LinkedIn Posts (NEW)
- **Format**: 150-300 words, 3,000 char limit
- **Critical rule**: Link in first comment, NOT in post body (algorithm penalty for external links in body)
- **Structure**: Hook line → 3-4 bullet insights → CTA ("Full article in the comments")
- **Hashtags**: 3-5 at end
- **Carousel option**: 6-9 slides, captions <100 chars each (Hook → Problem → Solution → How-to → Result → CTA)

#### Reddit Posts (NEW — template only, no API)
- **Format varies by subreddit**: r/programming wants discussion, r/webdev wants tutorials, r/SideProject accepts "I built X"
- **Key rule**: 90/10 ratio (90% genuine participation, 10% promotional)
- **Link placement**: URL in first comment, not in post body (many subreddits)
- **What works**: "war story" / "lessons learned" format, not product announcements
- **Never**: marketing language, identical posts across subreddits

#### Bluesky Threads (NEW)
- **Limit**: 300 chars/post. URLs = 22 chars always.
- **Culture**: Anti-corporate, privacy-oriented. Marketing language is unwelcome.
- **Structure**: 5-10 posts, numbered (1/7, 2/7), article link in final post. No aggressive CTA.
- **Tone**: Genuine technical sharing, builder-to-builder.

#### Mastodon Posts (NEW)
- **Limit**: 500 chars default (some instances allow more)
- **Culture**: Privacy-conscious, anti-corporate. Instance-specific communities (fosstodon.org = open source, hachyderm.io = tech professionals)
- **Content warnings (CW)**: Cultural norm for sensitive topics, not needed for technical content
- **No markdown rendering**: Plain text only

#### Newsletter / Email (existing email-drip skill — needs article-to-newsletter variant)
- **Length**: Under 500 words for repurposed article summary
- **Tone shift**: First-person, personal ("I found that..." not "This article covers...")
- **Remove**: SEO scaffolding, keyword headers, "In this article" intros
- **Format**: Plain text (white background, black text) outperforms designed templates for developers
- **Structure**: Personal hook (2-3 sentences) → 3-5 bullet insights → one actionable takeaway → link to full article
- **One CTA only**

#### Product Hunt (existing launch-post skill — needs PH template)
- **Tagline**: ~60 chars, action-oriented, self-explanatory. Formula: `[Product] – [Verb] [Outcome] for [Audience]`
- **Maker comment**: ≤800 chars. Structure: what changed → why it matters → where to start → CTA
- **No superlatives**, no hype language

#### Show HN (existing — adequate)
- **Critical constraint**: Show HN is for things people can run/try. Blog posts and sign-up pages are off-topic.
- **Body structure**: Who you are → what it does → problem → backstory → technical approach → differentiation → feedback ask

### Automation Boundary

| Automatable | Requires human editing |
|---|---|
| Extracting key claims from article | Selecting which hook formula to use |
| Applying character limits, splitting into posts | Choosing which 3-5 ideas to include |
| Generating hashtag candidates from tags | Calibrating tone per platform |
| Building newsletter skeleton | Reddit subreddit selection |
| Producing carousel slide text | Personal hook sentence for newsletter |
| Generating PH tagline candidates | PH maker comment first line |

## 3. Launch & Promotion Workflows

### Multi-Platform Launch Sequence

| Timeline | Platform | Action |
|----------|----------|--------|
| Day -14 to -1 | All | Build-in-public content, waitlist building (target 300+ signups) |
| Day -7 | DevHunt (optional) | Test run to refine messaging |
| Day 0 | Product Hunt | Main launch (12:01 AM PST, Tue-Thu) |
| Day 0, 00:05 | PH | Pin maker comment |
| Day 0, 00:15 | Twitter/X | Thread tagging @ProductHunt + micro-influencers |
| Day 0, 01:00 | Email | Notify waitlist with single CTA |
| Day 0, 06:00 | LinkedIn | Request feedback post |
| Day 1-3 | Hacker News | Show HN while PH momentum is fresh |
| Day 3-7 | Reddit | r/SideProject, r/IMadeThis posts |
| Week 2 | IndieHackers | Journey post with PH/HN results as hook |
| Week 2-4 | dev.to / Hashnode | "I built X" launch article |
| Ongoing | GitHub | Awesome list PRs, release announcements |

### Platform-Specific Launch Rules

**Product Hunt**:
- Post Tue-Thu at 12:01 AM PST (leaderboard reset)
- Respond to ALL comments within 5 minutes in first 4 hours
- Post-launch days 1-2: export commenter emails, add to drip with 20% offer

**Hacker News**:
- Post Tue-Thu, 8-10 AM PT
- First substantive comment within 5 minutes of submission
- Handle criticism by agreeing with something valid first
- Expected results for top launch: 400+ upvotes → 2,000+ signups in 48 hours

**Reddit**:
- Need 2-4 weeks account activity + 100-200 karma before promoting
- Permissive subreddits: r/SideProject, r/IMadeThis, r/AlphaAndBetaUsers
- Cautious: r/SaaS, r/Entrepreneur
- Avoid: r/programming, r/technology (direct promo)

**IndieHackers**:
- Journey posts with specific revenue numbers ($413/month, $0→$10K MRR)
- Posts 750-1,500 words outperform shorter ones
- Conversion rate 12-24% (vs PH's 1-3%) — but requires 90+ days community presence
- Headline formula: `[Specific number] + [Transformation] + [Timeframe]`

**GitHub**:
- Social preview image (1280x640px)
- Up to 20 repo tags
- Submit to awesome-* lists (each = permanent Google discovery path)
- GitHub Releases with full changelogs

### Three-Tier Platform Framework

| Tier | Purpose | Platforms | Lifespan |
|------|---------|-----------|----------|
| Spike generators | Initial traffic burst | Product Hunt, HN, BetaList | 24-72 hours |
| Community builders | Sustained engagement | IndieHackers, Reddit, Twitter #buildinpublic | Weeks |
| Long-tail engines | Compounding discovery | Directories, awesome lists, dev.to articles | Years |

## 4. Analytics & Tracking

### Platform Analytics APIs

| Platform | Endpoint | Auth | Metrics | Update frequency |
|----------|----------|------|---------|-----------------|
| dev.to | `GET /api/articles/me` | api-key header | page_views_count, public_reactions_count, comments_count | Once/day |
| dev.to | `GET /api/analytics/historical?start=&article_id=` | api-key header | Time-series breakdown | Once/day, rate-limited (200ms delay needed) |
| Hashnode | GraphQL `gql.hashnode.com` | Optional PAT | views, reactionCount, replyCount, responseCount | Near real-time |
| Twitter/X | `GET /2/tweets/:id?tweet.fields=public_metrics` | Bearer token | impressions, likes, replies, retweets, quotes | Real-time |
| Twitter/X | Non-public metrics (url_link_clicks) | OAuth user context | Click-throughs | Only <30 days old posts |
| HN | `hacker-news.firebaseio.com/v0/item/<id>.json` | None | score, descendants (comments) | Real-time |
| HN | Algolia `hn.algolia.com/api` | None | Full story search by title | Real-time |

### UTM Strategy

| Parameter | Value |
|-----------|-------|
| `utm_source` | `devto`, `hashnode`, `twitter`, `hackernews`, `bluesky`, `mastodon`, `linkedin` |
| `utm_medium` | `syndication` |
| `utm_campaign` | article slug |

**Where to apply UTMs**: On CTA links in Twitter threads (final tweet), LinkedIn first-comment link, Bluesky/Mastodon link posts. NOT on canonical_url (pollutes canonical attribution).

### Implementation: `stats_article` Command

The plugin already stores platform IDs in frontmatter (devto_id, hashnode_id, twitter_thread_id). A new `tools/stats_article.py` would:

1. Parse article frontmatter (reuse existing `parse_article`)
2. Fire HTTP requests to each platform API using stored IDs
3. For HN: search Algolia by title if no `hn_story_id` stored
4. Print unified table to stdout

```
Platform   | Views  | Reactions | Comments | URL
-----------|--------|-----------|----------|----
dev.to     | 1,234  | 42        | 7        | https://dev.to/...
Hashnode   | 876    | 23        | 3        | https://hashnode.dev/...
Twitter/X  | 5,400  | 89        | 12       | https://x.com/...
HN         | —      | 156 pts   | 34       | https://news.ycombinator.com/...
```

### Missing State: `hn_story_id`

Current `publish_hn.py` generates a submit URL but does not write back an ID (since HN has no API for submission). Add `hn_story_id` to `ArticleData` — user can manually add it after posting, or the stats command can discover it via Algolia title search.

## 5. Competitive Landscape

### Existing Tools

| Tool | Platforms | Tech | Strengths | Weaknesses |
|------|-----------|------|-----------|------------|
| **cross-post CLI** (npm) | dev.to, Hashnode, Medium | JavaScript | URL scraping + local markdown | No update/idempotent, Medium API dead, manual token config |
| **blogpub** (GitHub Action) | Medium, dev.to | TypeScript | CI/CD integration, Handlebars per-platform templates | Only 2 platforms, no social |
| **Sovereign Publisher** | Jekyll, X, LinkedIn | GitHub Actions | Local-first, 3-day cool-off queue, automated cron | Tied to Jekyll, no dev.to/Hashnode |
| **content-ops** (ours) | dev.to, Hashnode, Twitter/X, HN | Python | LLM-powered adaptation, skills system, dry-run, idempotent re-publish | No LinkedIn/Bluesky/Mastodon, no analytics, limited launch templates |

### Our Differentiators
1. **LLM-native content adaptation** — not just cross-posting markdown but generating platform-specific variants (threads, LinkedIn posts, HN titles)
2. **Skills system** — extensible via markdown skill files, no code changes needed for new templates
3. **Dry-run first** — all commands default to preview mode
4. **Idempotent re-publish** — stored IDs enable update-in-place
5. **Part of a plugin ecosystem** — integrates with other skill7 plugins

## 6. Recommendations — Roadmap

### Phase 1: New Platforms (commands + tools)
1. **`/publish-bluesky`** — post link card + excerpt. App password auth. Lowest effort.
2. **`/publish-mastodon`** — post link card + excerpt. OAuth per-instance. Similar to Twitter publisher.
3. **`/publish-linkedin`** — post article card + excerpt. OAuth 2.0, 60-day token management.

### Phase 2: Content Adaptation (skills)
4. **Upgrade `social-thread` skill** — add Bluesky (300 char), Mastodon (500 char), LinkedIn post variants. Improve Twitter thread to 8-12 tweets with hook formula selection.
5. **Add `newsletter-variant` skill** — convert article to newsletter format (personal hook, 500 words, plain text, single CTA).
6. **Enhance `launch-post` skill** — add Product Hunt (tagline + maker comment template), Reddit (per-subreddit templates), IndieHackers (journey post template), GitHub (release notes + awesome-list PR template).

### Phase 3: Launch Orchestration (skill)
7. **Add `launch-sequence` skill** — orchestrate multi-platform launch with timeline, platform-specific content generation, and checklist. Based on the three-tier framework (spike → community → long-tail).

### Phase 4: Analytics (command + tool)
8. **`/content-stats`** — aggregate stats from all platforms using stored IDs. Add `hn_story_id` to ArticleData. UTM parameter injection in CTA links.
9. **Add `--since` flag** — show deltas from last check (sidecar JSON file).

### Phase 5: Conditional Platforms
10. **Reddit** — add as conditional feature behind config flag if user has approved PRAW credentials.

---

## Sources

### Platform APIs & Documentation
- [LinkedIn Share on LinkedIn (self-service)](https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/share-on-linkedin)
- [LinkedIn Posts API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api)
- [Bluesky AT Protocol — Creating Posts](https://docs.bsky.app/blog/create-post)
- [Bluesky Rate Limits](https://docs.bsky.app/docs/advanced-guides/rate-limits)
- [Mastodon Statuses API](https://docs.joinmastodon.org/methods/statuses/)
- [Mastodon Rate Limits](https://docs.joinmastodon.org/api/rate-limits/)
- [Medium API (archived)](https://github.com/Medium/medium-api-docs)
- [Reddit Responsible Builder Policy](https://support.reddithelp.com/hc/en-us/articles/42728983564564-Responsible-Builder-Policy)
- [Substack Developer API](https://support.substack.com/hc/en-us/articles/45099095296916-Substack-Developer-API)
- [HN Firebase API](https://github.com/HackerNews/API)
- [X API Metrics](https://docs.x.com/x-api/fundamentals/metrics)

### Cross-Posting Tools
- [cross-post CLI (GitHub)](https://github.com/shahednasser/cross-post)
- [blogpub GitHub Action](https://dev.to/protium/publish-your-blog-articles-everywhere-with-this-github-action-3g6k)
- [Sovereign Publisher](https://www.adambourg.com/automation/software3.0/githubactions/sovereignty/2026/03/02/sovereign-publisher.html)
- [Blog Syndication Guide](https://dev.to/navinvarma/blog-syndication-cross-publishing-blog-posts-to-devto-hashnode-and-medium-1a5d)

### Content Strategy
- [Developer Content Syndication (draft.dev)](https://draft.dev/learn/syndicating-developer-content)
- [Twitter Thread Writing Masterclass](https://www.tweetarchivist.com/twitter-thread-writing-masterclass-2025)
- [LinkedIn Algorithm 2025 Content Format Guide](https://contentin.io/blog/linkedin-algorithm-2025-the-complete-content-format-strategy-guide/)
- [Reddit Self-Promotion Guide](https://vadimkravcenko.com/qa/self-promotion-on-reddit-the-right-way/)
- [Bluesky Character Limits](https://typecount.com/blog/bluesky-character-limit)

### Launch Workflows
- [Product Hunt Launch Guide 2026 (Calmops)](https://calmops.com/indie-hackers/product-hunt-launch-guide/)
- [How to Get Featured on Product Hunt 2025](https://www.flowjam.com/blog/how-to-get-featured-on-product-hunt-2025-guide)
- [HN Launch — 500 Upvotes Guide](https://calmops.com/indie-hackers/hacker-news-launch-500-upvotes/)
- [Dev Tool HN Launch (Markepear)](https://www.markepear.dev/blog/dev-tool-hacker-news-launch)
- [Reddit Promotion Without Ban Guide](https://www.wappkit.com/blog/reddit-promotion-without-ban-guide-2025)
- [IndieHackers Launch Strategy](https://awesome-directories.com/blog/indie-hackers-launch-strategy-guide-2025/)
- [Open Source Promotion (6K Stars in 6 Months)](https://dev.to/wasp/how-i-promoted-my-open-source-repo-to-6k-stars-in-6-months-3li9)

### Analytics
- [Dev.to API Statistics](https://blog.3d-logic.com/2024/02/25/better-dev-stats-with-dev-to-api/)
- [Hashnode GraphQL API Docs](https://apidocs.hashnode.com/)
- [UTM Tracking Guide](https://agencyanalytics.com/blog/utm-tracking)
- [Canonical URL Strategy for Syndication](https://www.seorce.com/posts/advanced-canonical-strategy-for-content-syndication)
