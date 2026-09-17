# Add qualification to the watcher table

[Back to LinkedIn Funnel](../README.md) · [Previous: collection](profile-watcher.md) · [Next: conversations](dm-conversion.md)

The first useful output is a short list of people who fit your buyer criteria, with reasons you can inspect. Keep company fit and the person's current remit separate. A highly engaged person at the wrong company should not pass.

## 1. Write your rubric

Copy [the blank rubric](../templates/icp-rubric.md) into `company/private/` and fill it using your own ICP, offer and exclusions. Define company criteria, person criteria, pass thresholds and evidence you consider mandatory. Make the points add to 100 independently for company and person.

The kit's [company example](../company/icp.example.md) and [persona example](../company/persona.example.md) show the level of detail. They are synthetic examples, not recommended criteria for every reader.

## 2. Inspect the collected evidence

```sh
oxygen tables describe YOUR_WATCHER_TABLE --json
oxygen tables query YOUR_WATCHER_TABLE --limit 10 --json
```

The watcher exposes person and employer evidence, including `profile_data` and `company_data`, plus attribution such as `source_profile_urls`, `source_post_urls` and `engagement_types`. Verify the exact keys in your table. Older/custom tables may differ. Update the prompt's bindings to those actual keys before adding it.

Review employment and enrichment state. Missing or unresolved fields should produce a review decision, not an invented company size, job responsibility or purchase intent. A company name alone is not enough to assume a domain or identity match.

## 3. Add one AI qualification column

Copy [the prompt](../templates/qualification-prompt.md) into `company/private/linkedin-qualification.md`. Replace its rubric block with the criteria from step 1. The prompt reads existing evidence; it performs no new web research and should not invent missing facts.

The UI equivalent is an AI column on your watcher table with that prompt, the actual evidence columns as inputs and the [structured output schema](../templates/qualification-output.schema.json). With the CLI, run from the repository root:

```sh
oxygen columns add YOUR_WATCHER_TABLE \
  --key qualification --label "Qualification" \
  --kind ai --data-type jsonb \
  --prompt company/private/linkedin-qualification.md \
  --output-schema-file templates/qualification-output.schema.json \
  --json
```

This writes a column definition; it does not execute or schedule it. Before adding it on a second attempt, describe the table and reuse the existing `qualification` column. Use the current `columns update` command to revise its definition deliberately.

The output contains company/persona scores, independent disqualifiers, a fit status, reasons, missing evidence and evidence used. **Qualified means passes the rubric; it does not mean approved for outreach.**

## 4. Preview and calibrate

Choose one row you can assess yourself. OXYGEN row IDs are returned as `_row_id`.

```sh
oxygen columns run YOUR_WATCHER_TABLE qualification \
  --row-id YOUR_ROW_ID --dry-run --json
```

Inspect the rendered prompt, bound evidence and credit estimate. Then, if you want that model call:

```sh
oxygen columns run YOUR_WATCHER_TABLE qualification \
  --row-id YOUR_ROW_ID --approved --max-credits YOUR_CHOSEN_CAP --json
oxygen table-runs wait RETURNED_RUN_ID --json
oxygen tables query YOUR_WATCHER_TABLE --limit 10 --json
```

Calibrate against a small reviewed set: a clear fit, a wrong-company case, a wrong-person case, and missing evidence. [Synthetic examples](../examples/qualification-decisions.json) show expected decisions; they are not model test results. Read the evidence behind each score and adjust the rubric before expanding. A dry run verifies prompt preparation and estimated cost, not model judgment.

Keep three views or filters: **Qualified**, **Review**, **Not fit**. Both scores must meet your thresholds; both disqualification flags must explicitly be false; mandatory evidence must be present. Keep engagement/recency separately for prioritization after fit. Never use an engagement bonus to rescue a failed fit gate.

## 5. Make it repeatable when the first batch works

Manual bounded batches are enough to start. If you want qualification for newly collected rows, configure OXYGEN's native table auto-run for that exact column and its own credit cap, after inspecting dependencies and a sample run. Discovery:

```sh
oxygen tables auto-run --help
oxygen capabilities search "run qualification when new table rows arrive" --json
```

Watcher refresh and paid AI auto-run are separate recurring settings. Hold rows until required enrichment has completed, and ensure they can be reconsidered after evidence changes. Review existing output before a forced rerun; changing the rubric does not automatically recalibrate old results.

If you later need the same rubric across several tables, discover native OXYGEN Functions and publish the reviewed qualification procedure with explicit evidence bindings. The single-column setup above is enough to start.

Hand off only a reviewed cohort to [the DM framework](dm-conversion.md) and native Sequences. This guide configures qualification, not automatic enrollment.
