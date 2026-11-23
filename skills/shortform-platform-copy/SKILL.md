---
name: shortform-platform-copy
description: Write platform-specific LinkedIn, X, Instagram Reel and YouTube Shorts copy for the author's short videos from the video and their supplied facts, then put the short on their scheduler with a cover on every channel that takes one. Use when preparing, adapting, uploading or scheduling a short for several social platforms.
---

Workspace: all context paths below (identity, audience, strategy, voice, brand, raw, output, index, log, workspace preferences and context scripts) resolve from `context/` in the kit root. Read both the root `AGENTS.md` and `context/AGENTS.md`.

# Short-form platform copy

Write 1 paste-ready version for each requested platform from the actual video, its transcript and the author's brief. Watch or read the whole short first. Preserve the video's context and any historical timeframe. Public numbers come only from the cleared figures in `identity/proof.md` or facts the author supplies now. Do not invent attribution, conversion rates, tools, links or a call to action. Keep leads, email opt-ins and product signups distinct.

## 1 short, 4 versions

Use the relevant parts of `linkedin-copywriter`, `linkedin-hook-writer` and `x-copywriter`, the voice guide (`voice/linkedin-voice.md`, plus any X voice page the author keeps) and the current brief. Do not force an identical caption everywhere.

| Platform | What the copy does |
|---|---|
| LinkedIn | A useful standalone post with enough concrete steps to reproduce the playbook: what goes in, what comes out, how a resource is chosen and delivered, when those facts are supplied |
| X | A concise version that reads on its own, in the author's voice |
| Instagram | A Reel caption, emotion first (rules below) |
| YouTube Shorts | A short title and a concise description |

Match each platform's current field limits and the account's tier. Check exact text and character counts before saving. Respect the author's edits, cut repeated conclusions, and keep the X, Instagram and YouTube versions much shorter than LinkedIn when asked. Add platform instructions only where the author asks for them.

**Story shorts.** When the short documents the author's journey (an episode toward their public goal, if they have one, a vlog, a podcast or live clip), the copy carries the story, not a tip list. Open on the moment and what is at stake, say where it stands toward the goal when the video does, and keep the product as the setting, never the pitch. Add nothing the video does not show.

Read every version, whole, against the voice guide and remove generic or AI-sounding lines before the author sees it.

## Instagram captions

Instagram works emotion first with a bit of rational, the reverse of LinkedIn. The first line answers "what's in it for them" as a feeling (seen, understood, inspired) or as the lesson, and it does not repeat the spoken hook word for word. Use the brief from `instagram-planner` when the piece has one: its hook type, its close and its format.

- For a Read the caption reel, the caption is the piece: the moment first, the lesson last, short paragraphs.
- A rewatch line ("Rewatch this and...") only where the video earns it.
- A comment keyword only when the resource exists and delivery is set up (`lead-magnet-delivery`).
- A carousel caption adds what the slides leave out; it does not summarize them.

## Covers on every channel

Every short goes out with its cover on each channel that takes one: LinkedIn, Instagram and YouTube. X usually has no cover field and shows a frame of the video. Do not report a short as scheduled until every cover is checked.

1. **Make the cover.** 1080 x 1920 JPG under 2 MB: a calm frame (mouth closed) with the hook's key number or phrase as the title, every word inside the 3:4 middle that Instagram's grid shows (y 240 to 1680 at 1920 high). Build it with `graphics-designer` or the edit's own tooling (`video-editor`, `shorts-edit`). Look at it before uploading and save it next to the copy.
2. **Attach it per channel.** Upload the cover once and reuse the same asset on every channel that accepts a custom cover. A frame offset is only a fallback.
3. **Verify.** Read each scheduled post back and confirm its cover asset. After a YouTube upload goes live, check publicly that it plays and that the cover shows, with no copyright restriction.

## Schedule as 1 post

Scheduling uses OXYGEN Publishing through `oxygen-linkedin-marketing`, `youtube-publisher` for YouTube, or each platform's own scheduler. Discover the installed commands first; do not copy flags from memory.

- When the scheduler can group channels, put LinkedIn, X, Instagram and YouTube into 1 post with 1 record per channel, not 4 separate posts. Each channel can carry its own media file; reuse 1 upload where the file is the same.
- **No library music on YouTube.** Content ID can block a short with a stock or bank track worldwide within minutes. YouTube gets a version without that music as its own media, while the other channels keep the version with music. Never attach a final with a library track to a YouTube post.
- When the author asks to post "it" on YouTube, name the short first: compare what is already scheduled or published with the channel's uploads and confirm which short is meant. Never publish a long-form video unless the author names it.
- Verify accounts, media, text and that each post is still unapproved. Report the YouTube link separately from the group.

Drafting is not authorization to approve, schedule or publish. Show the versions to the author and act on their go.
