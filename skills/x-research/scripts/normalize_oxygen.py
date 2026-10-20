#!/usr/bin/env python3
"""Normalize a saved OXYGEN X response locally; never calls a provider."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys


METRICS = {
    "likes": "like_count",
    "bookmarks": "bookmark_count",
    "reposts": "retweet_count",
    "replies": "reply_count",
    "quotes": "quote_count",
    "views": "impression_count",
}


def timestamp(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Timestamps must include a timezone")
    return parsed.astimezone(timezone.utc)


def unwrap(document):
    """Accept native integrations, generic tools, or raw X API payloads."""
    node = document
    query = None
    warnings = []
    for _ in range(10):
        if not isinstance(node, dict):
            raise ValueError("Expected an object containing X post data")
        if node.get("ok") is False or node.get("successful") is False or node.get("error"):
            raise ValueError("Provider response failed: " + json.dumps(node.get("error", node)))
        if node.get("mode") in ("dry_run", "dry-run") or node.get("dry_run"):
            raise ValueError("A dry-run response contains no fetched posts")
        query = (node.get("arguments") or node.get("request") or {}).get("query", query)
        if isinstance(node.get("data"), list):
            return node, query, warnings
        if isinstance(node.get("data"), dict) and "id" in node["data"] and "text" in node["data"]:
            return {**node, "data": [node["data"]]}, query, warnings
        if isinstance(node.get("meta"), dict) and node["meta"].get("result_count") == 0:
            return {**node, "data": []}, query, warnings
        if node.get("errors") and not node.get("data"):
            raise ValueError("Provider returned errors: " + json.dumps(node["errors"]))
        for key in ("result", "response", "raw", "data"):
            if isinstance(node.get(key), dict):
                node = node[key]
                break
        else:
            raise ValueError("No X posts found in this response envelope")
    raise ValueError("Response envelope is nested too deeply")


def normalize(document, captured_at):
    payload, query, warnings = unwrap(document)
    warnings.extend(payload.get("errors") or [])
    users = {str(u["id"]): u for u in payload.get("includes", {}).get("users", [])}
    posts = []
    seen = set()
    for post in payload["data"]:
        post_id = str(post.get("id", ""))
        if not post_id or "text" not in post or post_id in seen:
            continue
        seen.add(post_id)
        user = users.get(str(post.get("author_id", "")), {})
        long_text = (post.get("note_tweet") or {}).get("text")
        metrics = post.get("public_metrics") or {}
        age_hours = None
        if post.get("created_at"):
            try:
                age_hours = round((captured_at - timestamp(post["created_at"])).total_seconds() / 3600, 2)
            except (ValueError, TypeError):
                warnings.append("Invalid publication timestamp for " + post_id)
        posts.append({
            "id": post_id,
            "url": "https://x.com/" + user.get("username", "i") + "/status/" + post_id,
            "author": user.get("username"),
            "author_followers": (user.get("public_metrics") or {}).get("followers_count"),
            "published_at": post.get("created_at"),
            "age_hours_at_capture": age_hours,
            "text": long_text or post["text"],
            "text_source": "note_tweet" if long_text else "text",
            "metrics": {name: metrics.get(key) for name, key in METRICS.items()},
        })
    meta = payload.get("meta") or {}
    return {
        "query": query,
        "fetched_at": captured_at.isoformat(),
        "metrics_source": "provider-reported",
        "raw_result_count": len(payload["data"]),
        "unique_post_count": len(posts),
        "has_more": bool(meta.get("has_more") or meta.get("next_token")),
        "warnings": warnings,
        "posts": posts,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("response", type=Path)
    parser.add_argument("--sort", choices=[*METRICS, "recent"], default="likes")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--min-likes", type=int, default=0)
    parser.add_argument("--fetched-at", help="Actual capture time with timezone; defaults to labeled file mtime")
    args = parser.parse_args()
    if args.limit < 1 or args.min_likes < 0:
        parser.error("--limit must be positive and --min-likes non-negative")
    try:
        captured = timestamp(args.fetched_at) if args.fetched_at else datetime.fromtimestamp(
            args.response.stat().st_mtime, timezone.utc)
        result = normalize(json.loads(args.response.read_text()), captured)
        posts = result["posts"]
        if args.min_likes:
            posts = [p for p in posts if (p["metrics"]["likes"] or 0) >= args.min_likes]
        if args.sort == "recent":
            posts.sort(key=lambda p: -(p["age_hours_at_capture"] if p["age_hours_at_capture"] is not None else float("inf")), reverse=True)
        else:
            posts.sort(key=lambda p: p["metrics"][args.sort] if p["metrics"][args.sort] is not None else -1, reverse=True)
        result.update({
            "capture_time_source": "explicit" if args.fetched_at else "source_file_mtime",
            "ranking_scope": "retrieved sample only",
            "sort": args.sort,
            "min_likes": args.min_likes,
            "matching_post_count": len(posts),
            "posts": posts[:args.limit],
        })
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
