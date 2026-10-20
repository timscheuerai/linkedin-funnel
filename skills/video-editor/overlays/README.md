# Video overlays

The graphics kit behind the [video-editor](../SKILL.md) skill: 10 templates for long-form talking-head and screen-demo edits and vertical shorts, rendered with Remotion as clips that ffmpeg composites and DaVinci Resolve imports.

| Template | Job |
| --- | --- |
| Keyword | The 1 idea of a sentence, the speaker's words, optional `*serif*` accent (single or multi-word) |
| Lower | Name a person, tool or place: kicker plus title |
| Stat | 1 number with what it measures; the leading number counts up |
| List | Items that build on the spoken word (`items[].at`) |
| Chapter | Section change; serif numeral plus title |
| Media | A real screenshot in a quiet window frame with a URL label |
| Focus | Spotlight on a region of the recorded screen, the rest dims |
| Zoom | Opaque insert that scales the picture around a focus point |
| Captions | Clean word-by-word captions: off-white, lowercase, tight overlapping blocks; hero units build a small lead line and land a heavy serif or number payoff; placements beside the head; a translucent accent marker on specific key words; `mode: "hooks"` for long-form |
| Interlude | Full-frame flat dark or light beat with the same type units, centred |

## Make it the author's

Colours and fonts live in [src/theme.ts](src/theme.ts): change the hex values in `palette` to the author's colours from `context/brand/BRAND.md`, and swap the font files in `fonts/` (update the imports and family names in `theme.ts`) if the brand uses other faces. The defaults are neutral: Geist for the sans, Instrument Serif for the accent, DM Serif Display Italic for heavy payoffs, all under the SIL Open Font License (licences in `fonts/`).

`tone: "clean"` is the default: type straight on the picture in `palette.caption`, no surface, a barely visible shadow. `tone: "ink"` is the same in `palette.dark` with a light halo for bright footage such as white UI. `dark` and `light` keep an opaque card with a glass rim for Media and explicit requests. Motion: 16 frame spring in with a hair of overshoot and a blur-in, 8 frame exit, words rise one by one. Safe margin 76 px (4%) at 1080.

## Run

```bash
npm install                                  # once; Remotion 4.0.451 pinned
npx remotion studio src/index.ts             # preview every template with sample props
node scripts/render.mjs jobs.json            # overlays -> ProRes 4444 alpha, Zoom -> ProRes 422 HQ
node scripts/render.mjs jobs.json --still    # 1 transparent PNG per job at its fully built frame
```

`jobs.json` is written by `../scripts/build_edit.py`: `{ width, height, fps, jobs: [{ id, template, seconds, props, out }] }`. The renderer picks the design space from the footage (1920 x 1080 or 1080 x 1920) and scales to it; other aspect ratios are rejected. Absolute `props.src` files are hard-linked into `public/.jobs/` (git-ignored) before bundling.

Vertical footage (9:16) renders in a 1080 x 1920 design space: cards keep clear of the Shorts, Reels and TikTok chrome (top 10%, bottom 22%) and are set 15% larger. Studio samples in `src/Root.tsx` hold only required fields, because Remotion merges them under every render and an optional sample field would leak sample text into a real card.

`public/sfx/` holds the sound-effect library. It ships empty: see [its README](public/sfx/README.md).

## Licence note

Remotion has its own licence: free for individuals and companies of up to 3 people, a company licence above that. Check [remotion.dev/license](https://www.remotion.dev/license) before using the kit in a larger team.

## Measured

1080p, 6 s List overlay: about 45 MB as ProRes 4444. At 4K expect about 4 times that, so a 12 minute edit with 30 cards needs a few GB of `work/` space; delete `work/` after delivery if disk is tight. Stills for all templates render in about 25 s, full overlay clips in about 8 s each.
