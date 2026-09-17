---
name: oxygen-quickstart
description: Connect LinkedIn Funnel to the reader's OXYGEN workspace and prepare a native Profile Watcher preview using current command schemas.
---

# Start with OXYGEN

Read [the connection guide](../../guides/oxygen.md) and [Profile Watcher setup](../../guides/profile-watcher.md). Keep the user's selected profile and organization throughout the session.

For the first hosted step:

1. Read `oxygen whoami --json` and resolve the intended workspace. If access is not entitled, inspect the returned billing-owner guidance before proposing resources.
2. Search `oxygen capabilities search "LinkedIn profile watcher" --json` and inspect `oxygen tables watcher preview --help`.
3. Identify the actual public profile URLs and inspect existing watchers before proposing another one.
4. Preview the requested profiles. Report the schedule, rolling collection window, coverage limitations and per-cycle credit ceiling. Preview itself does not collect or schedule.
5. Route activation to `oxygen-linkedin-marketing` and the watcher guide. Creation begins immediate and recurring collection. Keep the returned hash and stable request ID with that configuration.

Prepare [qualification](../../guides/qualification.md) from the reader's offer and ICP. Adding the qualification definition, running a model and activating auto-run are separate actions with distinct scope and cost.

For broader onboarding, retrieve the current `oxygen-onboarding` procedure with `oxygen skills get oxygen-onboarding --json`; that optional live skill is not bundled here. Use existing company answers rather than restarting an interview.

Return the selected workspace, inspected resources, preview and next step. Continue within existing authorization; a request to connect or preview alone does not activate recurring collection or outreach.
