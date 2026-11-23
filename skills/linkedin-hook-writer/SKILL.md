---
name: linkedin-hook-writer
description: Write, revise or compare LinkedIn hooks in the author's voice, with measured character counts and mobile-first opening budgets. Use for hook options, first-line edits, or the opening pass inside linkedin-copywriter.
---

Workspace: all context paths below (identity, audience, strategy, voice, brand, raw, output, index, log, workspace preferences and context scripts) resolve from `context/` in the kit root. Read both the root `AGENTS.md` and `context/AGENTS.md`. Skill-local `scripts/` resolve from this skill directory.

# LinkedIn hook writer

Own the opening, including how it connects to the body. The full post's voice, facts and ending stay with `linkedin-copywriter`.

## Ground the hook

Read `voice/linkedin-voice.md` and the draft or factual brief. Identify the intended reader and the specific point the body supports. Check tone against the author's recent posts. Public numbers follow `identity/proof.md`.

The author's current instructions and wording come first. The first line can be a claim, question, confession, comparison, result, story detail or framework promise. No invented drama, no automatic "I" opener, no compulsory number.

## Hook families that work for founders

Before choosing a family, read what the author's own data says: a page on hook types and their measured lift, if `strategy/` has one, and their best-performing posts. Those usually point the same way: line 1 a big claim or result, line 2 says what follows or proves it.

- Result + "with this simple X": "I got a 51% reply rate with this simple sequence."
- Test or comparison: "I tested A vs B vs C" + a short stance on the next line.
- Big claim + "Here is how you can benefit".
- News + result: "<Tool> is out. Here is how we cut our costs by 72%."
- Confession + change: "I felt stuck and changed my rate from $200/h to $1k/h."
- Stakes: "Our biggest competitor just raised $100M." + "Here is how we try to survive."
- Before and after: "Last year I struggled with X." / "This year I built Y."
- Receipt as the promise: "<result> in <period> resulted in <outcome>."

Use the author's own numbers only. Avoid the "Everyone is doing X. Almost nobody says Y." opener; readers recognise it as AI copy.

A follow-up post on the same topic within a few days needs a different hook family, not the same receipt reworded. Open with another family (a status line such as "Claude Code is now my content team.") and move the receipt to line 2. The X version may keep the receipt first.

## Length: house targets, not platform limits

- **First line: aim for about 40 to 60 characters,** and under about 55 when it is a big claim or result. A stronger 35- or 85-character line can be right.
- **Essential opening: aim within 140 characters**, including spaces and newlines: usually the first line plus an informative second beat. Make line 1 meaningful on its own; do not hide the point after character 140.
- **1 empty line between the hook and the re-hook, always.** Line 1, an empty line, then line 2, never the 2 lines stacked. The empty line counts toward the 140 characters.
- **Inspect the first 210 characters** as an extra stress check.
- **The whole post has a 3'000-character limit.** Count the finished draft too.

The 140 and 210 figures are working budgets, not a published LinkedIn cutoff. Rendered wrapping, blank lines and viewport change the fold. Never claim a character slice is the exact feed preview.

## Shape and select

1. Identify the concrete point, why the reader cares and any real tension.
2. Draft or revise the opening. The second beat adds specificity, a consequence, a contrast or a clear promise. It does not repeat line 1.
3. For requested options, vary the angle, not the adjectives. Default to 3 only when options are asked for without a count; a full-post task needs 1 chosen hook.
4. Judge each candidate on clarity to a stranger, specificity, relevance, the author's voice and whether the body pays it off.
5. Run the counter on the exact chosen text and inspect the 140 and 210 slices. If a necessary word comes too late, move it earlier. Do not pad short hooks.

```bash
python3 skills/linkedin-hook-writer/scripts/check_hook.py draft.txt
# Or pipe the plain-text draft to the same command.
```

The counter measures Unicode code points, reports UTF-16 units for emoji-heavy text and preserves whitespace. Its slices are text checks, not a simulation of LinkedIn's layout.

## Return

For a hook-only request, return the selected opening with the counts for line 1 and the opening block. If options were requested, mark the recommended one and say why in 1 line. Keep counts outside the copy. Run every hook option through the slop pass in `linkedin-copywriter` before returning it. When called by `linkedin-copywriter` or `week-posts`, use the chosen opening in the draft and keep routine diagnostics internal.
