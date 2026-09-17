# Collect post engagers with Profile Watcher

[Back to LinkedIn Funnel](../README.md) · [Next: qualification](qualification.md)

OXYGEN's LinkedIn Profile Watcher collects reactions and comments on recent posts, resolves people and their current employers, and keeps one editable table with source profile/post attribution. Start with your own profile. Add other relevant public profiles only when that audience is useful to your ICP.

The current native watcher supports 1–10 public LinkedIn person profiles, a rolling 7-day post window and daily collection. Capture is bounded by provider pagination, available data and the per-cycle credit ceiling; it is not a promise to collect every engager. It uses public research, so no connected LinkedIn sender is needed for collection. Sending is separate.

## Set it up in the app

1. In OXYGEN, create a table and choose **LinkedIn Profile Watcher**.
2. Use **Add LinkedIn profile** for each real public profile URL.
3. Review the monitored profiles and choose **Create watcher** when you want collection to begin. Creation starts the first run and activates daily monitoring; it is not a saved draft.
4. Open the returned table, inspect people and their source posts, then follow [qualification](qualification.md).

The UI does not show a per-refresh price field. Usage varies with collection and enrichment. Use the CLI preview below when you want to inspect the explicit recurring cap first.

## Set it up with your agent or CLI

Install and authenticate the [OXYGEN CLI](https://oxygen-agent.com/docs/quickstart), then verify your selected workspace:

```sh
oxygen whoami --json
oxygen tables watcher preview --help
```

Use `oxygen --profile YOUR_PROFILE --org YOUR_ORG ...` throughout if you need to pin the destination. Replace uppercase values below; do not run a saved configuration with example profiles.

```sh
oxygen tables watcher preview \
  --name "LinkedIn Funnel" \
  --profiles-json '["YOUR_REAL_LINKEDIN_PROFILE_URL"]' --json
```

Preview is free: it creates nothing, collects nothing and schedules nothing. Inspect profiles, schedule, lookback window, coverage note, issues, estimated cost and `max_credits_per_cycle`. The current schedule is daily at 07:00 UTC. A cap is **per cycle**, not a monthly budget or the expected price. If you change the cap or profiles, preview the changed configuration again.

After approving that specific configuration and recurring spend, use the returned cap and hash:

```sh
oxygen tables watcher create \
  --name "LinkedIn Funnel" \
  --profiles-json '["YOUR_REAL_LINKEDIN_PROFILE_URL"]' \
  --max-credits APPROVED_CYCLE_CAP \
  --preview-hash HASH_FROM_PREVIEW \
  --request-id ONE_STABLE_UUID_FOR_THIS_INSTALLATION \
  --approved --json
```

Keep the request ID with the result. After a timeout, inspect state or retry with the same ID and exact configuration; do not create a second watcher. Open the returned `web_url` and read it back:

```sh
oxygen tables watcher get YOUR_TABLE --json
oxygen tables describe YOUR_TABLE --json
oxygen tables query YOUR_TABLE --limit 10 --json
```

The equivalent MCP operation is `oxygen_tables_watcher` with `action: preview`, then `action: create` using the inspected profiles, `max_credits_per_cycle`, `preview_hash`, stable `request_id` and approved scope. Discover its current schema in your connected workspace.

## Qualify the actual engager

Keep the profile and source-post evidence on the same person. Do not transfer one employee's engagement to another employee at their company. A like is an observed signal, not proof of buying intent. Missing employer enrichment stays unknown; qualify only after the required evidence exists.

Add the [qualification column](qualification.md). The watcher does not score your ICP, enroll contacts, deliver lead magnets or message anyone by itself.

## Pause and change it

```sh
oxygen tables watcher pause --table YOUR_TABLE --json
oxygen tables watcher get YOUR_TABLE --json
```

To change profiles or resume, preview the existing table again, inspect the current scope and cap, and use the returned hash with the corresponding update or resume command. Pause retains the rows already collected. Review coverage and actual spend in OXYGEN before expanding the watched list.

The advanced `linkedin-profile-engager-monitor` blueprint is a different, three-table installation whose workflow starts disabled. Use it only if you need that workflow-level control. This guide uses the native one-table watcher.
