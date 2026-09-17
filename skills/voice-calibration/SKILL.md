---
name: voice-calibration
description: Build or refine an author's writing guide from their own writing samples and edits, without importing another creator's voice.
---

Workspace: all context paths below (identity, audience, strategy, voice, brand, raw, output, index, log, workspace preferences and context scripts) resolve from `context/` in the kit root. Read both the root `AGENTS.md` and `context/AGENTS.md`. Skill-local `references/` and flowchart `scripts/` resolve from this skill directory.


# Calibrate the voice

Read `AGENTS.md`, `voice/linkedin-voice.md`, relevant identity and audience pages, and the source samples. Capture new sources through `capture-context` when needed.

Separate writing authored by the person, transcripts of speech, approved ghostwritten posts, rejected drafts and external inspiration. Human edits show preferences; engagement numbers show outcomes, not who wrote a sentence.

## Derive rules from examples

Use several representative samples when available. One sample supports tentative observations, not a universal style. Record the limits of the evidence.

Look for recurring choices in opening lines, sentence rhythm, paragraph length, vocabulary, punctuation, specificity, argument structure and endings. Quote short illustrative passages with source paths. Preserve meaningful irregularities instead of making the voice more polished by default.

Write observed rules in `voice/linkedin-voice.md` and format choices in `voice/formats.md`. Distinguish consistent patterns from context-dependent choices. Do not hard-code a dialect, numeric separator, slang quota, hook length or CTA frequency from this template.

## Calibrate with an actual draft

When drafting is requested, use a supplied, public-use source to write a short sample. Give the author a concrete passage to edit. File their actual corrections as evidence, then update the few rules the corrections support. Do not label your own imitation approved.

If writing samples are missing, collect them or produce a clearly labeled neutral draft when that is useful and requested. Do not claim to reproduce a specific voice from a biography alone.

Update source notes, index and log; run `scripts/wiki-lint.sh`. Return the guide and any unresolved voice choices.
