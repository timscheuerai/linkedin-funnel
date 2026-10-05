---
name: longform-edit
description: Edit a long-form YouTube recording into a finished upload, usually a designed talking-head intro with proof graphics followed by a clean, clip-only screen tutorial. Use when a video needs more than a plain cut: an animated intro, numbers shown when they are said, or a few motion graphics.
---

Workspace: all context paths below (identity, audience, strategy, voice, brand, raw, output, index, log, workspace preferences and context scripts) resolve from `context/` in the kit root. Read both the root `AGENTS.md` and `context/AGENTS.md`. Skill-local `references/` resolve from this skill directory.

# Long-form YouTube edit

Make 1 finished upload from the author's recording. Decide the treatment from the brief and the footage before building graphics. The common case is a designed intro followed by a clip-only tutorial: read [references/intro-and-tutorial.md](references/intro-and-tutorial.md).

## Edit decisions

- Start with the spoken hook. Remove opening dead air and false starts. Map exact source ranges from the transcript, then inspect picture and sound at every join. Keep pauses where the viewer needs to follow on-screen actions.
- Design the talking-head intro with short phrase captions, authentic supporting visuals, small camera moves and a few purposeful motion graphics. Leave the screen tutorial clear: "only clip the tutorial" means cutting unwanted time and stutters, not adding captions, zooms or overlays.
- Show a proof number at the phrase that says it, with the real source (an analytics screenshot, a chart from real data). Match the number and wording to what the author says, and only use numbers from `identity/proof.md`. When the spoken number differs from the receipt, show the receipt's number and tell the author.
- A graphic supports 1 spoken idea, then leaves the frame.
- Sound follows visible events: a few quiet cues at most. No music unless the brief asks for it.

## Production and QA

1. Inspect the recording, transcript, frame rate and audio. Write a source-range cut plan (`talking-head-video-cut` for the plain cut).
2. Build the intro as an editable motion composition (HTML-based tools such as HyperFrames or Remotion work well with coding agents; see `launch-video` and `video-use`). Review frames at the start, every graphic entrance and exit, the last intro frame and the joins. A passing structural check does not catch a graphic that stays on screen after its beat.
3. Assemble the rendered intro with the cleanly cut body and outro. Inspect audio and picture across every cut, especially the camera-to-screen handoff.
4. Export H.264 and AAC at the source frame rate. Aim near -14 LUFS integrated and at or below -1.5 dBTP. Run a full decode check, confirm duration and streams, and review a contact sheet of the final file.
5. Keep the editable composition, the cut plan and the QA notes next to the final file. Title, description, thumbnail and upload are separate steps (`youtube-description`, `youtube-thumbnail`, `youtube-publisher`).
