# Cross-niche packaging

An outlier can come from the idea, the title or the thumbnail. Inside 1 niche the topic and the packaging are tangled. A structure that wins on unrelated topics in 2 or more niches isolates the packaging. Well-known YouTube strategists such as Paddy Galloway describe the same habit: look for concepts that broke out in another niche and bring the format, never the video itself. Formats also wear out once a niche catches on, so the check has 2 halves: proven elsewhere, not worn here.

**Outlier** here: current views at least 3x the channel's own comparable uploads. Outlier tools commonly band ratios as 2 to 5x, 5 to 10x and over 10x. An outlier on a small channel is the stronger proof of a format: no audience carried it.

## Donor niches

Use 4 to 6 per structure, at least 2 outside the author's field.

| Niche | Why it donates | Seed nouns |
|---|---|---|
| AI tools and tutorials | fast packaging cycle, overlapping viewers | ChatGPT, Claude, AI agent, n8n |
| Entrepreneurship and making money | outcome packaging for business viewers | business, clients, agency |
| Personal finance and investing | stakes and numbers in titles, experiments with real money | money, stocks, invest, budget |
| Experiments and challenges | "I let" and timebox formats at full strength | 24 hours, 30 days, challenge |
| Productivity and self-improvement | "I tried X for N days", systems | habits, routine, productivity |
| Tech reviews | versus and verdict formats | iPhone, laptop, camera |
| Fitness and health | transformation timeboxes | workout, diet, gym |

## Structures

| Structure | Example skeleton | Seeds (1 per donor niche) | `--keep` regex |
|---|---|---|---|
| Experiment: I let X run my Y | I let <tool> run my <job> | "I let AI manage my money", "I let ChatGPT plan my week", "I let AI run my business" | `\bI (let\|gave\|made\|hired\|asked)\b` |
| Equation: X + Y = Z | <tool> + <tool> = <outcome machine> | tool pairs per niche: "ChatGPT Excel", "Notion AI", "n8n Claude" | `\+\|=` |
| Result in a timebox | how I got <result> in 7 days | "in 30 days", "in 7 days", "in 24 hours" plus a niche noun | `\bin (\d+\|one\|a) (days?\|hours?\|weeks?\|months?)\b` |
| Removed task | No more <painful task> | "stop doing", "never again", "no more" plus a niche noun | `^(stop\|never\|no more\|quit)\b\|\bwithout\b` |
| Verdict | <tool> honest review | "worth it", "honest review", "I tested" plus a niche product | `worth it\|honest\|i tested\|after \d+` |
| Versus | <tool A> vs <tool B> | "vs" plus 2 niche products | `\bvs\.?\b\|versus` |
| Plea | I'm begging you to <action> | "I'm begging you to" plus a niche verb | `begging` |
| Swap | I quit X and did Y instead | "I quit my job and", "I quit sugar and" plus niche methods | `\bi quit\b\|\bquitting\b\|\bi stopped\b` |

The `\|` in the table is a literal `|` in the regex.

## Validated so far

Keep the verdicts in `strategy/youtube-packaging-library.md`: the structure, the date, the donor outliers (URL, niche, ratio), the niche-saturation check and the verdict (validated, worn, not proven). Read it before drafting; add every new check there.

## Run

1 file of seeds per structure, `branch` set to the donor niche. From `context/`:

```sh
python3 ../skills/youtube-video-research/scripts/youtube-depth-first.py \
  --seeds research/<date>-<slug>/packaging-<structure>/seeds.json \
  --raw raw/<date>-<slug> \
  --out research/<date>-<slug>/packaging-<structure> \
  --days 90 --max-searches <number of seeds> --max-depth 0 \
  --keep '<regex>' --fit '<niche outcome regex>'
```

`--max-depth 0` searches the seeds only. The tree in `depth-first.md` then has 1 row per donor niche with its outliers and channels.

## Pass

1. **Proven elsewhere:** 3 or more outliers of 3x or more, from 3 or more channels, in 2 or more donor niches, in the last 90 days.
2. **Not worn here:** run the same structure on 3 or 4 niche seeds over 30 days. If 3 or more niche channels used it and their median is under 1.5x, the niche has caught on.
3. **Transfer:** keep the skeleton (word order, the parenthesis, the number slot), swap in the wave and the niche outcome, then run the promise check.

## Thumbnail

For each passing structure, open the top 5 donor thumbnails and note the subject (face to camera, back-shot, object, UI), the 1 hero object, the word count and the contrast. Brief [youtube-thumbnail](../../youtube-thumbnail/SKILL.md) with that archetype under the author's visual rules in `brand/BRAND.md`.

Read the author's own thumbnails the same way once the ledger has a few rows: which subject, object and words the hits had and the misses lacked. With fewer than 10 videos that is a lead to A/B test, not a rule.
