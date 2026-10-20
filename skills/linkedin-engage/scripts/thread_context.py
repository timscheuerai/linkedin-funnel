#!/usr/bin/env python3
"""What is already said under the LinkedIn posts the author may comment on.

Read only, OXYGEN managed scraper: 1 `scraper.linkedin_post_comments` call per
post, billed per comment returned (6 by default), each capped with
--max-credits and the whole read with --budget. For each post it lists the
comments read and whether the post's author answers commenters, so the draft
adds something new instead of repeating the thread. The managed list returns
top-level comments only, without reaction counts. Posts with 0 comments are
not read.

  python3 thread_context.py <scratch>/candidates.json --ids <id,id,...> --out <scratch>/threads.json
"""
import argparse, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from oxy import SPENT, me_slug, slug_of, tool  # noqa: E402
from fetch_candidates import comments_of  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("candidates")
    ap.add_argument("--ids", required=True, help="comma-separated post ids (the `id` field)")
    ap.add_argument("--per-post", type=int, default=6, help="comments to read per post (billed per comment)")
    ap.add_argument("--budget", type=float, default=80, help="credit ceiling for all thread reads")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cands = {c["id"]: c for c in json.load(open(a.candidates))["candidates"]}
    me = me_slug()
    out = {}
    for pid in [i.strip() for i in a.ids.split(",") if i.strip()]:
        c = cands.get(pid)
        if not c:
            print(f"{pid}: not in the candidates file")
            continue
        if not c["metrics"].get("comments"):
            out[pid] = {"author": c["author"], "comments_seen": 0, "author_answers": 0, "me_already": False, "top": []}
            print(f"{c['name']}: no comments yet, nothing to read")
            continue
        try:
            resp = tool("scraper.linkedin_post_comments", {"post": c["url"], "max_results": a.per_post},
                        a.per_post + 1, a.budget)
        except RuntimeError as e:
            print(f"{c['name']}: {str(e)[:160]}")
            if "budget" in str(e):
                break
            continue   # 1 failed read must not stop the others
        rows = [{"name": r.get("name"), "author": slug_of(r.get("linkedin_url")), "headline": (r.get("headline") or "")[:120],
                 "created_at": r.get("created_at"), "text": (r.get("comment") or "")[:400]} for r in comments_of(resp)]
        author = slug_of(c.get("author_url"))
        out[pid] = {"author": c["author"], "comments_seen": len(rows),
                    "author_answers": sum(1 for r in rows if r["author"] and r["author"] == author),
                    "me_already": any(r["author"] == me for r in rows), "top": rows}
        print(f"{c['name']}: {len(rows)} comments read, author answered {out[pid]['author_answers']}"
              + (", you already commented" if out[pid]["me_already"] else ""))
    json.dump(out, open(a.out, "w"), indent=1, ensure_ascii=False)
    print(f"{round(SPENT['credits'], 2)} credits -> {a.out}")


if __name__ == "__main__":
    main()
