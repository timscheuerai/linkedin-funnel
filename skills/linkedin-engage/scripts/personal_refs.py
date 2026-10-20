#!/usr/bin/env python3
"""Find the author's personal links to each picked post, before drafting.

  python3 personal_refs.py <candidates or run>.json --ids <id,id,...>

For every post it prints 3 things to read before writing the comment:
  1. history: the watchlist notes on the post's author and lines in `context/`
     that name them (a live, a podcast, a mention in the author's posts). No hit
     means no shared history: never claim one.
  2. bank: the stories in references/personal-bank.md whose topic matches the
     post, with the run that last used them (pause a story for 7 days; the
     renderer blocks wording repeated from the last 14 days).
  3. second brain: the best keyword hits in the author's identity, voice and
     raw source pages, the moments they have told in public.

It suggests, it does not decide: a story goes in only when it is the direct
parallel to the post (references/personal-bank.md, "How to use a story").
Free: no OXYGEN calls.
"""
import argparse, json, re, sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from oxy import ROOT, SKILL, runs_dir  # noqa: E402

CONTEXT = ROOT / "context"
# Pages that list creators without any history with them.
NOT_HISTORY = ("research/", "inspiration/", "templates/", "index.md", "log.md")
PERSONAL = ("identity/", "voice/", "audience/", "strategy/", "raw/")
STOP = set("""about after again against being below between could doesn every first from have here into just like
make more most much need only other over same should some still than that their them then there these they this
those through very want what when where which while will with without would your you're it's don't they're that's
always never really things thing people because before getting going something someone everyone actually
were said also didn't can't won't isn't around maybe pretty great quite literally whole""".split())


def words(text, least=4):
    return [w for w in re.findall(r"[a-z][a-z']{%d,}" % (least - 1), (text or "").lower()) if w not in STOP]


def stem(w):
    return w[:5]


def shingles(text, n=5):
    t = re.findall(r"[a-z0-9']+", (text or "").lower())
    return {" ".join(t[i:i + n]) for i in range(len(t) - n + 1)}


def pages():
    for f in sorted(CONTEXT.rglob("*.md")):
        rel = f.relative_to(CONTEXT).as_posix()
        yield rel, f


def bank_rows():
    """Stories from the '## Stories' table of references/personal-bank.md: Fits posts about | Moment | Source."""
    rows, on = [], False
    for line in (SKILL / "references/personal-bank.md").read_text().splitlines():
        if line.startswith("## "):
            on = line.strip() == "## Stories"
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if on and line.startswith("|") and len(cells) == 3 and cells[1] and not set(cells[0]) <= set("-: ") \
                and cells[0] != "Fits posts about":
            rows.append({"fits": cells[0], "line": cells[1].strip('"'), "source": cells[2]})
    return rows


def recent_drafts(days=14, skip=None):
    cut = datetime.now(timezone.utc) - timedelta(days=days)
    out = []
    folder = runs_dir()
    for f in sorted(folder.glob("*.json")) if folder.exists() else []:
        if skip and f.resolve() == Path(skip).resolve():
            continue
        try:
            q = json.loads(f.read_text())
            when = datetime.fromisoformat(q.get("fetched_at", "").replace("Z", "+00:00"))
        except Exception:
            continue
        if when >= cut:
            for i in q.get("items", []):   # tuning rounds carry 2 drafts per post
                out += [(f.stem, t) for t in [d.get("text") for d in i.get("drafts") or []] or [i.get("draft")] if t]
    return out


def history(name):
    """Lines in context/ naming the author, outside the pages that only list creators."""
    name = re.sub(r"^[^\w]+", "", name or "").strip()
    if len(name.split()) < 2:
        return []
    hits = []
    for rel, f in pages():
        if rel.startswith(NOT_HISTORY):
            continue
        for n, line in enumerate(f.read_text(errors="ignore").splitlines(), 1):
            if name.lower() in line.lower():
                hits.append(f"context/{rel}:{n}  {line.strip()[:200]}")
    return hits[:6]


def second_brain(query_words):
    """The best lines in the author's own pages for these words (a free, local keyword search)."""
    want = {stem(w) for w in query_words}
    scored = []
    for rel, f in pages():
        if not rel.startswith(PERSONAL) or rel.startswith(NOT_HISTORY):
            continue
        for n, line in enumerate(f.read_text(errors="ignore").splitlines(), 1):
            got = len({stem(w) for w in words(line)} & want)
            if got >= 2:
                scored.append((got, f"context/{rel}:{n}  {line.strip()[:220]}"))
    scored.sort(key=lambda x: -x[0])
    return [s for _, s in scored[:3]]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("file", help="candidates.json from the fetch or a saved run")
    ap.add_argument("--ids", help="comma separated post ids (default: every item)")
    ap.add_argument("--query", action="append", default=[], help="ID=words to search the second brain with your own words")
    a = ap.parse_args()
    q = json.load(open(a.file))
    items = q.get("items") or q.get("candidates") or []
    if a.ids:
        want = a.ids.split(",")
        items = [i for i in items if str(i["id"]) in want]
    custom = dict(x.split("=", 1) for x in a.query)
    rows = bank_rows()
    used = recent_drafts(skip=a.file)
    for r in rows:
        s = shingles(r["line"])
        r["last_used"] = next((run for run, d in reversed(used) if s & shingles(d)), None)
    for it in items:
        text = it.get("text") or ""
        stems = {stem(w) for w in words(text)}
        print(f"\n=== {it.get('name') or it.get('author')} ({it['id']})")
        print("  " + text.split("\n")[0][:120])
        if it.get("notes"):
            print(f"  watchlist notes: {it['notes']}")
        h = history(it.get("name"))
        print("  history:" + ("" if h else " none in context/, so no shared moment to mention"))
        for line in h:
            print("    " + line)
        scored = []
        for r in rows:
            score = len({stem(w) for w in words(r["fits"])} & stems)
            if score >= 2:
                scored.append((score, r))
        scored.sort(key=lambda x: -x[0])
        print("  bank:" + ("" if scored else " no topic match"))
        for score, r in scored[:4]:
            note = f" (used in {r['last_used']}, pause it)" if r["last_used"] else ""
            print(f"    [{score}] {r['line']}{note}\n        {r['source']}")
        own = set(words(it.get("name") or ""))
        custom_q = custom.get(str(it["id"]))
        top = words(custom_q) if custom_q else [w for w, _ in Counter(w for w in words(text, 5) if w not in own).most_common(6)]
        hits = second_brain(top)
        print(f"  second brain ({' '.join(top[:6])}):" + ("" if hits else " nothing personal, try --query with your own words"))
        for line in hits:
            print("    " + line)


if __name__ == "__main__":
    main()
