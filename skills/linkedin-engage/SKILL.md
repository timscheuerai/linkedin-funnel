---
name: linkedin-engage
description: Find fresh posts from the author's LinkedIn watchlist through OXYGEN's managed scraper, draft 1 or 2 natural comments each where the author has a real receipt, and publish a Copy & open queue page that learns from what they actually post. Use for a LinkedIn comment round or to grow reach through comments; it never comments, likes or messages on its own.
---

Workspace: all context paths below (identity, audience, strategy, voice, brand, raw, research) resolve from `context/` in the kit root. Read both the root `AGENTS.md` and `context/AGENTS.md`. Skill-local `scripts/`, `references/` and `config.example.json` resolve from this skill directory; run the commands below from the kit root.

# LinkedIn engage

Twice a day this finds fresh posts from creators the author cares about, drafts a comment per post in the author's comment voice and puts them on 1 page, where the author edits, taps Copy & open and posts each comment themselves. Commenting becomes a 10 minute job.

Why comments: an early comment under a bigger creator's post puts the author's name and headline in front of that creator's audience, and comments weigh more than likes in the feed. Only a comment that sounds like a person does that. The rules for a good comment are in [comment-voice.md](references/comment-voice.md).

## The hard rule: the author posts, the skill never does

LinkedIn bans automated commenting and the author's account is the asset. Nothing in this skill comments, likes, follows, connects or messages on LinkedIn: not through OXYGEN's connected LinkedIn sender, a workflow, a Sequence or any API, and also not when the author says "just do it". Every read goes through OXYGEN's managed scraper (`scraper.*`, cookieless, no connected account), so it never touches the author's own account or its limits. Never use the `linkedin.*` tools here. The page only copies text and opens the post. Lead-magnet replies are a separate system ([lead-magnet-delivery](../lead-magnet-delivery/SKILL.md)).

## What it needs

- The author's OXYGEN workspace and CLI ([guides/oxygen.md](../../guides/oxygen.md)). Post search is free at the time of writing; reading the author's comments, threads and single posts costs credits. Check current prices with `oxygen tools get <id> --json`; every paid call carries `--max-credits` and every script a `--budget`.
- The config at `.oxygen/linkedin-engage.json` (git-ignored), copied from `config.example.json`: see "Config" below.
- A filled comment voice, personal bank and watchlist. First time: run the setup in [setup.md](references/setup.md), with 2 stops for the author's OK.
- The author's context in `context/`: `identity/proof.md` for any number, `identity/` and `voice/` pages for who they are and how they write.

## The run

1. **Learn first.** If a run exists in `runs_dir`, fetch with `--last-queue <newest file>`. The `feedback` block shows each earlier draft against what the author actually posted (as drafted, with edits, not posted, and which of 2 drafts); `my_recent_comments` shows their own comments since. If the page saves picks (setup step 4), read its `feedback` collection with the ArtifactData tool into `<scratch>/page-feedback`, then:

   ```bash
   python3 skills/linkedin-engage/scripts/page_feedback.py <scratch>/page-feedback/feedback \
     --append-golden skills/linkedin-engage/references/golden-comments.md
   ```

   Add what both teach to [verdicts.md](references/verdicts.md); a pattern seen twice becomes a rule in [comment-voice.md](references/comment-voice.md). Say in the hand over, in 1 line, what you learned.
2. **Fetch.**

   ```bash
   python3 skills/linkedin-engage/scripts/fetch_candidates.py --hours 3 --limit 40 \
     --out <scratch>/candidates.json --last-queue <runs_dir>/<newest>.json
   ```

   It reads the watchlist (priorities 1 to 3), runs 1 free post search per profile (5 in parallel at most, failures retried 1 at a time), keeps each creator's own posts from the window, adds the config's niche searches for people outside the watchlist, drops posts the author already commented on and posts shown in the last run, and scores the rest: author size, engagement per hour, freshness, how crowded the comments are and `fit` (how many of the author's lanes the post touches). It flags comment-gated giveaways, hiring, promos, milestones, politics and non-English posts.
3. **Pick 10 to 12.** The score only finds fresh posts that are moving; fit is your call. Read every candidate in full and keep a post only when the author has a real receipt, stance or question for it, in their lanes. Skip sponsored posts, giveaways, job and milestone posts, product pitches, politics, tragedy and anything they would have to fake. Mix 3 to 5 big accounts (50k+) whose post is under 2 hours old with peers in their lane, especially creators the watchlist notes as warm. Freshness first: posts under 3 hours, never over 6 unless the post mentions the author. When the window is thin, show fewer cards and say so rather than padding with old posts.
4. **Read the threads** of the picks (billed per comment read):

   ```bash
   python3 skills/linkedin-engage/scripts/thread_context.py <scratch>/candidates.json \
     --ids <id,id,...> --out <scratch>/threads.json
   ```

   Never repeat a point already made in the thread.
5. **Find the personal link** (free, local):

   ```bash
   python3 skills/linkedin-engage/scripts/personal_refs.py <scratch>/candidates.json --ids <id,id,...>
   ```

   It shows the watchlist notes and any shared history in `context/`, the matching stories from [personal-bank.md](references/personal-bank.md) with when each was last used, and keyword hits in the author's own pages. When the hits miss, search with your own words (`--query <id>="lead quality paid ads"`). A story goes in only where it is the direct parallel, in 2 to 4 comments of 10.
6. **Draft.** While the author's picks are still settling (the first few runs), write 2 drafts per post with different moves from the moves table, at least 1 of them a 1 liner, and mix which one comes first so the picks show the move, not the slot. Once 1 draft would have matched their pick in most cards for 2 runs, go back to 1 draft per post. Draft with [comment-voice.md](references/comment-voice.md), [golden-comments.md](references/golden-comments.md), [verdicts.md](references/verdicts.md), the post, its thread and the watchlist notes. Every fact comes from the post or `context/`; every number from `identity/proof.md`, in that wording. No invented details, feelings or plans.
7. **Save the run** as `<runs_dir>/<YYYY-MM-DD>-<HHMM>z.json` (UTC): `run_id`, `fetched_at`, `window_start`, `watchlist_profiles`, `candidates_total`, `credits_used`, `items` (each picked candidate's fields plus `angle`, `why` and `drafts`: a list of `{move, label, text}`, and for a draft that uses a story `ref` and `ref_source`) and `skipped_top` (high scorers you skipped and why). The next run learns from this file. `runs_dir` sits under the git-ignored `context/research/`, so runs stay private.
8. **Refresh, check and render.**

   ```bash
   python3 skills/linkedin-engage/scripts/refresh_items.py <runs_dir>/<run>.json
   python3 skills/linkedin-engage/scripts/render_queue.py <runs_dir>/<run>.json \
     --out output/linkedin-comment-queue.html --cache output/li-image-cache
   ```

   The refresh re-reads every post for current counts and media and drops deleted ones. The renderer refuses drafts that break the rules in [comment-voice.md](references/comment-voice.md), including a batch that reads like a bot (the same opener twice, most comments in 1 shape, too many questions or laughs, wording repeated from another comment or from the runs of the last 14 days), and embeds avatars and images as data URIs because the page cannot load LinkedIn images. Fix the drafts it names and render again.
9. **Publish and hand over.** Publish with the Artifact tool to `page_url` from the config (on a redeploy, keep the page's capabilities as they are), or open the HTML file. Hand over in 2 lines: the link, how many comments, which 2 or 3 to do first because they age fastest.

## Cadence

Twice a weekday when the author's audience is on LinkedIn (ask them; a common default is mid-morning and mid-afternoon in their time zone), `--hours 3`, 10 to 12 comments. Weekends are thin: widen `--hours` back to the last run's `fetched_at` and say in the hand over that the posts are older. The author answers comments on their own posts themselves, so the fetch never queues those.

## The page

1 column, the freshest post first. Each card shows the post the way it looks on LinkedIn (avatar, name, headline, age, text, images, counts) and under it the comment in a box that grows with the text, a word and character count, the personal moment it uses and where it comes from, and Skip, Copy and Copy & open. Copy & open copies the comment, opens the post and marks the card done; Skip asks for a reason in 1 tap. Edits and marks stay in the browser; with a `db` capability the page also saves 1 document per card in `feedback` for `page_feedback.py`. The footer says nothing goes out until the author posts it themselves.

## Config

`.oxygen/linkedin-engage.json`, from `config.example.json`:

| Field | What it holds |
|---|---|
| `oxygen_profile`, `oxygen_org` | The author's CLI profile and org, or `null` for the active ones |
| `my_profile_url` | The author's LinkedIn profile URL |
| `watchlist_table` | The id of their LinkedIn Comment Watchlist table |
| `runs_dir` | Where run files go, under the git-ignored `context/research/` |
| `page_url` | The published queue page, so every run republishes to 1 URL |
| `lanes` | Lane name to keyword regex; a post's fit is how many it touches |
| `niche_searches`, `niche_min_reactions` | Free keyword searches for posts outside the watchlist |
| `company_name` | Named in at most 1 comment in 10 (`null` skips the check) |
| `thousands_separator` | How the author writes 1,000 |
| `automated_comment_patterns` | Regexes for automated comments to ignore in the feedback |
| `extra_banned_words` | Words the author never uses, blocked by the renderer |

## Related

- [x-engage](../x-engage/SKILL.md): the same system for X replies.
- [linkedin-copywriter](../linkedin-copywriter/SKILL.md): the author's own posts.
- [linkedin-unibox-reply](../linkedin-unibox-reply/SKILL.md): replies in existing DM threads.
