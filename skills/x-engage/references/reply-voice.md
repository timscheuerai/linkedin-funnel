# Reply voice

How the author's X replies under other people's posts are written. Their X and post voice lives in `context/voice/`; this page adds what is specific to a reply. `scripts/render_queue.py` enforces the mechanical rules.

> Status: the author's own lines start empty. Fill "The author's moves" from their real replies in setup ([setup.md](setup.md)) and keep "Taste" current from [verdicts.md](verdicts.md).

## Why the bar is high

X ranks the For You feed by predicted actions, with replies weighted far above likes, and it scores reply quality: low-effort, emoji-only or AI-sounding replies sink. Treat the exact weights in public write-ups as directional. In practice "thanks mate" replies sit at a handful of impressions, while 1 specific operator question or practice under a bigger account can reach hundreds. That is the model.

Reach depends on the post too. A reply under a post that ends with a few thousand views is seen by a few dozen people; under a post that travels to tens of thousands, several times more. Pick posts that are likely to travel (moving fast, from accounts whose posts travel), not only posts in the niche.

## Shape

A reply is a text to a peer, not a mini post.

- 1 thought. Usually 1 or 2 short sentences, 70 to 160 characters, never over 200 (the renderer stops anything longer).
- Say it the way the author would say it out loud: contractions, plain words, their own texture where it fits. No setup line, no punchline line.
- 1 receipt is enough. Don't stack a story, a number and a lesson, and don't flex numbers nobody asked for.
- At most 1 question, short, one the post's author can answer from experience, and after a concrete line, not instead of it.
- No colon reveals ("What cut it for me: ..."), no "What nobody tells you", no "X is the whole story", no triads, no 2-paragraph structure. The renderer blocks the common ones.
- No compliments as an opener or as filler.
- No links, hashtags or product plugs. The author's company by name only when it is the receipt itself, at most 1 reply in 10.
- No dashes.

## Before and after

The pattern of a reply rejected as sloppy against one that went out (shape only; the facts in the author's version come from their own pages):

| Rejected as sloppy | Chill |
|---|---|
| "Same with my setup. What cut the catch-up for me: 1 agent sends a rollup every morning and another routes everything else. I only open a chat when something needs my OK." | "Same here. Having 1 agent send me a morning rollup helped a lot, now I only jump in when something needs my ok" |
| "I did exactly this path. Agency first, then SaaS. What nobody tells you about the switch: a low-ticket SaaS needs 10 to 100x the distribution of a service." | "Did exactly this. The agency paid the bills and showed me what people actually pay for. Only thing I'd warn about is how much more distribution SaaS needs after" |
| "Our tier A is post engagers. Someone who commented this week gets a very different first line than a cold list pull. How do you decide when a lead moves up? A reply, a click, or something else?" | "Post engagers are tier A for us too. When do you move someone from B to A, does a reply do it?" |

## Moves

| Move | When | The author's version |
|---|---|---|
| Receipt | They have done the thing | |
| Missing half | The post skips the part they know | |
| Lived it | Advice they followed or broke | |
| Hack | The post leaves the how open and they have a concrete one | |
| Operator question | They want the how, after a concrete line | |
| Fair disagreement | They have a reason from their own work | |
| Humor with a fact | A joke post they can add a true line to | |

## Taste

Starting hypotheses that held for one creator over many runs. Test them, then replace them with the author's verdicts:

- Every reply carries 1 concrete practice, tool or result the author has now. Pure opinions, old stories and product plugs get skipped.
- Lead with a hack or a result, not a question. Question-only drafts rarely go out.
- React to the post's point first: agree with a how, answer their question, a joke the author can stand behind.
- Under a hype or results post, match the energy in the author's words, then 1 result or trick if any.
- No setup showcases (routines, repos, agent counts, subscriptions), even when the post is about a similar setup.
- Plain words over copywriter idioms; personal credentials (age, years, team size) left out unless asked.
- Don't reuse 1 failure story as a hook.
- Fresh or nothing: replies under posts 15 to 60 minutes old go out far more often than under posts over 3 hours.

## Never

- "Great post", "Love this", "So true", "100%", "This.", "Well said", "Spot on".
- Stock words: orchestrates, leverages, streamlines, seamless, unlock, game changer, delve, crucial (add the author's own in `extra_banned_words`).
- Invented anecdotes, customer stories or numbers. If the receipt is not in [receipts.md](receipts.md) or `context/identity/proof.md`, ask a question instead.
- Someone else's result presented as the author's, or a claim about a tool they have not used.
- A pitch, a booking link, "DM me", or "check out" the author's product.
- Replies to politics, drama, tragedy, or giveaways ("comment X to get").
