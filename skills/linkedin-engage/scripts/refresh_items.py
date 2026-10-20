#!/usr/bin/env python3
"""Bring a drafted LinkedIn run up to date right before it is rendered.

Read only, OXYGEN managed scraper: 1 `scraper.linkedin_post` call per post in
`items`, each capped with --max-credits and the whole refresh with --budget.
Updates reactions, comments and reposts, the text and the media, and drops
posts deleted since the fetch. Edits the run file in place and sets
`refreshed_at`.

  python3 refresh_items.py <runs_dir>/<run>.json
"""
import argparse, json, sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from oxy import SPENT, tool  # noqa: E402
from fetch_candidates import post_of  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("queue")
    ap.add_argument("--budget", type=float, default=30)
    a = ap.parse_args()
    q = json.load(open(a.queue))
    keep, dropped, failed = [], 0, 0
    for item in q.get("items", []):
        try:
            resp = tool("scraper.linkedin_post", {"url": item["url"]}, 2, a.budget)
        except RuntimeError as e:
            if "not_found" in str(e) or "404" in str(e):
                dropped += 1
                continue
            keep.append(item)   # over budget or a failed read: keep the item as fetched
            failed += 1
            continue
        el = (resp.get("raw") or {}).get("element")
        if not el:
            dropped += 1
            continue
        p = post_of(el, {})
        item["metrics"] = p["metrics"]
        item["text"] = p["text"] or item.get("text")
        if p["media"]:
            item["media"] = p["media"]
        keep.append(item)
    q["items"] = keep
    q["refreshed_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    json.dump(q, open(a.queue, "w"), indent=1, ensure_ascii=False)
    print(f"refreshed {len(keep) - failed} posts, {failed} left as fetched, {dropped} deleted since the fetch; "
          f"{round(SPENT['credits'], 2)} credits")


if __name__ == "__main__":
    main()
