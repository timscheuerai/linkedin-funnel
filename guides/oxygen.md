# Connect your OXYGEN workspace

[Back to LinkedIn Funnel](../README.md)

The content and brand skills work locally. For engagement collection, qualification and outreach, use your own OXYGEN workspace through its connected MCP tools or the [CLI](https://oxygen-agent.com/docs/quickstart).

Before using commands, verify the environment and workspace:

```sh
oxygen whoami --json
oxygen capabilities search "LinkedIn profile watcher" --json
oxygen tables watcher preview --help
```

Pin the intended destination with `oxygen --profile YOUR_PROFILE --org YOUR_ORG ...` when needed. Discover the installed command schema before building an operation; a copied example is not a substitute for the current interface.

## Follow the workflow

1. [Profile Watcher](profile-watcher.md): preview real profile URLs and the daily credit cap, then create the watcher when you want recurring collection to begin.
2. [Qualification](qualification.md): fill your rubric, inspect the actual table columns, add the prompt and preview a row. Calibrate paid scoring against a small reviewed set.
3. [Conversations](dm-conversion.md): review the cohort and message. Use native Sequences for new LinkedIn conversations and Unibox for existing threads.

The four bundled helpers are [oxygen-quickstart](../skills/oxygen-quickstart/SKILL.md), [oxygen-linkedin-marketing](../skills/oxygen-linkedin-marketing/SKILL.md), [oxygen-sequencer](../skills/oxygen-sequencer/SKILL.md) and [oxygen-unibox](../skills/oxygen-unibox/SKILL.md).

OXYGEN owns live rows, provider calls, schedules and delivery. Record installation IDs in ignored `.oxygen/` or another local configuration, never in this public template. Inspect returned objects and run state after writes; an accepted request does not prove processing or delivery completed. Reconcile ambiguous outcomes before retrying.

No live connection, installed Function, automatic enrollment or Notion-to-OXYGEN sync is bundled. Each guide shows the part you configure in your own workspace.
