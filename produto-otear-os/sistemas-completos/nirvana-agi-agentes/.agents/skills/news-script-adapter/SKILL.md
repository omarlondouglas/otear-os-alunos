---
name: news-script-adapter
description: Adapt a news item, headline, article, or briefing into a short-form video script using proven creator patterns for hooks, development structure, emotional triggers, pacing, and on-screen editing. Use when the user wants a news story turned into a TikTok/Reels/Shorts script, wants multiple creator-style angles, or wants a script broken into hook, development, screen direction, and delivery notes.
---

# News Script Adapter

Use this skill when the user gives you a news item and wants a short-form script built from the creator patterns analyzed in this repo.

## What This Skill Produces

Given a news item, produce:

- a chosen angle
- a hook
- development beats
- screen/editing directions
- delivery guidance
- primary emotional trigger
- optional alternative versions in other creator archetypes

## Archetypes

Read [references/creator-patterns.md](references/creator-patterns.md) before drafting if you need the full analysis.

Use these seven archetypes:

- `v_daily_journal`: daily briefing, factual, service-oriented
- `dylan_page`: breaking crisis update, high urgency
- `rpn`: practical AI leverage, insider advantage
- `gabrieladamuchi`: disruption, obsolescence, monetary upside
- `gigaqian`: technical explanation with metaphor and interpretation
- `dr_cintas`: compressed weekly roundup, high info density
- `kanekallaway`: future-shock narrative, wonder plus implication

## Default Workflow

1. Extract the raw facts from the news item.
2. Decide the strongest angle:
   - urgent development
   - practical consequence
   - market or technology shift
   - social impact
   - future implication
3. Choose the best archetype for that angle.
4. Choose the first trigger:
   - urgency
   - fear
   - curiosity
   - opportunity
   - obsolescence
   - wonder
   - authority
5. Write the script in this order:
   - `Theme`
   - `Primary trigger`
   - `Hook`
   - `Development`
   - `On-screen editing`
   - `Delivery style`
   - `Closing line`

## Output Format

When the user asks for one script, use:

```md
## Angle

## Theme

## Primary Trigger

## Script
Hook:

Development:

Closing:

## On-Screen Editing

## Delivery Notes
```

When the user asks for multiple options, give 3 versions maximum and label the archetype used.

## Drafting Rules

- Keep the hook in the first 1-2 sentences.
- Do not bury the core claim.
- Make the first trigger explicit in the opening.
- The development must escalate or clarify, not repeat the hook.
- Screen directions must support the claim:
  - headlines
  - screenshots
  - maps
  - charts
  - bullet overlays
  - facecam emphasis
  - demo footage
- If the topic is technical, explain significance before detail unless the user asks for a deep technical version.
- If the topic is a crisis or breaking event, prioritize update clarity and consequence.
- If the topic is AI/business, bias toward practical implications and competitive advantage.

## Style Selection Guide

- Choose `v_daily_journal` when trust, neutrality, and routine matter most.
- Choose `dylan_page` when the news has threat, escalation, spread, or ongoing updates.
- Choose `rpn` when the story is about tools, leverage, or creator advantage.
- Choose `gabrieladamuchi` when the story can be framed as old way versus new way.
- Choose `gigaqian` when the story needs explanation and interpretation.
- Choose `dr_cintas` when the user wants compressed recap or roundup language.
- Choose `kanekallaway` when the story signals a larger future shift and needs awe.

## If The User Asks For “Use These Foundations”

Default to:

- strongest hook logic from `dylan_page` or `gabrieladamuchi`
- clearest explanation from `gigaqian`
- best practical takeaway from `rpn`
- best compression from `dr_cintas`
- best future framing from `kanekallaway`

## Avoid

- generic hooks with no stake
- long intros before the main claim
- repeating the same point in different words
- screen notes that do not change viewer understanding
- neutral tone when the chosen archetype depends on tension

