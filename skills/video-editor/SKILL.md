---
name: video-editor
description: Turn a raw talking-head or screen-demo recording, or a short, into a publish-ready edit in 1 run, in a clean caption style (off-white word-by-word captions, serif payoffs, interludes, hard reframes, no boxes), with overlays timed to the spoken word, -14 LUFS audio, an editable DaVinci Resolve timeline and a QA sheet. Use for "edit this video", "make it publish ready" or "add captions"; it uses talking-head-video-cut for the cut and its bundled Remotion overlay kit for graphics.
---

Workspace: all context paths below (identity, audience, strategy, voice, brand, raw, output, index, log, workspace preferences and context scripts) resolve from `context/` in the kit root. Read both the root `AGENTS.md` and `context/AGENTS.md`. Skill-local `references/`, `scripts/`, `presets/` and `overlays/` resolve from this skill directory.

# Video editor

1 prompt in: where the footage is, a line of direction, optionally the music. Out: a finished MP4, a Resolve timeline the author can open and nudge, and a QA sheet. Keep going until QA passes (at most 3 passes), then report. Do not stop to ask between stages unless content selection is genuinely ambiguous.

Works for 16:9 long-form and 9:16 shorts (captions on, see the Shorts section of the style rules). The style lives in this folder, not in the model: [style-rules.md](references/style-rules.md) is the rulebook, [edit-schema.md](references/edit-schema.md) the plan format, and the template menu is fixed. Read both before planning. For a designed intro followed by a clean tutorial, [longform-edit](../longform-edit/SKILL.md) decides the treatment; this skill is the engine that builds it.

## Requirements

Python 3 with Pillow (and numpy for `match_grade.py`), ffmpeg and ffprobe, Node 18 or newer for the overlay kit (`npm install` in `overlays/` on first use; the build runs it when `node_modules` is missing). `uv` is optional: the Resolve export fetches `opentimelineio` through it. A word-timed transcript of the source (see [project-setup.md](references/project-setup.md) for the JSON shape). Read the Remotion licence note in [the overlay kit README](overlays/README.md).

Make the look the author's before the first edit: the colours and fonts in `overlays/src/theme.ts` from `brand/BRAND.md`. With an empty brand, keep the neutral defaults and say so.

## Pipeline

1. **Cut.** Run [talking-head-video-cut](../talking-head-video-cut/SKILL.md) (word-timed transcript, take selection, render). Its project folder `<source-dir>/edit/<slug>/` becomes this edit's project: `transcripts/`, `edl.json`, the cut MP4. Reuse an existing cut when the author points at one; for a clip cut elsewhere, follow [project-setup.md](references/project-setup.md).
2. **Map the words** onto the finished cut:

   ```bash
   V=skills/video-editor/scripts
   python3 $V/transcript_out.py "$PROJECT"        # transcript_out.md + words_out.json
   ```

3. **Look at the picture.** A labelled frame every 10 s (see [the scan](references/style-rules.md#scan)), then gridded full frames at every candidate moment. Measure the webcam box once and write it to `layout.cam`. Placement comes from pixels you have seen, never from guesses.
4. **Plan** `edit.json`: chapters first, then the moments that earn a card, spotlight or punch-in. Card text is the speaker's own words, trimmed. Every event has a `cue`, the words it lands on. For a short talking-head clip, draft the plan automatically and then review it:

   ```bash
   python3 $V/plan.py "$PROJECT" --base "$PROJECT/<cut>.mp4" --name <slug>   # presets/clean.json
   ```

   It prints the hooks, the marked word, drops, reframes and any flat stretch. Check the opening payoff is the word that matters, the closing payoff is a real payoff on a free side of the frame, the marked words are the key terms, ASR errors and brand names are fixed in `fixes`, and every flat stretch gets a beat.
5. **Check and preview**, fast, no video render:

   ```bash
   python3 $V/build_edit.py "$PROJECT/edit.json" check stills
   ```

   Read every `qa/stills/stills-sheet-*.jpg`. Fix wording, anchors and rects, rerun until the sheets are clean.
6. **Build everything:**

   ```bash
   python3 $V/build_edit.py "$PROJECT/edit.json"      # check, assets, audio, master, export, qa
   python3 $V/build_edit.py "$PROJECT/edit.json" assets master qa   # after a visual fix
   ```

   Only changed overlays re-render (hashes in `work/render-hashes.json`).
7. **QA.** Read `qa/report.md` and every `qa/master-sheet-*.jpg`. Pass means: 0 decode errors, duration equals the cut, loudness -14 ±1 LUFS, true peak at or under -1.5 dBFS, no black segments, every frame shows the card legible, off the face and matching the words. Fix and rebuild; stop after 3 passes and report what is left.
8. **Deliver.** Copy `out/<name>.mp4` into the upload folder the author uses (default `output/<date>-<slug>/`) and hand off to [youtube-description](../youtube-description/SKILL.md) (the Chapter cards are the chapter list). Give the author the `.fcpxml` path.

Optional audio and picture steps:

- A quiet mic with room noise: `scripts/voice_print.py <raw take> <edl.json> <out.wav>` learns a noise print from the longest silence and cuts it to the EDL; swap it in as the cut's audio and set `voice.clean` to `false`.
- One clip of a session graded by hand: `scripts/match_grade.py` learns that grade and bakes a `.cube` LUT for the other takes shot in the same light.

## Resolve handoff

In DaVinci Resolve (the free version is enough): File > Import > Timeline, pick `out/<name>.fcpxml` (fallback `out/<name>.otio`). Tracks:

| Track | Content |
| --- | --- |
| V1 | source clips, 1 per EDL range, every cut editable |
| V2 | zoom inserts; delete one to drop that zoom |
| V3+ | overlays, ProRes 4444 with straight alpha |
| A1 | source audio, raw (the master's voice clean-up is not applied here) |
| A2 | music stem, already ducked under the voice |
| A3+ | sound effects, 1 clip per hit |

Markers carry each event id and cue. The flattened master stays the reference; Resolve is for the author's hand edits. If an import breaks, note what broke and fix `scripts/export_timeline.py`.

## Hard rules

- Clean style (see the style rules): light type on the picture, no boxes, pills, highlights or pop animations.
- Graphics come only from the menu: Captions, Interlude, Lower, Stat, Keyword, List, Chapter, Media, Focus, Zoom. No improvised graphics.
- Sound effects exist only as a field of a visual event, and only from files the author has the rights to. No event, no sound.
- Show the real thing: Focus on the actual UI, Media with a real screenshot of the named repo, site or post. Never a stand-in.
- Words are the speaker's. Numbers only when spoken or on screen (add `source`), or from `identity/proof.md`.
- Never cover the webcam. A zoom keeps the webcam fully in or fully out.
- 1 card on screen at a time, at least 1 s apart.
- Never modify the source recordings. Synced folders (iCloud, Drive) may hold files offline; make sure the sources are local before a long render.

## Files

- `scripts/transcript_out.py` maps the transcript's words through `edl.json`.
- `scripts/plan.py` drafts `edit.json` for a talking-head clip from `presets/clean.json`.
- `scripts/build_edit.py` validates and builds; stages `check stills assets audio master export qa`.
- `scripts/export_timeline.py` writes `.fcpxml` and `.otio`.
- `scripts/voice_print.py` and `scripts/match_grade.py`: optional voice and grade helpers.
- `overlays/`: the Remotion graphics kit ([README](overlays/README.md)).
