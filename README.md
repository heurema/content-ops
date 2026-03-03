# content-ops

Content operations for indie developers who ship in public.

Create, QA, and distribute technical articles to dev.to, Hashnode, Twitter/X, and Hacker News — without leaving your editor.

## What it does

- **Create** blog posts from README, changelog, PR descriptions, commit messages
- **Generate** content ideas from your existing artifacts
- **QA** articles before publishing (frontmatter, tag limits, broken links)
- **Distribute** to dev.to, Hashnode, Twitter/X thread, and HN

## Install

```bash
claude plugin marketplace add heurema/emporium
claude plugin install content-ops@emporium
pip install -r $(claude plugin root content-ops)/requirements.txt
```

See [docs/setup.md](docs/setup.md) for credential setup.

## Skills

| Skill | Trigger |
|-------|---------|
| `content-context` | "set up content context", "my blog is about" |
| `post-from-artifact` | "README to post", "release notes to blog" |
| `content-ideas` | "content ideas", "what to write next" |
| `seo-for-devs` | "SEO audit", "optimize for search" |
| `content-qa` | "check article", "preflight", "is this ready to publish" |
| `social-thread` | "Twitter thread", "social variants" |
| `launch-post` | "HN Show post", "announce on HN" |
| `distribute` | "publish article", "distribute to platforms" |

## Commands

| Command | Description |
|---------|-------------|
| `/publish-devto` | Publish to dev.to (dry-run default) |
| `/publish-hashnode` | Publish to Hashnode (dry-run default) |
| `/publish-twitter` | Post as Twitter/X thread (dry-run default) |
| `/publish-hn` | Generate HN submitlink (human-in-loop) |
| `/content-ops-doctor` | Validate all platform credentials |

## License

MIT
