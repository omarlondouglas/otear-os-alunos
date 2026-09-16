# Social Media Calendar - Guidelines

Use this knowledge when planning an editorial calendar for social media.

## Objective

Create a repeatable content calendar with four core formats:

- Noticias
- Vlog
- Tutorial
- Review sincero

The goal is to balance trend relevance, trust, usefulness, and personality.

## Format Roles

### Noticias

Use for timely topics, market shifts, new tools, platform changes, AI updates, launches, controversies, and industry signals.

Output should include:

- headline
- source or trend angle
- why it matters
- short-form hook
- suggested platform
- CTA for comments or saves

### Vlog

Use for behind-the-scenes, personal routine, founder/operator point of view, process documentation, experiments, lessons from the day, and proof of work.

Output should include:

- scene or situation
- personal angle
- emotional beat
- simple narrative arc
- visual notes
- CTA for connection

### Tutorial

Use for practical education, step-by-step walkthroughs, frameworks, tool demos, templates, checklists, and repeatable processes.

Output should include:

- problem
- promise
- steps
- expected result
- assets needed
- CTA for saves or follow-up

### Review sincero

Use for honest evaluations of tools, products, workflows, trends, creators, campaigns, apps, or content formats.

Output should include:

- what is being reviewed
- who it is for
- what worked
- what failed
- verdict
- recommendation
- CTA for debate

## Weekly Mix

Default mix for a balanced calendar:

- 30% noticias
- 25% tutorial
- 25% vlog
- 20% review sincero

Adjust based on objective:

- Growth: increase noticias and review sincero.
- Authority: increase tutorial and noticias.
- Trust: increase vlog and review sincero.
- Conversion: increase tutorial and review sincero.

## Calendar Entry Schema

Use this structure when creating planned entries:

```json
{
  "title": "Short content title",
  "format": "noticias | vlog | tutorial | review_sincero",
  "platform": "instagram | tiktok | youtube | linkedin",
  "scheduled_at": "YYYY-MM-DDTHH:mm:ss",
  "hook": "Opening line",
  "angle": "Editorial angle",
  "notes": "Production notes, sources, assets, CTA"
}
```

For the existing `content_calendar` API, map:

- `title` to `title`
- `format` to `content_type`
- `platform` to `platform`
- `scheduled_at` to `scheduled_at`
- `hook`, `angle`, and production notes to `notes`

## Planning Workflow

1. Define period: week, month, launch window, or campaign.
2. Define audience and objective.
3. Pull timely inputs from News Radar when noticias are needed.
4. Select four-format distribution.
5. Generate titles, hooks, notes, and publishing dates.
6. Avoid repeating the same format on consecutive days unless it is intentional.
7. Save approved entries into the calendar.

## Quality Rules

- Every item must have a clear reason to exist.
- Every week should include at least one trust-building post.
- Tutorials must be specific enough to save.
- Reviews must include a real verdict, not neutral summary.
- Noticias must explain why the audience should care.
- Vlogs must reveal process, lesson, tension, or transformation.

