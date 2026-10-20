# Style rules

The edit style for long-form YouTube talking-head and screen-demo videos and for shorts. `build_edit.py check` enforces the numeric rules; the rest is judgement at the stills and QA review. Pacing, safe-area, caption and audio numbers are adapted from HeyGen's HyperFrames skills (Apache 2.0), whose talking-head recut is itself adapted from vtake-skills (MIT).

The look below is a default the author can change: colours and fonts live in `overlays/src/theme.ts`, timings and sizes in `presets/clean.json` and the templates. Record the author's own verdicts (what they cut, what they kept) at the end of this file so the next edit starts from them.

## House style: clean

Short talking-head clips can be planned automatically from the `clean` preset with `scripts/plan.py`.

Boxed cards, highlight pills and pop animations read as generic AI edits. The clean style:

- Type straight on the picture in a warm off-white (`palette.caption`), no boxes, no outlines, no coloured highlights, a shadow you can barely see. Every card template defaults to `tone: "clean"`; on bright footage (white UI, screen recordings) use `tone: "ink"` (dark type with a light halo), because white on white is unreadable. Dark and light card surfaces are for Media and explicit requests only.
- The words carry the edit: Captions (1 word at a time, lowercase, hard cut, centred at 65% of the height; filler 0.8x, `emphasis` 1.35x) and hero units (a small lead line builds, the payoff lands large in the heavy italic serif, or bold sans for a number).
- Serif is the only accent, and only on the payoff: about 1 per 5 to 10 s. Never 2 on screen.
- Interludes (flat dark or light frame, centred type) for the 1 idea or number a piece hangs on; 1 to 4 s, cut in hard.
- Reframes are hard cuts (`ease: 0`), 1.1 to 1.3, roughly every 2 to 3 s in shorts; no animated zoom ramps.
- Set tight and modest: small text at 0.7 leading so its lines touch, word spaces narrow, the serif hero's ascenders nearly touch the line above, the number sits right under it; sizes stay small.
- Vary the position: most words sit centred under the chin; now and then a hook or a run of words sits beside the head (`hero.place`, `placements`: `left` or `right`), set flush to that side. In a centred close-up the free space beside the head is the shoulder, not eye level: keep side text off the face (`check` stills) and reframe with a punch-in whose `focus` pushes the speaker to the other third when a side block needs room. Light text never sits on a bright wall.
- Accent marker: sometimes 1 specific key word gets a translucent accent marker (`palette.accent` at 30%) wiping in behind the caption type (`highlight`). Specific words only, never whole lines; at most 1 per 10 s, never on the serif word.
- Motion is soft and quiet: every word rises a little out of a blur (4 frames body, 6 lead, 16 hero, expo-out), the hook block drifts up over 1.2 s, a unit that ends in a pause blurs out over 6 frames. No springs, no bounce, no pop.
- Anything that repeats what is already on screen is cut.

## Why a fixed menu

One-shot AI edits tend to fail in the same 3 places: an improvised animated graphic that looks cheap, sound effects with nothing happening on screen (scissor sounds with nothing being cut), and an invented graphic where the real page should have been shown. The fix is structural: a closed template menu, sound effects that can only hang off a visual event, and a Media card for the real page.

## Overlay menu

Design space is 1920 x 1080; the kit scales to the footage. Default anchors avoid a bottom-left webcam; move them when the webcam sits elsewhere.

| Template | Use when | Do not use | Duration | Default anchor |
| --- | --- | --- | --- | --- |
| Captions | Shorts and social cuts: every word, with hero units for the hook and payoffs | Long-form YouTube (uploaded captions do the job) | whole clip | 65% height (80% landscape) |
| Interlude | The 1 idea or number the piece hangs on, full frame | More than 1 per 30 s | 1 to 4 s | centre |
| Keyword | The 1 idea of a sentence, 1 to 6 of the speaker's words, `*serif*` on the word that matters | Full sentences, filler, a paraphrase they did not say | 1.5 to 4 s | top-center |
| Lower | Name a person, tool or place on screen ("Dictating with / <tool>") | Repeating what the UI already labels large | 2.5 to 6 s | bottom-right |
| Stat | 1 number the speaker says or the screen shows, with what it measures | Numbers from memory; add `source` | 3 to 6 s | top-right |
| List | The speaker enumerates 3 to 6 things; each item appears on its word (`items[].at`) | Lists they do not say out loud | 3 to 18 s | right |
| Chapter | Section change; titles become the YouTube chapters | More than 1 per 45 s | 2 to 4 s | top-left |
| Media | The speaker names a repo, site, post or product that is not on screen: real screenshot | Invented or generated stand-ins | 3 to 9 s | right |
| Focus | Point at a region of the recorded UI; dims the rest | Regions that overlap the webcam | 1.5 to 6 s | rect |
| Zoom | Face punch-in on an emphatic line, or a UI zoom that clears the webcam | Zooms that slice the webcam | 1.2 s and up | focus point |

Copy: the speaker's words, trimmed, numerals ("1 agent"), no em dashes, sentence case. Keep 1 accent per card: the serif word or nothing.

## Pacing

- Cards per runtime: under 1 min every 6 to 8 s, 1 to 3 min every 8 to 12 s, 3 to 10 min every 12 to 20 s, 10 to 30 min every 20 to 35 s. Dense teaching x0.7, 1 slow argument x1.5.
- Break the pattern about every 30 s; `check` warns after 60 s without a visual change.
- 1 card at a time, at least 1 s between cards. Focus may sit under a card only on purpose.
- First motion 0.1 to 0.3 s after the cue; exits are faster than entrances (kit: 16 frame spring in, 8 frame out).
- A card lands on its cue word: `at` 0.2 to 0.5 s before the word starts.

## Safe areas and the webcam

- 4% margin on every edge (76 px at 1080). Title-safe content stays within the middle 80%.
- Measure the webcam box from a gridded frame and write `layout.cam`. `check` fails any card whose default footprint touches it.
- Zooms scale around `focus`; the visible region is `[fx - fx/s, fy - fy/s, 1/s, 1/s]`. With a baked-in webcam, keep it fully out (focus far from it) or fully in (a face punch-in: focus at the webcam corner, scale 1.2 to 1.35).
- Focus labels flip to `labelSide: "top"` when the rect is low on the frame.

## Audio

- Voice: high-pass 80 Hz, mud -3 dB at 250 Hz, presence +2.5 dB at 3 kHz, compressor 3:1 at -20 dB. Limiting happens in the final loudness pass. For a quiet mic with room noise, `scripts/voice_print.py` (learned noise print, constant gain) usually sounds more natural than blind denoising.
- Music: only a track the author has the rights to. Default under the intro and outro only, `gain_db` -16 (lands about 14 dB under the voice after ducking), 3 s fades, a static carve at 1 to 2.5 kHz, then sidechain ducking under the voice (threshold 0.03, ratio 8, attack 200 ms, release 400 ms). No whoosh or swell effects.
- Sound effects: only from `overlays/public/sfx/` (add your own licensed files, see its README), at most 1 per visual hit, 1.5 s apart. Suggested names: Keyword, Lower and List `tap`; Focus `click`; Chapter `impact` at -14 dB; Stat `publish`. Level -9 dB unless set. Without files, leave `sfx` out.
- Master: two-pass loudnorm to -14 LUFS integrated, true peak -1.5 dBFS, LRA 11.

## Shorts (vertical)

- Footage 9:16; the kit switches to a 1080 x 1920 design space. Upscale low-resolution cuts to 1080 x 1920 first (lanczos, light unsharp) so cards and captions render sharp; the picture stays as sharp as its source.
- Captions on by default, filler and stutters dropped (`drop`), numbers in the author's format (`fixes`).
- Open with a hook unit: the first line builds small, the payoff lands by about 2 s, then a hard reframe. Close on a serif payoff.
- Keep the opening short: single words until the last few before the payoff. Something changes about every 10 to 15 s (a serif payoff, a marked key term or an interlude); `plan.py` prints any flat stretch.
- 1 text element on screen at a time: an Interlude mutes the captions automatically; a card that only echoes the captions is cut.
- Cards, if any, sit clear of the platform chrome (top 10%, bottom 22%) and off the face.
- Music bed very low (`gain_db` -20) or none; no sound effects on captions.

## Captions

Not burned in by default for long-form: YouTube serves the uploaded captions. For shorts and social cuts use the Captions template in the house style above: 1 word at a time, zero gap between words, 70 to 85% of the transcript with filler and stutters dropped. Sizes at 1080 wide: body 68 px, emphasis 85, lead line 49, hero 126.

## Scan

A labelled frame every 10 s of the cut, 16 per sheet:

```bash
ffmpeg -v error -i "$CUT" -vf "fps=1/10,scale=480:-2" -q:v 4 "$PROJECT/qa/scan/f_%03d.jpg"
```

Tile them with Pillow (label = seconds), then extract gridded full frames (10% grid) at the moments you plan to use. Read the rects and anchors off the grid.

## QA checklist per frame

1. The card is legible at phone size and matches the words being spoken; no boxes, pills or highlights crept in.
2. Nothing covers the speaker's face; zooms show the whole webcam or none of it.
3. A Focus rect sits on the thing the speaker names; its label does not cover the evidence.
4. No card implies something false about what is on screen (a verdict card over someone else's work).
5. Sound: a hit exists only where something appears.

## The author's verdicts

| Date | Piece | Kept | Cut or changed, and why |
|---|---|---|---|
| | | | |
