---
name: content-waterfall
description: Run a weekly content waterfall: find the idea of the week from what is hot on YouTube, X and LinkedIn, make 1 or 2 long videos, grow each video's 3 roots into a newsletter, an X Article, posts and short-form on every platform, ship the week and turn the engagers into conversations. Use when the author gives the idea of the week, wants posts or a newsletter from a video, hands over a recording or YouTube link, or asks to repurpose. Orchestrates the stage skills.
---

Workspace: all context paths below (identity, audience, strategy, voice, brand, raw, output, index, log, workspace preferences and context scripts) resolve from `context/` in the kit root. Read both the root `AGENTS.md` and `context/AGENTS.md`. Skill-local `references/` resolve from this skill directory.

# Content waterfall

1 idea a week becomes 1 or 2 long videos, and everything else flows down from them. A common pair is a tutorial and a story video (a vlog or behind-the-scenes episode); each video is its own trunk. Plan the week from the videos down, never channel by channel. The idea is the most important piece, so it gets its own stage. Each live video is a trunk, 3 roots grow from it in parallel, idea posts fill open slots after the release week, and the people who engage become conversations. The full walkthrough is on YouTube: https://www.youtube.com/watch?v=8z_GiPtnO80. The map is `assets/content-waterfall.excalidraw` in the kit root; the guide is `guides/content-waterfall.md`.

This skill is the operating order. Each stage has its own skill; use it, do not redo its work here.

## The stages at a glance

| Stage | What happens | Output | The author decides |
|---|---|---|---|
| 0 Idea | Scan what is hot on YouTube, X and LinkedIn, add last week's signals | A slate of 3 to 5 ideas with proof of heat | The pick |
| 1 Brief | Packaging first, then the brief and a video outline | 1 brief page (`references/brief-template.md`) | Release date; their verdict when the video is a review |
| 2 Board | The big post as the video card only; sub-posts planned while the video is made | 1 card, its sub-posts added later, or a dated plan in chat | Nothing, unless a date collides |
| 3 Record | The author records from the outline | Raw recording | Everything on camera |
| 4 Package | Cut, transcript, titles, description, thumbnail, upload | The live YouTube video | Title and thumbnail pick; the upload |
| 5 Draft | Root by root, newsletter first; mine the transcript for idea posts | Copy in each sub-post | Edits; which ideas stand on their own |
| 6 Schedule | Queue each piece on its date | Scheduled posts, a newsletter draft | Go for anything that publishes or sends |
| 7 Convert | Engagers into conversations | Signals, qualified people, delivered resources, DM drafts | Every send that is not already granted |
| 8 Close | Review what shipped, rank the winners, collect questions | Results in the brief, next idea | The next idea; what doubles down |

Enter where the work is. A raw recording starts at stage 4 and a YouTube link at stage 5, but create the big post first if it is missing. Before the cut, the video's card must hold its title and thumbnail research; if it does not, start that research first (in background agents when available), then edit.

## Standing rules

- The idea is the author's. The slate proposes 3 to 5 ideas with proof of heat; the author picks. Never pick or invent the idea of the week for them; sharpen the one they pick.
- Truth over packaging: every title, thumbnail and newsletter claim must be shown in the video. Numbers come only from `identity/proof.md`; drop planned numbers the video does not show.
- Write in the author's voice (`voice/linkedin-voice.md`). Check the whole draft for generic AI phrasing before the author sees it, not only the lines they flagged. When the author calls a line generic or AI-sounding, rewrite the section from their own words instead of patching it.
- Act on small feedback immediately and show the result; do not ask again.
- Link videos with the full `https://www.youtube.com/watch?v=<id>` URL. Never a shortener: link shorteners trip spam and phishing filters.
- Every link to the author's own site carries UTM parameters: source = the platform (`linkedin`, `x`, `youtube`, `newsletter`), campaign = 1 short slug per waterfall, the same on every platform. Record the slug in the brief so signups can be traced back to the week.
- 1 big post per video with dated sub-posts, not a board full of separate cards. Every sub-post has a status, platform and date.
- Date everything from the video's release day (D). The newsletter and the X Article go out on D with the main video; posts follow.
- Short-form is personal storytelling at volume. Shorts, reels and clips document the author's journey toward a goal they have made public, through vlogs, live breakdowns, podcasts and short check-ins; tips are the minority. Mine the week for episodes: the brief notes what happened toward the goal, and the close records which story shorts worked. Short video copy for each platform comes from `shortform-platform-copy`.
- Instagram is planned in its own session with `instagram-planner`: it checks that talking reels, non-talking reels and carousels are all covered in the week, picks the sub-format per idea and writes each brief with the hook, the beats and the shot list. The waterfall hands it the week's videos as sources.
- Drafting is not publishing. Nothing is sent, scheduled or posted without the author's go.

## The system: 1 trunk, 3 roots

| Part | What it reuses | Pieces | Funnel job |
|---|---|---|---|
| Trunk | The live video: the file, the argument, the transcript. Customer wins feed it too | The YouTube video | |
| Root 1, the file | The video itself | LinkedIn video, X video: the native upload | Reach |
| Root 2, the argument | The newsletter's argument | Newsletter, X Article, lesson post, resource post | Belief; the resource post is Signup |
| Root 3, the transcript | Ideas that stand on their own | Chapter post, graphic, proof post, opinion post, micro posts, short-form episodes | Reach, or Belief for graphic and proof |

With 2 videos a week, split the roots by video: the tutorial feeds the newsletter, the X Article, the LinkedIn video and lesson post and 2 to 3 reels; the story video feeds the storytelling reels, a building-in-public thread on X and 1 or 2 LinkedIn posts.

Timing from D: the video, newsletter, X Article and X video on D; the LinkedIn video and lesson that week; the resource post on D+7. Idea posts fill open slots after that; the rest waits in a backlog. Winners get reposted on the other platform at the close.

Platform jobs: YouTube is the library, the newsletter the list you own, X the builders, LinkedIn the buyers. The funnel job (Reach, Belief, Signup) is a writing decision per piece, set before drafting; it decides the hook and the ask.

## Stage 0: Find the idea

| Scan | Tools | What to bring back |
|---|---|---|
| Your signals | Last week's close and `content-review` result: winners, the best questions from the comments, customer wins and calls | What already worked for this audience |
| YouTube | `youtube-video-research` gate 1 (depth-first scan of the niche, gap probes), then the vidIQ plugin if installed | Scored ideas: a wave that is hot right now, applied to the outcome the audience buys, while the angle is still open |
| X | X Radar (X Premium) on your keywords, X search through `x-research`, the viral lane of `x-planner` | Posts going viral in the niche |
| LinkedIn | By hand: scroll the creators you follow, LinkedIn search, saved posts | Outlier posts, with their hooks |

The slate: 3 to 5 ideas, each with its proof of heat (the outlier or the numbers), the pillar from `strategy/pillars.md`, the funnel job and the receipt the author can show on camera. Only ideas that pass the `youtube-video-research` scorecard go on the slate as video candidates. When the author's channel has a track record, check each video candidate against what their own past videos show works; topics that stalled on YouTube can still feed LinkedIn and X. Prefer ideas with more demand than supply. Content only about what the author finds interesting is the most common miss.

## Stage 1: Brief

1. Take the picked idea in the author's words. Choose 1 pillar and 1 funnel stage; ground in `identity/positioning.md`, `audience/ideal-follower.md` and the voice guide. When a real event supports the idea, capture it first (`capture-context`, `templates/context-interview.md`): the situation, the stakes, the author's actual decision or reaction, the outcome and what is still uncertain. Keep a concrete reader gift; do not invent drama or replace a useful practical explanation with a story.
2. Stance check: read what the author published on the topic recently. The video builds on it or names the change.
3. Facts: check every product, model or market claim at its source and date it.
4. Worked example and resource: prefer what the author can show on screen and what already exists. The resource is usually an existing kit, not a new build.
5. Packaging first: 2 titles (`youtube-title-outlier-packaging`) and 2 thumbnail directions (`youtube-thumbnail`) before the outline, each structure validated outside the niche (`youtube-video-research` gate 2) and marked validated in the packaging library; a worn structure stays out. The outline has to deliver that promise; the final pick waits for the cut.
6. Outline: the first 60 seconds scripted word for word (`youtube-video-research` gate 3), then chapters with what is on screen and which claim each makes deliverable. 1 chapter answers 1 buyer objection, so it can be sent as an answer in a DM later. Use `youtube-script` when a full script helps.
7. Check for work already under way: title, thumbnail or research work for the same video from an earlier session. Link it; do not redo it.
8. Write the brief from `references/brief-template.md`.

Ask the author only what they alone know: the release date and their verdict. Decide the rest and list it under open decisions.

## Stage 2: Board

Query the board for the dates around the release and for cards on the same topic first; reuse a card that exists and flag duplicates instead of creating a second one. With Notion configured (`guides/notion.md`, `strategy/notion-schema.md`): 1 big post for each video, each piece a sub-post linked to it with a status, platform and date. Without Notion, return the dated plan in chat and keep it in the brief.

A new video card starts as the video card only, with its status set to in progress. Plan the sub-posts below while the video is being made, not when the card is created.

Default sub-posts from release day D:

| Day | Piece | Platform | Root, job | Skill |
|---|---|---|---|---|
| D | The video (the big post) | YouTube | Trunk | stage 4 |
| D | Newsletter | Newsletter | Root 2, Belief | `newsletter-writer` |
| D | X Article | X | Root 2, Belief | `x-article-writer` |
| D | The video is live | X | Root 1, Reach | `x-article-writer` (the video post) |
| Author's pick | The video, native | LinkedIn | Root 1, Reach | `linkedin-copywriter` |
| That week's slot | The lesson | LinkedIn | Root 2, Belief | `linkedin-copywriter` |
| D+7 | The resource post | LinkedIn | Root 2, Signup: the keyword steps sit on the graphic; the text only says to follow them | `linkedin-copywriter`, `lead-magnet-delivery` |
| Open slots | 1 or 2 idea posts after the harvest | LinkedIn | Root 3 | `linkedin-copywriter` |

Create everything else only when it is picked: micro posts, chapter threads, reposts of winners. That keeps the card near 8 sub-posts, not 30. Other X posts are planned with the author in `x-planner`, which can still pick an angle from the video if it stands on its own. The LinkedIn lesson post is that pillar's post for the week, so `week-posts` drafts only the other pillars.

## Stage 3: Record

The author records from the outline. Remind them: a clean screen, accounts that are safe to show, no client data on screen, 1 dry run.

## Stage 4: Package

| # | Step | Skill | Done when |
|---|---|---|---|
| 1 | Cut | `talking-head-video-cut`, or `longform-edit` for a designed intro | Screen demos keep everything from the first word of the final complete take to just after the sign-off; only false starts and the tail go; QA passed |
| 2 | Final-cut transcript | `video-use` transcription | Chapter times come from the final cut, not the raw file |
| 3 | Promise check, title A/B | `youtube-title-outlier-packaging` | Both titles deliverable from the cut; if not, repackage |
| 4 | Description and chapters | `youtube-description` | Paste-ready block |
| 5 | Thumbnail | `youtube-thumbnail` | Checked at 1280 x 720 and 320 x 180 |
| 6 | Upload | The author, or `youtube-publisher` on request | The YouTube video ID; private first |

File the title and thumbnail research on the video's own card, never on a LinkedIn or X sibling, and render the thumbnails once it is in. Package the honest verdict: an experiment plus its verdict is a strong title structure for a review. If the platform asks for an identity confirmation an agent cannot pass, the author uploads from a prepared folder (the video, both thumbnails, an upload note with title, description and chapters). Record the video URL in the brief once it exists.

## Stage 5: Draft

Write the newsletter first with `newsletter-writer`; it is the approved argument every other piece reuses. Then the X Article from the newsletter, the X video post, then the LinkedIn posts. Do not re-derive the argument from the transcript for each piece. Run LinkedIn copy through `linkedin-copywriter` and `linkedin-hook-writer`. On LinkedIn, links go in the first comment and the post says so.

Root 3, the harvest: read the final-cut transcript and tag every idea by type: chapter, framework, proof moment, strong claim, line, receipt, take, story beat. Ask of each: does it stand on its own without the video? Yes: a chapter post, a graphic (`graphics-designer`, `flowchart`), a proof post, an opinion post, a short-form episode (`shortform-platform-copy`, `instagram-planner`) or a micro post through `x-planner`. No: the backlog. `repurpose-content` helps with the split.

## Stage 6: Schedule

Queue each piece on its date only on the author's go: OXYGEN Publishing (`oxygen-linkedin-marketing`) or the platform's own scheduler. The newsletter stays a draft in the email tool, checked with its preview, until approved. If the scheduler does not support native X Articles, hand over the draft and assets for the X editor. Keep each status truthful: in progress until it is live. Keep 1 LinkedIn post a day; idea posts fill open slots, never a second post.

## Stage 7: Convert

Impressions alone do not pay. Every engager becomes a signal, the right ones a conversation.

- Collect engagement with OXYGEN's Profile Watcher (`guides/profile-watcher.md`) and qualify company and person fit separately (`guides/qualification.md`).
- People who commented the keyword on a resource post get the resource by DM and nothing else: `lead-magnet-delivery`.
- Fitting engagers get a capped, reply-stopped warm sequence (`oxygen-sequencer`) that asks what they are working on.
- Replies: `linkedin-unibox-reply` drafts, the author sends (`oxygen-unibox`, `guides/dm-conversion.md`). Answer an objection with the chapter that answers it: the full YouTube URL plus `&t=<seconds>s`.
- No new workflow, cohort or send without the author's go.

## Stage 8: Close

Run `content-review` on the released pieces: the evidence, audience and funnel fit, product outcomes and production effort. Mark missing data explicitly and bring the review's selected experiment back into stage 0.

Mark each piece published as it goes live. Once the video is public, archive the final file, thumbnails, upload note and raw recording where the author keeps finished work. Rank the week's pieces, including older ones still running. The top 1 or 2 are candidates for a repost on the other platform (a LinkedIn winner to X through `x-planner`, an X winner to LinkedIn) and for the next video. Customer wins go into the next brief only with permission and cleared numbers. Bring the winners and the best questions to the author with the ask for next week's idea; the idea stays theirs. Record results, replies and time spent in the brief and `log.md`.

## Hand-off

After each stage, tell the author the file, card or ID and the next stage. Keep the brief current: titles, description, thumbnail files, dates and links.
