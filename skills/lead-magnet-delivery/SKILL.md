---
name: lead-magnet-delivery
description: Turn a LinkedIn lead-magnet post ("comment KEYWORD and I'll send it") into automatic delivery on OXYGEN. Every commenter who asks gets a DM with the link and a public "Sent it over:)" reply; 2nd-degree commenters are asked to connect first; nobody is messaged twice. Use when a lead-magnet post is live and the author asks to set up delivery or send the resource to commenters.
---

Workspace: all context paths below (identity, audience, strategy, voice, brand, raw, output, index, log, workspace preferences and context scripts) resolve from `context/` in the kit root. Read both the root `AGENTS.md` and `context/AGENTS.md`. Skill-local `references/` and `scripts/` resolve from this skill directory.

# Lead magnet delivery

The author posts a lead magnet with a keyword CTA. This skill makes OXYGEN deliver it: 1 hosted workflow per post that reads the comments, DMs the resource to everyone who asked, replies publicly under their comment and tracks each person in a ledger table. Read `guides/oxygen.md` first; `lead-magnet-creator` builds the resource itself.

The working delivery logic is [references/delivery-recipe.example.mjs](references/delivery-recipe.example.mjs), an OXYGEN durable recipe with every account-specific value as a placeholder.

## Steps

1. **Check the workspace.** `oxygen whoami`, then `oxygen senders list --json`: the LinkedIn sender that will send the DMs, its account ID and its limits.
2. **Resolve the post.** Expand a short `lnkd.in` link with `curl -sIL`. Take the number after `share-` (or `activity-`) in the post URL and call:

   ```sh
   oxygen tools run linkedin.posts_get --mode live \
     --input-json '{"post_id":"urn:li:share:<id>","account_id":"<ACCOUNT>"}'
   ```

   `response.id` is the composite post ID the recipe needs.
3. **Read the comments** with `linkedin.posts_comments_list` (same post, `limit: 100`, `sort_by: MOST_RECENT`). Test the `wantsAsset` keyword regex against every comment: it must catch the keyword and genuine asks ("would love to get the kit") and skip praise-only comments.
4. **Create the ledger table** (1 per post) with text columns `provider_id, name, first_name, profile_url, comment_id, comment_text, connection_degree, state, enrollment_id, reply_text, last_checked_at, note` and `delivery_receipt` as JSON.
5. **Fill in the recipe.** Copy the example and replace every placeholder: account, sender, connection, your own member ID, post, resource URL, ledger table, the keyword in `wantsAsset`, the DM text, the recipe `id` and `name`, the time zone. Keep `import { defineRecipe } from "@oxygen/recipe-sdk"` at the top. Run `node --check`.
6. **Mark people you already handled by hand** as `state: "complete"` in the ledger, keyed on `provider_id`, so they are not messaged again.
7. **Apply and arm** (both need explicit approval from the author):

   ```sh
   oxygen workflows apply --file <recipe>.mjs --approved --max-credits 1 --json
   oxygen workflows enable <slug> --approved --max-credits 1 --json
   ```

8. **Preview before sending.** Run it once in audit mode: `oxygen workflows call <slug> --mode live --approved --max-credits 1 --input-json '{"audit":true}'`, then `oxygen workflows tail <run_id>`. Audit mode reads the real comments and writes nothing; its `plan` lists every DM and reply it would make. Check that list before the first live cycle.
9. **Verify after sending.** Query the ledger, then read the replies back under each comment. A reply only counts once it is visible on LinkedIn.

## Defaults

- DM: `Heyo {first_name}:)`, a blank line, `Here is the <resource>:`, a blank line, the link. Match the noun to the resource.
- Public reply after a verified DM rotates through short variants (`Sent it over:)`, `Sent:)`, `Check your DMs:)`). Every variant must match the duplicate check `/\bsent\b|\binbox\b|\bdms?\b/i`, or a later run will not recognise its own reply.
- 2nd-degree commenters get a public "We first need to connect :) Send me a connection request so I can send you the <resource>." The DM goes out automatically once they are 1st-degree. Connect variants must not match the duplicate check. 3rd-degree and unknown are skipped.
- The order is fixed: DM, read the DM back, then reply publicly. Intent is saved to the ledger before every external write, so an uncertain send is reviewed, never repeated.
- A reply to the delivered DM suppresses the lead from further automation.

## Pacing

The sender's safety limits decide throughput, not the workflow. Read them with `oxygen senders list --json` (`limits`, `usage.today`) and keep the recipe's pacing at or above the minimum action spacing; shorter pacing gets refused. Typical limits allow about 10 people an hour. Lowering the spacing is an account-safety decision for the author, never a default. Cycle: every 10 minutes, a bounded number of DMs and replies per run.

## When hosted runs fail

If runs fail with `linkedin_quota_enforcement_unavailable`, run the same recipe locally through the CLI with [scripts/run-recipe-local.mjs](scripts/run-recipe-local.mjs):

```sh
OXYGEN_PROFILE=<profile> node scripts/run-recipe-local.mjs <recipe>.mjs --input '{"audit":true}'   # preview
OXYGEN_PROFILE=<profile> node scripts/run-recipe-local.mjs <recipe>.mjs --workflow <slug>          # live
```

It maps every tool call to the CLI, holds a lock so runs never overlap and stands down once the hosted workflow completes a scheduled run. Report the hosted failure to OXYGEN support.

## Check the post itself

Read the post before launch: the CTA keyword in the post, the graphic and the regex must match, and any link in the post must open the right page.
