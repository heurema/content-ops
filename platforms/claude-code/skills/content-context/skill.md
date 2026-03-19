---
name: content-context
description: Use when the user wants to set up or update their content profile. Also use when the user says "my blog is about", "content profile", "set up content context", or "who am I writing for". Stores context as .agents/content-context.md — read by all other content-ops skills first.
---

Help the user establish their content context. This file is read by all other content-ops skills to personalize output.

## What to capture

Ask the user (one question at a time):
1. What is your blog/site about? (1-2 sentences)
2. Who is your primary reader? (e.g., "senior backend engineers building APIs")
3. What's your writing style? (technical/conversational/terse)
4. What's your main distribution channel? (blog + dev.to + Hashnode / blog only / etc.)
5. Do you have a canonical URL pattern? (e.g., `https://example.com/posts/{slug}`)

## Output

Write the context to `.agents/content-context.md` in this format:

```markdown
# Content Context

## About
[User's blog/site description]

## Audience
[Primary reader description]

## Style
[Writing style]

## Distribution
[Channels: blog, dev.to, Hashnode, Twitter/X, HN]

## Canonical URL Pattern
https://example.com/posts/{slug}

## Tags
[Recurring tags/topics the user covers]
```

After writing: confirm the path and tell the user all other content-ops skills will now read this context automatically.
