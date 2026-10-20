# Comment voice

How the author's LinkedIn comments under other creators' posts are written. Comments on the author's own posts they answer themselves, so those are not drafted. `voice/linkedin-voice.md` in `context/` owns how the author writes posts; this page owns comments, because comment voice is not post voice. `scripts/render_queue.py` enforces the mechanical rules.

> Status: the measured sections start empty. Fill them in setup step 2 ([setup.md](setup.md)) from the author's real comments, then keep them current from [verdicts.md](verdicts.md). Until they are filled, draft with the defaults below and say so in the hand over.

## Measured shape

Fill from the author's last 50 to 100 comments under other people's posts (automated deliveries and answers on their own posts left out).

| Measure | Value |
|---|---|
| Comments read | |
| Median words | |
| Share of 1 liners | |
| Longest comment (words) and what it was | |
| How they usually open | |
| How they usually close | |

## Texture

Counted, not guessed: emojis and where they sit, laughs, the words they use for people, lowercase starts, punctuation habits, numbers and separators. Note how often each shows up; texture belongs in about half of the comments, never all.

-

## Moves

The author's moves, each with a verbatim line from their real comments. Draft keys stay fixed so the page and `page_feedback.py` can count them; replace the right column with the author's own lines.

| Key | Label | When | The author's version |
|---|---|---|---|
| `plain_opinion` | Plain opinion | A take they share or doubt | |
| `plain_answer` | Plain answer | The post asks something | |
| `honest_opinion` | Honest, then opinion | No clean answer exists | |
| `next_step` | My next step | The post describes a play they run too | |
| `what_i_use` | What I use | Tool or workflow posts | |
| `real_question` | Real question | They want to know how the author of the post does it | |
| `disagree` | Warm disagreement | They think the post is wrong, for a reason from their own work | |
| `agree_angle` | Agree + my angle | They agree and have 1 angle to add | |
| `my_story` | My story | A personal parallel from [personal-bank.md](personal-bank.md) | |
| `joke` | Joke | Something is funny and they can stand behind it | |
| `peer_win` | Win for a peer | Someone they know ships or grows | |

## How to write one

1. **Look the author of the post up first.** The watchlist `notes` and `scripts/personal_refs.py` say whether there is a shared history (a live, a podcast, a post that names them). That sets the register: someone the author knows gets their first name and more warmth; a stranger's post gets a comment that earns attention on its own. Private history (DMs, calls, deals) never shows up in a public comment.
2. **Read the post as the author.** What caught them? What would they say to the post's author in person? Start there, never with a summary of the post.
3. **Pick 1 move** from the table. A story only when it is the direct parallel (2 to 4 comments in 10).
4. **Write it the way the author types on their phone.** Then cut the setup, the summary and every word that only sounds smart.
5. **Read it out loud as the author.** If it could sit under any post, reads like a tip or grades the post, start again.

## Default shape

Until the measured shape says otherwise:

- Default 1 line, 6 to 30 words. Most of a batch should be 1 liners.
- 2 short paragraphs only for an honest first line and then an opinion, or a reaction and then 1 thing from the author's own work.
- A short numbered list only when answering the post's question with steps.
- From 2 sentences on, a blank line between them.
- At most 70 words and 450 characters.
- Questions only when the author would really want the answer, at most 4 in 10.

## What makes comments read like a bot

Each of these came from a real batch that was rejected as reading "like a bot":

- **1 shape for everything.** A verdict line, a blank line, then a receipt, in 9 comments of 10. Real people don't comment in a template.
- **Grading the post** instead of talking to its author: "Number 5 is the one I'd underline twice", "The approve step is the part I'd never drop".
- **The same 3 to 5 receipts on repeat.** Comments are public on the author's activity page; readers notice.
- **Post voice in a comment.** Tidy 2 or 3 paragraph mini posts, when the author's real comments are mostly 1 line.
- **Nothing personal, or the whole bio.** 0 personal moments reads generic; a story in every comment reads like a bot that found the bio.
- **Slogans and compliments.** "In person beats any amount of DMs." "Congrats, that's massive."
- **Credentials nobody asked for.** Years of experience, age, team size, a stack tour. Drop them for a plain take.
- **Copywriter idioms** ("they raised their hand") where the author would say it plainly ("they were interested once").

The shape of a bot comment against a human one (shape only; the facts in the author's version must come from their own pages):

> Bot: "Great breakdown! The point about hooks is the one most people miss. I've seen the same with my clients: once we fixed the first line, everything changed."
>
> Human: "The 'just be consistent' advice without ever saying what to post is my favourite haha"

## Starting hypotheses about taste

These held for one creator over several rounds. Treat them as defaults to test, and replace them with the author's own verdicts as they come in:

- A concrete practice, tool or result beats a soft take. On a technical post, give the concrete improvement the author would make (which tool, which order, the cost reason) rather than a question.
- Under a results or hype post, react first in the author's words, then 1 result or trick if they have one.
- No setup showcases unless the post is about exactly that setup.
- Don't reuse 1 failure story as a general hook; use it only where the post is about the same thing.
- Use the newest cleared number from `identity/proof.md`, not an older one.
- Bold, slightly edgy lines in the author's own words survive; sanded-down takes get skipped.

## Never

- "Great post", "Love this", "So true", "100%", "Spot on", "Well said", "Couldn't agree more", "Thanks for sharing", "This resonates", "Insightful" as an opener.
- Stock words: orchestrates, leverages, streamlines, seamless, unlock, game changer, delve, crucial, elevate, empower, testament, thrilled (the renderer blocks them; add the author's own in `extra_banned_words`).
- Invented anecdotes, feelings, clients, numbers or plans. If a sentence about the author has no source in `context/`, cut it or make it a question.
- Claims that the author's product has something that is not live.
- Dashes, hashtags, links, "DM me", "let's connect" or pitches. The author's company by name in at most 1 comment in 10.
- Comments under politics, tragedy, layoffs, job announcements, sponsored posts or comment-gated giveaways ("Comment GUIDE and I'll send it").

## Why the bar is high

LinkedIn weighs comments above likes, and marketing write-ups on the feed say most of a post's reach is set in its first 60 to 90 minutes and that "Great post!" comments count as noise. None of this comes from LinkedIn itself, so treat it as directional. A comment is also a profile visit: an early comment under a bigger creator's post puts the author's face and headline in front of that audience. A comment that sounds like a person gets read; a template gets scrolled past.
