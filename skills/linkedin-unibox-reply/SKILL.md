---
name: linkedin-unibox-reply
description: Draft LinkedIn DM replies in the author's voice for Unibox triage and 1:1 follow-ups, one at a time, and never send without the author's yes. Use to triage interested or unanswered LinkedIn threads, draft a DM reply, or rewrite a generic suggested reply into the author's voice.
---

Workspace: all context paths below (identity, audience, strategy, voice, brand, raw, output, index, log, workspace preferences and context scripts) resolve from `context/` in the kit root. Read both the root `AGENTS.md` and `context/AGENTS.md`. Skill-local `references/` resolve from this skill directory.

# LinkedIn Unibox reply

Draft 1 LinkedIn DM reply at a time in the author's voice. Show the thread link. Never send unless the author says yes to that exact draft. Thread reading and sending run through `oxygen-unibox`; the conversation framework is `guides/dm-conversion.md`.

Voice sources: `voice/linkedin-voice.md`, compressed for DMs, and the author's own past messages. Avoid the shapes in [references/anti-patterns.md](references/anti-patterns.md).

## DM, comment, post

| Surface | Length | Job |
| --- | --- | --- |
| LinkedIn DM | Short: usually under 240 characters, 1 to 4 short paragraphs | Answer their last message. Specific, founder to founder |
| Public comment | 1 to 3 lines | A real observation or question; almost never a CTA |
| Post or article | Long form | `linkedin-copywriter` |

## Voice rules

1. **Answer the thread.** Reference their last question, constraint or stack. No product monologue.
2. **Short and specific.** Everyday words with precise nouns. Keep the author's informal rhythm without a slang quota.
3. **Ship the artifact.** When they asked for the repo, recording or link, send it in the same message.
4. **Peer tone.** Credit their work; compare tools fairly.
5. **Admit uncertainty** when true. Never invent demos, timelines, capabilities or prices.
6. **No calendar push by default.** "Walk you through", "grab 15 minutes", "quick demo", "hop on a call" only when they asked, or a call is already being arranged.
7. **1 clear next step at most:** a link, a question or a deliverable. Prefer what unblocks them without a meeting.
8. **Match their language and register.**
9. **Never copy a tool's suggested reply.** Rewrite from the thread in the author's words.
10. **No em dashes.** A period, comma or "and".

## Workflow

1. **List** interested and unanswered LinkedIn threads (see `oxygen-unibox`). Cap a digest at 8 to 10 threads; prefer threads where the author already wrote.
2. **Read the thread:** the counterpart, the last inbound message, the author's earlier messages and the thread link.
3. **Classify 1 intent:** deliverable (send what they asked for), clarify (answer with the mechanism), qualify (1 or 2 concrete questions about their workflow), continue (1 specific advance), schedule (only if they asked), decline or redirect (an honest mismatch), social (peer warmth).
4. **Draft exactly 1 reply** and show: counterpart, intent, draft, thread link.
5. **Gate:** preview only. Send only after the author approves this exact copy; if the copy changes after approval, ask again.
6. **Learn:** when the author approves or edits a reply, keep their final wording as a voice example in their context.

## Morning digest

Interested and unanswered threads, each as: name, 1-line last message, intent, link. Then ask which to draft, or draft the first if the author said "just start".
