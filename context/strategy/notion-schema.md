---
type: configuration
status: stub
owner: unassigned
created: 2026-09-07
updated: 2026-09-07
sources: []
tags: [notion, template]
---

# Notion schema

This is a schema to create or map in a client's workspace. No live Notion page or databases are bundled.

Copy `strategy/notion.example.json` to ignored `strategy/notion.local.json` after selecting the destination. Record the fetched parent page, workspace and data source IDs. Never put access tokens here. Database URLs and data source IDs are distinct; fetch the database to discover its data source.

When adapting an existing installation, a legacy `strategy/notion.json` can supply its current IDs if no local file exists. Prefer the local file. A local file with incomplete IDs means setup is unfinished; do not fall back to another destination.

## Content Board

| Property | Type / values |
| --- | --- |
| Name | Title |
| Status | Select: Idea, Creating, Published, Backlog |
| Pillar | Multi-select: Pillar 1, Pillar 2, Pillar 3, Pillar 4 |
| Platform | Select: LinkedIn, X, YouTube, Instagram, Newsletter |
| Publish date | Date |

Use one pillar per piece; rename placeholder options after strategy decisions. Suggested views: Stages grouped by Status, Calendar by Publish date, All pieces as a table. The date is an editorial plan, not a publishing job.

Bodies contain one paste-ready text code block. Funnel stage is a drafting decision, not a required property. Source reasoning belongs in the run report or context pages. Adapt to an existing client schema without destroying fields or views.

## Pillars & Topics

| Property | Type / values |
| --- | --- |
| Name | Title |
| Level | Select: Pillar, Topic |
| Pillar | Select: the same pillar names as Content Board |
| Status | Select: Active, Parked |
| One line | Text |

Suggested views: Pillars filtered by Level, Topics filtered by Level and grouped by Pillar, All as a table. The starting scaffold has four pillars, four topics per pillar, four subtopics per topic. Change those counts when the client's strategy calls for it.

Use `templates/notion-pillar.md` and `templates/notion-topic.md` for page bodies. Subtopics live inside topic pages. These files are copyable text, not installed native Notion database templates. Leave database rows empty until the author has supplied content decisions.

## Hooks and Creator Inspo DB

Hooks: Hook (title), Type (select, optional initial Storytelling value). Store the pattern in the page body. Suggested Gallery and Table views.

Creator Inspo DB: Full Name (title), LinkedIn, X, Youtube and Instagram (URL). Store what to learn and what not to import in the page body. No sample creators or hooks are supplied.

## Write procedure

Read configuration, fetch the parent and relevant data sources, inspect property types and query existing entries. Check for an existing card with the same planned date and content before creating one. After a timeout, read back before retrying.

Use the connected tool's actual schema. Record created resource IDs immediately. If setup is interrupted, resume from verified IDs and existing titles under the selected parent instead of creating duplicate databases. Report missing access as inaccessible, not empty.

## Related Pages

- [[pillars]]
- [[funnel]]
- [[index]]

## Source Notes

Generic template configuration. Client connections and content are unfilled.
