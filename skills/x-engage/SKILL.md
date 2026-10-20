---
name: x-engage
description: Find fresh posts from the author's X watchlist through their OXYGEN X connection, draft 1 short reply each where the author has a real practice or result to add, and publish a Reply on X queue page that learns from what they actually post. Use for a daily X reply round or to grow reach through replies; it never posts, likes or follows on its own.
---

Workspace: all context paths below (identity, audience, strategy, voice, brand, raw, research) resolve from `context/` in the kit root. Read both the root `AGENTS.md` and `context/AGENTS.md`. Skill-local `scripts/`, `references/` and `config.example.json` resolve from this skill directory; run the commands below from the kit root.

# X engage

Replying becomes a 10 minute job: the posts are found, a reply is drafted in the author's voice, and the author edits and sends it from 1 page. Replies under bigger accounts are where new people meet a small account, and X ranks replies far above likes while scoring their quality, so a low-effort reply is worth close to nothing. The rules for a good reply are in [reply-voice.md](references/reply-voice.md).

## The hard rule: the author sends, the skill never does

X's automation rules ban automated replies, and the author's reputation is the asset. The skill drafts; the author taps Reply on X (an X intent link with the text filled in) and sends it in X themselves. No posting, liking, following or DMs through OXYGEN, an agent or any API from this skill, also not on "just do it".

## What it needs

- The author's OXYGEN workspace and CLI ([guides/oxygen.md](../../guides/oxygen.md)) with X connected. X bills its pay-per-use API for every post a read returns, whatever OXYGEN estimates, so the fetch is lean by default and every live call carries `--max-credits`.
- The config at `.oxygen/x-engage.json` (git-ignored), copied from `config.example.json`: see "Config" below.
- A filled reply voice, receipts, watchlist and circle. First time: run the setup in [setup.md](references/setup.md), with 2 stops for the author's OK.
- The author's context in `context/`: `identity/proof.md` for any number, `identity/` and `voice/` pages for who they are and how they write.

## The run

1. **Learn first.**

   ```bash
   python3 skills/x-engage/scripts/learn_taste.py
   ```

   It reads only the author's new replies and updates `taste.json` in `runs_dir`: accounts they answer get a boost, accounts they passed on 3 times drop out. Fetch with `--last-queue <newest run>`; its `feedback` block shows each draft against what the author posted (as drafted, with edits, not posted). Add what it teaches to [verdicts.md](references/verdicts.md) before drafting; a pattern seen twice becomes a rule in [reply-voice.md](references/reply-voice.md).
2. **Fetch.** Keep the window short: early replies are the ones seen.

   ```bash
   python3 skills/x-engage/scripts/fetch_candidates.py --hours 3 --limit 60 \
     --out <scratch>/candidates.json --last-queue <runs_dir>/<newest>.json
   ```

   It reads the watchlist and [the circle](references/circle.md) in `from:` batches (only posts inside the window come back), the author's replies of the last day and the replies to them, drops posts they already replied to and posts shown in the last run, and scores the rest: account size, engagement per hour, freshness, how crowded the replies are, `fit` (how many of their lanes the post touches), a boost for people who talk to them and for the circle. It flags giveaways, promos, hiring, styled-unicode promos and coordinated campaigns (the same phrase from 4+ accounts).

   - **Speed mode** for early replies under big accounts: `--speed --hours 1.5 --max-age-min 90`. It reads [big-accounts.md](references/big-accounts.md) plus watchlist accounts with 50k+ followers, keeps original posts under 90 minutes with fewer than 300 replies, any topic the author can stand behind, and scores freshness first. Pick 5 to 8 and publish fast; run again every 20 to 30 minutes while the author is replying.
   - **Keyword searches** (`--keywords`, add `--focus` for the core niche) find posts outside the watchlist. They are paid per post returned, so agree the budget first and keep `--kw-results` low.
   - **Thin window** (weekends, the author's main audience asleep): prefer a short page of posts under 3 hours and a second run later over padding with old posts.
3. **Pick with the checklist.** A post goes in only when all 4 are yes:
   1. **Niche.** It is in the author's lanes, not general news, culture, jokes or events.
   2. **A practice they use now.** The author can add 1 concrete thing they do, a tool they would pick or a result they have ([receipts.md](references/receipts.md)).
   3. **Not a plug, not a story, not a bare opinion.** No product mention, no "we shipped", no setup brag, no old personal story, no take without a practice in it.
   4. **Fresh.** Under 3 hours, best 15 to 60 minutes.

   Prefer posts likely to travel (moving fast, from accounts whose posts reach far). Put at least 1 circle reply in a batch when someone from the circle posted. 1 reply per account per day is plenty (`replied_to_author_recently`). Aim for 8 to 12 picks; fewer good ones beat more weak ones.
4. **Read the threads** of picks with 5+ replies (paid per reply read):

   ```bash
   python3 skills/x-engage/scripts/thread_context.py <scratch>/candidates.json \
     --ids <id,id,...> --out <scratch>/threads.json
   ```

   Drop a pick when its replies show a promo or bot crowd, and don't repeat a point already in the top replies. `author_answers` above 0 means the post's author talks back: good.
5. **Draft 1 reply per post** with [reply-voice.md](references/reply-voice.md), [receipts.md](references/receipts.md), [verdicts.md](references/verdicts.md), the post and its thread. Every fact comes from those files, `context/` or the post itself; every number from `identity/proof.md`.
6. **Save the run** as `<runs_dir>/<YYYY-MM-DD>-<HHMM>z.json` (UTC): `run_id`, `fetched_at`, `window_start`, `watchlist_handles`, `candidates_total`, `items` (each picked candidate's fields plus `angle`, `why` and `draft`) and `skipped_top`. The next run and `learn_taste.py` learn from this file. `runs_dir` sits under the git-ignored `context/research/`, so runs stay private.
7. **Refresh, check and render.**

   ```bash
   python3 skills/x-engage/scripts/refresh_items.py <runs_dir>/<run>.json
   python3 skills/x-engage/scripts/render_queue.py <runs_dir>/<run>.json \
     --out output/x-reply-queue.html --cache output/x-image-cache
   ```

   The refresh re-reads every post (current counts, images, avatar; deleted posts drop out). The renderer refuses drafts over 200 characters, with more than 1 line break, dashes, links, hashtags, generic openers, banned words, stock phrases, product plugs or the author's own taste blocks, and embeds images as data URIs because the page cannot load images from X.
8. **Publish and hand over.** Publish with the Artifact tool to `page_url` from the config, or open the HTML file. Hand over in 2 lines: the link, how many replies, which 2 or 3 to do first because they age fastest.

## Cadence

Twice a day when the author's targets are online (ask them; for a US audience, US morning and US afternoon), `--hours 3` each, 8 to 15 replies, about 10 minutes of the author's time. On a day they post, they answer the replies on their own post themselves, in the first hour.

## The page

1 column, the freshest post first. Each card shows the post the way it looks on X (avatar, name, text, images, likes and replies, a Circle chip for the circle) and under it the reply in a box that grows with the text, a character count, Skip, Copy and Reply on X, which opens the X composer with the text filled in and marks the card done. Edits and marks stay in the browser; the learning comes from what the author actually posts on X. The footer says nothing goes out until the author sends it.

## Config

`.oxygen/x-engage.json`, from `config.example.json`:

| Field | What it holds |
|---|---|
| `oxygen_profile`, `oxygen_org` | The author's CLI profile and org, or `null` for the active ones |
| `x_handle` | The author's X handle |
| `watchlist_table` | The id of their X Watchlist table |
| `runs_dir`, `page_url` | Where run files and `taste.json` go (git-ignored), and the published page |
| `x_toolkit`, `x_search_action`, `x_lookup_action` | The X read actions in their workspace (setup step 1) |
| `lanes`, `focus_lanes` | Lane name to keyword regex; the lanes `--focus` keeps |
| `niche_terms` | The junk gate: posts need `--min-niche` distinct terms (empty switches it off) |
| `keyword_queries`, `keyword_min_followers` | Opt-in searches outside the watchlist |
| `focus_queries`, `focus_min_followers` | Opt-in searches for the core niche, smaller peers allowed |
| `company_name` | Blocked in replies as a plug (`null` skips it) |
| `extra_banned_words`, `taste_blocks` | Words the author never uses; `{pattern, why}` blocks learned from their skips |

## Related

- [linkedin-engage](../linkedin-engage/SKILL.md): the same system for LinkedIn comments.
- [x-planner](../x-planner/SKILL.md): the author's own X posts.
- [x-copywriter](../x-copywriter/SKILL.md) and [x-article-writer](../x-article-writer/SKILL.md): X posts and Articles.
