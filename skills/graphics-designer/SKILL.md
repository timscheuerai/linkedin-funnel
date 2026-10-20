---
name: graphics-designer
description: Create an individual graphic, carousel or banner using the client's supplied visual rules, or a neutral unbranded layout when requested.
---

Workspace: all context paths below (identity, audience, strategy, voice, brand, raw, output, index, log, workspace preferences and context scripts) resolve from `context/` in the kit root. Read both the root `AGENTS.md` and `context/AGENTS.md`. Skill-local `references/` and flowchart `scripts/` resolve from this skill directory.


# Design a graphic

Read `AGENTS.md`, `brand/BRAND.md`, the content brief and relevant positioning, audience and voice pages. Read token files or reusable assets only if they actually exist. This template includes no preapproved visual kit.

Establish the reader, takeaway, required content, dimensions and any real next action from the brief, then the information relationship: a thesis, sequence, comparison, hierarchy, evidence or reflection. Before a new composition, state a short working direction: the focal element, the reading order, and how type, space and material express the idea. A poster can communicate through form with sparse copy; a teaching graphic needs accurate, usable labels. Split dense material before shrinking it into unreadable text.

## Copy on a graphic

Distill the source into a headline, useful points and necessary attribution. When the graphic accompanies a post, select the author's own lines verbatim instead of paraphrasing them into smoother copy, and do not paste the whole post. Preserve order, numbers and caveats that affect meaning. A missing number or screenshot is not permission to invent one.

On an instructional graphic, every line should tell the reader what to do or state a fact they can act on: "Create 1 folder and 1 rules file", not "the setup takes 1 afternoon". Lead with the verb and name the real thing (a folder, a command, a weekday). Descriptive lines read as AI filler. Do not force that grammar onto a quote, a name or an editorial statement.

Use dimensions from the requested destination or supplied brief. Verify current platform requirements when exact compliance matters. Infer routine layout details; ask only when a missing choice changes the content or format materially.

## Visual choices

Use approved brand rules when available. Otherwise create a plain unbranded draft when that fits the request: no invented logo, author signature, corporate palette, decorative footer or mandatory CTA. Mark temporary visual choices as draft choices rather than new brand policy.

Let spacing, hierarchy and truthful relationships carry the graphic. Do not force diagrams into quotes or turn every slide into identical cards. Use readable text and meaningful connector contrast. Keep authentic product screenshots intact and use supplied photography with known permissions.

For carousels, give each page a specific job and maintain continuity. Include a call to action only when the brief provides a useful next step.

## Build and inspect

Choose tools actually available in the environment. HTML/CSS or SVG works for exact text and diagrams; an image-generation tool is useful for suitable illustration work. If the user asks for a prompt, make it self-contained: exact copy, colours, composition, dimensions and references. A prompt or a generated raster is not an editable design. Use `flowchart` for editable process maps. The skill does not assume a bundled browser, renderer or design MCP.

Keep working assets in `output/<asset-name>/` or the user-selected destination. Save editable source alongside the export. Use local or licensed fonts and verify actual font loading when rendering.

Inspect the rendered asset at its intended size and a small viewing size. Check text accuracy, hierarchy, clipping, contrast, connector collisions and missing assets. For a carousel, inspect every page and the sequence; for a banner, check the avatar and crop safe area. Make 1 deliberate refinement pass on the largest visible weakness, adjusting hierarchy, line breaks, spacing or crop before adding decoration, and reinspect. If rendering or inspection is unavailable, deliver the source and state the exact unverified step.

Report the real state: source ready (render pending), prompt prepared, rendered (inspection pending), or rendered and inspected. Never claim a visual review from source code or automated checks alone.

Return file links, dimensions and relevant limitations. Producing one graphic does not authorize changing shared brand rules or publishing it.
