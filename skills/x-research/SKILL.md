---
name: x-research
description: Research X posts and conversations in the author's niche and turn the strongest ones into sourced content ideas and angles the author can support with their own evidence. Use for niche trend scans, finding strong posts, creator research or building an X creator watchlist; it produces research briefs, not published posts.
---

Workspace: all context paths below (identity, audience, strategy, voice, brand, inspiration, raw, research, output, index, log, workspace preferences and context scripts) resolve from `context/` in the kit root. Read both the root `AGENTS.md` and `context/AGENTS.md`. Skill-local `references/` and `scripts/` resolve from this skill directory.

# X research

Find useful conversations and unusually strong posts the author can contribute to from their own work. Reach is evidence of attention, not proof of truth or pipeline. The research loop: decompose the question, search, refine, follow threads, read linked sources, and synthesize with citations.

## Ground the research

Read the relevant context in order:

1. `identity/positioning.md` and `identity/proof.md`.
2. `audience/ideal-follower.md`.
3. `strategy/pillars.md` and `strategy/funnel.md`.
4. `voice/linkedin-voice.md` and `voice/formats.md` when forming angles or drafting. These calibrate the author's voice, not X's format or hook limits.
5. `inspiration/creator-bank.md` for creators the author already studies.

Search the context with `rg` or the optional `scripts/qmd.sh` for the author's receipts, previous framing and published pieces. Check dates before calling something current. The author's current instructions and supplied text take precedence over older files. Never turn another creator's result into the author's experience.

Read [niche.md](references/niche.md) for how to build search seeds, selection criteria and the brief structure. The author's existing pillars remain the taxonomy.

## Choose the research depth

- For a supplied post or narrow question, look it up and follow only the context needed to answer. Do not run a broad scan automatically.
- For a discovery request, start with 2 or 3 distinct queries and small pages. Refine based on noise, coverage and the author's time and spend limits.
- Prefer saved results and the author's bookmarks before paying to retrieve the same material again. Cached metrics need their capture date.
- Default to the last 7 days. State the actual window; older research needs an archive route, supplied URLs or browser search.

Retrieval routes, cheapest first:

1. **Browser search or supplied links**: no API spend. X's browser search supports engagement operators, for example `("cold email" OR outbound) min_faves:50 -filter:replies` plus a date range. Browser and API query dialects differ.
2. **OXYGEN's X connection**, if the author has an OXYGEN workspace with X connected: read [oxygen.md](references/oxygen.md) for discovery, preview, bounded live reads and normalization. It is billed per call; preview first.
3. **Grok or another semantic X search**, if the author already uses one: good for discovering conversations, but confirm every cited post at its source before attributing facts. A chat subscription does not include API credits.

For a creator watchlist and a queue of posts to engage with, read [engagement.md](references/engagement.md).

## Search, inspect, select

1. Translate the question into a topic query, a real audience problem, and optionally a known builder or concrete workflow. The seeds in the niche reference are starting points, not a mandatory batch.
2. Start with original posts. Include replies deliberately when looking for buyer language, objections, failures or implementation detail.
3. Inspect the actual post, media and relevant thread before explaining why it worked. Follow linked docs, repos or benchmarks for technical claims. A truncated snippet or an AI summary is not the full source.
4. Deduplicate by post ID. Prioritize audience fit, a substantive mechanism, meaningful discussion and an angle the author can support with evidence.
5. Compare engagement alongside age and author size. Call a post an outlier relative to that author's normal performance only when a comparable baseline was actually collected. Otherwise say "strong in this sample." Likes, bookmarks, replies and reposts are separate signals. Missing views are unknown; observed zero views are not proof of zero reach.
6. Separate source facts, hypotheses about performance, and the author's proposed contribution. A popular opinion does not establish algorithm mechanics, product truth, conversion or causality.

## Deliver the brief

Give a short recommendation and a sourced shortlist. For each selected item: post URL, author, publication date, observed metrics and capture time, relevance, format or mechanism, and the distinct angle the author could add. Mention sample and window limits. If no strong posts emerged, say so and report useful audience questions.

For content ideas, attach 1 existing pillar and 1 funnel stage, the author's actual receipt or the missing evidence, and a fitting asset. Recommend the strongest few; do not manufacture a quota. Short hooks are optional, not full drafts.

Save requested research under `research/<date>-x-<topic>/`. Keep raw responses separate from the synthesis, label capture time and query, and keep research distinct from the content board. File durable findings into the context pages through [capture-context](../capture-context/SKILL.md). Do not edit `raw/` sources in place.

## When the author also asks for drafts

Research alone does not imply creating or publishing posts. When drafting is requested, hand over to [x-copywriter](../x-copywriter/SKILL.md) or [x-planner](../x-planner/SKILL.md) with the brief. Preserve the author's supplied wording and proof numbers, including timeframe, units and qualifiers; use only proof from `identity/proof.md`. No invented drama, generic AI slogans, em dashes or obligatory calls to action.

Do not schedule, publish, reply, DM, follow or like as a side effect of research.

## Source

Adapted from [rohunvora/x-research-skill](https://github.com/rohunvora/x-research-skill) at commit `623cca7f41f2fb859bdd01dd7328b7b15da110ed`. The research method is retained; its standalone X API client and examples are replaced with browser, OXYGEN and optional semantic-search routes and this kit's author context.
