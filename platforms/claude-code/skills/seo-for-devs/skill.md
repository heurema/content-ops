---
name: seo-for-devs
description: 'Use when the user wants SEO help for a technical article. Triggers: "SEO audit", "keyword for article", "optimize for search", "is this SEO-ready", "meta description", "should I add keywords".'
---

Read `.agents/content-context.md` first (if it exists).

## Purpose

Lightweight SEO checklist for developers who don't think of themselves as marketers. Not keyword stuffing — just making good technical content findable.

## Checklist

Run through `references/checklist.md`. For each item, check the article and report: OK / Fix / Missing.

### Quick wins (do these first)

1. **Title** — includes the specific technology/problem (not just "Building stuff")
2. **Description** — under 160 chars, answers "what will I learn?"
3. **H1** matches or is close to title
4. **Code examples** — search engines reward real code; check there's at least one
5. **Canonical URL** — set in frontmatter

### Search intent

Ask: what would someone type to find this article? Verify that phrase appears naturally in title + first paragraph.

### Output

Produce a short report:
- Items that pass (list)
- Items to fix (with suggested edits)
- Keyword recommendation: one primary term the article should rank for

Do NOT recommend keyword density targets or schema markup — that's over-engineering for a dev blog.
