# OXYGEN research route

Use this route when the author has an OXYGEN workspace with an X connection. Read [the OXYGEN guide](../../../guides/oxygen.md) first. Do not silently switch workspace, environment or the author's default profile.

## Discover the workspace and operation

```bash
oxygen whoami --json
oxygen integrations list --json
oxygen integrations actions twitter --json
oxygen integrations run --help
```

Pin the intended destination with `oxygen --profile YOUR_PROFILE --org YOUR_ORG ...` when needed. Confirm the intended workspace and X connection. Do not hardcode a connection ID in a public file or expose OAuth credentials. If several connections are active, discover how the current command selects one and resolve ambiguity before a live call. Command names and schemas change: discover them, do not trust a copied example.

If a generic tool catalog lists an X operation that returns `tool_not_found` on preview, try the integration-specific route below before concluding X is not connected.

## Preview and make a bounded read

```bash
oxygen integrations run twitter TWITTER_RECENT_SEARCH \
  --input '{"query":"\"cold email\" -is:retweet -is:reply lang:en","max_results":10,"sort_order":"relevancy","tweet_fields":["created_at","public_metrics","author_id","note_tweet"],"expansions":["author_id"],"user_fields":["public_metrics","description"]}' \
  --dry-run --json
```

Inspect the complete preview, including nested success or error and the estimated credits. Do not promise free reads or translate credits into money without a current rate.

When the read is within the author's request and budget, repeat the same input with the live and approval flags the current CLI documents and a hard credit cap per call, instead of `--dry-run`. An approval flag records existing authorization; it never authorizes publishing or DMs.

For a normal small scan, plan 2 or 3 search calls and state their total estimated credits first. A request for free research means browser or supplied sources, not this billed route. Do not paginate automatically, repeatedly check identity or turn on a monitor. Stop on auth, entitlement, rate-limit, budget or repeated routing errors and report the concrete blocker. A search labeled as a write in a catalog is still a read; check the action's actual semantics.

Recent search covers 7 days. Keep pages small (10 to 20) and request `note_tweet` so long posts can be read in full. `sort_order: relevancy` is not an engagement ranking: filter and sort the returned sample locally. Browser operators such as `min_faves:` may be stripped by the API; use public metrics after retrieval.

For a single post, inspect the post-lookup schema before calling. To investigate a conversation, request `conversation_id` and search that conversation within the available window. Do not promise a complete thread if the parent is older or the response is paginated.

## Save and normalize

Capture the live JSON in `research/<date>-x-<topic>/raw/` or a temporary file. Do not print credentials or large raw payloads into the conversation. The offline normalizer handles integration and generic tool envelopes, prefers long-post text, joins authors, keeps unavailable metrics null and sorts the retrieved sample. It makes no network calls and cannot publish.

```bash
python3 skills/x-research/scripts/normalize_oxygen.py response.json \
  --sort bookmarks --limit 10 --fetched-at 2026-01-15T12:00:00Z
```

Run it from the kit root. Use the actual fetch timestamp; without `--fetched-at`, the file modification time is used and labeled as such. Output includes the query, a pagination flag and the returned sample size. Local sorting is not a claim about the best posts on X. Preserve provider-reported view counts as returned, label them provider-reported, and do not treat absent or zero views as a reliable denominator.
