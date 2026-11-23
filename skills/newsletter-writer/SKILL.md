---
name: newsletter-writer
description: Write a newsletter issue in the author's voice from a video, post or other source, with one reader takeaway. Holds the default shape for turning a YouTube video into an email, the HTML and plain-text build, validation and a draft that waits for the author's go.
---

Workspace: all context paths below (identity, audience, strategy, voice, brand, raw, output, index, log, workspace preferences and context scripts) resolve from `context/` in the kit root. Read both the root `AGENTS.md` and `context/AGENTS.md`.

# Write one issue

Read `voice/`, `audience/ideal-follower.md`, `strategy/`, `identity/proof.md` and the full supplied sources. Establish the newsletter's promise and the issue's one useful idea. Existing editions define recurring format; do not invent a permanent house style from one draft. In a content waterfall the newsletter is written first: it is the approved argument the X Article and the posts reuse.

## From a video (the default shape)

When the issue comes from a YouTube video, start from the author's final LinkedIn post about it if one exists and stay as close to it as you can, line by line: it is usually the most personal version. Otherwise work from the final-cut transcript. Then follow this order:

1. **Subject.** A short, strong promise, often the receipt itself (a result with its period), not a summary of the issue.
2. **The receipt in the first line.** The author's own result, then what it took (the time or effort, honestly), the reason they do it, and the reader's real question (for example: does this bring more pipeline?). Say early who the issue is for and why they should care.
3. **The key graphic early**, right after the 3 to 5 line intro. Then the honest verdict: say plainly when a tool or method is not a magic pill and where it still helps.
4. **The setup.** What the system is, including the tool layer, as 1 detailed graphic that shows the real cascade (real steps, platforms and logos, not 5 generic boxes), then a short numbered list: 1 plain line per step and 1 detail line under it, no heading per step.
5. **Where each option is better**, in plain sentences, only when the topic compares tools.
6. **2 things learned** (or 2 mistakes), 1 or 2 lines each, rather than lecturing the reader.
7. **The video at the bottom.** 1 plain line that says who should watch and why, the clickable thumbnail linked to the full `https://www.youtube.com/watch?v=<id>` URL, then only the button. The video promotion sits in the middle or at the end, never at the top.

Keep it near 350 to 400 words. A much longer issue reads as too long; a much shorter one loses the setup.

For a funnel or growth issue, follow the funnel in the order it runs: the receipt and proof, what got the author here (top of the funnel), how they scale (new acquisition channels), the middle of the funnel (lead magnets, partner events), how they nurture (the newsletter, a personal note to fitting signups), then the video thumbnail with its link, 2 things learned, a short line on the product and the button at the end.

## Write it like the author

- Write it like a LinkedIn post: 1 or 2 short lines per paragraph, a line break where the thought turns, short one-liners between explanations. Much less long text. Keep the plain-text version in the same order.
- Humble, not cocky. Say what it cost in time, use "I believe" for opinions, and drop bragging asides.
- 1 real CTA: a button to the video or the resource. No "hit reply" CTA.
- No filler headings or labels ("Full walkthrough", "The whole system in 1 picture", "See it on screen", "Here's the whole system") and no bold-label bullets ("**Cron jobs that just work.**"). Use a descriptive heading only where the argument turns.
- If the brand has a highlight style, give it to the key phrases only, about 8 to 12 per issue: the result, the cost, the tool stack, the core rule, each lesson. No large coloured panels or cards around the text.
- Few links: 1 resource or repository that helps the reader rebuild the system, and the author's product when relevant. Leave out tool-stack trivia and spend figures unless they are the point. Check every link returns HTTP 200; never link a private repository.
- Links to the author's own site carry UTM parameters (source `newsletter`, campaign = the waterfall's slug). YouTube, GitHub and LinkedIn links stay clean. Never a shortened link: shorteners can trip phishing filters.
- Attribute guest experience and separate opinion from evidence. Every metric comes from `identity/proof.md` with its population, period and source. A video made with 1 model is described as that model's walkthrough; a model comparison uses a current benchmark graphic with its source visible.
- A wide chart links to its full-size file with 1 small line ("Tap the chart to open it full size."), since its text is unreadable at email width.
- Check the whole draft for generic AI phrasing before the author sees it, not only the lines they flagged. Rewrite a weak line from scratch rather than patching it. Label any missing quote or fact outside the copy.

## Build and validate

- Keep the copy in 1 build script next to the email, so every edit rebuilds the HTML and plain-text versions together.
- Layout: a single column at most 600 px wide, left-aligned text, the author's brand colours and font from `brand/`, meaningful alt text, responsive images that keep their aspect ratio. The footer holds the legal name and postal address as plain text and the unsubscribe link; keep the email tool's merge and unsubscribe tokens unchanged in both versions.
- Images need stable public HTTPS URLs. Upload inspected files under a dated prefix with descriptive filenames, verify each URL returns HTTP 200 with the right content type, and never overwrite an existing file unless you are replacing that exact asset.
- Render the real HTML at desktop width and at 390 px and inspect the pixels: reading order, alignment, clipping, logo, highlights, CTA and footer. A passing check script is not a visual review.

## Draft, never send

Create the issue as a draft in the email tool the author uses, for example an OXYGEN email Sequence to the newsletter list (`oxygen-sequencer`) or their newsletter platform. Check it with the tool's preview and read it back: subject, preview text, sender, list, images, links and unsubscribe. Never send or schedule without the author's explicit go. When editing a scheduled issue, preserve its subject, sender, list and send time unless the author changes them. Before a full-list send, confirm the plan's contact limit and that the list or segment really holds everyone it should.

## Deliver

Subject, preview line, paste-ready body (or the draft's ID and preview link) and a short source and check list outside it. When requested, use `repurpose-content` to extract distinct posts. A completed issue is a draft until the requested publishing action actually succeeds.
