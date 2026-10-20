---
name: linkedin-unibox-reply
description: Draft LinkedIn DM replies in the author's voice for Unibox triage and 1:1 follow-ups, one at a time, and never send without the author's yes. Use to triage interested or unanswered LinkedIn threads, draft a DM reply, or rewrite a generic suggested reply into the author's voice.
---

Workspace: all context paths below (identity, audience, strategy, voice, brand, raw, output, index, log, workspace preferences and context scripts) resolve from `context/` in the kit root. Read both the root `AGENTS.md` and `context/AGENTS.md`. Skill-local `references/` resolve from this skill directory.

# LinkedIn Unibox reply

Draft 1 LinkedIn DM reply per thread in the author's voice, aimed at the smallest useful next step: help first, then signup, activation or, for qualified buyers, a call. Show the thread link. Never send unless the author says yes to that exact draft. Thread reading and sending run through `oxygen-unibox`; the conversation framework is `guides/dm-conversion.md`.

Voice sources: `voice/linkedin-voice.md`, compressed for DMs, and the author's own past messages. Avoid the shapes in [references/anti-patterns.md](references/anti-patterns.md).

## DM, comment, post

| Surface | Length | Job |
| --- | --- | --- |
| LinkedIn DM | Short: usually under 240 characters, 1 to 4 short paragraphs | Answer their last message. Specific, founder to founder |
| Public comment | 1 to 3 lines | A real observation or question; almost never a CTA |
| Post or article | Long form | `linkedin-copywriter` |

## Voice rules

1. **Answer the thread.** Reference their last question, constraint or stack. No product monologue: in a live buyer thread, react and ask about the next piece of their setup; explain the product only when they ask.
2. **Short and specific.** Everyday words with precise nouns. Keep the author's informal rhythm without a slang quota. Links on their own line, no sign-off.
3. **Ship the artifact.** When they asked for the repo, recording or link, send it in the same message.
4. **Peer tone.** Credit their work; compare tools fairly.
5. **Admit uncertainty** when true. Never invent demos, timelines, capabilities, prices, discount codes or the author's plans. Where 1 is needed, write `[AUTHOR: ...]` and hold the item.
6. **No calendar push by default.** Call links only for qualified buyers or when they asked (see "Route"). Chit-chat and networking get an answer in the thread, not a call.
7. **1 clear next step at most:** a link, a question or a deliverable. The closing question builds on what they said, not a stock question.
8. **Match their language and register.**
9. **Never copy a tool's suggested reply.** Rewrite from the thread in the author's words.
10. **Late replies:** when their last message is more than 3 days old, own the delay in a few words, with the real reason when there is 1. Vary the wording across a batch; the same apology on every draft reads like a bot.
11. **No em dashes.** A period, comma or "and".

## Establish who still needs an answer

Triage status and "needs reply" filters are candidates, not proof. Reread each thread and exclude it when the latest message is outbound or the order of messages is unclear. Read enough history to see earlier links, questions, signups and meeting commitments. Before treating an outbound message as the author's own voice, check it was not sent by a Sequence or another automation. If the person also talks to the author in Slack or email, check there before drafting.

## Route

| Thread | Draft |
| --- | --- |
| Resource request | The link plus 1 question about their work. 5 or more for the same resource: the DM-side delivery in `lead-magnet-delivery` |
| Compliment or new connection | Short thanks and what they are working on |
| Prospect, qualified (fits the buyer rubric from `guides/qualification.md` and shows a concrete need) | Answer, then offer the call as a question |
| Prospect, unknown or weaker fit | Answer, then the self-serve start (the website or signup) with help offered if questions come up |
| Signed-up user or customer | Help with where they are stuck; onboarding calls only when qualified or paying |
| Message that needs no answer (a thanks, "done" after booking, "will check it out") | No reply |
| Support problem | Thank them, ask where they are stuck; hold anything that needs a fix, refund or account change |
| Someone pitching the author | No reply, unless the author asks |
| Event, podcast, partner, money, legal or personal | Hold for the author |

Qualify before any call link: company fit, the contact's role, a concrete need and intent. A large employer or a senior title alone is not enough; unknown is not qualified. When someone says they will buy, help them take the next product step instead of adding a hurdle.

## Workflow

1. **List** interested and unanswered LinkedIn threads (see `oxygen-unibox`). A batch is bounded, not an inbox audit; say how much was covered.
2. **Read and route** each thread as above.
3. **Draft 1 reply per thread** and show a decision queue: ready to send (name, thread link, their latest point, fit evidence, route, the exact draft in a code block so line breaks show), then held items with the missing fact, then counts of already answered and noise. Buyers first, oldest unresolved first within each group.
4. **Gate:** reread each thread right before presenting and again before sending. A new inbound or outbound message invalidates the old draft. Send only what the author approved, exactly; if the copy changes after approval, ask again.
5. **Send paced:** approved replies go out a few minutes apart within the sender's limits. A send with an uncertain outcome is checked in the thread before any retry.
6. **Report:** sent, skipped, failed and held. Track signups, first product actions and qualified bookings separately from links sent.
7. **Learn:** when the author edits or rejects a draft, write the general rule behind it (never names or message text) into their voice context, and keep their final wording as a voice example.

## Drafting on a schedule

A recurring drafting run can prepare the queue for review, for example every few hours. It drafts and presents; it never sends. Keep its state (last run, open drafts, verdicts, a private do-not-reply list) outside the repository, and run only 1 loop at a time: 2 loops on the same inbox draft the same threads and can answer 1 person twice. Advance the checkpoint only after every fetched thread was handled or kept for review. Approval stays with the author until they explicitly turn on sending for named, obvious cases; no streak or elapsed time switches it on.

## Morning digest

Interested and unanswered threads, each as: name, 1-line last message, route, link. Then ask which to draft, or draft the queue if the author said "just start".

Paid profile or company reads to personalize a draft cost credits: quote the cost first and run them only on the author's yes.
