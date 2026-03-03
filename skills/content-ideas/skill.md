---
name: content-ideas
description: 'Use when the user wants content ideas or a backlog. Triggers: "content ideas", "what to write next", "build backlog", "ideas from changelog", "what should I post about", "content calendar".'
---

Read `.agents/content-context.md` first (if it exists).

## Purpose

Generate a content backlog from existing artifacts. Every project has latent content — shipped features, solved problems, interesting trade-offs. Surface them.

## Process

1. Ask what artifacts to mine (can select multiple):
   - CHANGELOG / git log
   - README sections
   - Open/closed GitHub issues
   - Commit messages from last 30 days
   - Past posts (to find gaps)

2. For each artifact, extract content hooks:
   - New feature shipped → "What I built" post
   - Bug fixed → "Debugging X" post
   - Refactor done → "How we simplified X" post
   - Decision made → "Why we chose X over Y" post
   - Perf improvement → numbers + approach post

3. Output as a prioritized backlog table:

| Title idea | Type | Source artifact | Estimated effort |
|------------|------|-----------------|------------------|
| ... | Tutorial | CHANGELOG v0.4 | Medium |
| ... | Decision post | GitHub issue #23 | Low |

4. Ask: Add any of these to a `content-backlog.md` file?

## Ranking heuristic

Prioritize: (1) things users asked about in issues, (2) non-obvious technical decisions, (3) results with concrete numbers.
Deprioritize: announcements without substance, ideas with no concrete code to show.
