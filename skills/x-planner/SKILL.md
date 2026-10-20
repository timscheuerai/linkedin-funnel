---
name: x-planner
description: Plan the author's X posts together with them, day by day, from 3 lanes: LinkedIn posts repurposed for X, native posts from what is going viral in their niche, and their own launches or assets. Presents a slate for the author to pick and cut, drafts the picks, records their verdicts. Use when planning X for the week or when the content waterfall hands over micro posts and chapter threads.
---

Workspace: all context paths below (identity, audience, strategy, voice, brand, raw, output, index, log, workspace preferences and context scripts) resolve from `context/` in the kit root. Read both the root `AGENTS.md` and `context/AGENTS.md`. Skill-local `references/` resolve from this skill directory.

# X planner

X gets its own planning session, made together with the author. The content waterfall owns 2 X pieces per video: the video post and the X Article. Everything else on X comes from here, including the waterfall's micro posts and chapter threads. Replies under other people's posts come from `x-engage`, not from here.

## The session

1. **Window.** Default the next 7 days. Read every planned piece in the window (all platforms), so X fits the week and nothing doubles.
2. **Gather the 3 lanes** below.
3. **Show the slate.** 1 table per day with about 1.5 times as many candidates as slots, so the author can cut:

   | Day | Lane | Angle | First line | Asset | Source |
   |---|---|---|---|---|---|

   Write the first line in full; the rest is 1 line. Mark your pick per day; the choice is the author's.
4. **The author picks, cuts and edits.** Keep their words verbatim.
5. **Draft the picks** (see "Writing for X").
6. **Save** each pick to the board (`strategy/notion-schema.md`) when Notion is configured, otherwise return them in chat.
7. **Schedule** only on the author's go.
8. **Learn.** Add what the author picked and cut, with the reason, to `references/verdicts.md`. The next slate starts from those verdicts.

When the author says they are overwhelmed but want to post today, skip the slate: hand over 1 finished post, ready to paste.

## What usually works

Measure the author's own X posts before assuming. Building in public often carries a founder's X: their own number, milestone, decision or mistake first, the lesson after. A how-to becomes "what we did and what it did"; a trend take becomes "what happened when we tried it". Posts with media usually beat posts without. Record what the author's numbers actually show in `references/verdicts.md`.

## Lane A: LinkedIn to X

Pick recent LinkedIn posts with 1 sharp point from the author's own experience: a result, a mistake and the rule it produced, a decision. Carry the point, not the LinkedIn shape. A repurpose can keep the LinkedIn hook verbatim and get to the point right after it. Default: the X version goes out the day after the LinkedIn post. The author may swap the LinkedIn hook for their own X line; keep it verbatim, and tag products and people by their real, verified handles.

Comment-to-DM resources often do far worse on X than on LinkedIn; measure them before planning more. When the author still wants one, the post stands alone (no counts from LinkedIn, no "now on X too"), the CTA is "1) Follow me 2) Comment "<KEYWORD>"" with the files sent by DM, and the visual keeps its 2-step CTA box with "Follow" in place of LinkedIn's "Connect". Never just crop the CTA off.

## Lane B: native X, from what is going viral

Search the last 7 days in the author's niche (X search, X Radar on X Premium, or a research tool). Keep posts that did unusually well for their author and sit in the author's lanes. The angle is always the author's own contribution: their receipt, their disagreement, how they do it. Never copy a post or present someone else's result as theirs. Check any news claim at its source before it goes in the slate. State any paid search spend before running it.

## Lane C: launches and assets

Product launches, videos, graphics and resources the author wants out. Ask once per session which are in the pipeline and in which order. Check what already went out so nothing posts twice. Captions describe what the viewer gets, in the product's own words, without hype adjectives.

## Writing for X

- The author's voice from `voice/linkedin-voice.md` and their recent X posts, in X's shape: 1 point per post, the point in the first line, short.
- Anti-slop on X: no role verbs ("orchestrates", "routes the work"), no "Label: description" bullets, no "Bonus:". Bullets are fine; the slop is labels and role verbs. Write a stack as tools with jobs ("Claude Code + Codex to do the work") and a process as first-person actions with plain verbs. Check the rule against posts from creators the author follows.
- A video post with a strong receipt leads with the receipt in the author's rounding; the claim comes second.
- A thread only when the material needs steps.
- Keep the operator detail that makes it theirs: the tool, the number, the mistake. Cut the rest.
- Final read: would this post stand on its own without the LinkedIn post or the video? If not, cut it or fix it.
- Numerals, numbers only from `identity/proof.md`, no em dashes, full YouTube URLs only.
- Links to the author's own site carry UTM parameters with the `x` source, also on a repurposed LinkedIn post.
