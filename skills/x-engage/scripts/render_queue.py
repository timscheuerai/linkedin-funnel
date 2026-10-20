#!/usr/bin/env python3
"""Check every draft in an X run, then render the X Reply Queue page.

  python3 render_queue.py <runs_dir>/<run>.json --out <scratch>/x-reply-queue.html

Checks every draft before rendering (rules in references/reply-voice.md): at
most 200 characters, at most 1 line break, no dashes, links, hashtags, generic
openers, banned words or stock phrases, no product plug, plus the author's own
taste blocks from the config. A failing draft stops the render, so a bad draft
never reaches the page.
"""
import argparse, base64, hashlib, json, re, sys, urllib.request
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).parent))
from oxy import config  # noqa: E402

# The page cannot load images from X (an Artifact's content security policy blocks
# other hosts), so avatars and post images are downloaded once and embedded.
IMAGE_HOSTS = {"pbs.twimg.com"}
MAX_IMAGE = 1_500_000       # bytes per image
MAX_TOTAL = 10_000_000      # bytes of embedded images per page


def sized(url, kind):
    """Smaller variants: post images at X's 'small' size, avatars at 'bigger' (73 px)."""
    if kind == "avatar":
        return url.replace("_normal.", "_bigger.")
    return url.split("?")[0] + "?name=small"


def fetch_image(url, cache):
    if urlparse(url).hostname not in IMAGE_HOSTS:
        return None
    cache.mkdir(parents=True, exist_ok=True)
    f = cache / hashlib.sha1(url.encode()).hexdigest()
    if not f.exists():
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=20) as r:
                ctype = r.headers.get("Content-Type", "")
                body = r.read(MAX_IMAGE + 1)
        except Exception:
            return None
        if not ctype.startswith("image/") or len(body) > MAX_IMAGE:
            return None
        f.write_bytes(ctype.encode() + b"\n" + body)
    ctype, body = f.read_bytes().split(b"\n", 1)
    return f"data:{ctype.decode()};base64,{base64.b64encode(body).decode()}"


def embed(q, cache):
    total = 0
    for item in q.get("items", []):
        if item.get("avatar"):
            d = fetch_image(sized(item["avatar"], "avatar"), cache)
            if d:
                item["avatar_data"] = d
                total += len(d)
        for m in item.get("media") or []:
            if total > MAX_TOTAL:
                break
            d = fetch_image(sized(m["src"], "media"), cache)
            if d:
                m["data"] = d
                total += len(d)
    return total


BANNED_OPENERS = re.compile(r"(?i)^(great|love|so true|this\b|100%|amazing|awesome post|nice post|well said|spot on)")
BANNED_WORDS = r"orchestrat\w*|leverag\w*|streamlin\w*|seamless\w*|unlock\w*|game[- ]changer|delve|crucial"
# Stock phrases that make a reply read like a post or a model, not a person typing.
STOCK = re.compile(r"(?i)(what nobody tells you|nobody talks about|here's the thing|the whole story|the real \w+ is|is the actual work|"
                   r"hits different|let that sink in|the best answer .{0,30} seen|biggest (change|difference|lesson) (for me|so far)\s*:|"
                   r"\b(what|this) (cut|changed|helped) .{0,25}:)")


def blocks(c):
    """Product plugs never go out in replies; the author's learned taste blocks come from the config."""
    out = [(re.compile(r"(?i)\bwe (just )?shipped\b|\bour (product|platform|tool)\b"), "product brag")]
    if c.get("company_name"):
        out.append((re.compile(r"(?i)\b" + re.escape(c["company_name"]) + r"\b"), f"names {c['company_name']} (a plug)"))
    out += [(re.compile(b["pattern"], re.I), b.get("why") or "taste block") for b in c["taste_blocks"]]
    return out


def check(item, banned, taste):
    d = item.get("draft") or ""
    errs = []
    if not d.strip():
        errs.append("empty draft")
    if len(d) > 200:
        errs.append(f"{len(d)} characters, over 200 (a reply is 1 thought)")
    if d.count("\n") > 1:
        errs.append("more than 1 line break (a reply is not a post)")
    s = STOCK.search(d)
    if s:
        errs.append(f"stock phrase '{s.group(0)}'")
    if "—" in d or "–" in d:
        errs.append("em or en dash")
    for rx, why in taste:
        if rx.search(d):
            errs.append(why)
    if re.search(r"https?://", d):
        errs.append("link in a reply")
    if re.search(r"(^|\s)#\w", d):
        errs.append("hashtag")
    if BANNED_OPENERS.search(d.strip()):
        errs.append("generic opener")
    m = banned.search(d)
    if m:
        errs.append(f"banned word '{m.group(0)}'")
    return errs


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("queue")
    ap.add_argument("--out", required=True)
    ap.add_argument("--cache", help="image cache folder (default: next to --out)")
    ap.add_argument("--no-images", action="store_true")
    a = ap.parse_args()
    c = config()
    extra = "|".join(re.escape(w) for w in c["extra_banned_words"])
    banned = re.compile(r"(?i)\b(" + BANNED_WORDS + ("|" + extra if extra else "") + r")\b")
    taste = blocks(c)
    q = json.load(open(a.queue))
    q.pop("on_my_posts", None)   # the author answers replies on their own posts themselves
    bad = [(i.get("author"), e) for i in q.get("items", []) if i.get("draft") is not None for e in check(i, banned, taste)]
    if bad:
        sys.exit("Drafts need fixing before render:\n" + "\n".join(f"  @{h}: {e}" for h, e in bad))
    size = 0 if a.no_images else embed(q, Path(a.cache) if a.cache else Path(a.out).parent / "x-image-cache")
    tpl = (Path(__file__).parent / "queue_template.html").read_text()
    payload = json.dumps(q, ensure_ascii=False).replace("</", "<\\/")
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(tpl.replace("/*QUEUE_DATA*/", payload))
    print(f"{len(q.get('items', []))} replies, {size // 1024} KB of images -> {a.out}")


if __name__ == "__main__":
    main()
