---
name: x-planner
description: Plan the author's X posts together with them, day by day, from 3 lanes (LinkedIn posts repurposed for X, native posts from what is going viral in their niche, and their own launches, videos and assets). Presents a slate for the author to pick and cut, drafts the picks with x-copywriter, puts them on the board, schedules on their go and records their verdicts. Use when planning X for the week, when the author wants X posts from LinkedIn posts, trends or videos, or when the content waterfall hands over micro posts and chapter threads.
---

Workspace: all context paths below (identity, audience, strategy, voice, brand, raw, output, index, log, workspace preferences and context scripts) resolve from `context/` in the kit root. Read both the root `AGENTS.md` and `context/AGENTS.md`. Skill-local `references/` resolve from this skill directory.

# X planner

X gets its own planning session, made together with the author. Generic derivatives of a video (a lesson post, a proof clip, a resource post) rarely stand on their own, so the content waterfall owns only 2 X pieces per video: the video post and the X Article. Everything else on X comes from here, including the waterfall's micro posts and chapter threads. Replies under other people's posts come from `x-engage`, not from here.

## The session

1. **Window.** Default the next 7 days. Read every planned piece in the window (all platforms), so X fits the week and nothing doubles.
2. **Gather the 3 lanes** below. Read `references/verdicts.md` first: the slate starts from the author's verdicts, newest at the bottom. Run the X scan in a background agent while you read the board and the asset pipeline.
3. **Show the slate.** 1 table per day with about 1.5 times as many candidates as slots, so the author can cut:

   | Day | Lane | Angle | First line | Asset | Source |
   |---|---|---|---|---|---|

   Write the first line in full; the rest is 1 line. Mark your pick per day; the choice is the author's. Offer 1 high-value thread per slate when the week has material for it.
4. **The author picks, cuts and edits.** Keep their words verbatim. Ask nothing else until they have picked. A slate line without the author's own receipt usually reads as slop; ask for or take their number and angle.
5. **Draft the picks** with `x-copywriter` (see "Writing for X").
6. **Save** each pick to the board (see "Board") when Notion is configured, otherwise return them in chat.
7. **Schedule** only on the author's go (see "Schedule").
8. **Learn.** Add what the author picked and cut, with the reason, to `references/verdicts.md`. The next slate starts from those verdicts.

When the author says they are overwhelmed but want to post today, skip the slate: hand over 1 finished post, ready to paste. When they hand over the pick ("schedule the 3 best"), schedule the drafts whose numbers they already said in public and keep the ones that wait on their input on the plan page.

## What usually works

Measure the author's own X posts before assuming, and refresh the read every 2 weeks (their scheduler's analytics export or X analytics), saved as a dated note. What often holds for founders:

- Building in public carries their X: their own number, milestone, decision or mistake first, the lesson after. A how-to becomes "what we did and what it did"; a trend take becomes "what happened when we tried it".
- Introductions with receipts, tagged lists of people to learn from, connect posts and milestones with short steps do well. LinkedIn frameworks pasted as they are do poorly.
- High-value threads (a full system, the author's receipts, nothing held back) earn far more bookmarks than the same topic as 1 post. Bookmarks are the value signal.
- Posts with media usually beat posts without.

Record what the author's numbers actually show in `references/verdicts.md`.

## Daily shape (default, the author changes it)

- Agree a daily KPI with the author (for example 2 posts a day) and plan the slots from it.
- 1 building-in-public post a day; lanes A and B feed it.
- Launch or demo videos on a set rhythm while the pipeline has them (for example every 2 days).
- A LinkedIn repurpose or native post only when it carries the author's own receipt; questions and polls rarely.
- Attach media where there is any: a photo, a screenshot, the graphic, the video.
- On a video's release day, its video post and X Article come from the waterfall; add nothing else that day unless the author asks.

## Lane A: LinkedIn to X

- Read the LinkedIn posts planned for the window and the last 14 days, with their copy. A card without copy cannot be adapted; skip it.
- Pick posts with 1 sharp point from the author's own experience: a result, a mistake and the rule it produced, a decision.
- Write every repurpose with `x-copywriter`: the author's LinkedIn writing in their own words, which may keep the LinkedIn hook, then straight to the examples or the list. Rebuild line 1 around 1 fresh receipt only when the author asks for "X native". The post ends on the last step or fact, never on an engagement question.
- Default timing: the X version goes out the day after the LinkedIn post, so LinkedIn stays first, or as a second channel of the same post (see "Schedule").
- The author may swap the LinkedIn hook for their own X line; keep it verbatim, and tag products and people by their real, verified handles.
- Comment-to-DM resources can work on X when the author wants them: the post stands alone (no LinkedIn counts, no "now on X too"), the CTA is "1) Follow me 2) Comment "<KEYWORD>"" with the files sent by DM, and the visual keeps its 2-step CTA box with "Follow" in place of LinkedIn's "Connect". Never just crop the CTA off. Measure gated posts and record the result.

## Lane B: native X, from what is going viral

Use `x-research` (X search, X Radar on X Premium, or a research tool) on the last 7 days in the author's niche, 2 to 3 bounded searches. Keep posts that did unusually well for their author and sit in the author's lanes. The angle is always the author's own contribution: their receipt, their disagreement, how they do it. Quote the post when the conversation is the value; write an original post when the author has their own take. Never copy a post or present someone else's result as theirs. Check any news claim at its source before it goes in the slate. State any paid search spend in the slate and get the author's OK before live calls; saved results and links the author sends cost nothing.

## Lane C: launches, videos and assets

- Product launches, launch or demo videos, graphics, shorts and resources the author wants out. Ask once per session which are in the pipeline and in which order, and write the order in the plan page. Do not guess which ones they approved.
- Check what already went out so nothing posts twice. Third-party or real-person footage without rights stays in drafts.
- Captions are 1 or 2 lines: what the viewer gets, in the product's own words from its live site, plus what this piece is about. No hype adjectives. A native video post is a short announcement; the video carries the explanation.
- The post carries the video natively, uploaded to the scheduler, never as a link alone.

## Writing for X

- Draft every post with `x-copywriter`: the author's own writing, line 1 with a number, line 2 that proves it, short lines, `→` lists, their texture, no closing question. A post the author wrote themselves goes out exactly as written.
- 1 point per post, the point in the first line. Keep the operator detail that makes it theirs (the tool, the number, the mistake). Cut the rest.
- Final read: would this post stand on its own without the LinkedIn post or the video? If not, cut it or fix it.
- Numerals, numbers only from `identity/proof.md`, no em dashes, full YouTube URLs only.
- Links to the author's own site carry UTM parameters with the `x` source, also on a repurposed LinkedIn post.

## Board

With Notion configured (`strategy/notion-schema.md`), each pick is a card: Name `X: <angle>`, Platform `X`, Status once drafted, Pillar, Publish date, and the copy in the body as 1 `text` code block. Link it with `Parent post` when it has a source card: the LinkedIn post it repurposes, or the video it belongs to. Native posts and launch videos have no parent. Verify a reused source card belongs to the current board before linking it.

Asset paths, scan links and spend go in a plan page, not on the card: `output/<YYYY-MM-DD>-x-week.md` with the slate, the author's picks and cuts and the asset order.

## Schedule

Only on the author's go, through OXYGEN Publishing (`oxygen-linkedin-marketing`) or the platform's own scheduler. Check the X connection first. Keep the status truthful: drafted until live, then published.

**1 piece, 1 post.** When the same piece goes out on more than 1 platform (LinkedIn and X, plus Instagram or YouTube for a short), it is 1 scheduled post with 1 channel per platform where the scheduler supports grouping, each channel with its own copy and media, the same upload reused. A grouped post has 1 publish time, so choose it for LinkedIn first; the X channel follows. Every channel stays unapproved until the author approves it. If the scheduler cannot group posts that already exist, delete the unapproved extra and recreate it as a channel of the first. Shorts follow the same rule in `shortform-platform-copy`.

When the author hands over points without naming the platform, ask or check where the piece is meant to go before queuing it.
