---
name: lead-magnet-delivery
description: Turn a LinkedIn lead-magnet post ("comment KEYWORD and I'll send it") into automatic delivery on OXYGEN. Every commenter who asks gets a DM with the link and a public "Sent it over:)" reply; 2nd-degree commenters are asked to connect first; nobody is messaged twice. Use when a lead-magnet post is live and the author asks to set up delivery or send the resource to commenters.
---

Workspace: all context paths below (identity, audience, strategy, voice, brand, raw, output, index, log, workspace preferences and context scripts) resolve from `context/` in the kit root. Read both the root `AGENTS.md` and `context/AGENTS.md`. Skill-local `references/` and `scripts/` resolve from this skill directory.

# Lead magnet delivery

The author posts a lead magnet with a keyword CTA. This skill makes OXYGEN deliver it: 1 hosted workflow per post that reads the comments, DMs the resource to everyone who asked, replies publicly under their comment and tracks each person in a ledger table. Read `guides/oxygen.md` first; `lead-magnet-creator` builds the resource itself.

The working delivery logic is [references/delivery-recipe.example.mjs](references/delivery-recipe.example.mjs), an OXYGEN durable recipe with every account-specific value as a placeholder: sender working hours and send caps, DMs before public replies, both comment sorts, deterministic date parsing and a `PUBLIC_REPLIES` switch. To clone a workflow that already runs instead, pull its bundle with `oxygen workflows revisions <slug> --include-manifest --limit 1 --json`, drop the inlined SDK and import `defineRecipe` again.

## Steps

1. **Check the workspace.** `oxygen whoami`, then `oxygen senders list --json`: the LinkedIn sender that will send the DMs, its account ID and its limits.
2. **Resolve the post.** Expand a short `lnkd.in` link with `curl -sIL`. Take the number after `share-` (or `activity-`) in the post URL and call:

   ```sh
   oxygen tools run linkedin.posts_get --mode live \
     --input-json '{"post_id":"urn:li:share:<id>","account_id":"<ACCOUNT>"}'
   ```

   `response.id` is the composite post ID the recipe needs.
3. **Read the comments** with `linkedin.posts_comments_list` (same post, `limit: 100`). Test the `wantsAsset` keyword regex against every comment: it must catch the keyword, typos of it and genuine asks ("would love to get the kit"), including bare asks without a noun ("please send :)"), and skip praise-only comments.
4. **Create the ledger table** (1 per post) with text columns `provider_id, name, first_name, profile_url, comment_id, comment_text, connection_degree, state, enrollment_id, reply_text, last_checked_at, note`, and `delivery_receipt` and `write_intent` as JSON. The recipe saves its intent to `write_intent` before every send; without that column the first real comment fails the run, while empty runs and audits still pass.
5. **Fill in the recipe.** Copy the example and replace every placeholder: account, sender, connection, your own member ID, post, resource URL, ledger table, the keyword in `wantsAsset`, the DM text, the recipe `id` and `name`, the time zone. Keep `import { defineRecipe } from "@oxygen/recipe-sdk"` at the top: the CLI only bundles a recipe whose source imports the SDK. Run `node --check`.
6. **Mark people you already handled by hand** as `state: "complete"` in the ledger, keyed on `provider_id`, so they are not messaged again.
7. **Apply and arm** (both need explicit approval from the author; applying alone leaves the workflow disabled):

   ```sh
   oxygen workflows apply --file <recipe>.mjs --approved --max-credits 1 --json
   oxygen workflows enable <slug> --approved --max-credits 25 --json
   ```

   The run checks each step's estimated cost against the enable cap before it executes. With a cap of 1, a run can send and verify the DM, then stop before the public reply. Actual spend stays near 0 when the LinkedIn actions run on the author's own connection.
8. **Preview before sending.** Run it once in audit mode: `oxygen workflows call <slug> --mode live --approved --max-credits 5 --input-json '{"audit":true}'`, then `oxygen workflows tail <run_id>`. Audit mode reads the real comments and writes nothing; its `plan` lists every DM and reply it would make. Check that list before the first live cycle. Dry-run mode stubs LinkedIn and shows 0 comments, so it only proves the code compiles.
9. **Verify after sending.** Query the ledger, then read the replies back under each comment. A reply only counts once it is visible on LinkedIn. After any change to the recipe, wait for 1 scheduled run and confirm it completed: an audit alone does not prove the cron path.

## Defaults

- DM: `Heyo {first_name}:)`, a blank line, `Here is the <resource>:`, a blank line, the link. Match the noun to the resource.
- The resource URL must be unique per post. The delivery check looks for the URL inside the DM thread, so re-sending a repo that an earlier magnet already delivered would count those people as done. Use a README anchor (`#the-section`) or a UTM-tagged URL (`utm_source=linkedin`, campaign = the post's slug, `utm_content=dm`) on the author's own site.
- Public reply after a verified DM rotates through short variants (`Sent it over:)`, `Sent:)`, `Check your DMs:)`). Every variant must match the duplicate check `/\bsent\b|\binbox\b|\bdms?\b/i`, or a later run will not recognise its own reply. The variant is picked by hashing the person, so a retry posts the same one.
- 2nd- and 3rd-degree commenters get a public "We first need to connect :) Send me a connection request so I can send you the <resource>." The DM goes out automatically once they are 1st-degree. Connect variants must not match the duplicate check. Unknown degree is skipped.
- The order is fixed: DM, read the DM back, then reply publicly. Intent is saved to the ledger before every external write, so an uncertain send is reviewed, never repeated. All public replies of a run are queued after its DMs, so a timed-out reply only cuts the tail.
- Suppression only gates new DMs. A reply to the delivered DM suppresses the lead from further automation; the public acknowledgement still follows.

## Pacing

The sender's safety limits decide throughput, not the workflow. Read them with `oxygen senders list --json` (`limits`, `usage.today`, working hours) and keep the recipe's pacing at or above the minimum action spacing plus its jitter; shorter pacing gets refused and wastes cycles. Expect about 20 to 30 actions an hour per LinkedIn account, roughly 10 people an hour. Lowering the spacing is an account-safety decision for the author, never a default.

- Cycle: every 15 minutes inside the sender's working hours, with a bounded number of comments inspected, DMs and replies per run. Posts over 500 comments stop the run by design.
- Give every automation on the same LinkedIn account its own cron minutes. 2 workflows on the same quarter hour race for the sender spacing, and the refused one ends as an uncertain write although nothing was sent.
- On a busy post, the run inspects uncertain DMs first, then 1st-degree requests without a delivery, then reply work. Otherwise the reply backlog fills the cap and DMs wait for days.

## Go easy on comment reads

Every run starts by reading the comments, and LinkedIn can rate-limit those reads for many hours on a busy post. Then no DMs go out at all. Keep reads few: a longer cycle (every 30 minutes) once a post is busy, and check progress in the ledger (`oxygen tables query <ledger> --fields provider_id,state`), not by reading the post's comments by hand during a live delivery.

Read both comment sorts. `MOST_RECENT` can lag and leave out the newest comments; the example also reads `MOST_RELEVANT` and merges by comment ID. When LinkedIn shows more comments than the ledger, compare the 2 sorts first.

## Commenters waiting to connect

Accepting the connection requests of commenters who are waiting for the resource belongs in its own workflow, never in the delivery recipe. A LinkedIn quota refusal parks a hosted run until the quota resets, even for an optional step, so 1 refused invitation read inside the delivery would stop every DM for hours. Relations reads have a small daily budget that other automations also spend: read only when someone is waiting and budget is left, and accept only invitations from waiting commenters.

## Viral posts: link replies instead of DMs

DMs are the default. When a post outgrows them (hundreds of comments in a day, comment reads rate-limited), the author may switch that post to public replies that carry the link. It needs the author's go per post; never switch on your own.

- 1 reply per request, any connection degree, oldest first, with varied wording per person. Mirror the author's own manual reply when they have posted one.
- Space the replies (about 90 seconds plus jitter, never under the sender's spacing) and respect the daily comment cap; check the cap before reading comments so runs past it cost no reads.
- Duplicate guard: the ledger state first, then the author's own replies in the thread.
- Back off after an unknown write: while a timed-out reply is younger than 2 hours, a run stops before any LinkedIn call. When LinkedIn rate-limits, stop.
- Read reply threads last and pause them for hours after a rate limit; LinkedIn can limit the thread endpoint alone while the comment list still works.

## Requests that arrive by DM

Many people ask for the resource in a DM or in their connection note instead of a comment, and the workflow does not see those. Find them read-only with `oxygen messages query --channel linkedin` since the post went live, filtered by the keyword and by threads with no outbound message containing the resource link. A keyword match is not always a request: drop threads that only discuss the topic or that the author already answered. Draft each reply in the author's voice (`linkedin-unibox-reply`), show the queue, and send only what the author approves, a few minutes apart, oldest first. Before each send, re-check the thread for the link: the comment workflow may have delivered it meanwhile.

## When hosted runs fail

Read the error with `oxygen workflows tail <run_id> --json`; the message is in the last event's `payload.error`.

- **`workflow_effect_outcome_uncertain` on a busy post:** a comment write timed out, and an uncertain write ends the run by design. Keep public replies queued after the DMs. Reconcile rows in review by reading each thread: reset the ones that never posted and clear their `write_intent`.
- **`recipe_sandbox_error` on scheduled runs only:** the recipe called `Date.parse`, `new Date` or `Date.now` on a time such as `input.scheduled_for`, which only cron runs carry. Parse ISO times with `isoMs` as the example does.
- **`recipe_sandbox_error` after the enrollment steps, audits included:** large tool results can come back trimmed (`structured_truncation`), so the campaign check refuses. The example pages each open enrollment status by offset in steps of 25; audit with `--max-credits 5`.
- **`linkedin_quota_enforcement_unavailable` on every run:** run the same recipe locally through the CLI with [scripts/run-recipe-local.mjs](scripts/run-recipe-local.mjs):

  ```sh
  OXYGEN_PROFILE=<profile> node scripts/run-recipe-local.mjs <recipe>.mjs --input '{"audit":true}'   # preview
  OXYGEN_PROFILE=<profile> node scripts/run-recipe-local.mjs <recipe>.mjs --workflow <slug>          # live
  ```

  It maps every tool call to the CLI, holds a lock so runs never overlap and stands down once the hosted workflow completes a scheduled run. Report the hosted failure to OXYGEN support.

## Check the post itself

Read the post before launch: the CTA keyword in the post, the graphic and the regex must match, and any link or mention in the post must open the right page.
