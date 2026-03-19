---
name: newsletter-variant
description: 'Use when the user wants to convert a blog article into a newsletter email. Triggers: "newsletter from article", "email version", "convert to newsletter", "article to email", "newsletter variant".'
---

Read `.agents/content-context.md` first (if it exists).

## Purpose

Convert a finished blog article into a newsletter email. One article — one focused email under 500 words, stripped of SEO scaffolding, written in first person.

## Format rules

- Plain text only — no HTML templates, no designed layouts. White background, black text outperforms designed templates for developer audiences.
- Under 500 words total.
- First-person voice throughout ("I found that..." not "This article covers...").
- No keyword headers, no "In this article we'll cover", no SEO intros.
- One CTA only — a single link to the full article at the end.

## Structure

1. **Personal hook** (2-3 sentences) — what prompted you to write this, a surprising result, or a concrete observation. Not a summary of what the article contains.
2. **Core insight** — either 3-5 tight bullets or 2 short paragraphs. Each bullet/paragraph carries standalone value; not a table of contents.
3. **One actionable takeaway** — a single thing the reader can do or think about differently right now.
4. **Link** — "Full article: [title] → [URL]" (or placeholder if URL unknown).

## Subject line

- 40-50 characters.
- Specific benefit or concrete outcome — not a topic label.
- Examples of the pattern: "How I cut deploy time by 40%" not "Deploy optimization tips".

## What to strip from the article

- Keyword-stuffed headers ("Best practices for X in Y")
- Meta-commentary ("In this post I'll walk you through...")
- Lengthy background sections written for search ranking
- Repeated CTAs, sidebar promos, related-posts links

## Process

1. Ask for the article (file path, URL, or paste).
2. Read the article.
3. Draft subject line — show it first, ask for approval or alternative.
4. Draft email body following the four-section structure above.
5. Count words. If over 500: trim core insight section first.
6. Show full draft. Ask for edits.
7. Output final as `newsletter-[slug].md` in the article's directory (or current directory if no article path).

## Scope

Text output only. No sending, no provider API. For sending: Mailchimp, ConvertKit, Resend, or Beehiiv require separate setup outside content-ops.
