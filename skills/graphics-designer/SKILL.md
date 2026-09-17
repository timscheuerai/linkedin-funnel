---
name: graphics-designer
description: Create an individual graphic, carousel or banner using the client's supplied visual rules, or a neutral unbranded layout when requested.
---

Workspace: all context paths below (identity, audience, strategy, voice, brand, raw, output, index, log, workspace preferences and context scripts) resolve from `context/` in the kit root. Read both the root `AGENTS.md` and `context/AGENTS.md`. Skill-local `references/` and flowchart `scripts/` resolve from this skill directory.


# Design a graphic

Read `AGENTS.md`, `brand/BRAND.md`, the content brief and relevant positioning, audience and voice pages. Read token files or reusable assets only if they actually exist. This template includes no preapproved visual kit.

Establish the information relationship before choosing a composition: a thesis, sequence, comparison, hierarchy, evidence or reflection. Keep the copy faithful to its source. A missing number or screenshot is not permission to invent one.

Use dimensions from the requested destination or supplied brief. Verify current platform requirements when exact compliance matters. Infer routine layout details; ask only when a missing choice changes the content or format materially.

## Visual choices

Use approved brand rules when available. Otherwise create a plain unbranded draft when that fits the request: no invented logo, author signature, corporate palette, decorative footer or mandatory CTA. Mark temporary visual choices as draft choices rather than new brand policy.

Let spacing, hierarchy and truthful relationships carry the graphic. Do not force diagrams into quotes or turn every slide into identical cards. Use readable text and meaningful connector contrast. Keep authentic product screenshots intact and use supplied photography with known permissions.

For carousels, give each page a specific job and maintain continuity. Include a call to action only when the brief provides a useful next step.

## Build and inspect

Choose tools actually available in the environment. HTML/CSS or SVG works for exact text and diagrams; an image-generation tool is useful for suitable illustration work. Use `flowchart` for editable process maps. The skill does not assume a bundled browser, renderer or design MCP.

Keep working assets in `output/<asset-name>/` or the user-selected destination. Save editable source alongside the export. Use local or licensed fonts and verify actual font loading when rendering.

Inspect the rendered asset at its intended size and a small viewing size. Check text accuracy, hierarchy, clipping, contrast, connector collisions and missing assets. Fix visible defects and rerender. If rendering or inspection is unavailable, deliver the source and state the exact unverified step.

Return file links, dimensions and relevant limitations. Producing one graphic does not authorize changing shared brand rules or publishing it.
