#!/usr/bin/env python3
"""Learn the author's taste from what they posted and skipped.

Read only, the author's OXYGEN X connection, 1 recent search for their replies
since the last time it ran (X bills every post returned); the replies it has
seen are kept in taste.json, so each run only reads the new ones. Compares
every drafted reply in the run files with what the author actually posted,
then writes `<runs_dir>/taste.json`: per-account shown and posted counts (the
fetch demotes accounts they keep skipping and boosts the ones they answer) and
posted rates by post age and by angle, printed as a short report.

  python3 learn_taste.py            # before every run
"""
import argparse, collections, json, re, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from oxy import config, runs_dir, search, text_of  # noqa: E402


def bucket_age(m):
    return "under 15m" if m < 15 else "15 to 60m" if m < 60 else "1 to 3h" if m < 180 else "over 3h"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--days", type=float, default=6, help="how far back to read the author's replies (recent search covers 7 days)")
    ap.add_argument("--cap", type=int, default=1)
    a = ap.parse_args()
    me = config()["x_handle"]
    runs = runs_dir()
    runs.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    old = json.loads((runs / "taste.json").read_text()) if (runs / "taste.json").exists() else {}
    posted = dict(old.get("posted_ids") or {})
    since = now - timedelta(days=a.days)
    if posted and old.get("updated_at"):
        since = max(since, datetime.fromisoformat(old["updated_at"].replace("Z", "+00:00")) - timedelta(hours=1))
    mine, _, _ = search(f"from:{me} is:reply", since.strftime("%Y-%m-%dT%H:%M:%SZ"), a.cap)
    for t in mine:
        for r in t.get("referenced_tweets", []):
            if r["type"] == "replied_to":
                posted[r["id"]] = re.sub(r"^(@\w+\s+)+", "", text_of(t)).strip()

    authors = collections.defaultdict(lambda: {"shown": 0, "posted": 0})
    by_age = collections.defaultdict(lambda: [0, 0])
    by_angle = collections.defaultdict(lambda: [0, 0])
    rows = 0
    counted = set()
    cutoff = now - timedelta(days=a.days)
    for f in sorted(runs.glob("20*.json")):
        q = json.loads(f.read_text())
        fetched = datetime.fromisoformat(q["fetched_at"].replace("Z", "+00:00"))
        if fetched < cutoff or (now - fetched) < timedelta(minutes=30):
            continue  # too old to check, or too new to judge
        if q.get("items") and not any(i["id"] in posted for i in q["items"]):
            continue  # nothing posted at all: a missed window, not a verdict on the drafts
        for item in q.get("items", []):
            if item["id"] in counted:
                continue  # carried over into a later run, judged once
            counted.add(item["id"])
            rows += 1
            got = item["id"] in posted
            au = item["author"].lower()
            authors[au]["shown"] += 1
            authors[au]["posted"] += got
            age = (fetched - datetime.fromisoformat(item["created_at"].replace("Z", "+00:00"))).total_seconds() / 60
            by_age[bucket_age(age)][0] += 1
            by_age[bucket_age(age)][1] += got
            by_angle[item.get("angle") or "?"][0] += 1
            by_angle[item.get("angle") or "?"][1] += got

    taste = {"updated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "drafts_judged": rows,
             "posted": sum(v["posted"] for v in authors.values()),
             "posted_ids": posted,
             "authors": dict(authors),
             "by_age": {k: {"shown": v[0], "posted": v[1]} for k, v in by_age.items()},
             "by_angle": {k: {"shown": v[0], "posted": v[1]} for k, v in by_angle.items()}}
    (runs / "taste.json").write_text(json.dumps(taste, indent=1, ensure_ascii=False))
    print(f"{rows} drafts judged, {taste['posted']} posted")
    for k in ("under 15m", "15 to 60m", "1 to 3h", "over 3h"):
        if k in by_age:
            s, p = by_age[k]
            print(f"  age {k:10} {p}/{s} posted")
    favs = sorted((h for h, v in authors.items() if v["posted"]), key=lambda h: -authors[h]["posted"])
    cold = sorted(h for h, v in authors.items() if v["shown"] >= 2 and not v["posted"])
    print("  answers:", ", ".join("@" + h for h in favs[:15]) or "nobody yet")
    print("  keeps skipping:", ", ".join("@" + h for h in cold) or "nobody yet")


if __name__ == "__main__":
    main()
