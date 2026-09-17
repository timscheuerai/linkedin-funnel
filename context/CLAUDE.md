# Content engine: agent rules

This repository holds the context and reusable procedures for one author. The owner, audience, offer, voice and visual identity start unfilled.

## Where things live

- `raw/`: exact source material, append only. Add a dated folder and manifest for each ingest.
- `identity/`, `audience/`, `strategy/`, `voice/`, `brand/`, `inspiration/`: linked context synthesized from those sources.
- Notion, when connected: pillars, topics, subtopics, content drafts, calendar, hooks and creator references. Read `strategy/notion-schema.md`.
- `research/`: temporary research. File durable findings in the context pages.
- `../skills/`: reusable procedures shared with the whole kit. `../.claude/skills` points to the same files.
- `output/`: local working exports and review artifacts, ignored by Git.

## Empty means unknown

A page with `status: stub` contains prompts, not author facts. Do not invent a biography, opinion, audience, metric, offer, voice or visual identity. Use supplied material to fill it. Creator references can inform technique but do not establish the author's experiences or beliefs.

Distinguish human statements, source-backed facts and proposed interpretations. Record source dates and public-use boundaries. Unclear public-use status means the material stays out of public copy until resolved.

## Read, then write

Start at `index.md`. Search with `rg` or the optional repo-scoped `scripts/qmd.sh`; read full sources behind claims. Before drafting, read the relevant identity, audience, strategy and voice pages. Check `identity/proof.md` before using a metric.

Use `templates/page.md` for short context pages with frontmatter and Source Notes. Update `index.md` and append to `log.md` when filing durable context. Keep the context `AGENTS.md` and `CLAUDE.md` identical.

## Connections and drafts

Local connection settings belong in ignored `workspace.local.json` and `strategy/notion.local.json`. Start from their example files. They store names, preferences and resource IDs, never credentials. Use the connected tool's authentication.

Fetch the configured Notion parent and relevant data sources before writing. Never infer a destination from another repository, account or search result. If Notion is unavailable, return drafts in chat; save local working files only when requested. Do not create a second posts database.

The default taxonomy scaffold has 4 pillars, 4 topics per pillar and 4 subtopics per topic. It is adjustable to the author's strategy. Subtopics live in topic page bodies. Pick one pillar and one funnel job per post. Dates, cadence, time zone, numeric formatting, hooks and calls to action come from the current brief and author context.

## Visual work

Start at `brand/BRAND.md`. No palette, fonts, logo, signature, footer or visual kit is preapproved. If a neutral graphic is requested while the brief is empty, produce a plain unbranded draft and label that choice. Do not treat it as the author's new identity. Deliver editable source and inspect rendered output when tools permit.

## Changes and delivery

Preserve existing edits and raw sources. Run `scripts/wiki-lint.sh` and relevant skill checks before committing. Follow the user's Git instructions.

A request for a draft does not authorize publication, scheduling or outreach. A context capture does not authorize paid collection or enrichment. Use the user's actual scope for those actions.
