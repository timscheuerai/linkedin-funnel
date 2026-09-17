---
name: shorts-qa
description: Verify an edited video for complete speech, correct captions, synchronized graphics, audio integrity, image quality and playback.
---

# Verify the final export

Inspect the final encoded artifact against its source and edit plan. No automated seven-check harness is bundled; run available measurements and report what each actually checked.

| Check | Evidence |
|---|---|
| Cuts | Listen to every join; complete words and coherent meaning |
| Captions | Check names/numbers, short words, timing, line breaks and crop |
| Motion | Compare cue/payoff timing while playing audio; inspect overlaps |
| Image | Compare aligned source/output frames outside intentional effects |
| Audio | Listen at matched level; measure peaks/loudness and channel layout |
| Playback | Decode the whole file and open it in the target player when available |
| Pacing | Review the whole story; no duplicate takes or unexplained gaps |

For frame comparisons, align source and output and exclude intended overlays/crops before interpreting quality scores. A threshold from another clip is not universal. Use per-run temporary directories so measurements cannot mix artifacts.

A failed check needs a location, observed defect and fix. Re-check affected portions after correction, then confirm the final file corresponds to the reviewed version. A JSON parse or renderer exit code cannot prove visual/audio quality.

Deliver a short report distinguishing measured, manually inspected and unverified checks. Do not claim a passed gate when the measurement tool or playback inspection was unavailable.
