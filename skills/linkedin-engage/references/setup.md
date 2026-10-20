# LinkedIn engage setup

First-time setup for an author on their own OXYGEN workspace. Ask only what you cannot find out yourself. There are 2 stops for the author's OK: after the voice (step 2) and after the watchlist (step 3). Then do a first run and show the page before calling the setup done.

## Step 1: OXYGEN access and prices

1. If `oxygen` is missing, follow [the OXYGEN guide](../../../guides/oxygen.md) to install and log in. Run `oxygen whoami --json` and check it is the author's workspace. If they have several CLI profiles, put theirs in `oxygen_profile` in the config; never switch the global active profile.
2. Run `oxygen tools get <id> --json` for `scraper.linkedin_post_search`, `scraper.linkedin_profile_comments`, `scraper.linkedin_profile_posts`, `scraper.linkedin_post_comments` and `scraper.linkedin_post`, and tell the author each current price. If one is missing, stop and say so.
3. Copy `config.example.json` to `.oxygen/linkedin-engage.json` at the kit root (git-ignored) and fill `my_profile_url`. Every call goes through the CLI:

   ```bash
   oxygen tools run <tool_id> --input-json '<json>' --mode live --approved --max-credits <cap> --json
   ```

   It prints an envelope `{ok, data, error}`; the provider response is at `data.result.response`, the credits spent at `data.credits.credits_used`. Free calls take `--max-credits 0`. Every paid call carries a cap and every script a `--budget`.

## Step 2: learn the voice from real comments, not posts

This step decides whether the comments sound like the author. Drafts copied from post voice come out as tidy 2 or 3 paragraph mini posts, while most real comments are 1 line.

1. Pull the author's latest comments with `scraper.linkedin_profile_comments`: `{"profile": "<their url>"}`, then `{"profile": "<their url>", "page": n, "pagination_token": "<raw.pagination.paginationToken>"}` while `raw.pagination.has_more` is true, a small cap per page. Rows carry `created_at`, `comment`, `post_url`, `post_id` and `post_author_name`.
2. Drop everything automated or templated: lead-magnet deliveries ("sent", "check your DMs"), comments with links or UTM tags, replies that repeat word for word. Put patterns for those in `automated_comment_patterns`. Split the rest into comments under other people's posts (the model) and answers on their own posts (texture only).
3. Pull their latest posts with `scraper.linkedin_profile_posts` (`{"profile": "<their url>", "per_page": 25}`, then `page` and `pagination_token`, 2 or 3 pages).
4. Fill [comment-voice.md](comment-voice.md): the measured shape, the texture, a verbatim line per move, and any "never" words they don't use (check, don't guess). Tune the default shape to what you measured.
5. Fill [personal-bank.md](personal-bank.md): 15 to 30 public moments from their posts and `context/identity/`, with only the details the source gives.
6. Derive their 3 to 5 lanes (topics they post and comment about) and write each as a keyword regex in `lanes`; add 3 to 5 `niche_searches` in their lanes.
7. Show the author the shape numbers, the 5 comments you find most like them, the lanes and the bank. Wait for their OK.

## Step 3: the watchlist

An OXYGEN table called "LinkedIn Comment Watchlist" in the author's workspace, empty by default. Check the current table commands with `oxygen tables --help`, create it, then add rows. Columns: `name`, `profile_url`, `followers`, `headline`, `priority` (`1`, `2`, `3` or `off`), `lane`, `notes`. `notes` says how the author knows the person (client, friend, met at an event, a podcast together) and sets how warm the comment can be. The author edits the table in the OXYGEN web app; `off` drops a row.

Seed it with 50 to 100 people: the creators the author already comments on most (from step 2), the ones they name, and people in their lanes who show up in the niche searches with real engagement. Fill `followers` where the data has it (the score falls back to 2,000). Put the table id in `watchlist_table`. Show the list and wait for the author's OK.

## Step 4: first run and the page

Run the skill once ([SKILL.md](../SKILL.md), "The run"). Publish the page with the Artifact tool when the agent has one; it stays private until the author shares it. To let the page save picks, edits and skip reasons, publish it with a `db` capability whose `feedback` collection only the author can read and write. Write the page URL into `.oxygen/linkedin-engage.json` as `page_url`, so every later run republishes to the same URL and the author keeps 1 bookmark. Without an Artifact tool, open the HTML file in the browser; it works offline with the images embedded, and picks stay in that browser.

## Scraper notes

- Post fields differ between endpoints, so `fetch_candidates.py` reads them defensively: the url is `url` or `linkedinUrl`; the author `author.name`, `author.linkedinUrl` or `author.url`; the time `posted_at` or `postedAt.date`; the counts `engagement.*` or `*_count`. In a post search the avatars come separately in `results[]` as `author_picture_url`, keyed by `post_url`.
- The post id is the 19 digit number after `activity-` or `activity:` in the url. A repost of the author's own post has a new urn but the original url and `share_urn`, so dedupe by share id.
- `scraper.linkedin_post_comments` returns top-level comments only, without reaction counts, and stamps Berlin wall time with a `Z`; the scripts convert it to real UTC.
- "Capacity is busy" (`rate_limit_exceeded`): back off and retry, never more than 5 calls in parallel. `provider_outcome_unknown` on a paid read: retry once. `provider_response_error`: the second pass, 1 at a time. Weekends are flakier.
- 1 failed profile, thread read or refresh never stops the run. It lands in `errors` and the summary line.
- Match the author's comments to posts by the 19 digit ids. When comparing a draft with what they posted, strip the leading @mention name and normalise whitespace.
