# content-ops

Content operations for indie developers who ship in public.

Create, QA, and distribute technical articles to dev.to, Hashnode, Twitter/X, and Hacker News — without leaving your editor.

## Install

<!-- INSTALL:START -->
```bash
claude plugin marketplace add heurema/emporium
claude plugin install content-ops@emporium
```
<!-- INSTALL:END -->

Install Python dependencies (PyYAML, requests, tweepy):

```bash
pip install -r $(claude plugin root content-ops)/requirements.txt
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
EOF
chmod 600 ~/.config/content-ops/.env
```

Explicit env vars always take precedence over the file. A local `./.env` in the current directory overrides the global file.

See [docs/setup.md](docs/setup.md) for step-by-step credential instructions per platform.

## Quick start

```bash
# 1. Check credentials
/content-ops-doctor

# 2. Lint your article (catches em-dashes, missing frontmatter, tag issues)
/lint-article article.md

# 3. Auto-fix detected dashes
/lint-article --fix article.md

# 4. Dry-run preview (default, no API call)
/publish-devto article.md

# 5. Publish for real
/publish-devto --confirm article.md
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

## Commands

| Command | Description |
|---------|-------------|
| `/lint-article` | Lint article — em-dash check, description length, missing frontmatter, tag format. Exits non-zero on errors. Use `--fix` to auto-replace dashes. |
| `/publish-devto` | Publish to dev.to. Defaults to dry-run — pass `--confirm` to post. Re-runs update existing posts (via `devto_id` in frontmatter). |
| `/publish-hashnode` | Publish to Hashnode via GraphQL. Dry-run by default. Re-runs update existing posts (via `hashnode_id`). |
| `/publish-twitter` | Post as Twitter/X thread. Dry-run by default. |
| `/publish-hn` | Generate Hacker News submitlink. No auth — always human-in-loop. |
| `/content-ops-doctor` | Validate all configured platform credentials. |

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
| `devto_url` | auto | written back after first publish to dev.to |
| `hashnode_id` | auto | written back after first publish to Hashnode |
| `hashnode_url` | auto | written back after first publish to Hashnode |
| `twitter_thread_id` | auto | first tweet ID, written back after posting |

## Platform notes

**dev.to** — Tags must be alphanumeric only (no hyphens, no spaces). Max 4 tags.

**Hashnode** — Uses GraphQL API. Always returns HTTP 200; auth errors appear in the response body. Max 5 tags. Re-runs update the existing post.

**Twitter/X** — Requires OAuth 1.0a app credentials. X free tier allows 500 posts/month. Thread length limited by article structure (max ~7 tweets). URLs are always counted as 23 chars by Twitter regardless of length.

**Hacker News** — No API. The plugin generates a submit URL. Paste it in your browser, add "Show HN:" prefix for tools/projects.

## License

MIT
