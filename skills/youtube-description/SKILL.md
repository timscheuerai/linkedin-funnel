---
name: youtube-description
description: Create a YouTube description, resource links and chapters from the actual final video or timestamped transcript.
---

# Package the final video

Read the final cut or its timestamped transcript, viewer promise and actual offer links. If only a script exists, label timings provisional and do not claim final chapters.

Open with exactly 1 sentence of at most about 16 words that says what the video is, built on the main search phrase a stranger would type ("content strategy", "LinkedIn lead generation"), plus the main tool when it fits. It shows in search and above "more". The links, next step and chapters follow; no second sentence. Leave internal numbers and tool lists to the video and the chapters; no keyword stuffing, no hashtag block. Example: "How I use Claude Code as a content team to turn 1 video into a week of posts."

Add useful resources with verified URLs and clear labels. Link YouTube videos with the full `https://www.youtube.com/watch?v=<id>` URL, never a shortener. Links to the author's own site carry UTM parameters (source `youtube`, campaign = the waterfall's slug) so signups from YouTube are attributed to it; a pinned comment's link gets its own content tag. GitHub, LinkedIn and X links stay clean. Include disclosures or credits from the actual brief, and one relevant next step. Do not invent a sponsor, product entitlement or download link.

Derive chapter starts from the final cut. Verify sequence, labels and destination platform chapter rules using current documentation when exact upload readiness matters. Check that cuts did not shift old script timestamps.

Deliver a paste-ready description, proposed title if asked, chapters and a separate list of unresolved links or timing checks. Use `youtube-publisher` only for an explicitly requested upload or publishing action.
