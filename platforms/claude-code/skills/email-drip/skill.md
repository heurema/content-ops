---
name: email-drip
description: 'Use when the user wants to write a welcome sequence or email drip campaign. Triggers: "welcome sequence", "newsletter drip", "onboarding emails", "email series", "welcome email". Note: generates drafts only — no sending, no API.'
---

Read `.agents/content-context.md` first (if it exists).

## Purpose

Generate email drip sequence drafts. Output is Markdown text — no email sending, no provider API integration.

## Sequences

### Welcome sequence (3-5 emails)

Email 1 (day 0 — welcome):
- Subject: "Welcome — here's what to expect"
- Body: who you are, what they'll get, one thing to do now (read a post, reply with a question)

Email 2 (day 2 — best content):
- Subject: "Start here: [best post title]"
- Body: your single best piece of content + why it's useful to them

Email 3 (day 5 — build trust):
- Subject: something you got wrong / a lesson learned
- Body: honest post about a mistake or wrong assumption. Developer readers respect candor.

Email 4 (day 10 — soft CTA):
- Subject: [optional project/tool they might use]
- Body: introduce what you're building, what problem it solves, link to try it

Email 5 (day 21 — stay or go):
- Subject: "Still finding this useful?"
- Body: reminder of value + easy unsubscribe signal

## Process

1. Ask: What type of sequence? (welcome, course, launch, re-engagement)
2. Ask: How many emails?
3. Generate drafts in order.
4. Output as `email-sequence-draft.md` in current directory.

## Scope

This skill generates text only. For sending: Mailchimp, ConvertKit, Resend, etc. require separate setup outside content-ops.
