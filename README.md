# content-ops

Content operations for indie developers who ship in public.

Create, QA, and distribute technical articles to dev.to, Hashnode, Twitter/X, Bluesky, Mastodon, LinkedIn, and Hacker News — without leaving your editor.

## Install

<!-- INSTALL:START -->
```bash
claude plugin marketplace add heurema/emporium
claude plugin install content-ops@emporium
```
<!-- INSTALL:END -->

Install Python dependencies (PyYAML, requests, tweepy, atproto):

```bash
pip install -r $(claude plugin root content-ops)/requirements.txt
```

Optional (for full QA pipeline):

```bash
brew install vale
npm install -g markdownlint-cli2
```

## Credentials

All tools auto-load `~/.config/content-ops/.env` on startup. Create it once:

```bash
mkdir -p ~/.config/content-ops
cat > ~/.config/content-ops/.env <<'EOF'
DEVTO_API_KEY=your-dev-to-api-key
HASHNODE_TOKEN=your-hashnode-personal-access-token
HASHNODE_PUBLICATION_ID=your-publication-id
# X_API_KEY=
# X_API_KEY_SECRET=
# X_ACCESS_TOKEN=
# X_ACCESS_TOKEN_SECRET=
# BLUESKY_HANDLE=
# BLUESKY_APP_PASSWORD=
# MASTODON_ACCESS_TOKEN=
# MASTODON_INSTANCE_URL=
# LINKEDIN_ACCESS_TOKEN=
# LINKEDIN_PERSON_URN=
EOF
chmod 600 ~/.config/content-ops/.env
```

See [docs/setup.md](docs/setup.md) for step-by-step credential instructions per platform.

## Quick start

```bash
# 1. Check credentials
/content-ops-doctor

# 2. Run 4-layer content QA (structural + editorial + platform-fit + style drift)
/qa article.md

# 3. Lint article (em-dashes, missing frontmatter, tag issues)
/lint-article article.md

# 4. Dry-run preview (default, no API call)
/publish-devto article.md

# 5. Publish for real
/publish-devto --confirm article.md

# 6. Publish to all platforms at once
/distribute article.md
```

Your article needs YAML frontmatter:

```yaml
---
title: "Your Post Title"
description: "One-line summary (max 160 chars)"
date: 2026-01-15
tags: [python, ai, devtools]   # no hyphens — dev.to rejects them
lang: en
canonical_url: https://yourblog.com/your-post  # optional: marks original source
---
```

## Content QA pipeline

The `/qa` command runs a 4-layer pre-publish validation pipeline:

| Layer | What it checks | Tool |
|-------|---------------|------|
| Structural | Required frontmatter, markdown formatting | markdownlint |
| Editorial | Prose quality, AI-pattern detection (8 custom rules) | Vale |
| Platform fit | Title/description/tag limits per platform | Built-in |
| Style drift | Vocabulary diversity, sentence variance, voice consistency | Built-in |

Returns a composite score (0-100) with pass/review/block decision. The `/distribute` command runs QA automatically before publishing (use `--skip-qa` to bypass).

## Skills

| Skill | When Claude uses it |
|-------|---------------------|
| `content-context` | "set up content context", "my blog is about", "who am I writing for" |
| `post-from-artifact` | "README to post", "release notes to blog", "blog post from PR" |
| `content-ideas` | "content ideas", "what to write next", "build backlog" |
| `seo-for-devs` | "SEO audit", "optimize for search", "meta description" |
| `content-qa` | "check article", "preflight", "is this ready to publish" |
| `social-thread` | "Twitter thread", "tweetstorm", "social variants" |
| `launch-post` | "HN Show post", "announce on HN", "product launch post" |
| `distribute` | "publish article", "distribute to platforms", "cross-post" |
| `copy-review` | "review this copy", "improve headline", "landing page copy" |
| `email-drip` | "welcome sequence", "email drip", "newsletter onboarding" |
| `launch-sequence` | "pre-launch campaign", "launch sequence" |
| `newsletter-variant` | "newsletter from article", "email version" |

## Commands

| Command | Description |
|---------|-------------|
| `/qa` | 4-layer content QA: structural + editorial + platform-fit + style drift. Composite score with pass/review/block. |
| `/lint-article` | Deterministic lint — em-dashes, description length, frontmatter, tags. Use `--fix` to auto-replace. |
| `/publish-devto` | Publish to dev.to. Dry-run by default — `--confirm` to post. |
| `/publish-hashnode` | Publish to Hashnode via GraphQL. Dry-run by default. |
| `/publish-twitter` | Post as Twitter/X thread. Dry-run by default. |
| `/publish-bluesky` | Post to Bluesky via AT Protocol. Dry-run by default. |
| `/publish-mastodon` | Post to Mastodon instance. Dry-run by default. |
| `/publish-linkedin` | Post to LinkedIn via ugcPosts API. Dry-run by default. |
| `/publish-hn` | Generate Hacker News submitlink. Always human-in-loop. |
| `/content-ops-doctor` | Validate all configured platform credentials. |
| `/content-stats` | Show engagement stats across platforms. |

## Frontmatter fields

| Field | Required | Notes |
|-------|----------|-------|
| `title` | yes | |
| `description` | yes | max 160 chars |
| `date` | recommended | YYYY-MM-DD |
| `tags` | yes | array; no hyphens or spaces for dev.to |
| `lang` | no | default `en` |
| `canonical_url` | no | marks original source across platforms |
| `devto_id` | auto | written back after first publish to dev.to |
| `hashnode_id` | auto | written back after first publish to Hashnode |
| `twitter_thread_id` | auto | first tweet ID, written back after posting |
| `bluesky_post_id` | auto | written back after first publish to Bluesky |
| `mastodon_post_id` | auto | written back after first publish to Mastodon |
| `linkedin_post_id` | auto | written back after first publish to LinkedIn |

## Platform notes

**dev.to** — Tags must be alphanumeric only (no hyphens, no spaces). Max 4 tags.

**Hashnode** — Uses GraphQL API. Max 5 tags. Re-runs update the existing post.

**Twitter/X** — OAuth 1.0a. Free tier: 500 posts/month. URLs count as 23 chars.

**Bluesky** — AT Protocol with JWT auth. 300 grapheme limit per post.

**Mastodon** — Per-instance REST API. 500 char default limit.

**LinkedIn** — OAuth 2.0 (60-day tokens). ugcPosts format.

**Hacker News** — No API. Generates a submit URL for manual paste.

## License

MIT

