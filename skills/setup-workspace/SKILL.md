---
name: setup-workspace
description: Initialize this content workspace for a new author, including local preferences and optional Notion or local search setup.
---

Workspace: all context paths below (identity, audience, strategy, voice, brand, raw, output, index, log, workspace preferences and context scripts) resolve from `context/` in the kit root. Read both the root `AGENTS.md` and `context/AGENTS.md`. Skill-local `references/` and flowchart `scripts/` resolve from this skill directory.


# Set up the workspace

Read `AGENTS.md`, `README.md`, `index.md`, `workspace.example.json` and `strategy/notion-schema.md`. Resolve paths from this skill's repository, not an unrelated current directory.

## Local setup

Inspect existing context and local configuration before writing. A populated workspace is not a blank template: preserve its sources, settings and user edits.

Gather the author's name, language, audience, content goal and available source material from the conversation. Ask only for missing choices that affect the requested next step. Time zone, posting days and platform are needed for a dated plan, not for an initial interview.

Create or merge ignored `workspace.local.json` from the example. Leave unknowns null or empty. Keep credentials in the connected tool's authentication store. This file holds preferences, not evidence for biographical or business claims. Durable decisions go in the relevant context pages with source notes.

Use `templates/context-interview.md` to start capture. Do not populate identity, proof, voice, hooks or topics with sample answers. No bulk rename is needed to make the generic skills work.

## Optional Notion setup

Local drafting works without Notion. Set it up only when included in the request.

1. Read `strategy/notion.local.json` if present, otherwise inspect legacy `strategy/notion.json` if this installation has one. Fetch the configured destination. For a new setup, ask for the parent page or locate the explicitly named one and verify its identity.
2. Inspect the selected parent's children and existing schemas. Reuse an existing matching setup rather than duplicating it.
3. Create or map the four databases from `strategy/notion-schema.md` using the available connector's documented arguments. Store each confirmed ID in `strategy/notion.local.json` as it is created. Do not copy IDs from the example, another project or an unrelated search result.
4. Add supported views. If a connector cannot configure a view or native template, report that specific limitation. Do not claim it exists.
5. Fetch the resulting schemas and query each data source. For a new blank setup, verify all four have no rows. Preserve existing rows when resuming a populated setup.

After any ambiguous write result, inspect the destination before retrying. A database ID and its data source ID may differ.

## Optional search and handoff

If search is requested and qmd is installed, run `scripts/qmd-setup.sh`, then search a known page through `scripts/qmd.sh`. Otherwise use `rg`. Do not install packages or embedding models merely to initialize context.

Run `scripts/wiki-lint.sh`. Report what is connected, what remains blank and the next source to capture. Setup does not schedule content, publish posts or send outreach.
