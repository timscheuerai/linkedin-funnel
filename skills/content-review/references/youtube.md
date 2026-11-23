# YouTube review

Read this for a channel review, a video retrospective or the YouTube part of a waterfall review. Start from the channel ledger that `youtube-video-research` keeps (1 row per upload), any YouTube performance notes in `strategy/`, and the title and thumbnail test log kept by `youtube-thumbnail`.

## Collect in layers

### 1. Public channel snapshot

The public YouTube Data API reads video metadata and public counters. It does not expose private Studio analytics. Confirm the channel is the one requested before reading. A configured OAuth grant can read public videos without proving it owns the author's channel.

Public reads publish nothing. Save each snapshot under a new dated file and never overwrite existing raw evidence; do not rerun only because analytics are missing. Write a manifest for the new observation and reference the exact file.

Inventory Shorts and lives separately from long-form; a missing ledger row is not proof that nothing was published. Lifetime views per day are not first-7-day performance or a measured current rate.

### 2. Owner analytics and experiment results

Check already-connected owner analytics first. If they do not provide the needed fields, use YouTube Studio in the author's existing signed-in browser (whichever browser tool is available) or a Studio export they provide. If sign-in or owner consent is needed, report that exact gap and continue with the public review. Never expand OAuth scopes or claim an uploader grant owns another channel.

Owner-authorized Analytics and Reporting APIs can be used when actually available. Discover the currently supported reports rather than assuming every Studio field exists in every API.

For the reviewed videos, look for:

| Evidence | Record with it |
|---|---|
| Impressions and native impression CTR | Date range, traffic source and denominator; all video views are not impression-derived clicks |
| Views, watch time, average view duration and percentage viewed | Video length, format and same-age window |
| Retention at 0:30 and 1:00 and material dips or spikes | Actual curve, timestamps and audience segment if available; not applicable for shorter content |
| Browse, suggested, search and external traffic | Shares or counts, source-specific performance and search terms when exposed |
| Returning and new viewers, subscribers gained | Native scope; channel-level evidence must not be assigned to a single video |
| Title and thumbnail test | Exact packages, dates, status, native result and watch-time share; keep no-winner and insufficient-data results |
| Changes after publication | What changed, when, and which metric windows include both versions |

Impression CTR does not cover every source of views. Keep the native number rather than dividing total views by impressions. A title and thumbnail changed together test their combined package. Read a completed native test result rather than declaring a winner from aggregate views.

### 3. What the viewer actually saw

Inspect the published package and the footage you can access. Use the transcript to locate claims and timings, not to infer unseen visuals or audio quality. For long-form, inspect the opening, the first real proof, any major retention events and the closing next action. For a deep craft review inspect the whole piece; otherwise say which segments were inspected.

Check whether the promised outcome appears early, what the viewer has to understand first, screen legibility, audio clarity, filler, demonstration failures and the usefulness of the final action. Cite actual timestamps. Connect retention events to observations as hypotheses: a dip may be a skip, not an exit caused by that sentence. Keep the author's established style preferences unless they change them.

### 4. Product outcomes and production

Use the video's actual links and its UTM campaign to identify signups by source and campaign. That is not automatically a per-video activation or paid-conversion report; find the matching read for those outcomes.

A campaign shared across a waterfall's pieces measures the waterfall. Use piece identifiers or link content tags only where captured; never split a campaign total among videos by view share. Count activated and paid accounts on their declared entity and window, apart from user signup totals. Without attribution, mark unknown; zero tracked conversions does not prove zero influence.

Read production facts from the brief, edit and handoff records and the author's stated time. Separate human work, render or agent runtime and waiting. Check whether the asset was ready before recording, whether promise changes caused reshoots and whether approval or upload handoffs delayed publication. Without a time baseline, propose collecting one next cycle.

## Compare without fooling yourself

Use the same format, comparable length, goal, source mix and publication age. For long-form, default to first-7-day outcomes where both videos have that window; D+1 and D+3 are early checkpoints and D+28 a later follow-up. Use all recent comparable uploads and exclude the evaluated video from its own median. Show cohort size and exclusions. A sparse cohort supports a tentative read, not a stable benchmark.

Do not compare a 2-day-old video's lifetime views with a 6-month-old video's. If only public counters exist, describe the age mismatch and limit the conclusions. Subscriber-normalized ratios and channel outliers are context, not measured CTR or causal tests.

## Diagnose the constraint

| Pattern, against a comparable baseline | Candidate explanation | Next useful check |
|---|---|---|
| Low exposure, healthy response among viewers | Narrow topic, distribution or audience size | Source mix, search demand, coverage and impressions |
| Healthy exposure, weak CTR | Unclear or weakly relevant promise or package | The exact title and thumbnail pair in a competing feed; source-specific CTR |
| Healthy clicks, weak early retention | Promise mismatch, late proof or opening friction | Opening footage against the title promise and the curve |
| Strong opening, later watch loss | Pacing, clarity or viewers skipping to an answer | Timestamped footage, chapters and retention context |
| Useful viewing, little tracked next action | CTA, resource fit or attribution gap | Actual links, clicks, viewer goal and conversion path |
| Signups, weak activation | Resource-to-product handoff or product friction | The agreed activation event and cohort, not another thumbnail |
| Good result, too much creator effort | Rework, asset readiness or handoff friction | Stage time and revisions before choosing an automation |

These are diagnostic hypotheses. Without the distinguishing metrics, say which alternatives remain open instead of choosing a confident cause.

## Write back precisely

Add owner metrics with their dates and windows; do not put all-time values into a first-7-day table. Record test closeout in the existing thumbnail test log, including native inconclusive results. Update performance notes only to the strength of the new evidence and link the dated review. Do not relabel small-sample hypotheses as proven rules.

## Metric and access references

Use current official definitions when an integration or interpretation is uncertain:

- [Owner-authorized channel reports](https://developers.google.com/youtube/analytics/channel_reports): owner analytics require authorization for the requested channel.
- [Reporting metric definitions](https://developers.google.com/youtube/reporting/v1/reports/metrics): native impression CTR and watch-duration definitions. Reporting field names are not interchangeable with Analytics API fields.
