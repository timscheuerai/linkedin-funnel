---
name: x-copywriter
description: Write or rewrite the author's X posts the way they actually write, including the X version of a LinkedIn post, intro and progress posts, quote posts and high-value threads. A post the author wrote themselves goes out exactly as written. Use for any X copy; x-planner decides what goes out and when, x-article-writer writes X Articles, x-engage writes replies under other people's posts.
---

Workspace: all context paths below (identity, audience, strategy, voice, brand, raw, output, index, log, workspace preferences and context scripts) resolve from `context/` in the kit root. Read both the root `AGENTS.md` and `context/AGENTS.md`. Skill-local `references/` resolve from this skill directory.

# X copywriter

X posts are written the way the author writes: their own X posts and their LinkedIn posts. What carries over from LinkedIn is the writing (the hooks, their story, their texture), not a pasted post. LinkedIn frameworks pasted unchanged usually underperform on X; the author's personal posts that lead with their own receipts usually win.

## Ground the work

- Read the author's newest posts in their own words (an export in `raw/`, or the posts they paste), then the posts that performed best for them, then `voice/linkedin-voice.md` and `voice/formats.md`.
- Read the X verdicts in `../x-planner/references/verdicts.md`. The author's verdicts win over this page.
- For a repurpose, use the source post's final copy as the brief. For facts, use `identity/proof.md` and `identity/backstory.md`. Never invent a number, tool, price or result. A number that is not cleared in `identity/proof.md` stays out, even if the author used it once before.

## The shape

1. **Line 1: the author and a number, short (about 55 characters or less), ending in a full stop.** "I grew my LinkedIn to <N> followers.", "In the last 30 days we made <$N> in revenue.", "30 days ago I started on X as a <role>."
2. **Line 2 proves it or raises the stakes.** What the number led to, or why the reader should care.
3. **The story in short lines, 1 thought per line, a blank line between.** The backstory, the struggle, how it felt, what they do now. The body educates, connects and transforms.
4. **A list where there are steps or items.** 1 line that says what follows, then `1)` sections with `→` items, or a plain `→` list. Steps name the tool doing the work.
5. **The author's texture stays.** Their greetings, fillers, asides, self-deprecating jokes, number formatting and non-native English. Do not polish it into neutral copy.
6. **End on the last step, an honest line or a plain connect line** ("Looking to connect with people who are into" and a short list). No closing question unless the author wrote it: engagement-bait questions ("What would you add?", "Which one would you push first?") read as AI slop.
7. **Length is what the story needs.** Long posts work on X when every line earns its place. Always attach media: a photo of the author, a screenshot, the graphic or the video.

## When the author writes the post themselves

It goes out exactly as they wrote it. Fix only a clear spelling mistake and say which. Never rewrite their hook, reorder their lines, swap their `-` for `→`, add lines or turn their points into shorter ones. When they ask for "shorter", shorten around their points, never the points themselves. Their own posts are the model for everything this skill writes, not drafts to improve. When "this post" is ambiguous, check which post they mean before rewriting anything.

## The X version of a LinkedIn post

- Start from the LinkedIn post in the author's own words. It may keep its LinkedIn hook and line 2.
- **Get to the substance fast.** After the hook and line 2, go straight to the examples or the list. Cut the argument, the setup math and the supporting numbers that LinkedIn needed. A 2'000-character LinkedIn post often becomes about half that on X.
- Remove LinkedIn-only parts: "connect with me", the LinkedIn comment-gate wording, "now on X too", LinkedIn counts.
- Swap every LinkedIn tag for the X handle (see "Tags"), and the LinkedIn UTM source for `x`.
- Rebuild line 1 around 1 fresh receipt ("X native") only when the author asks for it.
- Default timing: the X version goes out the day after the LinkedIn post, or as a second channel of the same post when the author's scheduler supports grouping (see "Deliver").

## What differs on X

- The newcomer frame works: "Now I'm trying to crack X too."
- Lists of people tag them: `@handle → what you learn from them`, 1 per line.
- No link in the post body: links go in the first reply, with UTM source `x`.
- A lead magnet can use a comment gate, adapted to X: "1) Follow me 2) Comment "<KEYWORD>"", with the resource sent by DM, and no link reply. The visual's CTA box says "Follow", never LinkedIn's "Connect". Measure gated posts on X before planning more; they often do worse than on LinkedIn.
- A native video post is a 1 to 2 line announcement; the video carries the explanation.
- A ranking or tier-list post carries the author's own ranking, never the source creator's order. Familiar meme formats keep their familiar look.
- Anti-slop: no role verbs ("orchestrates", "routes the work", "leverages"), no "Label: description" bullets, no "Bonus:" or "Pro tip:", no em dashes, no hashtags, no emoji beyond the author's own. Bullets are fine; the slop is labels and role verbs. Write a stack as tools with jobs and a process as first-person actions with plain verbs.

## Tags

Tag every creator and company the post names by its X handle, which is often different from its LinkedIn tag. Verify each handle (an X user lookup, or the profile page): keep it only when the name and bio match. No match, no tag; write the name as plain text. A brand without an X account stays plain text. Photo tags work on images only, not on a GIF or video.

## Quote posts and intro posts

- **Quote post:** 1 to 3 lines on top of the quoted post: the author's receipt, disagreement or how they do it. Never present someone else's result as theirs.
- **Intro post:** the facts stated plainly (who, what they build, where it stands, the goal), a short personal list, a connect line. Lead with 1 result about the work, not a stack of vanity numbers.
- **Progress post:** where it stands, the number, what worked and what didn't, the next step. Honest beats impressive.

## Threads

High-value material goes out as a thread: a full system or playbook the author used, with their receipts, nothing held back. Bookmarks are the value signal. Everything else is 1 post.

- **Tweet 1 stands alone:** 2 short sentences, the proof then the promise, ending on 🧵 ("I grew <X> to <N>." / "I'd use this <N>-step system if I had to do it again 🧵"). Tweet 1 carries the proof and the image; most readers never open tweet 2.
- Then 1 tweet of context, 1 step per tweet under 280 characters with its picture, 1 honest line, the CTA tweet last.
- Count characters the way X does: `→` and many emoji weigh 2. Use the composer or supported tooling for exact counts.

## Borrowed shapes, only on request

When the author asks to write "like <creator>", study that creator's recent top posts and copy the shape (line 1 type, list markers, length, close), never their claims or results. Record the shape in `voice/formats.md` so it can be reused. Without a request, write in the author's own shape.

## Deliver

- Run the whole draft through the anti-slop checks above and the author's voice guide; name what you cut.
- 1 paste-ready post in a `text` block with its character count; a thread as numbered tweets.
- With Notion configured (`strategy/notion-schema.md`): the X copy on the card in 1 code block, above any LinkedIn source copy, Platform X. Link a new card to its source with `Parent post` only when the source is a separate LinkedIn card.
- When the same piece goes out on LinkedIn and X and the scheduler supports it (OXYGEN Publishing, `oxygen-linkedin-marketing`), the X version is a second channel of the same post with its own copy, not a separate post.
- A draft never authorizes posting or scheduling. x-planner schedules only on the author's go.
- Add the author's verdicts on the copy to `../x-planner/references/verdicts.md`.
