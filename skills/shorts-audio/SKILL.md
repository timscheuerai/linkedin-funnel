---
name: shorts-audio
description: Improve recorded speech using measured levels, restrained noise treatment and listening comparisons against the source.
---

# Treat the actual audio problem

Listen to the original and measure sample rate, channels, loudness and peaks with the available audio tooling. Identify noise, clipping, uneven delivery, room tone or low level separately. Increasing level is not denoising.

Start with the smallest useful change. A constant gain preserves dynamics when headroom allows. If compression or limiting is needed, make it deliberate and listen for pumping, clipped consonants and lost room tone. Inspect current filter help; a requested linear mode may have constraints.

For noise reduction, use representative silence and compare speech before/after at matched loudness. Reject settings that create burbling or remove the speaker's texture. Do not prescribe a universal denoiser or fixed gain from another recording.

Apply channel conversion, EQ, dynamics and final level in an intentional order. Check the final mix including music and sound effects, especially overlapping peaks and mono/stereo changes.

Measure and listen to the encoded artifact, not just the intermediate PCM. Report the actual treatment, output measurements and audible tradeoffs. Use `shorts-qa` for the combined video/audio deliverable.
