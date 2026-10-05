---
name: talking-head-video-cut
description: Cut and merge raw OBS or screen-recorded talking-head clips by selecting complete takes, trimming dead air and setup transitions, preserving the native picture, and QAing every join. Use for "remove the pauses", "cut the false starts", "just cut and merge" or a clean long-form YouTube cut.
---

Workspace: all context paths below (identity, audience, strategy, voice, brand, raw, output, index, log, workspace preferences and context scripts) resolve from `context/` in the kit root. Read both the root `AGENTS.md` and `context/AGENTS.md`. Skill-local `references/` and `scripts/` resolve from this skill directory.

# Talking-head video cut

Produce a clean long-form edit from raw recordings without adding creative treatment nobody asked for.

## Default outcome

- Keep the best complete performance, usually the last attempt that finishes.
- Remove abandoned starts, long dead air and on-screen setup or search transitions.
- Preserve short natural breaths and the speaker's cadence.
- Keep the source resolution, frame rate, framing and colour.
- Add 30 ms audio fades at every cut, encode each kept segment once, then concatenate without another video encode.
- Deliver 1 clearly named MP4. Put working files in `<source-dir>/edit/<project-slug>/` and never modify the source recordings.

"Just cut and merge" approves this strategy. Ask only when the order or content selection cannot be inferred.

## Screen demos

For a screen demo with a webcam, "remove the tries at the beginning and cut the end" means: start on the first word of the final complete take and end about 150 ms after the sign-off. Turn pause removal off (`"min_seconds": 9999`): trimming silences while the speaker types or clicks makes the screen jump.

## Workflow

1. Inventory every named source with `ffprobe`. Use the user's order; with timestamped OBS files and no stated order, use recording order.
2. Transcribe only the named sources with word-level timestamps (see `video-use`; any word-timed transcript works). External transcription uploads audio to a provider; when that is not allowed, cut on acoustic pauses only.
3. Choose keep windows with [editorial-rules.md](references/editorial-rules.md). Use word starts for boundaries, about 60 ms before the first kept word and 150 ms after the last.
4. Mark deliberate drops silence cannot find: screen searches, spoken transition markers, failed restarts, repeated setup phrases.
5. Write `plan.json` with [plan-schema.md](references/plan-schema.md), then render:

   ```bash
   python3 skills/talking-head-video-cut/scripts/render_cut.py "$PROJECT/plan.json"
   ```

6. QA every join in the output timeline (the renderer writes `edl.json`): no black or single-frame flash, no clipped word, no click, no long dead air. Then decode and check the whole file:

   ```bash
   ffmpeg -v error -i "$FINAL" -f null -
   ffprobe -v error -show_entries format=duration,size:stream -of json "$FINAL"
   ffmpeg -hide_banner -nostats -i "$FINAL" -vf 'blackdetect=d=0.10:pix_th=0.05' -an -f null -
   ffmpeg -hide_banner -nostats -i "$FINAL" -af 'silencedetect=noise=-45dB:d=0.60' -f null -
   ```

   Inspect the opening, middle and ending frames. Fix and re-render when a join fails; stop after 3 passes and report what remains.

## Defaults

| Setting | Default |
| --- | --- |
| Silence threshold | -45 dB |
| Pause eligible for trimming | 600 ms or longer |
| Silence kept after a cut | 180 ms in total |
| First-word padding | 60 ms before |
| Last-word padding | 150 ms after |
| Video | H.264, CRF 18, preset medium, yuv420p |
| Audio | AAC 192 kbps, 48 kHz stereo |
| Cut-edge fade | 30 ms in and out |

No colour grading, captions, music, zooms, reframing or graphics unless requested; use `longform-edit` for a designed intro.

## Report

The delivered file, runtime, size, resolution and frame rate, what was removed and the QA result. Keep the transcript, plan, EDL and QA frames in the project folder.
