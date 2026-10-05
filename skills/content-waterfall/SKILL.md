---
name: content-waterfall
description: Run a weekly content waterfall: find the idea of the week from what is hot on YouTube, X and LinkedIn, make 1 long video, grow its 3 roots into posts on every platform, ship the week and turn the engagers into conversations. Use when the author gives the idea of the week, wants posts from a video, hands over a recording or YouTube link, or asks to repurpose. Orchestrates the stage skills.
---

Workspace: all context paths below (identity, audience, strategy, voice, brand, raw, output, index, log, workspace preferences and context scripts) resolve from `context/` in the kit root. Read both the root `AGENTS.md` and `context/AGENTS.md`. Skill-local `references/` resolve from this skill directory.

# Content waterfall

1 idea a week becomes 1 long video, and everything else flows down from it. The idea is the most important piece, so it gets its own stage. The live video is the trunk, 3 roots grow from it in parallel, idea posts fill open slots after the release week, and the people who engage become conversations. The full walkthrough is on YouTube: https://www.youtube.com/watch?v=8z_GiPtnO80. The map is `assets/content-waterfall.excalidraw` in the kit root; the guide is `guides/content-waterfall.md`.

This skill is the operating order. Each stage has its own skill; use it, do not redo its work here.

## The stages at a glance

| Stage | What happens | Output | The author decides |
|---|---|---|---|
| 0 Idea | Scan what is hot on YouTube, X and LinkedIn, add last week's signals | A slate of 3 to 5 ideas with proof of heat | The pick |
| 1 Brief | Packaging first, then the brief and a video outline | 1 brief page (`references/brief-template.md`) | Release date; their verdict when the video is a review |
| 2 Board | The big post plus its dated sub-posts | 1 card with its sub-posts, or a dated plan in chat | Nothing, unless a date collides |
| 3 Record | The author records from the outline | Raw recording | Everything on camera |
| 4 Package | Cut, transcript, titles, description, thumbnail, upload | The live YouTube video | Title and thumbnail pick; the upload |
| 5 Draft | Root by root, newsletter first; mine the transcript for idea posts | Copy in each sub-post | Edits; which ideas stand on their own |
| 6 Schedule | Queue each piece on its date | Scheduled posts, a newsletter draft | Go for anything that publishes or sends |
| 7 Convert | Engagers into conversations | Signals, qualified people, delivered resources, DM drafts | Every send that is not already granted |
| 8 Close | Mark what shipped, rank the winners, collect questions | Results in the brief, next idea | The next idea; what doubles down |

Enter where the work is. A raw recording starts at stage 4 and a YouTube link at stage 5, but create the big post first if it is missing.

## Standing rules

- The idea is the author's. The slate proposes 3 to 5 ideas with proof of heat; the author picks. Never pick or invent the idea of the week for them.
- Truth over packaging: every title, thumbnail and newsletter claim must be shown in the video. Numbers come only from `identity/proof.md`; drop planned numbers the video does not show.
- Write in the author's voice (`voice/linkedin-voice.md`). When the author calls a line generic or AI-sounding, rewrite the section from their own words.
- Link videos with the full `https://www.youtube.com/watch?v=<id>` URL. Never a shortener: link shorteners trip spam and phishing filters.
- 1 big post per waterfall with dated sub-posts, not a board full of separate cards. Every sub-post has a status, platform and date.
- Date everything from the video's release day (D). The newsletter and the X Article go out on D; posts follow.
- Text, image and graphic pieces carry the week. The video itself goes out only as the native upload of the finished video on LinkedIn and X.
- Drafting is not publishing. Nothing is sent, scheduled or posted without the author's go.

## The system: 1 trunk, 3 roots

| Part | What it reuses | Pieces | Funnel job |
|---|---|---|---|
| Trunk | The live video: the file, the argument, the transcript | The YouTube video | |
| Root 1, the file | The video itself | LinkedIn video, X video: the native upload | Reach |
| Root 2, the argument | The newsletter's argument | Newsletter, X Article, lesson post, resource post | Belief; the resource post is Signup |
| Root 3, the transcript | Ideas that stand on their own | Chapter post, graphic, proof post, opinion post, micro posts | Reach, or Belief for graphic and proof |

Timing from D: the video, newsletter, X Article and X video on D; the LinkedIn video and lesson that week; the resource post on D+7. Idea posts fill open slots after that; the rest waits in a backlog. Winners get reposted on the other platform at the close.

Platform jobs: YouTube is the library, the newsletter the list you own, X the builders, LinkedIn the buyers. The funnel job (Reach, Belief, Signup) is a writing decision per piece, set before drafting; it decides the hook and the ask.

## Stage 0: Find the idea

| Scan | Tools | What to bring back |
|---|---|---|
| Your signals | Last week's close: winners, the best questions from the comments, customer wins and calls | What already worked for this audience |
| YouTube | The vidIQ plugin if installed (trend radar, video ideas), `youtube-thumbnail-outlier-research`, `youtube-title-outlier-packaging` | Outliers and rising topics in the niche, with their titles and thumbnails |
| X | X Radar (X Premium) on your keywords, X search, the viral lane of `x-planner` | Posts going viral in the niche |
| LinkedIn | By hand: scroll the creators you follow, LinkedIn search, saved posts | Outlier posts, with their hooks |

The slate: 3 to 5 ideas, each with its proof of heat (the outlier or the numbers), the pillar from `strategy/pillars.md`, the funnel job and the receipt the author can show on camera. Prefer ideas with more demand than supply. Content only about what the author finds interesting is the most common miss.

## Stage 1: Brief

1. Take the picked idea in the author's words. Choose 1 pillar and 1 funnel stage; ground in `identity/positioning.md`, `audience/ideal-follower.md` and the voice guide.
2. Stance check: read what the author published on the topic recently. The video builds on it or names the change.
3. Facts: check every product, model or market claim at its source and date it.
4. Worked example and resource: prefer what the author can show on screen and what already exists. The resource is usually an existing kit, not a new build.
5. Packaging first: 2 titles (`youtube-title-outlier-packaging`) and 2 thumbnail directions (`youtube-thumbnail`) before the outline. The outline has to deliver that promise.
6. Outline: chapters with what is on screen and which claim each makes deliverable. 1 chapter answers 1 buyer objection, so it can be sent as an answer in a DM later. Use `youtube-script` when a full script helps.
7. Write the brief from `references/brief-template.md`.

Ask the author only what they alone know: the release date and their verdict. Decide the rest and list it under open decisions.

## Stage 2: Board

Query the board for the dates around the release and for cards on the same topic first; reuse a card that exists. With Notion configured (`guides/notion.md`, `strategy/notion-schema.md`): 1 big post for the video, each piece a sub-post linked to it with a status, platform and date. Without Notion, return the dated plan in chat and keep it in the brief.

Default sub-posts from release day D:

| Day | Piece | Platform | Root, job | Skill |
|---|---|---|---|---|
| D | The video (the big post) | YouTube | Trunk | stage 4 |
| D | Newsletter | Newsletter | Root 2, Belief | `newsletter-writer` |
| D | X Article | X | Root 2, Belief | `x-article-writer` |
| D | The video is live | X | Root 1, Reach | `x-copywriter` |
| Author's pick | The video, native | LinkedIn | Root 1, Reach | `linkedin-copywriter` |
| That week's slot | The lesson | LinkedIn | Root 2, Belief | `linkedin-copywriter` |
| D+7 | The resource post | LinkedIn | Root 2, Signup | `linkedin-copywriter`, `lead-magnet-delivery` |
| Open slots | 1 or 2 idea posts after the harvest | LinkedIn | Root 3 | `linkedin-copywriter` |

Create everything else only when it is picked: micro posts, chapter threads, reposts of winners. That keeps the card near 8 sub-posts, not 30. Other X posts are planned with the author in `x-planner`.

## Stage 3: Record

The author records from the outline. Remind them: a clean screen, accounts that are safe to show, no client data on screen, 1 dry run.

## Stage 4: Package

| # | Step | Skill | Done when |
|---|---|---|---|
| 1 | Cut | `talking-head-video-cut`, or `longform-edit` for a designed intro | Only false starts, dead air and the tail removed from screen demos; QA passed |
| 2 | Final-cut transcript | `video-use` transcription | Chapter times come from the final cut, not the raw file |
| 3 | Promise check, title A/B | `youtube-title-outlier-packaging` | Both titles deliverable from the cut |
| 4 | Description and chapters | `youtube-description` | Paste-ready block |
| 5 | Thumbnail | `youtube-thumbnail` | Checked at 1280 x 720 and 320 x 180 |
| 6 | Upload | The author, or `youtube-publisher` on request | The YouTube video ID; private first |

## Stage 5: Draft

Write the newsletter first; it is the approved argument every other piece reuses. Then the X Article from the newsletter, the X video post, then the LinkedIn posts. Do not re-derive the argument from the transcript for each piece. Run LinkedIn copy through `linkedin-copywriter` and `linkedin-hook-writer`. On LinkedIn, links go in the first comment and the post says so.

Root 3, the harvest: read the final-cut transcript and tag every idea by type: chapter, framework, proof moment, strong claim, line, receipt, take. Ask of each: does it stand on its own without the video? Yes: a chapter post, a graphic (`graphics-designer`, `flowchart`), a proof post or an opinion post, or a micro post through `x-planner`. No: the backlog. `repurpose-content` helps with the split.

## Stage 6: Schedule

Queue each piece on its date only on the author's go: OXYGEN Publishing (`oxygen-linkedin-marketing`) or the platform's own scheduler. The newsletter stays a draft in the email tool until approved. Keep each status truthful: drafted until it is live. Keep 1 LinkedIn post a day; idea posts fill open slots, never a second post.

## Stage 7: Convert

Impressions alone do not pay. Every engager becomes a signal, the right ones a conversation.

- Collect engagement with OXYGEN's Profile Watcher (`guides/profile-watcher.md`) and qualify company and person fit separately (`guides/qualification.md`).
- People who commented the keyword on a resource post get the resource by DM and nothing else: `lead-magnet-delivery`.
- Fitting engagers get a capped, reply-stopped warm sequence (`oxygen-sequencer`) that asks what they are working on.
- Replies: `linkedin-unibox-reply` drafts, the author sends (`oxygen-unibox`, `guides/dm-conversion.md`). Answer an objection with the chapter that answers it: the full YouTube URL plus `&t=<seconds>s`.
- No new workflow, cohort or send without the author's go.

## Stage 8: Close

Mark each piece published as it goes live. Rank the week's pieces, including older ones still running. The top 1 or 2 are candidates for a repost on the other platform and for the next video. Customer wins go into the next brief only with permission and cleared numbers. Bring the winners and the best questions to the author with the ask for next week's idea; the idea stays theirs. Record results, replies and time spent in the brief and `log.md`.

## Hand-off

After each stage, tell the author the file, card or ID and the next stage. Keep the brief current: titles, description, thumbnail files, dates and links.
