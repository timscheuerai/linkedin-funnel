---
name: shorts-cut
description: Select complete takes and remove false starts or dead air while preserving speech meaning and word boundaries.
---

# Choose the usable performance

Read the full transcript and inspect/listen to candidate ranges. Determine whether repeats are retakes or intentional emphasis. The last *complete* attempt is a useful preference for retake-heavy footage; the strongest coherent take wins when the brief or performance supports it.

For each beat, record source, in/out times and the reason for choosing that range. Reject unfinished fragments even when they occur last. Retakes can happen inside a phrase; inspect at word level.

ASR timing is a starting point. Listen around every proposed cut so consonants and breath are not clipped. Remove unnecessary silence inside a take only when pacing improves; preserve intentional pauses.

Build the EDL from source time and derive output positions cumulatively. After changing the cut, regenerate downstream timing maps and captions. Do not hand-maintain two conflicting timelines.

Render or play every join in context. Return the selected ranges, rejected alternatives where useful, final duration and any uncertain transcription. Use `shorts-qa` for the completed output.
