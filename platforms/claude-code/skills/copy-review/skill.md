---
name: copy-review
description: 'Use when the user wants feedback on marketing copy, headlines, or landing page text. Triggers: "edit landing page", "improve headline", "copy feedback", "review this copy", "is this headline good", "landing page copy review".'
---

Read `.agents/content-context.md` first (if it exists).

## Purpose

Review and improve marketing copy: headlines, landing page text, CTAs, email subjects. Not content-ops core — this is bonus.

## Framework

### Headline

Check:
1. **Specificity** — does it say what the user gets? ("Ship blog posts without leaving your editor" > "Content made easy")
2. **Clarity** — can you understand it in 3 seconds?
3. **Developer resonance** — would a developer find this credible, or does it sound like marketing fluff?

Offer 3 headline variants at different angles:
- Benefit-led: "X so you can Y"
- Problem-led: "Stop doing X manually"
- Result-led: "Y in under 5 minutes"

### Body copy

Check:
- Uses "you", not "we" (customer focus)
- Specific numbers and outcomes vs. vague adjectives
- Removes "powerful", "simple", "easy", "innovative" — show don't tell
- CTA is one clear action

### Output format

```
## Copy Review

### Original
[paste]

### Issues
- Line 2: "Powerful tool" — replace with specific capability
- Missing: what happens after sign-up?

### Suggested rewrites
[3 options]
```
