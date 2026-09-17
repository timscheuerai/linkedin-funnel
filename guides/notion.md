# Set up your Notion content board

[Back to LinkedIn Funnel](../README.md)

The existing [Adam Robinson Content Example](https://prospera-service.notion.site/3d4b3dd667a781dcac4aea561260a788) is a public worked example with a Content Board, Pillars & Topics, and Hooks. It is linked from the [webinar repository](https://github.com/OXYGEN-CRO/adam-robinson-content-engine).

## Use the existing example

1. Open the public page while signed into your own Notion account.
2. If **Duplicate** is available, duplicate the complete parent page into your workspace so the databases travel together.
3. Give your agent the URL of your copy. Ask it to fetch the parent and discover its actual database and data-source IDs, then record those in ignored `context/strategy/notion.local.json`, starting from [the example config](../context/strategy/notion.example.json).
4. Replace the example pillars, topics and hooks with your own strategy. Check linked views point into your copy.

The public page was readable on September 17, 2026. Template duplication could not be confirmed in the anonymous view; the repo does not claim that control is enabled. If it is unavailable, create your own blank board with the included schema below. Public source IDs are never write destinations.

## Build the blank version from this repo

Give your agent a destination page you own and paste:

```text
Use setup-workspace. Set up the blank content system under this Notion parent:
[MY PARENT PAGE URL]. Read context/strategy/notion-schema.md. Inspect the
parent first and reuse matching databases if present. Create or map Content
Board, Pillars & Topics, Hooks and Creator Inspo DB. Keep author-specific rows
empty until we define them. Store verified IDs in
context/strategy/notion.local.json. Verify the resulting schemas and tell me
which views or native templates, if any, still need a UI step.
```

The [schema](../context/strategy/notion-schema.md) and [page-body templates](../context/templates) are bundled. This option does not depend on the public example's sharing settings.

| Database | Main fields |
|---|---|
| Content Board | Name, Status, Pillar, Platform, Publish date |
| Pillars & Topics | Name, Level, Pillar, Status, One line |
| Hooks | Hook, Type; the reusable pattern in the body |
| Creator Inspo DB | Full Name and platform URLs |

Use one pillar per piece. Store the paste-ready post in a text code block. Keep voice, source evidence and proof in the repo. The public webinar example has three databases; Creator Inspo DB is an optional addition from the blank schema.

Changing a date or status in Notion does not schedule a LinkedIn post. Use OXYGEN Publishing when you are ready to review the exact copy, media, sender and time. There is no bundled automatic Notion-to-OXYGEN sync.
