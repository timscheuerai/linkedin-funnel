---
name: qmd
description: Search and retrieve this repository's author context with optional qmd, using an isolated index for each client folder.
---

Workspace: all context paths below (identity, audience, strategy, voice, brand, raw, output, index, log, workspace preferences and context scripts) resolve from `context/` in the kit root. Read both the root `AGENTS.md` and `context/AGENTS.md`. Skill-local `references/` and flowchart `scripts/` resolve from this skill directory.


# Retrieve context

Start at `index.md`. Use this repository's `scripts/qmd.sh` wrapper, which selects an index derived from the repository's absolute path. Do not use another project's global collection.

If qmd is installed, read its version-matched instructions using `scripts/qmd.sh skill show` or its help output. Run `scripts/qmd-setup.sh` when setting up the local index is part of the request.

Search known wording with:
```sh
./scripts/qmd.sh search "search terms" -c context
```

Read full relevant files or retrieve them through the same wrapper. A snippet is a pointer, not sufficient support for a factual claim. A stub is an unanswered prompt, not author context.

If qmd is missing or its index is unavailable, use `rg` and direct file reads. Do not install software, download models or configure global MCP servers just to answer a context question.

After context changes, refresh an already configured index with `scripts/qmd-refresh.sh`. Moving the repository creates a different index name; run setup at the new location. Use `scripts/qmd.sh --print-index` to inspect the index name without running qmd.

Answer with source paths and relevant uncertainty. For current external facts, verify using appropriate sources rather than treating an old local snapshot as current.
