#!/usr/bin/env python3
"""Depth-first YouTube outlier search: dive into the hottest branch until it saturates.

Each round searches a batch of queries (recent window), samples the channels of
the results for a baseline, ranks every candidate with youtube-rank.py, then
turns the phrases that recur in the round's outlier titles into the next
queries. The batch is always the children of 1 parent, the strongest unexplored
one at the deepest level, so the search goes deep before it goes wide. A branch
is saturated when its searches add no new outlier channel and no new phrase.

After the dive, --probes spends extra searches on the crossover gap: the
hottest phrases plus each --anchors term ("<wave> <anchor>"), counting how
many recent videos already take the niche angle and how they did.

Needs YOUTUBE_API_KEY (or OAuth variables) in the environment; see youtube_api.py:
  python3 youtube-depth-first.py \\
      --seeds research/<date-slug>/seeds.json \\
      --raw raw/<date-slug> --out research/<date-slug> \\
      --fit "lead|leads|b2b|pipeline" --probes 6 --anchors "lead gen,B2B"

Seeds JSON: [{"query": "Claude Code lead generation", "branch": "claude-code"}, ...].
Evidence (every API response) lands in --raw through youtube-depth-scan.py.
Ratios are youtube-rank.py ratios: cross-sectional current views against the
channel's own comparable uploads. Not views/hour, not CTR, not causation.
Re-running with the same --out resumes from depth-first-state.json.
"""

import argparse
import json
import math
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
STOP = set("""a an and are as at be but by can do does for from get got has have how i i'm if in into is it
it's its just me my no not now of on or our out so than that the their them then there these they this to
too up us vs was we what when where which who why will with without you your yours ever every new best
one two three first last full complete ultimate easy fast free real actually literally finally here only
way ways step steps make made making use using used need want go going show shows let lets did dont don't
day days week weeks month months year years hour hours minute minutes min 2025 2026 live part video
videos tutorial guide beginners beginner explained review honest tested test testing tips secret secrets
better more most much many ever this that what's thing things stop start started really insane crazy
everything anything nothing someone everyone people run runs running try tried trying turn turned
change changes changed official officially announced released release launch launched leaked leak finally
just dropped drops here's watch before after why forever massive biggest huge built amazing powerful
incredible you're we're they're i've you've we've that's there's won't can't isn't doesn't didn't
you'll i'll it'll back still even again""".split())
# Too broad to stand alone as a query; still fine inside a 2-word phrase ("ai agents", "openai sora").
GENERIC_UNIGRAMS = set("""ai agent agents business money marketing sales tool tools app apps build
building automation automate automated workflow workflows system systems content strategy growth income
online work side hustle company startup founder founders chatgpt openai google claude gemini model models
news update""".split())


def load(path, default):
    return json.loads(path.read_text()) if path.exists() else default


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def words(title):
    title = re.sub(r"https?://\S+|[#@]\w+", " ", title.lower().replace("\u2019", "'"))
    return re.findall(r"[a-z0-9][a-z0-9.+'-]*[a-z0-9+]|[a-z0-9]", title)


def core(text):
    """Alphabetic tokens of a phrase, hyphens split: 'GPT-6 Astra' and '6 astra' share {gpt, astra}."""
    return frozenset(t for t in re.findall(r"[a-z]+", text.lower()) if t not in STOP)


def phrases(title):
    toks = words(title)
    out = set()
    for i, t in enumerate(toks):
        # A lone version number ("2.5") is not a wave; "seedance 2.5" is.
        if t not in STOP and t not in GENERIC_UNIGRAMS and re.search(r"[a-z]", t) and len(t) > 2:
            out.add(t)
        if i + 1 < len(toks):
            a, b = t, toks[i + 1]
            if a not in STOP and b not in STOP and not (a.isdigit() and b.isdigit()):
                out.add(f"{a} {b}")
    return out


def run(cmd):
    print("$ " + " ".join(str(c) for c in cmd), flush=True)
    done = subprocess.run([str(c) for c in cmd], text=True, capture_output=True)
    sys.stdout.write(done.stdout[-1500:])
    if done.returncode:
        sys.stderr.write(done.stderr[-3000:])
        raise SystemExit(f"step failed: {cmd[1]}")
    return done.stdout


def ratio(r):
    return r["age_band_ratio"] or r["recent_ratio"] or 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--seeds", type=Path, required=True)
    p.add_argument("--raw", type=Path, required=True, help="raw/sources/<date-slug>, append only")
    p.add_argument("--out", type=Path, required=True, help="research/scans/<date-slug>")
    p.add_argument("--days", type=int, default=30, help="search window: published in the last N days")
    p.add_argument("--max-searches", type=int, default=24, help="dive budget (100 quota units per search)")
    p.add_argument("--max-depth", type=int, default=3)
    p.add_argument("--breadth", type=int, default=4, help="children searched per dive")
    p.add_argument("--outlier", type=float, default=3.0, help="ratio that counts as an outlier")
    p.add_argument("--channels-per-round", type=int, default=50)
    p.add_argument("--uploads", type=int, default=30, help="uploads sampled per channel for the baseline")
    p.add_argument("--order", default="relevance", choices=["relevance", "viewCount", "date"])
    p.add_argument("--fit", required=True,
                   help="regex of the author's niche outcome terms (for example 'lead|leads|b2b|pipeline'), "
                        "used to measure the crossover gap")
    p.add_argument("--keep", default=".", help="regex a title must match to count (packaging-structure mode)")
    p.add_argument("--probes", type=int, default=0, help="extra searches for the crossover gap after the dive")
    p.add_argument("--anchors", default="", help="comma-separated niche terms for the probes, for example 'lead gen,B2B'")
    args = p.parse_args()
    if args.probes and not args.anchors.strip():
        p.error("--probes needs --anchors (the niche terms to pair with each hot wave)")

    args.out.mkdir(parents=True, exist_ok=True)
    args.raw.mkdir(parents=True, exist_ok=True)
    if not (args.raw / "channel-uploads.json").exists():
        save(args.raw / "channel-uploads.json", {})
    state = load(args.out / "depth-first-state.json", None)
    if state is None:
        after = (datetime.now(timezone.utc) - timedelta(days=args.days)).date().isoformat()
        state = {"started_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "after": after,
                 "nodes": [], "rounds": [], "searched": 0, "outlier_channels": [], "seen_phrases": [], "probes": []}
        for s in json.loads(args.seeds.read_text()):
            state["nodes"].append({"id": len(state["nodes"]), "query": s["query"], "branch": s.get("branch", s["query"]),
                                   "depth": 0, "parent": None, "priority": 1e9, "status": "open"})
    state.setdefault("probes", [])
    fit, keep = re.compile(args.fit, re.I), re.compile(args.keep, re.I)

    def search_round(tag, specs):
        """Search, sample the result channels for baselines, rank. Returns (ranked rows by id, ids per spec node)."""
        qfile = args.out / f"queries-{tag}.json"
        save(qfile, specs)
        run([sys.executable, HERE / "youtube-depth-scan.py", "--out", args.raw, "--queries", qfile,
             "--max-searches", len(specs), "--max-calls", 60 + 4 * len(specs)])
        searches = load(args.raw / "searches.json", [])
        videos = load(args.raw / "videos.json", {})
        ids = {}
        for spec in specs:
            match = [s for s in searches if s["spec"].get("node") == spec["node"]
                     and s["spec"].get("query") == spec["query"] and s.get("status") == "ok"]
            ids[spec["node"]] = match[-1]["ids"] if match else []
        best = {}
        for vid in {v for vs in ids.values() for v in vs}:
            if vid in videos:
                cid = videos[vid]["snippet"]["channelId"]
                best[cid] = max(best.get(cid, 0), int(videos[vid].get("statistics", {}).get("viewCount", 0)))
        uploads = load(args.raw / "channel-uploads.json", {})
        need = [c for c, _ in sorted(best.items(), key=lambda x: -x[1]) if c not in uploads][: args.channels_per_round]
        if need:
            cfile = args.out / f"channels-{tag}.json"
            save(cfile, need)
            run([sys.executable, HERE / "youtube-depth-scan.py", "--out", args.raw, "--channels", cfile,
                 "--uploads", args.uploads, "--max-searches", 0, "--max-calls", 40 + 3 * len(need)])
        run([sys.executable, HERE / "youtube-rank.py", "--source", args.raw, "--out", args.out, "--title-pattern", "."])
        return {r["id"]: r for r in load(args.out / "ranked.json", {"rows": []})["rows"]}, ids

    def pick_batch():
        open_nodes = [n for n in state["nodes"] if n["status"] == "open"]
        if not open_nodes:
            return []
        if not state["rounds"]:  # round 1 measures every seed, so the first dive starts from the hottest
            return open_nodes
        deepest = max(n["depth"] for n in open_nodes)
        top = max((n for n in open_nodes if n["depth"] == deepest), key=lambda n: n["priority"])
        siblings = sorted((n for n in open_nodes if n["parent"] == top["parent"] and n["depth"] == deepest),
                          key=lambda n: -n["priority"])
        return siblings[: args.breadth]

    while state["searched"] < args.max_searches:
        batch = pick_batch()[: args.max_searches - state["searched"]]
        if not batch:
            break
        rnd = len(state["rounds"]) + 1
        ranked, ids_by_node = search_round(f"round-{rnd}", [
            {"branch": n["branch"], "query": n["query"], "after": state["after"], "order": args.order,
             "node": n["id"], "depth": n["depth"]} for n in batch])
        state["searched"] += len(batch)

        seen_channels, seen_phrases = set(state["outlier_channels"]), set(state["seen_phrases"])
        taken = [core(n["query"]) for n in state["nodes"]]
        summary = []
        for n in batch:
            rows = [ranked[v] for v in ids_by_node[n["id"]] if v in ranked and keep.search(ranked[v]["title"])]
            scored = [r for r in rows if ratio(r)]
            outs = [r for r in scored if ratio(r) >= args.outlier]
            new_ch = {r["channel_id"] for r in outs} - seen_channels
            # Phrases that recur across outlier titles from at least 2 channels become the children.
            weight, chans = defaultdict(float), defaultdict(set)
            for r in outs:
                for ph in phrases(r["title"]):
                    weight[ph] += math.log2(ratio(r))
                    chans[ph].add(r["channel_id"])
            cands = sorted((ph for ph in weight if len(chans[ph]) >= 2), key=lambda ph: -weight[ph])
            new_ph = [ph for ph in cands if ph not in seen_phrases]
            scored_sorted = sorted(ratio(r) for r in scored)
            n.update(status="done", round=rnd, results=len(ids_by_node[n["id"]]), scored=len(scored),
                     outliers=len(outs), outlier_channels=len({r["channel_id"] for r in outs}),
                     new_outlier_channels=len(new_ch), fit_outliers=sum(bool(fit.search(r["title"])) for r in outs),
                     median_ratio=round(scored_sorted[len(scored_sorted) // 2], 2) if scored else None,
                     yield_score=round(sum(math.log2(ratio(r)) for r in outs), 2), phrases=cands[:12],
                     top=[{"id": r["id"], "title": r["title"], "channel": r["channel"], "views": r["views"],
                           "ratio": ratio(r), "age_days": r["age_days"]}
                          for r in sorted(outs, key=lambda r: -ratio(r))[:5]])
            n["saturated"] = not new_ch and not new_ph
            if not n["saturated"] and n["depth"] < args.max_depth:
                added = 0
                for ph in cands:
                    c = core(ph)
                    # Skip near-duplicates: same words as the parent, a sibling or anything searched already.
                    if not c or any(c <= t or t <= c for t in taken if t):
                        continue
                    taken.append(c)
                    state["nodes"].append({"id": len(state["nodes"]), "query": ph, "branch": n["branch"],
                                           "depth": n["depth"] + 1, "parent": n["id"],
                                           "priority": round(n["yield_score"] * 1000 + weight[ph], 3), "status": "open"})
                    added += 1
                    if added == args.breadth:
                        break
            seen_channels |= {r["channel_id"] for r in outs}
            seen_phrases |= set(cands)
            summary.append(f"{n['query']} → {n['outliers']} outliers, {n['new_outlier_channels']} new channels"
                           + (" (saturated)" if n["saturated"] else ""))
        state["outlier_channels"], state["seen_phrases"] = sorted(seen_channels), sorted(seen_phrases)
        state["rounds"].append({"round": rnd, "nodes": [n["id"] for n in batch],
                                "finished_at": datetime.now(timezone.utc).isoformat(timespec="seconds")})
        save(args.out / "depth-first-state.json", state)
        print(f"round {rnd}: " + "; ".join(summary), flush=True)

    rows = load(args.out / "ranked.json", {"rows": []})["rows"]
    todo = args.probes - len(state["probes"])
    if todo > 0:
        anchors = [a.strip() for a in args.anchors.split(",") if a.strip()]
        hot = [ph for ph, _ in heat(rows, args, fit, keep) if not fit.search(ph)]
        done = {pr["query"].lower() for pr in state["probes"]}
        specs = []
        for ph in hot:
            for a in anchors:
                q = f"{ph} {a}"
                if q.lower() not in done and len(specs) < todo:
                    specs.append({"branch": "probe", "query": q, "after": state["after"], "order": args.order,
                                  "node": f"probe-{len(state['probes']) + len(specs)}", "phrase": ph, "anchor": a})
        if specs:
            ranked, ids = search_round(f"probes-{len(state['probes']) + 1}", specs)
            videos = load(args.raw / "videos.json", {})
            for spec in specs:
                need = core(spec["phrase"])
                match = [v for v in ids[spec["node"]] if v in videos and need <= core(videos[v]["snippet"]["title"])
                         and fit.search(videos[v]["snippet"]["title"])]
                with_base = [ranked[v] for v in match if v in ranked and ratio(ranked[v])]
                best = max(with_base, key=ratio, default=None)
                state["probes"].append({"query": spec["query"], "phrase": spec["phrase"], "anchor": spec["anchor"],
                                        "results": len(ids[spec["node"]]), "niche_matches": len(match),
                                        "with_baseline": len(with_base),
                                        "outliers": sum(ratio(r) >= args.outlier for r in with_base),
                                        "views_max": max((int(videos[v]["statistics"].get("viewCount", 0)) for v in match), default=0),
                                        "best": {"title": best["title"], "url": best["url"], "ratio": ratio(best),
                                                 "views": best["views"], "channel": best["channel"]} if best else None})
            save(args.out / "depth-first-state.json", state)
            rows = load(args.out / "ranked.json", {"rows": []})["rows"]
    write_report(args, state, rows, fit, keep)


def heat(rows, args, fit, keep):
    """Phrases across keyword-discovered outliers in the window, by number of channels."""
    outs = [r for r in rows if r["discovery"] == "keyword" and r["age_days"] <= args.days
            and keep.search(r["title"]) and ratio(r) >= args.outlier]
    stats = defaultdict(list)
    for r in outs:
        for ph in phrases(r["title"]):
            stats[ph].append(r)
    hot, kept = [], []
    for ph in sorted(stats, key=lambda ph: (-len({r["channel_id"] for r in stats[ph]}), -len(stats[ph]))):
        if len({r["channel_id"] for r in stats[ph]}) < 2:
            break
        c = core(ph)
        if not c or any(c <= k or k <= c for k in kept):
            continue  # "astra" and "gpt-6 astra" are 1 wave; "2.5" alone is no wave
        kept.append(c)
        hot.append((ph, stats[ph]))
    return hot


def write_report(args, state, rows, fit, keep):
    thousands = lambda n: f"{n:,}"
    in_window = [r for r in rows if r["age_days"] <= args.days and keep.search(r["title"])]
    popping = sorted((r for r in in_window if ratio(r) >= args.outlier), key=lambda r: -ratio(r))
    outs = [r for r in popping if r["discovery"] == "keyword"]
    side = [r for r in popping if r["discovery"] != "keyword"]
    probe_note = f", probes: {len(state['probes'])}" if state["probes"] else ""
    lines = ["# Depth-first YouTube scan", "",
             f"Generated {datetime.now(timezone.utc).date().isoformat()} by `scripts/youtube-depth-first.py`. "
             f"Window: published after {state['after']} ({args.days} days). Outlier: ratio ≥ {args.outlier}x. "
             f"Dive searches: {state['searched']}{probe_note}. Raw evidence: `{args.raw}`.", "",
             "Ratios are current views against the channel's own comparable uploads (youtube-rank.py): "
             "a cross-sectional snapshot, not views/hour, not CTR, not proof the topic caused it.", "",
             "## The tree", "",
             "| Round | Depth | Query | Results | Outliers | Channels (new) | Niche-fit outliers | Median ratio | Status |",
             "|---|---|---|---|---|---|---|---|---|"]
    by_parent = defaultdict(list)
    for n in state["nodes"]:
        by_parent[n["parent"]].append(n)

    def walk(parent, depth):
        for n in sorted(by_parent[parent], key=lambda n: (n.get("round") or 99, -n["priority"])):
            if n["status"] != "done":
                continue
            dived = any(c["status"] == "done" for c in by_parent[n["id"]])
            status = "saturated" if n.get("saturated") else ("dived" if dived else "not followed")
            lines.append(f"| {n['round']} | {n['depth']} | {'· ' * depth}{n['query']} | {n['results']} | {n['outliers']} | "
                         f"{n['outlier_channels']} ({n['new_outlier_channels']}) | {n['fit_outliers']} | "
                         f"{n['median_ratio'] if n['median_ratio'] is not None else 'n/a'} | {status} |")
            walk(n["id"], depth + 1)
    walk(None, 0)
    unexplored = [n["query"] for n in state["nodes"] if n["status"] == "open"]
    if unexplored:
        lines += ["", "Queued but not searched (budget): " + ", ".join(f"`{q}`" for q in unexplored[:20])]

    lines += ["", "## Heat: waves across all outliers", "",
              "A phrase is hot when several channels have outliers with it. Near-duplicates are folded into the "
              "first form. Few niche-fit outliers on a hot phrase is the crossover gap: the wave exists, the niche "
              "angle is still thin. Confirm with the probes below.", "",
              "| Phrase | Outliers | Channels | Median ratio | Niche-fit outliers | Newest (days) |", "|---|---|---|---|---|---|"]
    for ph, rs in heat(rows, args, fit, keep)[:25]:
        med = sorted(ratio(r) for r in rs)[len(rs) // 2]
        lines.append(f"| {ph} | {len(rs)} | {len({r['channel_id'] for r in rs})} | {med:.1f}x | "
                     f"{sum(bool(fit.search(r['title'])) for r in rs)} | {min(r['age_days'] for r in rs):.0f} |")

    if state["probes"]:
        lines += ["", "## Crossover gap probes", "",
                  "Searches for a hot wave plus a niche term. Niche matches: results whose title has the wave's words "
                  "and a niche word. Few matches with low views on a hot wave is an open slot; outliers here mean "
                  "the angle is already taken.", "",
                  "| Probe | Niche matches | With baseline | Outliers | Most views | Best match |", "|---|---|---|---|---|---|"]
        for pr in state["probes"]:
            b = pr["best"]
            best = (f"[{b['title'].replace('|', '/').replace(chr(0x2014), ',')}]({b['url']}) {b['ratio']:.1f}x, "
                    f"{b['channel']}") if b else ""
            lines.append(f"| {pr['query']} | {pr['niche_matches']} | {pr['with_baseline']} | {pr['outliers']} | "
                         f"{thousands(pr['views_max'])} | {best} |")

    def table(rs):
        for r in rs:
            title = r["title"].replace("|", "/").replace("[", "(").replace("]", ")").replace("\u2014", ",")
            subs = thousands(int(r["subscribers"])) if r["subscribers"] else "?"
            lines.append(f"| {ratio(r):.1f}x | {thousands(r['views'])} | {r['age_days']:.0f} | {r['channel']} ({subs}) | "
                         f"[{title}]({r['url']}) | {'yes' if fit.search(r['title']) else ''} |")
    lines += ["", "## Top outliers in the window", "", "| Ratio | Views | Age (days) | Channel (subs) | Title | Fit |",
              "|---|---|---|---|---|---|"]
    table(outs[:40])
    lines += ["", "## Also popping on the sampled channels", "",
              "Outliers from the channel libraries sampled for baselines, not from a search: adjacent topics "
              "the same audience is clicking right now.", "",
              "| Ratio | Views | Age (days) | Channel (subs) | Title | Fit |", "|---|---|---|---|---|---|"]
    table(side[:15])
    (args.out / "depth-first.md").write_text("\n".join(lines) + "\n")
    print(f"report: {args.out / 'depth-first.md'} ({len(outs)} keyword outliers in window)")


if __name__ == "__main__":
    main()
