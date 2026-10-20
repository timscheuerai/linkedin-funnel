#!/usr/bin/env python3
"""What is already said under the X posts the author may reply to.

Read only, the author's OXYGEN X connection, 1 recent search per post
(`conversation_id:<id>`), capped with --max-credits. X bills every reply it
returns, so it reads --per-post replies (10 by default) and only when a post
already has 5+ replies. For each post it lists the top replies by likes and
whether the post's author has been answering, so the draft adds something new
instead of repeating the thread.

  python3 thread_context.py <scratch>/candidates.json --ids 123,456 --out <scratch>/threads.json
"""
import argparse, json, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from oxy import search, text_of  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("candidates")
    ap.add_argument("--ids", required=True, help="comma-separated post ids")
    ap.add_argument("--top", type=int, default=8)
    ap.add_argument("--per-post", type=int, default=10, help="replies read per post (10 to 100), each a paid X read")
    ap.add_argument("--cap", type=int, default=1)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cands = {c["id"]: c for c in json.load(open(a.candidates))["candidates"]}
    since = (datetime.now(timezone.utc) - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
    out = {}
    for pid in [i.strip() for i in a.ids.split(",") if i.strip()]:
        c = cands.get(pid, {})
        if (c.get("metrics") or {}).get("reply_count", 0) < 5:
            print(f"@{c.get('author')}: under 5 replies, not read")
            continue
        replies, users, _ = search(f"conversation_id:{pid} is:reply", since, a.cap, max_results=max(10, min(100, a.per_post)))
        rows = []
        for t in replies:
            u = users.get(t["author_id"], {})
            rows.append({"author": u.get("username"), "followers": (u.get("public_metrics") or {}).get("followers_count"),
                         "likes": t["public_metrics"]["like_count"], "text": text_of(t)[:280]})
        rows.sort(key=lambda r: -r["likes"])
        author = (c.get("author") or "").lower()
        out[pid] = {"author": c.get("author"), "replies_seen": len(rows),
                    "author_answers": sum(1 for r in rows if (r["author"] or "").lower() == author),
                    "top": rows[: a.top]}
        print(f"@{c.get('author')}: {len(rows)} replies, author answered {out[pid]['author_answers']}")
    json.dump(out, open(a.out, "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
