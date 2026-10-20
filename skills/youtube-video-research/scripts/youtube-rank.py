#!/usr/bin/env python3
"""Rank snapshot candidates against transparent, target-excluded channel cohorts.

Age-band ratio is a cross-sectional comparison, NOT historical views at equal
age and NOT current views/hour. Never label it velocity. Shorts/streams excluded.
"""

import argparse
import csv
import json
import re
import statistics
from datetime import datetime, timezone
from pathlib import Path


def seconds(text):
    match = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", text)
    return sum(int(x or 0) * factor for x, factor in zip(match.groups(), [3600, 60, 1])) if match else 0


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--as-of", default=datetime.now(timezone.utc).isoformat())
    p.add_argument("--title-pattern", default=".",
                   help="Regex selecting candidate titles; baselines still use all eligible uploads")
    args = p.parse_args()
    asof = datetime.fromisoformat(args.as_of.replace("Z", "+00:00"))
    videos = json.loads((args.source / "videos.json").read_text())
    hits = json.loads((args.source / "hits.json").read_text())
    uploads = json.loads((args.source / "channel-uploads.json").read_text())
    channels = json.loads((args.source / "channels.json").read_text())
    rows = {}
    for vid, v in videos.items():
        sn = v["snippet"]
        age = (asof - datetime.fromisoformat(sn["publishedAt"].replace("Z", "+00:00"))).total_seconds() / 86400
        duration = seconds(v.get("contentDetails", {}).get("duration", ""))
        views = v.get("statistics", {}).get("viewCount")
        live = bool(v.get("liveStreamingDetails")) or sn.get("liveBroadcastContent") in ("live", "upcoming")
        lang = sn.get("defaultAudioLanguage", "")
        # Language metadata can be missing/wrong. Final recommendation gets manual review.
        eligible = age >= 1 and duration >= 240 and not live and views is not None
        rows[vid] = {"id": vid, "title": sn["title"], "channel": sn["channelTitle"], "channel_id": sn["channelId"],
                     "published": sn["publishedAt"], "age_days": round(age, 2), "duration_seconds": duration,
                     "views": int(views or 0), "likes": v.get("statistics", {}).get("likeCount"),
                     "comments": v.get("statistics", {}).get("commentCount"),
                     "subscribers": channels.get(sn["channelId"], {}).get("statistics", {}).get("subscriberCount"),
                     "language": lang, "eligible": eligible, "stream": live,
                     "url": "https://www.youtube.com/watch?v=" + vid}
    ranked = []
    for vid, row in rows.items():
        if not row["eligible"] or row["age_days"] > 90:
            continue
        if not re.search(args.title_pattern, row["title"], re.I):
            continue
        if row["language"] and not row["language"].startswith("en"):
            continue
        cid = row["channel_id"]
        if cid not in uploads:
            continue
        recent = [rows[x] for x in uploads[cid]["ids"] if x in rows and x != vid and rows[x]["eligible"]
                  and 3 <= rows[x]["age_days"] <= 90]
        recent.sort(key=lambda x: x["published"], reverse=True)
        recent = recent[:20]
        # Similar current age, same channel, comparable length; target excluded.
        age_min, age_max = max(3, row["age_days"] / 2), min(90, max(7, row["age_days"] * 2))
        peers = [rows[x] for x in uploads[cid]["ids"] if x in rows and x != vid and rows[x]["eligible"]
                 and age_min <= rows[x]["age_days"] <= age_max
                 and row["duration_seconds"] / 3 <= rows[x]["duration_seconds"] <= row["duration_seconds"] * 3]
        row = dict(row)
        row["discovery"] = "keyword" if vid in hits else "channel-depth"
        row["queries"] = "; ".join(x["query"] for x in hits.get(vid, []))
        row["recent_n"] = len(recent)
        row["recent_median"] = statistics.median(x["views"] for x in recent) if len(recent) >= 5 else None
        row["recent_ratio"] = round(row["views"] / row["recent_median"], 2) if row["recent_median"] else None
        row["age_band_min"] = round(age_min, 2)
        row["age_band_max"] = round(age_max, 2)
        row["age_band_n"] = len(peers)
        row["age_band_median"] = statistics.median(x["views"] for x in peers) if len(peers) >= 5 else None
        row["age_band_ratio"] = round(row["views"] / row["age_band_median"], 2) if row["age_band_median"] else None
        row["peer_ids"] = [x["id"] for x in peers]
        row["recent_ids"] = [x["id"] for x in recent]
        row["lifetime_views_per_day"] = round(row["views"] / max(row["age_days"], 1), 1)
        row["gtm_title"] = bool(re.search(r"gtm|marketing|sales|lead|outbound|business|company|client|crm|linkedin", row["title"], re.I))
        ranked.append(row)
    ranked.sort(key=lambda x: (-(x["age_band_ratio"] or 0), -x["views"]))
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "ranked.json").write_text(json.dumps({"as_of": asof.isoformat(), "title_pattern": args.title_pattern, "rows": ranked}, indent=2, ensure_ascii=False) + "\n")
    if ranked:
        fields = [x for x in ranked[0] if x not in ("eligible", "peer_ids", "recent_ids")]
        with (args.out / "ranked.tsv").open("w") as fh:
            writer = csv.DictWriter(fh, fields, delimiter="\t", extrasaction="ignore")
            writer.writeheader()
            writer.writerows(ranked)
    print(json.dumps({"eligible_candidates": len(ranked), "with_age_band_baseline": sum(x["age_band_ratio"] is not None for x in ranked)}))


if __name__ == "__main__":
    main()
