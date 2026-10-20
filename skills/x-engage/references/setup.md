# X engage setup

First-time setup for an author on their own OXYGEN workspace. Ask only what you cannot find out yourself. Stop for the author's OK after the voice (step 2) and after the watchlist (step 3), then do a first run and show the page.

## Step 1: OXYGEN and the X connection

1. Follow [the OXYGEN guide](../../../guides/oxygen.md) to install the CLI and log in. Run `oxygen whoami --json` and check it is the author's workspace; put a non-default CLI profile in `oxygen_profile`, never switch the global active profile.
2. Connect X in the author's OXYGEN workspace (its integrations settings). Then discover the current read actions with `oxygen integrations --help` and `oxygen capabilities search "X recent search" --json`. The scripts default to the `twitter` toolkit with `TWITTER_RECENT_SEARCH` and `TWITTER_POST_LOOKUP_BY_POST_IDS`; if the names differ in the author's workspace, set `x_toolkit`, `x_search_action` and `x_lookup_action` in the config.
3. Tell the author what reads cost. OXYGEN may estimate 0 credits, but X bills its pay-per-use API for every post a read returns. A lean run (the watchlist's `from:` batches, the author's own replies, replies to them) reads tens of posts; keyword searches return full pages whatever the window and can make a run cost dollars, so they stay opt-in. Agree a budget before the first `--keywords` run.
4. Copy `config.example.json` to `.oxygen/x-engage.json` at the kit root (git-ignored) and fill `x_handle`.

## Step 2: the voice

1. Read the author's last 50 or more replies under other people's posts (`from:<handle> is:reply`, bounded) and their recent posts. Leave out automated replies.
2. Fill "The author's moves" in [reply-voice.md](reply-voice.md) with their verbatim lines, and note their texture (laughs, emojis, lowercase, the words they use for people) in the Shape section.
3. Fill [receipts.md](receipts.md) from `context/identity/` and their posts: practices and tools they use now, results they may quote (from `identity/proof.md`), stances in their words, and what is not live.
4. Derive 3 to 5 lanes as keyword regexes in `lanes`, the subset to keep in `--focus` runs in `focus_lanes`, the junk gate `niche_terms`, and 3 to 6 `keyword_queries` (and optional `focus_queries`) in X search syntax with `-is:retweet -is:reply lang:en`.
5. Show the author the moves, receipts and lanes. Wait for their OK.

## Step 3: the watchlist, circle and big accounts

1. An OXYGEN table called "X Watchlist" in the author's workspace, empty by default (check `oxygen tables --help`). Columns: `handle`, `name`, `followers`, `priority` (`1`, `2`, `3` or `off`), `lane`, `notes`. Seed it with 50 to 150 accounts: the ones the author already replies to most, the ones they name, and active peers in their lanes. Put the table id in `watchlist_table`.
2. Pick about 10 accounts for [circle.md](circle.md) with the author: people in the niche who post often and reply to others.
3. Optionally fill [big-accounts.md](big-accounts.md) for speed mode.
4. Show the lists and wait for the author's OK.

## Step 4: first run and the page

Run the skill once ([SKILL.md](../SKILL.md), "The run"). Publish the page with the Artifact tool when the agent has one and write its URL into the config as `page_url`, so every later run republishes to the same URL. Without an Artifact tool, open the HTML file in the browser; it works offline with the images embedded.
