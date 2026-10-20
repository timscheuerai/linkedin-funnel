# X creator watchlist and engagement queue

A watchlist of peers in the niche and a queue of their posts worth replying to. Keep the working state in one place the author chooses: an OXYGEN Table when they use OXYGEN, a Notion database when Notion is configured (`strategy/notion-schema.md`), otherwise a local file in `research/`. Record table or database IDs in ignored local configuration (`workspace.local.json` or `.oxygen/`), never in this public template. Never silently create the list in another workspace.

## Suggested columns

| List | Key for deduplication | Useful columns |
|---|---|---|
| Creator watchlist | normalized `handle` | name, followers, lane (which pillar), cohort (peer or specialist), reply evidence, reply URL, tools mentioned, status, notes |
| Engagement queue | `post_id`, stored as text | post URL, author, published at, observed metrics, capture time, why it fits, the author's angle, grounding, status (`To review`, `Replied`, `Skipped`), notes |

## Who belongs on the watchlist

Ask the author for the follower range they want to engage with. Peers a little ahead of the author usually beat the largest accounts: they reply, and their audience overlaps. Prioritize people who take part in conversations and share implementations, lessons, diagnostics and first-person work. A keyword mention, follower band, generic tool list, claimed revenue number or lead-magnet CTA is not enough on its own. Results the creators state remain their claims unless separately verified. Keep smaller specialists as a separate cohort.

`reply evidence` records an observed recent reply to another user. A short acknowledgement counts as observed, not as proof of thoughtful reciprocity. No observed reply means limited sample coverage, not that the creator never replies. Tool mentions come from sampled posts, not the creator's complete stack. Being on the list means suggested for the watchlist, not followed; do not infer friendship or intent to buy from inclusion.

## Refresh method

1. Read the working watchlist and queue. Preserve the author's additions, exclusions, priorities, notes and completed statuses. Re-read immediately before writes. Treat rows removed by the author as exclusions; update existing rows by row ID so an old snapshot cannot restore a removed account.
2. Resolve handles against live X identities. Old handles and similar names are not sufficient.
3. Use bounded `from:` queries, excluding retweets and normally replies. Group handles within the provider's query limit and rotate groups if a few prolific accounts dominate the sample. Quoted authors in the response are not matches of the original query.
4. Request full long-post text, timestamps, metrics, authors and quoted context. Choose recency for engagement opportunities. Do not gate on minimum likes.
5. Inspect each selected post. Rank by fit, a specific contribution the author can substantiate, freshness and room for useful discussion. Follower count and likes are context. Do not invent a baseline or call a small sample exhaustive.
6. Store post URL, ID, author, publication time, observed metrics, capture time, why it fits, the author's angle and grounding. Preserve missing metrics as unknown. Flag media or threads not inspected before proposing a reply that depends on them.
7. Import only the reviewed rows with the current schema. Upsert by the key, without overwriting the author's status or notes. Read back counts and types.

State the reads and their estimated cost before running them. No recurring monitor, follows, likes, replies or DMs are enabled by this skill. A recurring refresh belongs in a hosted OXYGEN Workflow or another scheduler the author authorizes with a cadence and budget, not a local loop.
