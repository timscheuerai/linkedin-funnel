# The content waterfall

[Back to the template](../README.md)

**Watch the full walkthrough on YouTube: https://www.youtube.com/watch?v=8z_GiPtnO80**

1 idea a week becomes 1 long video, and the video waterfalls into posts on every platform. Claude Code skills do most of the drafting; you pick the idea, record, read and edit. The rest of the week stays free for customers.

![The content waterfall](../assets/content-waterfall.gif)

[High-resolution graphic](../assets/content-waterfall@2x.png) · [Editable map (Excalidraw)](../assets/content-waterfall.excalidraw) · [Map as PNG](../assets/content-waterfall-map.png) · [The orchestrator skill](../skills/content-waterfall/SKILL.md)

## The 5 stages and the skills that run them

| Stage | What happens | Skills |
|---|---|---|
| 0 Find the idea | Scan what is hot on YouTube, X and LinkedIn, add last week's signals, pick 1 idea | [youtube-title-outlier-packaging](../skills/youtube-title-outlier-packaging/SKILL.md), [youtube-thumbnail-outlier-research](../skills/youtube-thumbnail-outlier-research/SKILL.md), [x-planner](../skills/x-planner/SKILL.md), the vidIQ plugin (optional), LinkedIn by hand |
| 1 Make the video | Title and thumbnail first, then the outline, record, cut, describe, upload | [youtube-script](../skills/youtube-script/SKILL.md), [talking-head-video-cut](../skills/talking-head-video-cut/SKILL.md), [longform-edit](../skills/longform-edit/SKILL.md), [youtube-thumbnail](../skills/youtube-thumbnail/SKILL.md), [youtube-description](../skills/youtube-description/SKILL.md) |
| 2 Grow the roots | The file: native video on LinkedIn and X. The argument: newsletter, X Article, lesson and resource posts. The transcript: chapter posts, graphics, proof posts, opinion posts, micro posts | [newsletter-writer](../skills/newsletter-writer/SKILL.md), [x-article-writer](../skills/x-article-writer/SKILL.md), [linkedin-copywriter](../skills/linkedin-copywriter/SKILL.md), [linkedin-hook-writer](../skills/linkedin-hook-writer/SKILL.md), [x-planner](../skills/x-planner/SKILL.md), [graphics-designer](../skills/graphics-designer/SKILL.md), [flowchart](../skills/flowchart/SKILL.md), [repurpose-content](../skills/repurpose-content/SKILL.md) |
| 3 Ship it | Every piece on 1 board, dated from the video's release day; you give the go, the week gets scheduled | [content-waterfall](../skills/content-waterfall/SKILL.md), [Notion](notion.md) (optional), [oxygen-linkedin-marketing](../skills/oxygen-linkedin-marketing/SKILL.md) (optional) |
| 4 Convert the engagers | Collect who engaged, check who fits, deliver the resource to commenters, start warm conversations | [Profile Watcher](profile-watcher.md), [qualification](qualification.md), [lead-magnet-delivery](../skills/lead-magnet-delivery/SKILL.md), [oxygen-sequencer](../skills/oxygen-sequencer/SKILL.md), [linkedin-unibox-reply](../skills/linkedin-unibox-reply/SKILL.md), [DM framework](dm-conversion.md) |

Every week closes the loop: rank the winners, collect the best questions from the comments, and pick the next idea from them.

## Set it up in Claude Code

1. Click **[Use this template](https://github.com/new?template_name=linkedin-funnel&template_owner=timscheuerai)** and create your own repository. Choose **Private** if you will add personal or customer information.
2. Clone it and open the folder in Claude Code. The skills in `skills/` are discovered through `.claude/skills`.
3. Fill your context first: run the starter prompt in the [README](../README.md#start-here) so your positioning, audience and voice exist. The waterfall writes in your voice only after that.
4. Optional: install the vidIQ plugin for YouTube trend research, set up [Notion](notion.md) for the board, and connect [OXYGEN](oxygen.md) for scheduling, engager collection and resource delivery. Everything else works without them.
5. Paste this prompt with your idea of the week:

```text
Read AGENTS.md, README.md and guides/content-waterfall.md. Run the
content-waterfall skill for this week. My idea: [YOUR IDEA, OR "show me a
slate"]. My video goes live on [DATE]. Start with stage 0 if I have no idea
yet, otherwise write the brief: packaging first, then the outline. Plan the
pieces dated from my release day and draft nothing that needs proof I
haven't given you. Ask me only what I alone can decide.
```

After you record, hand over the raw file or the YouTube link with:

```text
Here is my recording: [PATH OR YOUTUBE URL]. Continue the content
waterfall from stage 4: cut it, write the description and chapters, then
draft the newsletter first and the rest of the roots from it.
```

## What to expect

- About a day of work a week once the system is set up: the idea, the recording, and reading and editing the drafts.
- Volume comes from reuse, not from writing more: 1 video feeds the newsletter, the X Article, the native uploads and a week of posts.
- The idea matters most. Check demand before you record; content only about what you find interesting rarely travels.
- Without a system, volume burns you out. Batch the work into 1 content day.

Nothing here publishes, schedules or sends by itself. Every post, newsletter and message waits for your go.
