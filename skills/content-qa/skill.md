---
name: content-qa
description: 'Use before publishing any article. Triggers: "check article", "preflight", "validate post", "is this ready to publish", "QA my post", "pre-publish check". Run this before distribute or any publish command.'
---

Run pre-publish validation on the article. Check all platforms' requirements before sending.

## Checks

Read the article at the path the user provides. Run through `references/platform-limits.md`.

### Frontmatter completeness
- [ ] `title` — present and non-empty
- [ ] `description` — present, under 160 chars
- [ ] `date` — present, valid YYYY-MM-DD format
- [ ] `tags` — present, list format
- [ ] `lang` — present (en, ru, etc.)
- [ ] `canonical_url` — present (or can be derived from slug)

### Title length
- General: 50-60 chars optimal
- Dev.to: max 128 chars
- Hashnode: max 100 chars

### Description length
- Dev.to: max 160 chars
- Hashnode: max 250 chars

### Tags
- Dev.to: max 4 tags, lowercase, hyphens only
- Hashnode: max 5 tags

### Body
- [ ] Has at least one heading
- [ ] Has at least one paragraph (not just code)
- [ ] Has a CTA (link to repo, newsletter, or next post) in last 3 paragraphs
- [ ] No broken relative image links (images should use absolute URLs for cross-posting)

### Output format

```
## Content QA Report: <title>

### Frontmatter
OK title: "..."
OK description: "..." (143 chars)
WARNING tags: 6 tags — dev.to will truncate to 4

### Body
OK Has headings
OK Has CTA in last paragraph
WARNING Line 47: relative image path ./images/foo.png — convert to absolute URL

### Verdict
2 warnings — fix before publishing to dev.to
```

Fix any failures before publish. Warnings are platform-specific.
