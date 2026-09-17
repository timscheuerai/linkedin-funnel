---
name: oxygen-sequencer
description: Operate native OXYGEN Sequences for new conversations and outreach cadence, including sender readiness, previews, enrollment, dispatch and recovery.
---

# Operate the Sequence

Read [the connection guide](../../guides/oxygen.md), [qualification](../../guides/qualification.md) and [the DM framework](../../guides/dm-conversion.md). Start with a reviewed cohort and a message grounded in each recipient's actual context.

New LinkedIn conversations belong to Sequences even for one recipient. Cadenced or multi-recipient outreach uses Sequences. Existing-thread replies and direct email without cadence use [Messages](../oxygen-unibox/SKILL.md).

Discover exact commands with `oxygen capabilities search "preview outreach sequence" --json`, then `commands get` for the selected operation.

Inspect these together:
- Sender profiles, exact accounts/mailboxes, health, channel limits and stable recipient-to-sender binding.
- Definition/version, ordered steps, delays, variants, send windows/time zone and any channel fallback.
- Recipient identity, mapped variables, exclusions, suppression, prior-contact rules and tags.
- Dispatch limits, lifetime budget, live-run cap, reply stops and bounce behavior.

Preview the actual recipient scope and render messages with their real variables. Report unresolved identities individually. A connected sender is not proof of readiness. If email sender setup or health is relevant, discover the current native commands and retrieve `oxygen-email-infra` or `oxygen-deliverability` through `oxygen skills get`; those optional procedures are not bundled here.

Enrollment and dispatch are separate actions. Inspect the selected Sequence's current state: draft or paused enrollments may remain pending, while an active Sequence may deliver after enrollment. Execute only the user's authorized send scope and current platform gates; a cap is not authorization.

Record enrollment, variant and run IDs. For results, inspect campaign events/analytics and preserve actual sender attribution; missing identity stays unattributed. Separate delivered messages, replies, qualified conversations and opportunities, preserving the source post where known.

For recovery, preview the narrow failed/deferred scope and reconcile provider outcomes before retrying. Pause/resume, retirement and capacity recovery have distinct semantics; discover them before acting. Return counts, held reasons, actual state, budget and deep-links.
