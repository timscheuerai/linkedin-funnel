---
name: linkedin-copywriter
description: Draft or edit one LinkedIn post using the author's context, best-performing posts, factual sources and intended funnel job, structured to skim and run through a slop pass before delivery.
---

Workspace: all context paths below (identity, audience, strategy, voice, brand, raw, output, index, log, workspace preferences and context scripts) resolve from `context/` in the kit root. Read both the root `AGENTS.md` and `context/AGENTS.md`. Skill-local `references/` and flowchart `scripts/` resolve from this skill directory.


# Write a LinkedIn post

Read `AGENTS.md`, `index.md`, relevant identity and audience pages, `identity/proof.md`, `voice/linkedin-voice.md`, `voice/formats.md` and the selected pillar/funnel context. Read the full source behind the central claim.

Drafts sound like a bot when the only voice input is a style guide. If the context holds the author's verbatim words (calls, DMs, voice notes, past posts), a story bank (`identity/backstory.md`, "Stories to tell") or a page on what performs on their account, read the relevant parts too. A story the author has not told in public needs their yes before it goes into copy.

For a new draft, read 2 full posts by the author chosen for a similar job, preferably from their best performers (for example the posts that reached a multiple of their median impressions). Those posts set the target shape; older or average posts are a weaker anchor. For an edit, the user's wording is the primary voice anchor.

Precedence: the author's current instructions and edits, the supplied draft, their recent best posts and calibrated voice guide, older examples, generic copywriting advice. Never let a creator template overrule the author's wording or actual facts.

## Check the current stance

Before drafting on a topic, read what the author published about it in the last few weeks. Build on it or name the change ("Yesterday I said I don't get the hype. Here is what changed."). Never let a new hook silently contradict a public stance from days ago; tell the author when their brief does.

## Find the post

Identify one useful point, its source, the intended reader and the post's job. Work from the supplied brief and existing context; ask for missing information only when it would change the substance. Do not invent a milestone, anecdote, number, customer quote or feeling to make an idea interesting. When something is missing, narrow the claim or flag the gap.

Structure before sentences: a post that is easy to skim is easy to read. Pick 1 spine for the shape (descending, ascending, ranked, countdown or flat) and mix at most 2 devices; blending spines is the most common structural failure. Then run a skim test: line 1, the list heads and the last line alone must carry the argument. If they do not, re-pick the structure before editing sentences.

Choose the shape the material supports: a sequence for a process, a story for a real change, evidence for a claim, a comparison for a decision, or a resource. Do not force a spine the material does not support, a fixed list length or a long-post default.

## Moves that tend to perform

Use the ones the material supports; check them against the author's own best posts.

- Give the reader a system to copy: a framework, org chart, architecture, stack or list with a name and a number, shown in full on the visual.
- Line 1 is a big claim or result, short (under about 55 characters); line 2 says what follows or proves it.
- Always 1 empty line between line 1 (the hook) and line 2 (the re-hook), never the 2 lines stacked.
- 1 belief line for the why ("Your outputs are only as good as your inputs.").
- Each step names the tool or person doing the work; `1)` sections with `→` items, or `[1]` layers. Generic steps flop.
- 1 honest line beside the claim ("Big words, I know. Here is what I mean.") and 1 contrast number when a real one exists.
- End by handing something over: the link in the comments, the graphic's instructions, a DM, or 1 real question.
- An event, launch, partnership or milestone gets a copyable system inside it; on its own it tends to underperform.
- Keep the author's own texture (their shorthand and casual phrasing). Never add slang, typos, a self-roast or profanity they do not use.

## Line breaks

- Intro and story: every sentence is its own paragraph with an empty line after it, never 2 prose lines stacked.
- A section header (`1) The first hook`) or a question header ("Why broader?") gets an empty line after it.
- The `→` items under a header stay stacked, with no empty lines between them.
- An explanation of 3 or 4 short lines may stack; its conclusion line stands alone after an empty line.

## Draft or edit

- Find the real friction: what the author expected versus what happened, a costly mistake, a decision, a change in the work, or a specific reader problem. A simple useful explanation does not need a dramatic reversal. Use the audience's own phrasing and objections from `audience/ideal-follower.md`.
- For a firsthand story, stay with the real decision or unresolved situation long enough for the reader to understand the stakes: what the author thought or felt (if supplied), what they tried, what happened and what remains uncertain. Let the lesson emerge from that experience. Do not invent dialogue or feelings or turn every story into a confession.
- When a sprint or launch is the point, get to what the author wants to ship or achieve early. The backstory explains the work; it does not delay it.
- Select details for what they add, not because they are concrete. Keep the ones that explain the action or feeling; cut those that only illustrate an already clear point. Technical explanations still need the specifics that make them useful.
- Give the author's own emotional perspective room when they supply it, in their terms, instead of replacing it with a generic moral.
- Keep an explicitly approved hook verbatim unless the author asks to revise it. A request for a new body does not reopen the hook.
- For the opening pass, follow [linkedin-hook-writer](../linkedin-hook-writer/SKILL.md). It owns the character budgets, hook selection and counter.

**From an X post.** When the author supplies a final X post as the source or as the correction for a LinkedIn draft, treat its idea selection and sequence as the brief: result, proof, formula, build promise. Add only 1 short causal layer LinkedIn needs (why the formula works, or what the attached video contains) and stop before it becomes a tutorial. Keep a stronger direct hook and deliberate repetition. Clean accidental grammar unless the author asks to keep the wording, and keep each metric's scope and period accurate.

**From a long source.** Select one argument rather than compressing the whole source into a post. In a content waterfall, reuse the approved newsletter argument instead of re-deriving it from the transcript.

## Edit for substance

Check that each paragraph adds a fact, a reason, a step or a real feeling. Cut generic praise, unsupported superlatives, repeated morals, empty transitions and slogan-like conclusions. Keep necessary explanations and the caveat beside the claim. Read the full paragraphs, not just the punchlines, to check that the causal logic holds.

Check every factual claim, quote, date and number against its source and public-use status in `identity/proof.md`. Keep reported results, targets, predictions and illustrative examples distinct. Use a CTA only when it fits the funnel job and a real available offer.

Links: resource and video links go in the first comment and the post says so. A link to the author's own site carries UTM parameters (source `linkedin`, 1 campaign slug per piece or waterfall); other links stay clean. Link videos with the full `https://www.youtube.com/watch?v=<id>` URL, never a shortener.

A lead-magnet post never writes "comment X for Y" in the text. The graphic carries the steps (for example Connect, Comment KEYWORD); the text only points to them ("follow the instructions in the post"). Delivery runs through `lead-magnet-delivery`.

**Tagging.** Tag who the post names. A post about the author's work with a customer or partner tags the author's company page, the other company's page and each named person. Tag each person or company once, at first mention; later mentions stay plain unless the author wants their own company tagged at every mention. Name the company with the person at first mention ("@person from @company chose @your-company"), not paragraphs later. Verify every handle before queuing (OXYGEN Publishing can resolve mentions; see `oxygen-linkedin-marketing`). Guessed `firstname-lastname` handles often fail because profiles carry a suffix: ask for the profile URL instead.

For revisions, address the requested changes first and preserve the user's facts and meaningful phrasing. Remove the smallest amount needed to fix repetition and ordering before rewriting whole paragraphs.

## Slop pass

Before showing any draft, run the whole draft (not only flagged lines) through a slop pass and through anything listed under "Edits and rejected drafts" in `voice/linkedin-voice.md`:

- No "Everyone is doing X. Almost nobody says Y." opener, bold-label bullets, stock labels or a benefit sentence after every item.
- No closing moral, `TAKEAWAY`, signature or automatic question.
- No em dashes, Unicode fake bold, Markdown emphasis or hashtags in the post.
- When the author flags a line as slop, replace it with their suggested words or a plain fact, not a new slogan.

## Deliver or save

Return one paste-ready draft, brief source notes and any material uncertainty. Offer alternate hooks only when useful or requested. Keep measurements, process commentary and reasoning outside the copy.

When saving to Notion is requested, follow `strategy/notion-schema.md`, fetch the configured destination and use `templates/notion-content.md`. Set Status to Creating, one Pillar and the selected Platform. Add a Publish date only if a date is agreed. Check for the existing card before creating another. If Notion is unconfigured, deliver in chat and state it was not saved. Never silently use another board.

When the author asks to schedule the same piece on LinkedIn and other platforms through OXYGEN Publishing (`oxygen-linkedin-marketing`), it is 1 post with 1 channel per platform, never separate posts: create the LinkedIn channel with the publish time, then add each other platform to the same post with its own copy and media. A grouped post has 1 publish time for every channel, so choose it for LinkedIn first (the author's usual posting time). Every channel stays unapproved until the author approves it. Short videos follow the same rule in `shortform-platform-copy`. Writing or saving a draft does not authorize publishing, scheduling, comments or messages.

For a requested voice refresh, fetch the author's current profile activity, filter by their author identity, deduplicate and select the newest requested count by date. Keep only the author's outer text for a commented repost. Add a new dated raw folder, then update the voice synthesis; never rewrite old raw evidence. Do not refetch the whole corpus for every ordinary draft.
