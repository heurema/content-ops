---
name: post-from-artifact
description: 'Use when the user wants to turn a technical artifact into a blog post. Triggers: "README to post", "release notes to blog", "docs to article", "turn changelog into post", "write post from my PR description", "blog post from commit messages".'
---

Read `.agents/content-context.md` first (if it exists) for audience and style.

## Purpose

Convert a developer artifact (README, CHANGELOG, PR description, commit messages, docs) into a publishable blog post. This is the core content-ops workflow — ship in public by writing about what you already built.

## Process

1. Ask: What artifact are we working from? (file path or paste)
2. Ask: What angle? Options:
   - "What I built" — explain the feature/project
   - "What I learned" — lessons and trade-offs
   - "How to use it" — tutorial/walkthrough
   - "Why I built it" — motivation and problem statement
3. Read the artifact.
4. Generate a blog post draft:
   - Title: specific and searchable (not "My new project")
   - Opening: problem + what you built (no fluff)
   - Body: code-first, real examples from the artifact
   - Closing: link to repo/docs + what's next
5. Add YAML frontmatter:
   ```yaml
   ---
   title: "..."
   description: "..."  # 1 sentence, under 160 chars
   date: YYYY-MM-DD
   tags: [...]
   lang: en
   ---
   ```
6. Ask: Save to `content/posts/slug.md`? Confirm path.

## Voice

Developer-to-developer. First person. Show don't tell — code snippets over abstract descriptions. Assume smart reader who skims.
