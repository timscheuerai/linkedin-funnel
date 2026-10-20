#!/usr/bin/env python3
"""Check every draft in a LinkedIn run, then render the LinkedIn Comment Queue page.

  python3 render_queue.py <runs_dir>/<run>.json --out <scratch>/linkedin-comment-queue.html

Checks every draft before rendering (rules in references/comment-voice.md): a
comment under someone else's post is 6 to 70 words and at most 450
characters; 2 sentences or more get a blank line between paragraphs (at most 4
paragraphs, 35 words each); no dashes, links, hashtags, generic openers,
stock phrases, banned words, pitches or large numbers without a thousands
separator; the author's company in at most 1 comment of 10. Across the batch
it stops what makes a batch read like a bot even when every comment passes:
the same opener twice, most comments in the same multi-paragraph shape, too
many questions, laughs in every comment, too few comments in the first person,
and wording repeated from another comment or from the runs of the last 14
days (comments stay public on the author's activity page). A failing draft
stops the render, so a bad draft never reaches the page.

Tuning rounds carry 2 drafts per post in `drafts`, each with a `move` from the
moves table in references/comment-voice.md. Every draft gets the
single-comment checks, the 2 drafts of a card need different moves, and the
batch checks run on each set (all first drafts, all second drafts), since the
author posts 1 of the 2.
"""
import argparse, base64, hashlib, json, re, shutil, subprocess, sys, tempfile, urllib.request
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).parent))
from oxy import config  # noqa: E402

# The page cannot load images from LinkedIn (an Artifact's content security policy
# blocks other hosts), so avatars and post images are downloaded once and embedded.
IMAGE_HOSTS = {"media.licdn.com"}
MAX_IMAGE = 4_000_000       # bytes downloaded per image
SHRINK_OVER = 350_000       # larger images are scaled down (macOS sips, or Pillow when installed)
MAX_TOTAL = 12_000_000      # bytes of embedded images per page


def shrink(body, width):
    with tempfile.TemporaryDirectory() as d:
        src, dst = Path(d) / "in", Path(d) / "out.jpg"
        src.write_bytes(body)
        if shutil.which("sips"):
            r = subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "70", "-Z", str(width), str(src), "--out", str(dst)],
                               capture_output=True)
            return dst.read_bytes() if r.returncode == 0 and dst.exists() else body
        try:
            from PIL import Image
            im = Image.open(src).convert("RGB")
            im.thumbnail((width, width))
            im.save(dst, "JPEG", quality=70)
            return dst.read_bytes()
        except Exception:
            return body


def fetch_image(url, cache, width):
    if not url or urlparse(url).hostname not in IMAGE_HOSTS:
        return None
    cache.mkdir(parents=True, exist_ok=True)
    f = cache / (hashlib.sha1(url.encode()).hexdigest() + f"-{width}")
    if not f.exists():
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=20) as r:
                ctype = r.headers.get("Content-Type", "")
                body = r.read(MAX_IMAGE + 1)
        except Exception:
            return None
        if not ctype.startswith("image/") or len(body) > MAX_IMAGE:
            return None
        if len(body) > SHRINK_OVER:
            body, ctype = shrink(body, width), "image/jpeg"
        f.write_bytes(ctype.encode() + b"\n" + body)
    ctype, body = f.read_bytes().split(b"\n", 1)
    return f"data:{ctype.decode()};base64,{base64.b64encode(body).decode()}"


def embed(q, cache):
    total = 0
    for item in q.get("items", []):
        d = fetch_image(item.get("avatar"), cache, 96)
        if d:
            item["avatar_data"] = d
            total += len(d)
        for m in item.get("media") or []:
            if total > MAX_TOTAL or m.get("type") != "image":
                continue
            d = fetch_image(m.get("src"), cache, 900)
            if d:
                m["data"] = d
                total += len(d)
    return total


BANNED_OPENERS = re.compile(r"(?i)^(great|love (this|it|that)|so true|this\b|100%|amazing|awesome|nice (post|one)|well said|spot on|"
                            r"thanks for sharing|couldn'?t agree more|absolutely|totally agree|insightful|nailed it|powerful)")
BANNED_WORDS = (r"orchestrat\w*|leverag\w*|streamlin\w*|seamless\w*|unlock\w*|game[- ]?changer|delve|crucial|"
                r"insightful|resonat\w*|invaluable|paramount|testament|elevat\w*|empower\w*|synerg\w*|thrilled")
# Stock phrases that make a comment read like a template or a model, not a person typing.
STOCK = re.compile(r"(?im)(what nobody tells you|nobody talks about|here's the thing|the whole story|the real \w+ is|is the actual work|"
                   r"hits different|let that sink in|the best answer .{0,30} seen|biggest (change|difference|lesson) (for me|so far)\s*:|"
                   r"\b(what|this) (cut|changed|helped) .{0,25}:|couldn'?t agree more|this resonates|thanks for sharing|great insights?|"
                   r"key takeaway|food for thought|at the end of the day|it'?s not just about|in today'?s|a must[- ]read|"
                   r"great (post|read|breakdown|share)|love this|"
                   # Template moves: grading the post instead of talking to its author.
                   r"\b(the|is the) (one|part|bit) (i'?d|i would|most people)\b|underline (it )?twice|"
                   r"\bsame (setup|split|here)( here| for me)?\s*[.!]?\s*$|"
                   r"\bcongrats\b[^.!?\n]{0,40}\b(massive|huge|insane|amazing|incredible)\b)")
PITCH = re.compile(r"(?i)\b(dm me|check out|link in|book a call|calendly|cal\.com|happy to (help|chat|connect)|let'?s connect)\b")
NUMBER = re.compile(r"(?<![\d'.,$])(\d{4,})(?![\d'.,])")


def banned_words():
    extra = "|".join(re.escape(w) for w in config()["extra_banned_words"])
    return re.compile(r"(?i)\b(" + BANNED_WORDS + ("|" + extra if extra else "") + r")\b")


def check(d, banned, sep):
    words = len(re.findall(r"\S+", d))
    errs = []
    if not d.strip():
        return ["empty draft"]
    if len(d) > 450:
        errs.append(f"{len(d)} characters, over 450 (1 point, not a mini post)")
    if words < 6:
        errs.append(f"{words} words, under 6")
    if words > 70:
        errs.append(f"{words} words, over 70")
    # 1 thought per short paragraph, a blank line between them.
    paras = [p.strip() for p in re.split(r"\n\s*\n", d.strip()) if p.strip()]
    sentences = len(re.findall(r"[.!?](\s|$)", d.strip().rstrip(".!?") + "."))
    if re.search(r"\n\s*\n\s*\n", d):
        errs.append("2 blank lines in a row")
    if len(paras) > 4:
        errs.append(f"{len(paras)} paragraphs, at most 4")
    if len(paras) < 2 and sentences > 1:
        errs.append("2 sentences without a line break (put a blank line between them)")
    for p in paras:
        if len(p.split()) > 35:
            errs.append(f"a paragraph of {len(p.split())} words, at most 35 (break it up)")
    s = STOCK.search(d)
    if s:
        errs.append(f"stock phrase '{s.group(0).strip()}'")
    if "—" in d or "–" in d or re.search(r"\s-\s", d):
        errs.append("dash")
    if re.search(r"https?://|www\.|\.com\b", d):
        errs.append("link")
    if re.search(r"(^|\s)#\w", d):
        errs.append("hashtag")
    if BANNED_OPENERS.search(d.strip()):
        errs.append("generic opener")
    m = banned.search(d)
    if m:
        errs.append(f"banned word '{m.group(0)}'")
    p = PITCH.search(d)
    if p:
        errs.append(f"pitch '{p.group(0)}'")
    for n in NUMBER.findall(d):
        if not (1900 <= int(n) <= 2099):
            errs.append(f"'{n}' needs a thousands separator ({int(n):,})".replace(",", sep))
    return errs


TEXTURE = re.compile(r"(?i)(\bhah\w*|\bahah\w*|\blol\b|:\)|;\)|\btbh\b|\bofc\b|\bimo\b)")
FIRST_PERSON = re.compile(r"(?i)\b(i|i'm|i'd|i've|i'll|my|me|we|we're|we've|our|us)\b")


def variants(item):
    """The drafts of 1 card: `drafts` in tuning rounds, else the single `draft`."""
    if item.get("drafts"):
        return [d for d in item["drafts"] if (d.get("text") or "").strip()]
    if item.get("draft"):
        return [{"text": item["draft"], "move": item.get("move"), "ref": item.get("ref"), "ref_source": item.get("ref_source")}]
    return []


def shingles(text, n=6):
    t = re.findall(r"[a-z0-9']+", text.lower())
    return {" ".join(t[i:i + n]) for i in range(len(t) - n + 1)}


def column_checks(drafts, tag, company):
    """The bot tells within 1 set of comments the author could post together."""
    n, errs = len(drafts), []
    if not n:
        return errs
    openers = Counter(" ".join(re.findall(r"[a-z0-9']+", d.lower())[:2]) for d in drafts)
    errs += [(tag, f"{c} comments open with '{o}'") for o, c in openers.items() if c > 1]
    if n >= 5:
        # Most real comments are 1 line, so a batch of 1 liners is natural; the bot tell
        # is the same multi-paragraph template every time.
        shape, c = Counter(len([p for p in re.split(r"\n\s*\n", d.strip()) if p.strip()]) for d in drafts).most_common(1)[0]
        if shape >= 2 and c > 0.6 * n:
            errs.append((tag, f"{c} of {n} comments have {shape} paragraphs: most real comments are 1 line"))
        long = sum(len(re.findall(r"\S+", d)) > 45 for d in drafts)
        if long > 0.3 * n:
            errs.append((tag, f"{long} of {n} comments run over 45 words: comments are short"))
    asks = sum("?" in d for d in drafts)
    if asks > max(2, 0.4 * n):
        errs.append((tag, f"{asks} of {n} comments ask a question, at most 4 in 10"))
    laughs = sum(bool(TEXTURE.search(d)) for d in drafts)
    if n >= 5 and laughs > 0.6 * n:
        errs.append((tag, f"haha, lol, :) or tbh in {laughs} of {n} comments: keep it to about half"))
    mine = sum(bool(FIRST_PERSON.search(d)) for d in drafts)
    if n >= 5 and mine < 0.5 * n:
        errs.append((tag, f"only {mine} of {n} comments speak from the author's own work (I, my, we, our)"))
    if company:
        named = sum(1 for d in drafts if re.search(r"(?i)\b" + re.escape(company) + r"\b", d))
        if named > max(1, n // 10):
            errs.append((tag, f"{company} named in {named} of {n} comments, at most 1 in 10"))
    return errs


def batch_checks(q, path, company):
    """What makes a batch read like a bot even when every single comment passes."""
    items = [i for i in q.get("items", []) if variants(i)]
    if not items:
        return []
    who = lambda i: i.get("name") or i.get("author")
    errs = []
    width = max(len(variants(i)) for i in items)
    for k in range(width):
        tag = "queue" if width == 1 else f"queue, draft {'AB'[k] if k < 2 else k + 1}"
        errs += column_checks([variants(i)[min(k, len(variants(i)) - 1)]["text"] for i in items], tag, company)
    for i in items:
        vs = variants(i)
        moves = [v.get("move") for v in vs]
        if len(vs) > 1 and (None in moves or len(set(moves)) < len(moves)):
            errs.append((who(i), f"the {len(vs)} drafts need different moves (got {moves})"))
    seen = {}
    for i in items:
        for v in variants(i):
            for s in shingles(v["text"]):
                if s in seen and seen[s] != who(i):
                    errs.append(("queue", f"'{s}' is in the comments to {seen[s]} and {who(i)}"))
                seen.setdefault(s, who(i))
    try:
        now = datetime.fromisoformat(q.get("fetched_at", "").replace("Z", "+00:00"))
    except ValueError:
        return errs
    for f in sorted(path.parent.glob("*.json")):
        if f.resolve() == path.resolve():
            continue
        try:
            old = json.loads(f.read_text())
            when = datetime.fromisoformat(old.get("fetched_at", "").replace("Z", "+00:00"))
        except Exception:
            continue
        if not now - timedelta(days=14) <= when <= now:
            continue
        past = set().union(*[shingles(v["text"]) for o in old.get("items", []) for v in variants(o)] or [set()])
        for i in items:
            hit = sorted(set().union(*[shingles(v["text"]) for v in variants(i)]) & past)
            if hit:
                errs.append((who(i), f"repeats '{hit[0]}' from run {f.stem} (comments are public, say it new)"))
    return errs


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("queue")
    ap.add_argument("--out", required=True)
    ap.add_argument("--cache", help="image cache folder (default: next to --out)")
    ap.add_argument("--no-images", action="store_true")
    a = ap.parse_args()
    c = config()
    banned, sep, company = banned_words(), c["thousands_separator"], c.get("company_name")
    q = json.load(open(a.queue))
    q.pop("on_my_posts", None)   # the author answers comments on their own posts themselves
    bad = []
    for i in q.get("items", []):
        vs = variants(i)
        for k, v in enumerate(vs):
            label = (i.get("name") or i.get("author")) + (f", draft {'AB'[k] if k < 2 else k + 1}" if len(vs) > 1 else "")
            bad += [(label, e) for e in check(v["text"], banned, sep)]
        if vs:   # the page takes the first draft as `draft`
            i["draft"] = vs[0]["text"]
    bad += batch_checks(q, Path(a.queue), company)
    cards = [i for i in q.get("items", []) if variants(i)]
    refs = sum(1 for i in cards if any(v.get("ref") for v in variants(i)))
    if cards and not refs <= max(2, round(len(cards) * 0.4)):
        print(f"note: {refs} of {len(cards)} cards carry a personal story (aim for 2 to 4 in 10, references/personal-bank.md)")
    if bad:
        sys.exit("Drafts need fixing before render:\n" + "\n".join(f"  {h}: {e}" for h, e in bad))
    size = 0 if a.no_images else embed(q, Path(a.cache) if a.cache else Path(a.out).parent / "li-image-cache")
    tpl = (Path(__file__).parent / "queue_template.html").read_text()
    payload = json.dumps(q, ensure_ascii=False).replace("</", "<\\/")
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(tpl.replace("/*QUEUE_DATA*/", payload))
    print(f"{len(q.get('items', []))} comments, {size // 1024} KB of images -> {a.out}")


if __name__ == "__main__":
    main()
