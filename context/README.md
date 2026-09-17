# Your company and author context

This is the blank context workspace inside the [LinkedIn Funnel](../README.md). Start at [the index](index.md) or [the interview](templates/context-interview.md).

Supply an interview, notes and writing samples, then ask your agent to use **setup-workspace**, **capture-context** and **voice-calibration**. Skills live in [the shared library](../skills); no second repository or skill install is needed.

| Folder | Purpose |
|---|---|
| identity | Positioning, beliefs and cleared proof |
| audience | Intended readers, buyer problems and language |
| strategy | Goals, pillars, funnel and optional Notion mapping |
| voice | Writing samples and observed editing preferences |
| brand | Your visual rules and assets |
| inspiration | Outside references, separate from your own evidence |
| raw | Original supplied sources and manifests |
| templates | Interview, context and source templates |

Stub pages are unanswered prompts. They do not describe an author or provide usable proof. Company qualification rubrics belong in the kit's company/private folder; public-use voice and storytelling context belong here. Link the two where useful.

Notion and QMD are optional. Drafts can stay in chat. Configure your own destinations in ignored workspace.local.json and strategy/notion.local.json; credentials belong in the connected tool. No IDs are preconfigured.

For the complete LinkedIn path, use [LinkedIn Funnel](../README.md). Its [Notion guide](../guides/notion.md) connects the public webinar example and the bundled blank schema to your own workspace.

From the kit root, run:

```sh
python3 context/scripts/wiki_lint.py                  # requires Python 3
./context/scripts/qmd-setup.sh         # optional; requires installed qmd
./context/scripts/qmd.sh search backstory -c context
```

Context scripts scope themselves to this folder. They install no packages or embedding models. Raw source folders, local connections and output are ignored. Populated context pages are tracked, so use a private working repository for sensitive client material. Share the blank public kit rather than a populated client history.
