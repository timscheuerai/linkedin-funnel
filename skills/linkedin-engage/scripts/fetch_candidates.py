#!/usr/bin/env python3
"""Fresh LinkedIn posts worth a comment from the author, from their LinkedIn Comment Watchlist.

Read only. Uses OXYGEN's managed LinkedIn scraper (cookieless, no connected
account, so the author's own account and its rate limits are never touched):

- `scraper.linkedin_post_search`, free at the time of writing: 1 call per
  watchlist profile (the managed search takes 1 author per request), newest
  first, last 24 hours, then kept to the window; plus the keyword searches in
  the config for niche posts outside the watchlist.
- `scraper.linkedin_profile_comments`, paid per page: the author's own recent
  comments, to skip posts they already commented on and, with --last-queue, to
  compare each earlier draft with what they actually posted.

Check current prices with `oxygen tools get <id> --json` before the first run.
Every paid call carries --max-credits and the whole run stops paying at
--budget. Comments on the author's own posts are not fetched: they answer those
themselves. Nothing is posted, liked, followed or messaged.

  python3 fetch_candidates.py --hours 3 --out <scratch>/candidates.json
  python3 fetch_candidates.py --hours 3 --out <scratch>/c.json --last-queue <runs_dir>/<newest>.json
"""
import argparse, difflib, json, math, re, sys, time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).parent))
from oxy import SPENT, cli, config, me_slug, slug_of, tool  # noqa: E402


def ids_in(*urls):
    """LinkedIn activity, ugcPost and share ids (19 digits) found in post urls or urns."""
    out = set()
    for u in urls:
        out.update(re.findall(r"\d{19}", str(u or "")))
    return out


def ts(s):
    return datetime.fromisoformat(str(s).replace("Z", "+00:00"))


def berlin(s):
    """The managed comment list stamps Berlin wall time with a Z. Returns real UTC."""
    if not s:
        return s
    local = datetime.fromisoformat(str(s).replace("Z", "")).replace(tzinfo=ZoneInfo("Europe/Berlin"))
    return local.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def comments_of(resp):
    """Comments from scraper.linkedin_post_comments with their real UTC time."""
    return [{**c, "created_at": berlin(c.get("created_at"))} for c in resp.get("results") or []]


def age_minutes(created, now):
    return (now - ts(created)).total_seconds() / 60


def post_of(e, pictures):
    """1 post from a raw scraper element; `pictures` maps post url to the author's avatar.
    Field names differ between endpoints, so every field is read defensively."""
    eng = e.get("engagement") or {}
    a = e.get("author") or {}
    media = [{"type": m.get("type"), "src": m["url"]} for m in e.get("media") or [] if m.get("url")]
    url = e.get("url") or e.get("linkedinUrl")
    m = re.search(r"activity[-:](\d{19})", url or "")
    return {
        # A repost of the author's own post carries a new urn but the original's url
        # and share id; the url's activity id is the post itself.
        "id": m.group(1) if m else str(e.get("urn") or ""), "share_id": next(iter(ids_in(e.get("share_urn"))), None),
        "url": url,
        "name": a.get("name"), "author_url": a.get("linkedinUrl") or a.get("url"), "headline": a.get("headline"),
        "created_at": e.get("posted_at") or (e.get("postedAt") or {}).get("date"),
        "metrics": {"reactions": eng.get("likes", e.get("reactions_count")) or 0,
                    "comments": eng.get("comments", e.get("comments_count")) or 0,
                    "reposts": eng.get("shares", e.get("reposts_count")) or 0},
        "media": media, "avatar": pictures.get(e.get("url")), "text": e.get("text") or e.get("content") or "",
    }


def search_posts(inp, budget):
    resp = tool("scraper.linkedin_post_search", inp, 0, budget)
    pictures = {r.get("post_url"): r.get("author_picture_url") for r in resp.get("results") or [] if r.get("author_picture_url")}
    return [post_of(e, pictures) for e in (resp.get("raw") or {}).get("elements") or []]


def score(m, followers, age_min, fit):
    age_h = max(age_min / 60, 0.25)
    velocity = (m["reactions"] + 3 * m["comments"] + 2 * m["reposts"]) / age_h
    fresh = 1.0 if age_h <= 1 else 0.85 if age_h <= 2 else 0.7 if age_h <= 3 else 0.45 if age_h <= 6 else 0.2
    crowd = 1.0 if m["comments"] < 15 else 0.8 if m["comments"] < 60 else 0.55 if m["comments"] < 150 else 0.35
    reach = math.log10((followers or 2000) + 10)
    return round(reach * (1 + math.log10(1 + velocity)) * fresh * crowd * (0.4 + 0.3 * fit), 2), round(velocity, 1)


def lanes():
    """The author's lanes from the config, as compiled regexes. A post's fit is how many it touches (0 to 3)."""
    return {name: re.compile(rx, re.I) for name, rx in (config().get("lanes") or {}).items()}


def fit_of(text, rxs):
    if not rxs:
        return 1          # no lanes configured: every post is neutral on fit
    return min(3, sum(1 for rx in rxs.values() if rx.search(text)))


FLAGS = [
    ("comment_gate", re.compile(r"\b[Cc]omment\s+(?:below\s+)?[\"'“‘]?[A-Z][A-Z0-9]{2,}\b|(?i:comment .{0,40}(?:and|&) I'?ll (?:send|dm|share))|(?i:drop (?:a|your) comment)")),
    ("hiring", re.compile(r"(?i)\b(we'?re hiring|#hiring|now hiring|job opening|open roles?|apply (now|here|below))\b")),
    ("politics", re.compile(r"(?i)\b(election|democrat|republican|war)\b")),
    ("promo", re.compile(r"(?i)\b(sponsored|in partnership with|promo code|discount code|% off|limited spots|register (now|here)|join (the|our) webinar|webinar)\b")),
    ("milestone", re.compile(r"(?i)(starting a new position|new position as|work anniversary|happy to (share|announce)|excited to announce|thrilled to (share|announce)|i'?m humbled)")),
    ("link_only", re.compile(r"^\s*https?://\S+\s*$")),
]
ENGLISH = re.compile(r"(?i)\b(the|and|you|is|to|of|that|it|for|with)\b")


def flags_of(text):
    out = [n for n, rx in FLAGS if rx.search(text)]
    if len(ENGLISH.findall(text)) < max(3, len(text.split()) // 25):
        out.append("non_english")
    return out


def my_comments(budget, cutoff, max_pages=4):
    """The author's recent comments, newest first, until older than `cutoff`. Paid per page."""
    out, token = [], None
    for page in range(1, max_pages + 1):
        inp = {"profile": config()["my_profile_url"]}
        if page > 1:
            if not token:
                break
            inp.update({"page": page, "pagination_token": token})
        resp = tool("scraper.linkedin_profile_comments", inp, 3, budget)
        rows = resp.get("results") or []
        out += rows
        pg = (resp.get("raw") or {}).get("pagination") or {}
        token = pg.get("paginationToken")
        if not pg.get("has_more") or not rows or ts(rows[-1]["created_at"]) < cutoff:
            break
    return out


def strip_mention(text, name=None):
    """A comment without the leading @mention LinkedIn renders as the person's name."""
    t = (text or "").replace(" ", " ").strip()
    for n in (name, re.sub(r"^[^\w]+", "", name or "")):
        if n and t.lower().startswith(n.lower()):
            return t[len(n):].lstrip(" ,:")
    return t


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--hours", type=float, default=3, help="how far back to look for fresh posts")
    ap.add_argument("--priorities", default="1,2,3", help="watchlist priorities to include")
    ap.add_argument("--limit", type=int, default=40, help="candidates to keep after scoring")
    ap.add_argument("--workers", type=int, default=5, help="parallel watchlist searches (at most 5); failures get a second pass 1 at a time")
    ap.add_argument("--budget", type=float, default=40, help="credit ceiling for the whole run (search is free)")
    ap.add_argument("--last-queue", help="an earlier run JSON, to compare drafts with what the author posted")
    ap.add_argument("--no-niche", action="store_true", help="skip the keyword searches outside the watchlist")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    c = config()
    me = me_slug()
    rxs = lanes()
    automated = [re.compile(p) for p in c["automated_comment_patterns"]]
    now = datetime.now(timezone.utc)
    start = now - timedelta(hours=a.hours)
    rows = cli(["tables", "query", c["watchlist_table"], "--limit", "500", "--fields",
                "name,profile_url,followers,headline,priority,lane,notes"], max_chars=100000)["rows"]
    wanted = set(a.priorities.split(","))
    watch = {}
    for r in rows:
        s = slug_of(r.get("profile_url"))
        if s and s != me and str(r.get("priority") or "1") in wanted:
            watch[s] = r

    last = json.load(open(a.last_queue)) if a.last_queue else {}
    cutoff = ts(last["fetched_at"]) if last.get("fetched_at") else now - timedelta(hours=48)
    errors = []
    mine_failed = False
    try:
        mine = my_comments(a.budget, cutoff)
    except RuntimeError as e:   # without them the run still works, minus feedback and the already-commented check
        errors.append(f"my comments: {str(e)[:160]}")
        mine, mine_failed = [], True
    commented = set()
    for m in mine:
        commented |= ids_in(m.get("post_url"), m.get("post_id"))
    shown = set()
    for i in last.get("items", []):
        shown |= {x for x in (i.get("id"), i.get("share_id")) if x}

    failed = {}

    def one(slug):
        r = watch[slug]
        try:
            return slug, search_posts({"profile": r["profile_url"], "posted_limit": "24h", "sort_by": "date", "max_results": 5}, None)
        except Exception as e:  # 1 failed profile must not stop the run
            failed[slug] = str(e)[:160]
            return slug, []

    with ThreadPoolExecutor(max_workers=min(5, a.workers)) as ex:
        results = list(ex.map(one, sorted(watch)))
    # Second pass, 1 at a time: busy or provider errors under parallel load usually clear on a retry.
    retry = sorted(failed)
    failed.clear()
    for slug in retry:
        time.sleep(2)
        results.append(one(slug))
    errors += [f"{s}: {e}" for s, e in failed.items()]
    if retry:
        print(f"{len(retry)} profiles failed in parallel, {len(retry) - len(failed)} recovered on the second pass")

    seen, cands = set(), []

    def add(p, source, w):
        key = p["share_id"] or p["id"]
        if not p["id"] or key in seen or not p.get("created_at"):
            return
        seen.add(key)
        if ts(p["created_at"]) < start:
            return
        age = age_minutes(p["created_at"], now)
        fit = fit_of(p["text"], rxs)
        followers = w.get("followers")
        s, vel = score(p["metrics"], followers, age, fit)
        p.update({"author": slug_of(p["author_url"]) or p["name"], "followers": followers, "priority": w.get("priority"),
                  "lane": w.get("lane"), "notes": w.get("notes"), "age_min": round(age), "score": s, "velocity": vel,
                  "fit": fit, "source": source, "flags": flags_of(p["text"]),
                  "already_commented": bool(ids_in(p["id"], p["share_id"]) & commented)})
        cands.append(p)

    for slug, posts in results:
        for p in sorted(posts, key=lambda p: p.get("created_at") or ""):   # the original before its reposts
            if slug_of(p["author_url"]) == slug:      # the author's own posts, not reshares of others
                add(p, "watchlist", watch[slug])
    if not a.no_niche:
        for q in c["niche_searches"]:
            try:
                posts = search_posts({**q, "posted_limit": "24h", "sort_by": "date", "max_results": 100,
                                      "min_reactions": c["niche_min_reactions"]}, None)
            except Exception as e:
                errors.append(f"niche {q}: {str(e)[:160]}")
                continue
            for p in posts:
                s = slug_of(p["author_url"])
                if not s or s in watch or s == me:     # people only, outside the watchlist
                    continue
                if (rxs and fit_of(p["text"], rxs) < 2) or set(flags_of(p["text"])) & {"promo", "politics", "hiring", "non_english"}:
                    continue
                add(p, "search", {})

    cands = [x for x in cands if not x["already_commented"] and not ({x["id"], x["share_id"]} & shown)]
    cands.sort(key=lambda x: -x["score"])

    # Earlier drafts against what the author actually posted.
    feedback = []
    for item in last.get("items", []):
        # Tuning rounds carry 2 drafts per post (`drafts`); otherwise 1 (`draft`).
        texts = [d.get("text") or "" for d in item.get("drafts") or []] or [item.get("draft") or ""]
        if not any(t.strip() for t in texts):
            continue
        item_ids = ids_in(item.get("url"), item.get("id"), item.get("share_id"))
        posted = [m for m in mine if ids_in(m.get("post_url")) & item_ids
                  and not any(rx.search(m.get("comment") or "") for rx in automated)
                  and ts(m["created_at"]) >= ts(last["fetched_at"])]
        final = posted[-1]["comment"] if posted else None
        picked = None
        if final is None:
            verdict = "unknown, the author's comments could not be read" if mine_failed else "not posted"
        else:
            clean = " ".join(strip_mention(final, item.get("name")).split())   # line breaks may come back differently
            norm = [" ".join(t.split()) for t in texts]
            picked = max(range(len(norm)), key=lambda k: difflib.SequenceMatcher(None, norm[k].lower(), clean.lower()).ratio())
            tag = f" ({'AB'[picked] if picked < 2 else picked + 1})" if len(texts) > 1 else ""
            verdict = ("posted as drafted" if clean == norm[picked] else "posted with edits") + tag
        feedback.append({"id": item["id"], "author": item.get("author"), "name": item.get("name"), "followers": item.get("followers"),
                         "angle": item.get("angle"), "draft": texts[0], "drafts": item.get("drafts"), "picked": picked,
                         "posted": final, "verdict": verdict})

    organic = [{"created_at": m.get("created_at"), "on": m.get("post_author_name"), "comment": m.get("comment")}
               for m in mine if not any(rx.search(m.get("comment") or "") for rx in automated)]
    out = {"fetched_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "window_start": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
           "watchlist_profiles": len(watch), "candidates_total": len(cands), "candidates": cands[: a.limit],
           "feedback": feedback, "my_recent_comments": organic,
           "credits_used": round(SPENT["credits"], 2), "errors": errors}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    print(f"{len(watch)} profiles, {len(cands)} fresh posts in {a.hours:g}h, kept {min(len(cands), a.limit)}; "
          f"{len(feedback)} earlier drafts checked; {round(SPENT['credits'], 2)} credits; {len(errors)} errors -> {a.out}")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        sys.exit(str(e))
