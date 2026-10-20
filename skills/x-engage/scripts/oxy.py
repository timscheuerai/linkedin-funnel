#!/usr/bin/env python3
"""Shared helpers for x-engage: the author's config, the OXYGEN CLI wrapper and the X reads.

The config holds names and IDs, never credentials. Copy
`skills/x-engage/config.example.json` to `.oxygen/x-engage.json` at the kit
root (git-ignored) and fill it, or point X_ENGAGE_CONFIG at another file.
X reads go through the X connection in the author's OXYGEN workspace. X bills
its pay-per-use API for every post a read returns, whatever OXYGEN estimates,
so every read here is bounded. Nothing here posts, likes, follows or messages.
"""
import json, os, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]          # the kit root: scripts -> skill -> skills -> root
SKILL = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / ".oxygen" / "x-engage.json"
RETRYABLE = {"network_timeout", "rate_limited", "provider_error", "server_error", "provider_unavailable"}
TWEET_FIELDS = ["created_at", "public_metrics", "note_tweet", "conversation_id", "author_id",
                "attachments", "referenced_tweets", "in_reply_to_user_id", "entities"]
EXPANSIONS = ["author_id", "attachments.media_keys"]
USER_FIELDS = ["public_metrics", "username", "name", "verified", "profile_image_url"]
MEDIA_FIELDS = ["type", "url", "preview_image_url", "width", "height", "alt_text"]
_CONFIG = {}


def config():
    """The author's config, loaded once. Exits with a clear message when it is missing or unfilled."""
    if _CONFIG:
        return _CONFIG
    path = Path(os.environ.get("X_ENGAGE_CONFIG") or DEFAULT_CONFIG)
    if not path.exists():
        sys.exit(f"No config at {path}. Copy {SKILL / 'config.example.json'} there and fill it (see SKILL.md, setup).")
    c = json.loads(path.read_text())
    for key in ("x_handle", "watchlist_table"):
        if not c.get(key) or str(c[key]).startswith("YOUR"):
            sys.exit(f"Fill {key} in {path} first.")
    c["x_handle"] = c["x_handle"].lstrip("@")
    c.setdefault("runs_dir", "context/research/engage/x")
    c.setdefault("x_toolkit", "twitter")
    c.setdefault("x_search_action", "TWITTER_RECENT_SEARCH")
    c.setdefault("x_lookup_action", "TWITTER_POST_LOOKUP_BY_POST_IDS")
    c.setdefault("lanes", {})
    c.setdefault("focus_lanes", [])
    c.setdefault("niche_terms", "")
    c.setdefault("keyword_queries", [])
    c.setdefault("keyword_min_followers", 5000)
    c.setdefault("focus_queries", [])
    c.setdefault("focus_min_followers", 2000)
    c.setdefault("extra_banned_words", [])
    c.setdefault("taste_blocks", [])
    _CONFIG.update(c)
    return _CONFIG


def runs_dir():
    return ROOT / config()["runs_dir"]


def cli(args, max_chars=None, tries=3):
    """Run 1 read-only OXYGEN CLI call; retry timeouts and provider hiccups (reads are safe to repeat)."""
    c = config()
    cmd = ["oxygen"]
    if c.get("oxygen_profile"):
        cmd += ["--profile", c["oxygen_profile"]]
    if c.get("oxygen_org"):
        cmd += ["--org", c["oxygen_org"]]
    cmd += [*args, "--json"]
    if max_chars:
        cmd += ["--max-chars", str(max_chars)]
    for attempt in range(tries):
        try:
            out = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        except subprocess.TimeoutExpired:
            if attempt + 1 < tries:
                continue
            sys.exit("oxygen CLI timed out 3 times")
        try:
            data, _ = json.JSONDecoder().raw_decode(out.stdout.strip())
        except json.JSONDecodeError:
            if attempt + 1 < tries:
                time.sleep(3)
                continue
            sys.exit(f"oxygen CLI returned no JSON: {out.stderr[:400] or out.stdout[:400]}")
        if data.get("ok"):
            return data["data"]
        code = (data.get("error") or {}).get("code")
        if code in RETRYABLE and attempt + 1 < tries:
            time.sleep(5 * (attempt + 1))
            continue
        sys.exit(f"oxygen CLI error: {json.dumps(data.get('error'))[:600]}")


def _unpack(res, what):
    if not res.get("ok"):
        sys.exit(f"X {what} failed: {json.dumps(res.get('error'))[:600]}")
    body = res.get("data") or {}
    inc = body.get("includes") or {}
    users = {u["id"]: u for u in inc.get("users", [])}
    media = {m["media_key"]: m for m in inc.get("media", [])}
    return body.get("data") or [], users, media


def _run(action, inp, cap):
    c = config()
    return cli(["integrations", "run", c["x_toolkit"], c[action], "--input", json.dumps(inp),
                "--live", "--approved", "--max-credits", str(cap)])


def search(query, start, cap, max_results=100, pages=1):
    """X recent search, newest first, following next_token for up to `pages` pages.
    Returns (posts, users by id, media by key). Every post returned is a paid X read."""
    inp = {"query": query, "start_time": start, "max_results": max_results, "tweet_fields": TWEET_FIELDS,
           "expansions": EXPANSIONS, "user_fields": USER_FIELDS, "media_fields": MEDIA_FIELDS}
    posts, users, media = [], {}, {}
    for _ in range(max(1, pages)):
        data = _run("x_search_action", inp, cap)
        p, u, m = _unpack(data["result"], "search")
        posts += p
        users.update(u)
        media.update(m)
        token = ((data["result"].get("data") or {}).get("meta") or {}).get("next_token")
        if not token:
            break
        inp["next_token"] = token
    return posts, users, media


def lookup(ids, cap):
    """Current state of up to 100 posts by id. Returns (posts, users by id, media by key)."""
    inp = {"ids": ids[:100], "tweet_fields": TWEET_FIELDS, "expansions": EXPANSIONS,
           "user_fields": USER_FIELDS, "media_fields": MEDIA_FIELDS}
    return _unpack(_run("x_lookup_action", inp, cap)["result"], "lookup")


def text_of(t):
    return (t.get("note_tweet") or {}).get("text") or t.get("text", "")


def media_of(t, media):
    """Photos as-is; videos and GIFs as their preview frame."""
    out = []
    for k in (t.get("attachments") or {}).get("media_keys", []):
        m = media.get(k)
        if not m:
            continue
        src = m.get("url") or m.get("preview_image_url")
        if src:
            out.append({"type": m.get("type"), "src": src, "w": m.get("width"), "h": m.get("height"), "alt": m.get("alt_text")})
    return out
