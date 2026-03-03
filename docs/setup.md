# content-ops Setup Guide

## Prerequisites

- Python 3.10+
- `pip install -r requirements.txt` (in plugin root)

## Platform Credentials

Store credentials in a `.env` file in your project root (never commit this file):

```bash
# .env — add to .gitignore
DEVTO_API_KEY=your-dev-to-api-key
HASHNODE_TOKEN=your-hashnode-personal-access-token
HASHNODE_PUBLICATION_ID=your-publication-id
X_API_KEY=your-x-api-key
X_API_KEY_SECRET=your-x-api-key-secret
X_ACCESS_TOKEN=your-x-access-token
X_ACCESS_TOKEN_SECRET=your-x-access-token-secret
```

Load with: `source .env` or use a tool like `direnv`.

## Getting Credentials

### dev.to
1. Go to `dev.to/settings/extensions`
2. "DEV Community API Keys" → Generate API key
3. Copy to `DEVTO_API_KEY`

### Hashnode
1. Go to `hashnode.com/settings/developer`
2. Generate personal access token
3. Go to your publication → Settings → find Publication ID
4. Copy both to `HASHNODE_TOKEN` and `HASHNODE_PUBLICATION_ID`

### Twitter/X
1. Go to `developer.x.com` → create a project + app
2. In App settings → enable OAuth 1.0a
3. Keys and Tokens tab → generate Access Token + Secret
4. Copy all 4 values to `X_API_KEY`, `X_API_KEY_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET`

**Platform risk:** X free tier (500 posts/month) is subject to change. All Twitter commands default to `--dry-run`. Pass `--confirm` to actually post.

### Hacker News
No credentials required. HN submissions are always human-in-loop (browser).

## Verify Setup

Run content-ops-doctor: `/content-ops-doctor`

## Reddit (v2 — not in MVP)

Reddit ended self-service API access in November 2025. New apps require manual approval through Reddit's Responsible Builder Policy (rare for personal scripts). Reddit publishing is deferred to v2 when/if API access situation changes.
