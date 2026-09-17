---
name: oxygen-unibox
description: Triage OXYGEN Messages and Unibox conversations, prepare grounded replies and send only within the user's specified account and thread scope.
---

# Work the existing conversation

Read [the runtime contract](../../guides/oxygen.md). Messages owns existing email, LinkedIn and WhatsApp threads, plus direct email without cadence. New LinkedIn conversations and outreach programs use [Sequences](../oxygen-sequencer/SKILL.md).

Discover with `oxygen capabilities search "triage unanswered inbox threads" --json`, then hydrate the selected inbox/messages/reviews command. Query a bounded slice by channel, time, status, participant or shared Tag. An unfiltered inbox includes answered threads; use the documented unanswered filter for a reply queue.

Read the full relevant conversation and current Knowledge/CRM context before classifying or drafting. Preserve provider thread IDs, participants, sending account and delivery state. Use the actual message-review surface when appropriate.

LinkedIn visibility is sender-scoped. Inspect the account's inbox scope if expected threads are missing. Do not interpret an empty restricted view as the entire inbox or opt an account into full ingestion merely to find more messages.

For a reply, prepare the exact content, thread, account and recipients. Send only within the user's explicit authorization. For tags/archive/bulk changes, expose the actual count and scope and preserve unrelated conversations.

A message timeout is not proof of non-delivery. Inspect returned message/run provenance before any retry. A public comment on a post belongs to Posts/Publishing, not Unibox.

Return a bounded triage summary, draft or verified message links, classifications and unresolved threads. Do not file feedback or forward conversation/transcript content elsewhere merely because an error occurred.
