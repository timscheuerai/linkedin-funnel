---
name: shorts-edit
description: Turn raw talking-head recordings into finished shorts using reviewed take selection, audio, captions, cue-based graphics and final QA.
---

# Edit a short

Read the supplied brief and inspect the actual footage. Preserve source files. Establish the intended message, aspect ratio and target runtime; infer routine edit choices within the request.

Keep `raw/`, `transcripts/`, `edit/` and `renders/` inside the requested ignored output directory. Create an edit decision list with source file, start/end times, beat and reason. No prebuilt video pipeline is bundled.

Use `shorts-cut` for take selection, `shorts-audio` for audio treatment, and `shorts-motion` for useful graphics. Captions come from the final cut's words/timings, not stale source offsets. Keep names, numbers and units manually checked against the recording.

Prefer one final encode from preserved sources when practical. Cache generated/transcribed material with enough configuration to distinguish versions. Inspect installed tools before using their command grammar.

Run `shorts-qa` against the final artifact. Deliver the file, EDL/project, source-to-output map and verification results. A script that has not rendered successfully is not a completed edit.
