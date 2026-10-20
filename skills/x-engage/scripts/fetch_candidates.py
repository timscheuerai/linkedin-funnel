#!/usr/bin/env python3
"""Fresh X posts worth a reply from the author, from their X Watchlist.

Read only. Uses the X connection in the author's OXYGEN workspace through the
CLI: 1 Tables read for the watchlist, then bounded recent searches (`from:`
batches) for fresh original posts from the watchlist and the circle, 1 for the
author's own replies of the last day (to skip posts they already answered) and
1 for replies to them in the last day (people who talk to them get a boost).
Replies on the author's own posts are not queued: they answer those themselves.

Cost: X bills its pay-per-use API for every post a read returns. The `from:`
batches return only posts inside the window, so a default run reads tens of
posts. Keyword searches return a full page whatever the window, so they are
opt-in (--keywords, at --kw-results posts each). Nothing is posted, liked or
followed.

  python3 fetch_candidates.py --hours 3 --out <scratch>/candidates.json
  python3 fetch_candidates.py --hours 3 --out <scratch>/c.json --last-queue <runs_dir>/<file>.json

Output: JSON with `candidates` (scored) and, with --last-queue, `feedback`
(each earlier draft against what the author actually posted).
"""
import argparse, json, math, re, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from oxy import SKILL, cli, config, media_of, runs_dir, search, text_of  # noqa: E402

QUERY_LIMIT = 480  # X recent search allows 512 characters on the self-serve tiers
SPEED_MIN_FOLLOWERS = 50000
SPEED_MAX_REPLIES = 300


def batches(handles, base):
    """Group handles into `(from:a OR from:b) <base>` queries under the length limit."""
    out, cur = [], []
    for h in handles:
        trial = cur + [h]
        q = "(" + " OR ".join(f"from:{x}" for x in trial) + ") " + base
        if len(q) > QUERY_LIMIT and cur:
            out.append(cur)
            cur = [h]
        else:
            cur = trial
    if cur:
        out.append(cur)
    return ["(" + " OR ".join(f"from:{x}" for x in b) + ") " + base for b in out]


def age_minutes(t, now):
    return (now - datetime.fromisoformat(t["created_at"].replace("Z", "+00:00"))).total_seconds() / 60


def score(t, followers, now, fit=1):
    m = t["public_metrics"]
    age_h = max(age_minutes(t, now) / 60, 0.25)
    signal = m["like_count"] + 3 * m["reply_count"] + 2 * m["retweet_count"] + m.get("bookmark_count", 0)
    velocity = signal / age_h
    fresh = 1.0 if age_h <= 1 else 0.75 if age_h <= 2 else 0.5 if age_h <= 3 else 0.2
    crowd = 1.0 if m["reply_count"] < 30 else 0.7 if m["reply_count"] < 100 else 0.4
    reach = math.log10((followers or 0) + 10)
    return round(reach * (1 + math.log10(1 + velocity)) * fresh * crowd * (0.4 + 0.3 * fit), 2), round(velocity, 1)


def speed_score(t, followers, now):
    """Freshness first (under 15 minutes is best), then how crowded the replies are, then size and speed."""
    m = t["public_metrics"]
    age_m = age_minutes(t, now)
    fresh = 1.0 if age_m <= 15 else 0.85 if age_m <= 30 else 0.65 if age_m <= 45 else 0.5 if age_m <= 60 else 0.3
    r = m["reply_count"]
    crowd = 1.0 if r < 20 else 0.8 if r < 60 else 0.6 if r < 150 else 0.35
    velocity = (m["like_count"] + 3 * r + 2 * m["retweet_count"]) / max(age_m / 60, 0.1)
    return round(math.log10((followers or 0) + 10) * fresh * crowd * (1 + math.log10(1 + velocity)), 2)


def handles_in(name, section=None):
    """@handles listed as `- @handle` lines in a references page, optionally only under 1 `## ` section."""
    try:
        text = (SKILL / "references" / name).read_text()
    except OSError:
        return set()
    if section:
        text = text.split(f"## {section}", 1)[-1].split("\n## ", 1)[0] if f"## {section}" in text else ""
    return {h.lower() for h in re.findall(r"(?m)^\s*-\s*@(\w+)", text)}


def load_taste():
    try:
        return json.loads((runs_dir() / "taste.json").read_text()).get("authors", {})
    except Exception:
        return {}


FLAGS = [
    ("giveaway", re.compile(r"\b[Cc]omment\s+[\"'“]?[A-Z]{2,}\b|\b[Rr]eply\s+[\"'“][A-Za-z]+|\bRT\s*\+\s*[Ff]ollow|\b[Gg]iveaway\b")),
    ("politics", re.compile(r"(?i)\b(election|democrat|republican|war)\b")),
    ("link_only", re.compile(r"^\s*https?://\S+\s*$")),
    ("promo", re.compile(r"(?i)\b(airdrop|presale|\$[A-Z]{2,6}\b|web3|crypto|token launch|whitelist|escrow|jobs found today|telegram|bonding curve|"
                         r"hours left|final hour|limited spots|dm me for|i help founders|sponsored)\b")),
    ("hiring", re.compile(r"(?i)\b(hiring|job alert|we're hiring|now hiring|job type|work mode|apply here|remote jobs?)\b|💼|📍 location")),
    ("styled", re.compile("[\U0001D400-\U0001D7FF]{4,}")),  # unicode bold headlines are almost always promos
]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--hours", type=float, default=3, help="how far back to look for fresh posts")
    ap.add_argument("--priorities", default="1,2,3", help="watchlist priority digits to include")
    ap.add_argument("--cap", type=int, default=1, help="--max-credits per live call")
    ap.add_argument("--limit", type=int, default=40, help="candidates to keep after scoring")
    ap.add_argument("--last-queue", help="an earlier run JSON, to compare drafts with what the author posted")
    ap.add_argument("--keywords", action="store_true", help="opt in to the keyword searches outside the watchlist (paid X reads)")
    ap.add_argument("--kw-results", type=int, default=25, help="posts per keyword search page (10 to 100); each one is a paid X read")
    ap.add_argument("--pages", type=int, default=1, help="pages per keyword search; a broad search fills 1 page in minutes")
    ap.add_argument("--focus", action="store_true", help="with --keywords, add the config's focus_queries and keep only posts in focus_lanes")
    ap.add_argument("--speed", action="store_true", help="big accounts only (references/big-accounts.md and watchlist 50k+), posts under --max-age-min, any topic but politics and promos")
    ap.add_argument("--max-age-min", type=float, default=None, help="drop posts older than this (default 90 in speed mode, 180 otherwise)")
    ap.add_argument("--broad", action="store_true", help="switch off the niche gate (any topic)")
    ap.add_argument("--min-niche", type=int, default=1, help="distinct niche terms a post needs (a junk gate; the real filter is the pick checklist)")
    ap.add_argument("--feedback-only", action="store_true", help="only compare --last-queue drafts with what the author posted; no new candidates")
    ap.add_argument("--since-days", type=float, default=1, help="how far back to read the author's own replies (each one is a paid X read)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    c = config()
    me = c["x_handle"]
    lanes = {n: re.compile(rx, re.I) for n, rx in c["lanes"].items()}
    niche_rx = re.compile(c["niche_terms"], re.I) if c["niche_terms"] else None

    def fit_of(text):
        return min(3, sum(1 for rx in lanes.values() if rx.search(text))) if lanes else 1

    def niche_of(text):
        if not niche_rx:
            return 1      # no niche terms configured: the gate is off
        return min(4, len({m.group(0).lower().rstrip("s") for m in niche_rx.finditer(text)}))

    now = datetime.now(timezone.utc)
    start = (now - timedelta(hours=a.hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
    if a.max_age_min is None:
        a.max_age_min = 90 if a.speed else 180
    taste = load_taste()
    circle = handles_in("circle.md", "The circle")
    rows = cli(["tables", "query", c["watchlist_table"], "--limit", "500", "--fields",
                "handle,name,followers,priority,lane,notes"], max_chars=100000)["rows"]
    wanted = set(a.priorities.split(","))
    watch = {}
    for r in rows:
        h = (r.get("handle") or "").lstrip("@").strip()
        if h and h.lower() != me.lower() and str(r.get("priority") or "")[:1] in wanted:
            watch[h.lower()] = r
    for h in circle:
        watch.setdefault(h, {"handle": "@" + h, "notes": "circle"})
    if a.speed:
        big = handles_in("big-accounts.md") | circle
        big |= {h for h, r in watch.items() if (r.get("followers") or 0) >= SPEED_MIN_FOLLOWERS}
        for h in big:
            watch.setdefault(h, {"handle": "@" + h, "notes": "big reach"})
        if not big:
            print("speed mode has no accounts: fill references/big-accounts.md or the circle, or add 50k+ accounts to the watchlist")
        queries = batches(sorted(big), "-is:retweet -is:reply")
    else:
        queries = batches(sorted(watch), "-is:retweet -is:reply")

    # Posts the author already replied to, so they are skipped.
    mine, _, _ = search(f"from:{me} is:reply", (now - timedelta(days=a.since_days)).strftime("%Y-%m-%dT%H:%M:%SZ"), a.cap)
    replied_to = {ref["id"] for t in mine for ref in t.get("referenced_tweets", []) if ref["type"] == "replied_to"}
    replied_conv = {t.get("conversation_id") for t in mine}
    replied_users = {}
    for t in mine:
        uid = t.get("in_reply_to_user_id")
        if uid:
            replied_users[uid] = replied_users.get(uid, 0) + 1
    # Replies to the author in the last 24 hours: who talks to them (for the boost).
    to_me, to_me_users, _ = search(f"to:{me} -from:{me} is:reply", (now - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ"), a.cap, max_results=50)
    talks_to_me = {t["author_id"] for t in to_me}

    seen, cands = set(), []
    runs = [(q, "watchlist") for q in queries]
    if a.keywords and not a.speed:
        runs += [(q, "search") for q in c["keyword_queries"]]
    if a.keywords and a.focus:
        runs += [(q, "focus") for q in c["focus_queries"]]
    if a.feedback_only:
        runs = []
    for q, source in runs:
        if source == "watchlist":
            posts, users, media = search(q, start, a.cap)
        else:
            posts, users, media = search(q, start, a.cap, max_results=max(10, min(100, a.kw_results)), pages=a.pages)
        for t in posts:
            if t["id"] in seen:
                continue
            seen.add(t["id"])
            u = users.get(t["author_id"], {})
            handle = u.get("username", "")
            w = watch.get(handle.lower(), {})
            followers = (u.get("public_metrics") or {}).get("followers_count") or w.get("followers")
            floor = {"search": c["keyword_min_followers"], "focus": c["focus_min_followers"]}.get(source)
            if floor is not None and (handle.lower() in watch or (followers or 0) < floor or handle.lower() == me.lower()):
                continue
            body = text_of(t)
            fit, niche = fit_of(body), niche_of(body)
            in_circle = handle.lower() in circle
            if age_minutes(t, now) > (max(a.max_age_min, 360) if in_circle else a.max_age_min) \
                    or (not a.broad and niche < a.min_niche):
                continue
            liked = taste.get(handle.lower(), {})
            if liked.get("shown", 0) >= 3 and not liked.get("posted") and not in_circle:
                continue  # the author has passed on this account 3 times
            if a.focus and c["focus_lanes"] and not any(lanes[l].search(body) for l in c["focus_lanes"] if l in lanes):
                continue
            s, vel = score(t, followers, now, fit)
            if a.speed and not in_circle:
                if t["public_metrics"]["reply_count"] > SPEED_MAX_REPLIES or (followers or 0) < SPEED_MIN_FOLLOWERS:
                    continue
                s = speed_score(t, followers, now)
            if t["author_id"] in talks_to_me:
                s = round(s * 1.3, 2)
            if liked.get("posted"):
                s = round(s * 1.3, 2)
            elif liked.get("shown", 0) >= 2 and not in_circle:
                s = round(s * 0.5, 2)
            if in_circle:
                s = round(s * 1.6, 2)
            s = round(s * (0.6 + 0.2 * min(niche, 4)), 2)
            cands.append({
                "id": t["id"], "url": f"https://x.com/{handle}/status/{t['id']}",
                "author": handle, "name": u.get("name"), "followers": followers,
                "priority": w.get("priority"), "lane": w.get("lane"), "notes": w.get("notes"),
                "created_at": t["created_at"], "age_min": round(age_minutes(t, now)),
                "metrics": t["public_metrics"], "has_media": bool(t.get("attachments")),
                "media": media_of(t, media), "avatar": u.get("profile_image_url"),
                "is_quote": any(r["type"] == "quoted" for r in t.get("referenced_tweets", [])),
                "text": body, "score": s, "velocity": vel, "fit": fit, "niche": niche, "source": source,
                "taste": liked or None, "circle": in_circle,
                "talks_to_me": t["author_id"] in talks_to_me,
                "replied_to_author_recently": replied_users.get(t["author_id"], 0),
                "already_replied": t["id"] in replied_to or t.get("conversation_id") in replied_conv,
                "flags": [n for n, rx in FLAGS if rx.search(body)],
            })
    # Coordinated campaigns: the same 3-word phrase in posts from 4+ different authors in 1 fetch.
    stop = {"the", "a", "an", "and", "or", "to", "of", "in", "on", "for", "is", "it", "you", "your", "with", "that", "this", "i", "we", "my", "are", "be", "at", "as", "from"}

    def trigrams(text):
        w = re.findall(r"[a-z0-9']+", text.lower())
        return {" ".join(w[i:i + 3]) for i in range(len(w) - 2) if not set(w[i:i + 3]) <= stop}
    seen_by = {}
    for x in cands:
        for g in trigrams(x["text"]):
            seen_by.setdefault(g, set()).add(x["author"].lower())
    hot = {g for g, au in seen_by.items() if len(au) >= 4}
    for x in cands:
        if hot & trigrams(x["text"]):
            x["flags"].append("campaign")
    shown = set()
    if a.last_queue:
        shown = {i["id"] for i in json.load(open(a.last_queue)).get("items", [])}
    cands = [x for x in cands if not x["already_replied"] and x["id"] not in shown
             and not (x["source"] in ("search", "focus") and (x["fit"] < 2 or "promo" in x["flags"] or "politics" in x["flags"]))
             and "campaign" not in x["flags"]]
    cands.sort(key=lambda x: -x["score"])

    feedback = []
    if a.last_queue:
        last = json.load(open(a.last_queue))
        posted = {ref["id"]: text_of(t) for t in mine for ref in t.get("referenced_tweets", []) if ref["type"] == "replied_to"}
        posted_metrics = {ref["id"]: t["public_metrics"] for t in mine for ref in t.get("referenced_tweets", []) if ref["type"] == "replied_to"}
        for item in last.get("items", []):
            if not item.get("draft"):
                continue
            final = posted.get(item["id"])
            if final is None:
                verdict = "not posted"
            else:
                clean = re.sub(r"^(@\w+\s+)+", "", final).strip()
                verdict = "posted as drafted" if clean == item["draft"].strip() else "posted with edits"
            author_id = next((uid for uid, u in to_me_users.items() if u.get("username", "").lower() == (item.get("author") or "").lower()), None)
            feedback.append({"id": item["id"], "author": item.get("author"), "followers": item.get("followers"),
                             "angle": item.get("angle"), "draft": item["draft"],
                             "posted": final, "verdict": verdict, "reply_metrics": posted_metrics.get(item["id"]),
                             "author_replied_back": bool(final and author_id and author_id in talks_to_me)})

    out = {"fetched_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "window_start": start,
           "watchlist_handles": len(watch), "queries": len(runs) + 2,
           "candidates_total": len(cands), "candidates": cands[: a.limit],
           "feedback": feedback}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    print(f"{len(watch)} handles, {len(queries)} batches, {len(cands)} fresh posts, kept {min(len(cands), a.limit)}; "
          f"{len(feedback)} earlier drafts checked -> {a.out}")


if __name__ == "__main__":
    main()
