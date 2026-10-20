---
name: youtube-video-research
description: Decide the author's next YouTube video before they record it, in 3 gates. An idea found depth-first inside their niche (a wave that is hot now, applied to their audience's outcome while the niche angle is still open), packaging proven by outliers in other niches, and the first 60 seconds scripted word for word. Ends in a go or no-go scorecard and logs every upload in a channel ledger. Use for "what should my next video be", "is this a good video idea", "validate this title or thumbnail" or "script the intro".
---

Workspace: all context paths below (identity, audience, strategy, voice, brand, raw, research, output, index, log, workspace preferences and context scripts) resolve from `context/` in the kit root. Read both the root `AGENTS.md` and `context/AGENTS.md`. Skill-local `references/` and `scripts/` resolve from this skill directory.

# YouTube video research

No recording until 3 gates pass. The pattern behind them: videos that break out on a small channel usually pair a **wave** that is hot that week (a model, a tool, a launch) with the **outcome the niche wants**, while bigger channels in the niche have not taken that angle yet. Misses usually lack the gap (a bigger channel got there first) or the wave and the niche (a topic the audience does not buy for). The channel ledger turns that into the author's own calibration: every upload adds a row.

| Gate | Question | Where to look | Output | The author decides |
|---|---|---|---|---|
| 1 Idea | Will the author's audience click on this topic now? | Inside the niche, depth-first | A slate of 3 scored ideas | The pick |
| 2 Packaging | Is this the strongest title and thumbnail for it? | Outside the niche: outliers in other niches | 2 titles, 2 thumbnail directions, each with its donor outliers | The pair for an A/B test |
| 3 Hook | Does the click stay past 0:30 and 1:00? | The 5-beat script, the author's past intros | The first 60 seconds, word for word, with the screen per beat | Reads it aloud, edits |
| 4 Ledger | What did this video teach? | The author's channel stats and YouTube Studio | 1 ledger row, the rubric recalibrated | Nothing |

## Ground

Read in order:

1. `strategy/youtube-channel-ledger.md` if it exists: the author's pattern and last uploads. If it does not, create it at the first gate 4 run (template below) and treat the rubric as uncalibrated until it has 3 or more rows.
2. `identity/proof.md`: only numbers cleared for public use are quotable.
3. `audience/ideal-follower.md` and `identity/positioning.md`: whose outcome the video serves and what that outcome is.
4. `strategy/pillars.md` and `strategy/funnel.md`: where YouTube sits in the author's system.
5. Recent trend research, for example an [x-research](../x-research/SKILL.md) brief: the waves of the week.

Write the niche down before gate 1 as 1 line: the audience and the outcome they pay for ("B2B SaaS founders who want pipeline", "physiotherapists who want more private patients"). Every gate refers to it.

## Evidence standard

- Every claim cites a measurement: the video URL, its views, the channel's median and the ratio, with the capture date. No view count from memory or a web snippet when the API can measure it.
- 1 viral video is an anecdote. A trend or a title structure is **validated** only with 3 or more outliers (3x or more) from 3 or more channels in 2 or more niches. Record every verdict in `strategy/youtube-packaging-library.md`.
- A tip someone sends gets measured before it counts, the same day, with the same method.
- The author's own picks are proven only in the ledger: views a day at D+7 against the channel median, Studio CTR, the share still watching at 0:30, A/B test results.
- Ratios compare current views with the channel's own comparable uploads. They are not CTR, not views an hour and not causation.

## Measuring

Use what is available, best first:

1. **The bundled scanner** in `scripts/` with a YouTube Data API v3 key (`YOUTUBE_API_KEY` in the environment, from your own secret manager; never in a file). It needs Python 3 and `requests`. It only calls read-only endpoints and keeps every API response as evidence.
2. The vidIQ plugin or a similar outlier tool, if installed. Record the URLs and ratios it shows.
3. Manual: search YouTube for the last 30 days, open each result's channel and compare the video with the median of that channel's last 20 to 30 long-form uploads.

The scanner, from this skill's `scripts/` folder:

- `youtube-depth-first.py` measures every seed, then dives into the branch with the strongest outliers: phrases that recur across outlier titles from 2 or more channels become the next searches, deeper until the branch saturates (no new outlier channel, no new phrase), then it backtracks. `--probes` searches "<hot wave> <anchor>" to measure the gap. Report: `<out>/depth-first.md`. Re-running the same command resumes.
- `youtube-depth-scan.py` does the searches and channel samples and saves the raw responses; `youtube-rank.py` ranks candidates against their channel's comparable uploads (non-live, 4 minutes or longer, similar age and length, at least 5 peers or no ratio).
- Budget: a search costs 100 quota units of the default 10,000 a day. Keep a run under 30 searches unless the author asks for more. Run 1 scan per raw folder at a time; the scanner refuses a second writer.

## Gate 1: the idea, depth-first inside the niche

1. **Seeds.** 6 to 10 in `research/<date>-<slug>/seeds.json`: the waves of the last 30 days (models, tools, launches from trend research and the channels the audience watches) and 2 or 3 niche outcomes ("<tool> lead generation", "<tool> for <audience>"). Format: `[{"query": "...", "branch": "..."}]`.
2. **Dive.**

   Run from `context/`:

   ```sh
   python3 ../skills/youtube-video-research/scripts/youtube-depth-first.py \
     --seeds research/<date>-<slug>/seeds.json \
     --raw raw/<date>-<slug> --out research/<date>-<slug> \
     --days 30 --max-searches 20 --max-depth 3 \
     --fit "<regex of the niche outcome words>" --probes 6 --anchors "<niche term>,<niche term>"
   ```

   Add a `manifest.md` to the raw folder (what, when, which command).
3. **Read `depth-first.md`.** The tree shows where the heat is, the heat table ranks waves by how many channels have outliers on them, the probes show the gap, and "Also popping on the sampled channels" catches waves nobody seeded. Follow up a new wave with a second run of 4 to 6 seeds at `--max-depth 0`, including "<wave> <niche outcome>".
4. **Check by hand** what the script cannot: open the 5 strongest outliers (title, thumbnail at `https://i.ytimg.com/vi/<id>/hqdefault.jpg`, and the first 60 seconds of captions, for example with `yt-dlp --skip-download --write-auto-subs`). Drop off-topic hits, keynotes and results in other languages, but note a foreign outlier on the niche angle: it proves the demand. Date the wave at its source. List every niche video on the wave and its ratio: many small ones at baseline is a crowded slot, a bigger niche channel with an outlier is a closed one. For a wave under a week old the ratio understates (the channel median comes from older uploads): read views a day as well. Check the author can actually use the tool where they live and on their plan; an idea they cannot run scores Receipt 0.
5. **Score** each candidate with [the idea scorecard](references/idea-scorecard.md). Pass: 8 or more of 10 and no 0 on Heat, Gap or Fit.
6. **Slate.** 3 ideas, best first, in `research/<date>-<slug>/README.md`: the idea in 1 line ("<wave> for <niche outcome>"), the score per criterion with its evidence (3 outlier URLs with ratios, the probe row, the wave's start date), the receipt the author can show, and the overlap with their last 3 videos. Say plainly when fewer than 3 pass. The author picks; never pick for them.

## Gate 2: packaging, validated outside the niche

The niche decides the topic. Other niches prove the packaging: a structure that wins on unrelated topics in 2 or more niches wins because of its shape.

1. Draft 3 to 5 titles for the picked idea with the structures in [youtube-title-outlier-packaging](../youtube-title-outlier-packaging/SKILL.md). Every title names the wave and the niche outcome.
2. For each structure, run the cross-niche check in [cross-niche packaging](references/cross-niche-packaging.md): seeds in 4 to 6 donor niches, `--keep` set to the structure's regex, `--days 90 --max-depth 0`.
3. Keep a structure only if it has outliers of 3x or more from 3 or more channels in 2 or more donor niches, and it is not worn in the author's niche.
4. Thumbnail: describe the donor outliers' archetype (subject, 1 hero object, 2 to 4 words, contrast) and brief [youtube-thumbnail](../youtube-thumbnail/SKILL.md), with [youtube-thumbnail-outlier-research](../youtube-thumbnail-outlier-research/SKILL.md) for more references. The words name the niche outcome and the wave's logo is the hero object. No other creators' faces unless the video is about them.
5. Promise check: every claim on the title and thumbnail is shown in the video; numbers only from `identity/proof.md`.

Deliver 2 titles and 2 thumbnail directions for an A/B test, each with its donor outliers (URL, niche, ratio) and its niche-saturation check.

## Gate 3: the first 60 seconds, scripted

Write the opening word for word with [the first 60 seconds](references/hook-60s.md): 5 beats, about 160 words, each beat with what is on screen. The first sentence says the title's promise; the first frame shows the thumbnail's hero object. Write 3 versions of the first sentence; the author reads them aloud and picks. The author records the opening as its own take, as often as it needs, before the rest. The edit then follows [longform-edit](../longform-edit/SKILL.md).

## Gate 4: the ledger

After the upload, at D+1, D+3, D+7 and D+28, record in `strategy/youtube-channel-ledger.md`: views, views a day against the channel median, and from YouTube Studio what the public API cannot read (impressions, CTR, the share still watching at 0:30 and 1:00, average view duration). Add the video's scorecard row and 1 line on what it teaches. If a video scoring 8 or more misses, or one under 8 hits, change the rubric and say why in `log.md`.

Ledger row template:

```text
| Date | Title | Idea score (H·G·F·T·R) | Views a day D+7 / channel median | CTR | 0:30 | 1:00 | Lesson |
```

## Rules

- The author picks the idea and the packaging. The skill proposes and proves.
- No number without a source: ratios from this run, the author's results from `identity/proof.md`.
- Never record on a gate that failed. Bring the slate back instead.
- Evidence in `raw/<date>-<slug>/` (append only, with `manifest.md`), the synthesis in `research/<date>-<slug>/README.md`, durable lessons in the ledger and the packaging library, then `index.md` and `log.md`.
- No paid research or new tool spend without the author's go.
- Numerals, no em dashes.

## Deliver

1. The gate you ran and its verdict (pass, fail, why).
2. Gate 1: the slate with scores and evidence. Gate 2: titles and thumbnail directions with donor outliers. Gate 3: the script, beat by beat.
3. Paths to the research folder and the updated ledger.
4. The next gate and what it needs from the author.

Pairs with [content-waterfall](../content-waterfall/SKILL.md), which calls this skill to pick the week's video.
