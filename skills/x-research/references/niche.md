# Niche and content brief

## Audience and selection

Start from `audience/ideal-follower.md` and `identity/positioning.md`: who the author writes for, what that audience is trying to achieve and what blocks them. That is the research lens, not a new taxonomy. Map each of the author's pillars from `strategy/pillars.md` to what to look for and what the author could add:

| Pillar (from `strategy/pillars.md`) | Look for | The author's possible contribution |
|---|---|---|
| <pillar 1> | <the audience problems and conversations this pillar answers> | <a mechanism, receipt or decision the author can show> |
| <pillar 2> | ... | ... |

Example for an author whose audience is B2B founders who want pipeline: a "GTM engineering" pillar looks for posts about ICP qualification, enrichment and outbound systems, and the author's contribution is a working mechanism with its tradeoffs. A "building in public" pillar looks for launches, pricing and onboarding decisions, and the author's contribution is their own dated receipts.

For a weekly cross-pillar scan, cover every pillar without forcing a low-signal pillar to meet a popularity threshold.

## Query seeds

Use the requested topic first. Build 6 to 10 seeds from the pillar table: the audience's problem in their own words, the tools they use, and the outcomes they want. These examples fit X API recent-search syntax; adjust after reading current schemas. Do not run every seed automatically.

| Intent | Example query (B2B founder example) |
|---|---|
| Core topic | `"GTM engineering" -is:retweet -is:reply lang:en` |
| A buyer problem | `("founder led" OR "founder-led") (distribution OR sales) -is:retweet lang:en` |
| A tool in use | `("Claude Code" OR Codex) (sales OR marketing OR onboarding) -is:retweet -is:reply lang:en` |
| Failure and lessons | `("cold email" OR outbound) (mistake OR failed OR lesson) -is:retweet -is:reply lang:en` |
| Company decisions | `("building in public") (pricing OR signups OR churn) -is:retweet -is:reply lang:en` |

Noise exclusions such as `-giveaway` are responses to actual noise, not defaults. Do not exclude all resource offers: a useful lead magnet in the niche may fit. Broaden queries that return too little and narrow generic commentary.

Use `from:<author handle> -is:retweet` for the author's recent X history. Build a creator watchlist from verified relevant posts and the author's choices. No inherited lists, assumed relationships or automatic follows.

## What makes a useful candidate

- Direct relevance to the audience's problem or goal.
- A workflow, demo, candid decision, resource, experiment or specific objection.
- A distinct contribution the author can substantiate; source popularity alone is weak.
- Engagement in context. Keep modest-reach posts when they show a real buyer problem.
- Replies that add information; inspect them before inferring sentiment from counts.

Reject irrelevant celebrity reach, empty hot takes, copied anecdotes and unverified outcome claims. Derive ideas and formats without copying distinctive phrasing or presenting other people's screenshots or results as the author's own.

## Brief handoff

Use a compact table or prose, whichever suits the request:

| Field | Content |
|---|---|
| Source | Canonical post link, handle and publication date |
| Evidence | Observed likes, bookmarks, replies, reposts, views if present; capture time |
| Why study it | Audience problem and a hypothesis about what drew attention |
| The author's angle | The specific point they can add from their work |
| Grounding | Local receipt or source path, or an explicit evidence gap |
| Placement | Existing pillar and exactly 1 funnel stage |
| Asset | Existing GIF, diagram, screenshot, repo or none |

Keep borrowed research evidence and the author's own proof separate. Public metrics are observations, not a claim that attention created signups or revenue. Use `identity/proof.md` and current figures the author supplies and approves. Keep qualifiers and time windows.
