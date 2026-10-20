#!/usr/bin/env python3
"""Bring a drafted X run up to date right before it is rendered.

Read only, the author's OXYGEN X connection, 1 post lookup for every post in
the run (up to 100 ids per call, capped with --max-credits). Updates likes,
replies and the rest, adds the post's images (video and GIF previews) and the
author's avatar, and drops posts deleted since the fetch. Edits the run file
in place.

  python3 refresh_items.py <runs_dir>/<run>.json
"""
import argparse, json, sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from oxy import lookup, media_of, text_of  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("queue")
    ap.add_argument("--cap", type=int, default=1)
    a = ap.parse_args()
    q = json.load(open(a.queue))
    q.pop("on_my_posts", None)   # the author answers replies on their own posts themselves
    items = q.get("items", [])
    ids = [i["id"] for i in items]
    if not ids:
        print("nothing to refresh")
        return
    posts, users, media = lookup(ids, a.cap)
    live = {t["id"]: t for t in posts}
    keep, dropped = [], 0
    for item in items:
        t = live.get(item["id"])
        if not t:
            dropped += 1
            continue
        u = users.get(t["author_id"], {})
        item["metrics"] = t["public_metrics"]
        item["text"] = text_of(t)
        item["media"] = media_of(t, media)
        item["avatar"] = u.get("profile_image_url") or item.get("avatar")
        item["name"] = u.get("name") or item.get("name")
        item["followers"] = (u.get("public_metrics") or {}).get("followers_count") or item.get("followers")
        keep.append(item)
    q["items"] = keep
    q["refreshed_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    json.dump(q, open(a.queue, "w"), indent=1, ensure_ascii=False)
    with_media = sum(1 for i in keep if i.get("media"))
    print(f"refreshed {len(keep)} posts, {with_media} with images, {dropped} deleted since the fetch")


if __name__ == "__main__":
    main()
