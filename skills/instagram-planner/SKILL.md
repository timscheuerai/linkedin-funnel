---
name: instagram-planner
description: Plan the author's Instagram week with them and shape each piece into a proper format. Checks that the 3 format families (talking reel, non-talking reel, carousel) are all covered, picks a sub-format per idea, writes the hook (type, wider angle, visual hook), the problem-pursuit-payoff beats, the b-roll shot list and the caption plan, and puts each pick on the content board. Use for "plan Instagram", "reels for this week", "make this a reel", "make this a carousel", "which format", "b-roll list" or "shot list". Not for the edit itself (video-editor, shorts-edit), the final platform copy and scheduling (shortform-platform-copy) or carousel rendering (graphics-designer).
---

Workspace: all context paths below (identity, audience, strategy, voice, brand, raw, output, index, log, workspace preferences and context scripts) resolve from `context/` in the kit root. Read both the root `AGENTS.md` and `context/AGENTS.md`. Skill-local `references/` resolve from this skill directory.

# Instagram planner

Short-form that is only value tips tends to feel soulless and too businessy. This skill turns an idea into a piece in a format that fits it, before anything is recorded or edited.

Read first, in this order:

1. `strategy/goals.md` and `strategy/pillars.md`: the author's Instagram goal and cadence, and what a piece is about. If the author documents a journey toward a public goal, that journey is the main source.
2. `voice/formats.md` and `inspiration/creator-bank.md`: the formats and creators the author already measures against.
3. `references/verdicts.md`: what the author picked and cut before.

House rules: the author's voice, numerals, numbers only from the cleared figures in `identity/proof.md`, private stories only when the author marked them public, nobody else on camera without their yes, and every draft read against the voice guide before the author sees it.

## The 3 families

Cover all 3 every week: they pull different growth levers.

| Family | Sub-formats | What it needs from the author |
|---|---|---|
| Talking | Yapping, Actionable, Voiceover, Vlog | A take or a day of phone footage |
| Non-talking | Story with timestamps, Read the caption, Before and after, Single b-roll plus text | Clips from the b-roll library and 1 line of text |
| Carousel | Lists, Split screen, Timeline, Step-by-step guide, Transformation, Day in the life | Photos of their life and the slide text |

A starting week for 7 reels plus carousels: 4 talking, 3 non-talking, 2 carousels. It is a default, not evidence; adjust it from measured results. The non-talking reels and the carousels are the cheap volume: they come out of the b-roll library and the week's long videos without a new recording.

How to choose the sub-format for an idea:

| The idea is | Use |
|---|---|
| Something that happened this week (a deal, a miss, a decision) | Vlog, or Yapping told as a story |
| A lesson the author can prove with their own result | Actionable, or a Step-by-step carousel |
| A feeling or a thought without footage of the moment | Voiceover over library clips |
| A change over time with dates or ages | Story with timestamps, Timeline or Transformation carousel |
| 2 states that contrast | Before and after, or Split screen |
| A longer text worth reading | Read the caption (1 clip, the hook on screen, the story in the caption) |
| 1 strong line | Single b-roll plus text |
| A set of things (tools, mistakes, rules) | Lists carousel |
| A normal day on the way to the goal | Day in the life carousel, or Vlog |

For a serial, episodes are events, not days: a day counter on its own does not pull. Offer an episode when something happened.

## The session

1. **Window.** Default the next 7 days. Query the content board (`strategy/notion-schema.md`) for every card in the window, all platforms. Count the Instagram cards per family. Name the family that is missing or thin before proposing anything.
2. **Sources.** In this order: the week's long videos (from `content-waterfall`), what happened toward the author's goal this week (ask for 3 events if the board does not show them), public story moments from `identity/backstory.md`, then formats the author is testing. Carousel ideas need photos: ask what they have on their phone.
3. **Slate.** 1 table, about 1.5 times the open slots, so the author can cut:

   | Day | Family | Sub-format | Idea | Hook, spoken or on screen | Feeling | Needs |
   |---|---|---|---|---|---|---|

   Write the hook in full. "Feeling" answers "what's in it for them": seen, understood, inspired, or the lesson. "Needs" is what the author has to record or find. Mark your pick per day; the choice is theirs.
4. **The author picks and cuts.** Keep their words. Ask nothing else until they have picked. A picked story with no outline yet gets a short interview first: what happened, what was at stake, what they decided, how it ended.
5. **Brief each pick** (below). 1 short brief per piece, in the card body.
6. **Board.** See "Board".
7. **Learn.** Add what they picked, cut and said to `references/verdicts.md`.

A single idea outside a session ("make this a reel") skips to step 5: propose the 2 best sub-formats with their hooks, let the author choose, then brief it.

## The brief

Every brief has the same 6 parts and fits on 1 screen.

1. **Format.** Family and sub-format, and why it fits this idea in 1 line.
2. **Hook.** For the author's own story (a vlog, a story reel, a check-in, a personal carousel), the hook is theirs: take it from the interview, name its type and write none for them. For any other piece, give 3 options from different types (positive statement, negative statement, authority, numbered list, transformation, relatable question). Each opens a curiosity gap and carries a stake, not a plan: a hook that makes the goal sound easy does not pull. Add the visual hook: what is on screen in second 1 (text over b-roll, a split screen with the contrast on top, a realisation line).
3. **Angle.** Start on something people outside the niche already care about (business, AI and tech, self development), then narrow: the idea they care about, the pain or desire, the author's industry, the lesson.
4. **Beats.** Problem, pursuit, payoff, 1 line each, from what really happened. For the author's own story, paste their outline as it is, labelled "your words, not new copy", and do not rewrite it. No invented scenes or feelings.
5. **Footage.** Per beat, the clip: a library segment by its id, or a shot to record. Missing clips become the shot list for the next recording block.
6. **Close.** The call to action and the caption plan. A rewatch line where it is honest ("Rewatch this and..."), a comment keyword only when a real resource exists (`lead-magnet-delivery`).

Family specifics:

- **Talking.** 3 bullets, no script (the moment, the turn, what now). Start the take on the result. Yapping and Vlog are the raw tier; Actionable can be the polished tier. The edit goes to `video-editor` or `shorts-edit`.
- **Non-talking.** 7 to 15 seconds. The on-screen text is the whole piece: write it word for word, 1 line per clip, inside the safe zone. For Read the caption, write the caption as the story (moment first, lesson last) and keep the screen text to the hook.
- **Carousel.** Hook slide, rehook slide (the reason to reach slide 3), content, CTA slide. Photos of the author's life, not a LinkedIn-post look. 1 idea per slide, 5 to 9 slides. Write every slide's text in the brief; rendering goes to `graphics-designer`.

## The b-roll library

Keep b-roll in a local library outside git and outside any cloud sync that might evict files. Keep camera files whole, one folder per shoot date and place. One recording often holds several emotions, so index each file in segments, 1 row per segment: location, emotion, story beat, shot, look, start and end in seconds, and where a 9:16 window sits. A small script that finds and cuts segments by those fields (with a vertical 1080 x 1920 crop) pays for itself fast.

- Useful emotion tags: Frustrated, Working, Thinking, Happy, Neutral. Useful beat tags: Problem, Pursuit, Payoff, Transition, Detail.
- Keep a set of ready short vertical clips (2 to 8 seconds, no audio) and use those first; cut a new one only when none fits.
- For a brief, read the index and name segments by id. Missing clips become the shot list for the next recording block. After each shoot, note what the library lacks (happy moments, night, a second outfit, walking-in shots from outside) and ask for those first.
- 4K horizontal footage gives a sharp enough 9:16 window for 1080 x 1920 when the subject stays in the middle third. A native vertical take is only needed for a tight close-up or a full-body shot.
- Screen clips show real text. Read the frame before one goes out.
- New footage: copy it into its dated folder, read frames every few seconds, add the segments to the index.

A b-roll reel that works:

- **A short sequence of shots.** The author sits down once (from the side, then the front), the working shots come from other angles and stay faceless (hands typing, the desk), and the payoff shot is held longest. About 6 seconds in all; 0.6 s is the shortest cut, for a burst only. No proof screenshot inside the reel; it belongs in the caption or the cover.
- **Colour.** B-roll gets a correction (white balance on a neutral surface), not a stylized look, unless the author's brand says otherwise (`brand/BRAND.md`).
- **Text.** The author's brand type, set large with 1 accent word, a small subline, no shadow or plate; the lines fade in one after another.

## Rules for the cut

Pass these to the edit skill with the brief:

- Everything readable sits inside the safe zone (for the cover, the 3:4 middle: y 240 to 1680 at 1920 high).
- B-roll cuts run about 0.6 s at the shortest, in a burst; a whole reel paces slower.
- Something changes every 2 to 5 seconds: a slight zoom, b-roll, the angle, an overlay, movement.
- Captions stay calm: if the author finds them forced or distracting, use the calmer option.

## Board

Each pick is a card on the content board (`strategy/notion-schema.md`): Name `IG: <idea>`, Platform `Instagram`, the family in a Format property if the board has one (otherwise as the first line of the brief), Status Idea until briefed and Creating once recorded, Pillar, Publish date, the brief in the body. Link it to the long video it comes from when the board uses parent posts. Scheduling runs through `shortform-platform-copy`, only on the author's go.

After the week, read each piece's plays, saves and follows against the author's own Instagram median and write the result into `references/verdicts.md`. A format that clearly beats the median becomes the author's own measured format.
