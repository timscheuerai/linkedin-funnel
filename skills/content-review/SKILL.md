---
name: content-review
description: Review the author's published content, platform performance and production workflow, then turn the evidence into the next experiment. Use for a YouTube review, a content retrospective, why a piece underperformed, the close of a content waterfall or a review across platforms. YouTube has the detailed collection workflow; LinkedIn, X and newsletters share the review framework. For researching the next video, use youtube-video-research.
---

Workspace: all context paths below (identity, audience, strategy, voice, brand, raw, research, output, index, log, workspace preferences and context scripts) resolve from `context/` in the kit root. Read both the root `AGENTS.md` and `context/AGENTS.md`. Skill-local `references/` resolve from this skill directory.

# Content review

Review the whole path: audience need, idea, packaging, opening, delivery, distribution, response, product outcome and production effort. Explain where the evidence points and what to change next. The output is a decision, not a list of metrics or an automatic rewrite of the author's content strategy.

## Choose the review

Use the platform, account, piece and dates the user supplied. Without a platform, start with YouTube. Without dates, review the last 28 days plus the previous comparable period. If there are few uploads, include recent older pieces and label the expanded window. A single-video request stays a single-video review, with relevant channel context.

For YouTube, read [references/youtube.md](references/youtube.md). It holds the collection layers, comparison rules and diagnostic checks.

For an all-platform request or a waterfall close, use the shared framework below for each platform that has evidence, then review the waterfall as a whole. Say which platforms were actually inspected. Other platforms use discovered read capabilities or provided exports, not a claimed complete integration.

| Platform | Keep its native context |
|---|---|
| YouTube | Long-form, Shorts and live separately; impression source, package, retention, next action |
| LinkedIn | Personal/company, organic/paid and format separately; reach, substantive response, resource requests and product outcomes |
| X | Originals, replies, threads, Articles and paid separately; distribution, profile/link actions and useful conversations |
| Newsletter | Delivered audience, clicks, replies, unsubscribes and product outcomes; opens may be distorted by privacy protection |
| Other | Discover the native definitions and available account evidence before choosing metrics |

Never add platform view definitions into a total unique audience. A shared campaign identifies a waterfall, not necessarily an individual post.

## Ground and collect

Read the relevant parts of `index.md`, `identity/positioning.md`, `audience/ideal-follower.md`, `strategy/funnel.md`, `strategy/goals.md`, any performance baselines the author keeps in `strategy/`, and the voice guide. Search with `qmd` where available. Read the previous review and any experiment due for a result. Use the waterfall's UTM campaign to interpret signups. The author's content audience and their product's buyer profile can differ; if buyer-fit evidence is absent, leave buyer fit unknown.

Prefer live native account reads, then dated native exports, then existing snapshots. Public counters and secondary summaries help but cannot replace owner analytics or direct inspection. Verify account identity, timezone, window and access before drawing conclusions. A registered tool or stored token does not prove access to this account's analytics.

For each piece keep its ID/URL, format, publication and observation dates, goal (Reach, Belief or Signup), source and metric window. Record a coverage table: available, stale, denied, unavailable or not applicable. Missing is not zero. If a field is blocked, continue with supported findings and name the smallest missing input that would resolve it; do not stall the whole review.

Collect first, then diagnose. Preserve new captures under a fresh dated `raw/sources/` folder with a manifest (`templates/manifest.md`): account, time, filters, source URLs or export names, and limits. Keep secrets and identifiable customer data out of committed evidence. A transcript is not required to review counters, but content you could not access cannot get an audiovisual craft verdict. Label description-only or secondary analysis clearly.

## Make the review useful

Use [references/report.md](references/report.md) as the report shape, scaled to the request. For each material finding give the evidence, confidence, alternative explanation, practical change and next observation.

Review these lenses together:

- **Audience and idea:** the viewer's problem, intended funnel job, personal relevance and demonstrated demand. Views alone do not prove buyer fit.
- **Promise and delivery:** title, hook and visual agreement, speed to proof, clarity and the moment the viewer gets the promised result.
- **Distribution and response:** native exposure and response against a comparable baseline; tell genuine questions apart from giveaway requests.
- **Product outcome:** attributed visits, signups, agreed activation and paid conversion where observable. Keep first-touch, assisted and self-reported influence separate. A Reach piece is not a failure merely for having no directly attributed sale.
- **Production effort:** actual creator time, agent runtime, waits, revisions and recording-to-publication delay. Compare with the plan; do not invent hours saved because an automation exists.

Separate measured facts, supported interpretations and hypotheses. Compare like with like; show sample size and age. Do not turn one winner, an LLM score or an empty local log into proof of a universal rule or a missing capability. Keep inconclusive tests inconclusive.

End with the most consequential constraint, what to keep and a small set of experiments the next content cycle can actually run. Each experiment needs a hypothesis, a changed variable, the intended goal and metric, a comparison, a review point and a keep/change/inconclusive rule. Where practical, change 1 variable; when comparing complete packages, limit the conclusion to the package. Do not make up numeric success thresholds without a baseline. Pick 1 experiment for the next week's brief.

## Close the loop

In a repo-backed review, save the report to `research/reviews/YYYY-MM-DD-<platform-or-waterfall>.md` from `templates/page.md`, with Source Notes. Check every public result the report quotes (signups, revenue, followers, impressions) against the cleared figures in `identity/proof.md` and label any other figure as internal. Update the matching performance page or experiment log only when new evidence actually resolves a result. Add the report to `index.md` and append to `log.md`. Reuse these locations, not a second content database; working content and publication status stay on the board and the scheduler.

Propose concrete prompt or skill edits when warranted; apply them only when the user asked for those changes. A review can record evidence and learnings without changing approved creative preferences. The next brief cites the selected experiment and the previous result. Route video ideation to `youtube-video-research`, packaging to `youtube-title-outlier-packaging` and `youtube-thumbnail`, and production to `content-waterfall`.

When local scripts, browser access or repository writes are unavailable, return the report and the missing-data request in chat; do not pretend files or ledgers were updated.

A review is read-only on external platforms. It does not change live titles, thumbnails, posts, campaigns, messages or schedules. A concrete follow-up still needs the user's go. This skill does not schedule recurring reviews or grant spending authority.
