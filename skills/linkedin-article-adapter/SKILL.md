---
name: linkedin-article-adapter
description: Adapt a finished X Article into a native LinkedIn article while preserving its text and inline figures, recompose the cover at LinkedIn's article ratio, and prepare a numbered upload folder plus a short post to share it. Use after x-article-writer when the author wants the same article on LinkedIn.
---

Workspace: all context paths below (identity, audience, strategy, voice, brand, raw, output, index, log, workspace preferences and context scripts) resolve from `context/` in the kit root. Read both the root `AGENTS.md` and `context/AGENTS.md`. Skill-local `references/` resolve from this skill directory.

# LinkedIn article adapter

Turn a finished X Article into a reviewable LinkedIn article handoff. Read the final X Article and its latest image pack, editable sources, figure map and proof notes before changing anything. The latest hand-edited text is the source; do not reconstruct it from an older brief or preview.

## Adapt the article

Keep the title, argument, section order, examples, links, figures and the author's voice substantially intact. The one link change: links to the author's own site switch their UTM source from `x` to `linkedin` and keep the campaign slug, so LinkedIn readers are not counted as X. Make only platform-specific edits that improve reading in the LinkedIn article editor: clean up X-only references, adjust an opening or call to action that depends on X, and correct obvious formatting. Do not turn the article into a feed post, add a new hook, inflate its length or update claims without a source. Keep numbers, time windows, qualifiers and the distinction between observed and proposed work exactly scoped, checked against `identity/proof.md`. If the article is already about LinkedIn, minimal text edits are expected.

Preserve the intended figure insertion points and captions. Reuse approved full-resolution inline exports when they are still accurate. If a figure needs a platform fit change, adapt its editable source and inspect the new export; do not stretch a raster or silently replace a detailed diagram with generic cards. Use [graphics-designer](../graphics-designer/SKILL.md) for artwork and [flowchart](../flowchart/SKILL.md) when editing a process map. Follow `brand/BRAND.md` and the approved design of the article. Keep visual changes scoped to this article.

## Recompose the article cover

Make a LinkedIn **article cover**, not a profile background banner. Check [LinkedIn's current article-cover guidance](https://www.linkedin.com/help/linkedin/answer/a521719) at execution time; it has recommended 1920 x 1080 at 16:9, and the profile-banner size does not apply. Recompose the X cover (5:2) from its editable source at the article ratio. Preserve the recognizable result, hierarchy, typography, palette and real system imagery, while giving the taller canvas intentional spacing. Keep key text clear of likely crop edges and inspect at native size and at a narrow feed-preview width. Keep an editable source and export an upload-ready PNG or JPEG within LinkedIn's current size and format limits. Never merely resize a 5:2 bitmap into 16:9.

A cover layout that works for a results-led article: the result headline on the left, 1 or 2 supporting proof numbers together in a card at the upper right, and the real workflow diagram across the full width below. Keep each number's qualifier (time window, unit) attached to that number only. Treat this as one option, not a template for every cover.

## Prepare the upload folder

Create 1 clearly named folder in `output/` (or where the author asks) for this article. Put only the files needed for manual drag and drop at its top level:

- `00-cover.png` for LinkedIn's cover field.
- `01-...png`, `02-...png`, and so on for every inline figure in article order, using the best inspected full-resolution exports.
- `ARTICLE.md` with the complete adapted title and body. Reference the local image filenames at the exact insertion points; keep captions and working links.
- `START-HERE.txt` with the source article link, the cover instruction, the ordered image placement and any material text changes. This is a short upload guide, not a second manuscript.

Use a new folder or replace only a clearly matching earlier handoff after checking its contents. Do not move or delete the X source assets. Keep editable artwork with its source and link it from the guide. Check file dimensions, type, readability, image order, local links and the complete article text. The folder should be usable without extracting a ZIP.

If the source article is in Notion, read its complete page and image order, then write the local handoff from that final version. Do not rely on expiring signed Notion image URLs when local exports exist. Keep the X draft intact. Save a LinkedIn draft on the content board only when the author asks, using `strategy/notion-schema.md`, platform LinkedIn, draft state and a full readback. Creating files does not authorize publishing or scheduling.

## Description and share post

When the handoff also needs an article description or a post to share it with the network, write a short description and a separate paste-ready post with [linkedin-copywriter](../linkedin-copywriter/SKILL.md) in the author's LinkedIn voice. The post gives a reason to open the article without repeating its full instructions. Keep public metrics scoped by `identity/proof.md`. See [the worked example](references/share-post-example.md) for the shape. Include both in the upload folder for convenient pasting.

Finish with the folder path, the adapted article and editable cover, their dimensions, and any remaining editor step. The author should be able to open the folder and drag the files into a native LinkedIn article in order.
