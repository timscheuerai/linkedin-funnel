#!/usr/bin/env python3
"""Incremental YouTube discovery and channel deep dives, with raw evidence.

Needs YOUTUBE_API_KEY (or OAuth variables) in the environment; see youtube_api.py.
Queries JSON: [{"branch": "claude-code", "query": "Claude Code", "after": "2026-01-01"}].
Channels JSON: an array of channel IDs. Each invocation has bounded API caps.
"""

import argparse
import atexit
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from youtube_api import YouTubeClient


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def read(path, default):
    return json.loads(path.read_text()) if path.exists() else default


def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--queries", type=Path)
    p.add_argument("--channels", type=Path)
    p.add_argument("--uploads", type=int, default=100)
    p.add_argument("--max-searches", type=int, default=40)
    p.add_argument("--max-calls", type=int, default=1000)
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    # 2 scans on 1 folder overwrite each other's JSON; refuse instead of losing data.
    lock = args.out / ".scan.lock"
    try:
        os.close(os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
    except FileExistsError:
        raise SystemExit(f"another scan is writing to {args.out}; wait, or delete {lock} if none is running")
    atexit.register(lambda: lock.unlink(missing_ok=True))
    responses = args.out / "responses"
    responses.mkdir(exist_ok=True)
    client = YouTubeClient(args.max_searches, args.max_calls)
    videos = read(args.out / "videos.json", {})
    channels = read(args.out / "channels.json", {})
    hits = read(args.out / "hits.json", {})
    uploads = read(args.out / "channel-uploads.json", {})
    searches = read(args.out / "searches.json", [])

    def fetch(endpoint, **params):
        started = now()
        data = client.get(endpoint, **params)
        digest = hashlib.sha256(json.dumps([endpoint, params], sort_keys=True).encode()).hexdigest()[:16]
        stamp = started.replace(":", "").replace("+", "_")
        write(responses / f"{stamp}-{endpoint}-{digest}.json",
              {"captured_at": started, "endpoint": endpoint, "params": params, "response": data})
        return data

    def enrich(ids, kind, target, parts):
        needed = sorted(set(ids) - set(target))
        for i in range(0, len(needed), 50):
            data = fetch(kind, part=parts, id=",".join(needed[i:i + 50]))
            for item in data.get("items", []):
                target[item["id"]] = item

    if args.queries:
        for query in json.loads(args.queries.read_text()):
            if any(s["spec"] == query and s.get("status") == "ok" for s in searches):
                continue
            params = {"part": "snippet", "q": query["query"], "type": "video", "maxResults": 50,
                      "order": query.get("order", "relevance"), "relevanceLanguage": "en"}
            if query.get("after"):
                params["publishedAfter"] = query["after"] + "T00:00:00Z"
            data = fetch("search", **params)
            ids = [x["id"]["videoId"] for x in data.get("items", []) if x.get("id", {}).get("videoId")]
            searches.append({"spec": query, "status": "ok", "captured_at": now(), "ids": ids})
            for vid in ids:
                hits.setdefault(vid, [])
                if query not in hits[vid]:
                    hits[vid].append(query)
            write(args.out / "hits.json", hits)
            write(args.out / "searches.json", searches)
            print(f"search {len(searches)}: {query['query']} → {len(ids)} results", flush=True)
        enrich(hits, "videos", videos, "snippet,statistics,contentDetails,liveStreamingDetails")
        write(args.out / "videos.json", videos)
        enrich([v["snippet"]["channelId"] for v in videos.values()], "channels", channels,
               "snippet,statistics,contentDetails")
        write(args.out / "channels.json", channels)

    if args.channels:
        channel_ids = json.loads(args.channels.read_text())
        enrich(channel_ids, "channels", channels, "snippet,statistics,contentDetails")
        write(args.out / "channels.json", channels)
        for index, cid in enumerate(channel_ids):
            if len(uploads.get(cid, {}).get("ids", [])) >= args.uploads or uploads.get(cid, {}).get("complete"):
                continue
            playlist = channels.get(cid, {}).get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")
            if not playlist:
                continue
            ids, page = [], None
            while len(ids) < args.uploads:
                params = {"part": "contentDetails", "playlistId": playlist, "maxResults": min(50, args.uploads - len(ids))}
                if page:
                    params["pageToken"] = page
                data = fetch("playlistItems", **params)
                ids.extend(x["contentDetails"]["videoId"] for x in data.get("items", []))
                page = data.get("nextPageToken")
                if not page:
                    break
            uploads[cid] = {"captured_at": now(), "ids": ids, "complete": not bool(page)}
            enrich(ids, "videos", videos, "snippet,statistics,contentDetails,liveStreamingDetails")
            write(args.out / "videos.json", videos)
            write(args.out / "channel-uploads.json", uploads)
            print(f"channel {index + 1}/{len(channel_ids)}: {channels[cid]['snippet']['title']} → {len(ids)} uploads", flush=True)
    run = {"finished_at": now(), "search_file": str(args.queries) if args.queries else None,
           "channel_file": str(args.channels) if args.channels else None,
           "calls": dict(client.counts), "max_searches": args.max_searches, "max_calls": args.max_calls,
           "discovered_videos": len(hits), "all_videos": len(videos), "channels": len(channels),
           "channels_with_uploads": len(uploads)}
    runs = read(args.out / "runs.json", [])
    runs.append(run)
    write(args.out / "runs.json", runs)
    print(json.dumps(run), flush=True)


if __name__ == "__main__":
    main()
