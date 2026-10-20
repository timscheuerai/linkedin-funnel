#!/usr/bin/env python3
"""Draft edit.json for a talking-head clip from a style preset.

Reads words_out.json (from video-editor/scripts/transcript_out.py) and writes a
complete plan for video-editor/scripts/build_edit.py: captions with fixes and
drops, the opening hook, the closing payoff, highlight words, hard reframes,
music and loudness. The draft is a starting point; the agent reviews wording,
payoffs and placements on the stills sheet before the full build.

Usage:
  python plan.py <project> --base <cut.mp4> [--preset clean] [--variant default]
                 [--name NAME] [--out edit.json]
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
FILLER = set(
    "a an the of to in on at for and or but so is are was were be been it its it's that this these those "
    "i me my we our us you your as with by from if then than just".split()
)


def norm(w: str) -> str:
    return re.sub(r"[^a-z0-9äöü']", "", w.lower())


def probe(path: Path) -> tuple[int, int, float]:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:format=duration",
         "-of", "json", str(path)], check=True, text=True, capture_output=True).stdout
    d = json.loads(out)
    return int(d["streams"][0]["width"]), int(d["streams"][0]["height"]), float(d["format"]["duration"])


def sentences(words: list[dict], clauses: bool = False) -> list[list[dict]]:
    """Split on sentence ends and long pauses; with clauses=True also on a comma followed by a pause."""
    out: list[list[dict]] = []
    cur: list[dict] = []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        comma = clauses and nxt is not None and w["w"].endswith(",") and nxt["s"] - w["e"] >= 0.3
        if nxt is None or re.search(r"[.?!]$", w["w"]) or nxt["s"] - w["e"] >= 0.6 or comma:
            out.append(cur)
            cur = []
    return out


def payoff(sent: list[dict], lead_max: int, number_ok: bool) -> dict | None:
    """Pick the hero of a sentence: a spoken number, else its last 1 or 2 content words."""
    if number_ok:
        for i, w in enumerate(sent):
            if re.search(r"\d", w["w"]):
                return {"start": w["s"], "words": 1, "lead": min(i, lead_max), "style": "number", "_idx": i}
    k = len(sent) - 1
    while k > 0 and norm(sent[k]["w"]) in FILLER:
        k -= 1
    if k < 1:
        return None
    two = k >= 1 and norm(sent[k - 1]["w"]) not in FILLER and len(norm(sent[k - 1]["w"]) + norm(sent[k]["w"])) <= 14
    first = k - 1 if two else k
    lead = min(first, lead_max)
    while lead and norm(sent[first - lead]["w"]) in {"and", "so", "but", "or", "then"}:
        lead -= 1  # a lead line never opens on a conjunction
    return {"start": sent[first]["s"], "words": 2 if two else 1, "lead": lead, "style": "serif", "_idx": first}


def music_file(name: str) -> Path:
    """A music path from the preset: absolute, or relative to this skill folder."""
    path = Path(name).expanduser()
    return path if path.is_absolute() else SKILL / path


def clean_words(words: list[dict], cap: dict) -> tuple[dict, list, list, list]:
    """Display fixes, filler drops and stutter drops; returns (fixes, drop, drop_at, kept words)."""
    # Display fixes: optional Swiss thousands, no trailing sentence punctuation.
    fixes: dict[str, str] = {}
    for w in words:
        d = w["w"]
        if cap.get("swiss_numbers"):
            d = re.sub(r"(?<=\d),(?=\d{3}\b)", "'", d)
        if cap.get("strip_punctuation"):
            d = re.sub(r"[.,;:]+$", "", d)
        if d != w["w"]:
            fixes[w["w"]] = d

    # Drops: filler by token, stutters and false starts by time.
    filler = {norm(x) for x in cap.get("drop", [])}
    drop = sorted({w["w"] for w in words if norm(w["w"]) in filler or w["w"] in cap.get("drop_exact", [])})
    drop_at: list[float] = []
    after = [w for w in words if w["w"] not in drop]  # stutters hide behind fillers: "inbound, um, inbound"
    for i, w in enumerate(after[:-1]):
        if cap.get("drop_stutters") and (
            (re.search(r"[,-]$", w["w"]) and norm(w["w"]) == norm(after[i + 1]["w"])) or w["w"].endswith("--")
        ):
            drop_at.append(w["s"])
    kept = [w for w in words if w["w"] not in drop and not any(abs(w["s"] - t) < 0.02 for t in drop_at)]
    return fixes, drop, drop_at, kept


NUMBER_WORDS = {w: i for i, w in enumerate("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split())}
NUMBER_WORDS.update({w: 10 * (i + 2) for i, w in enumerate("twenty thirty forty fifty sixty seventy eighty ninety".split())})
LIST_PREFIX = {"we", "have", "you", "they", "its", "theres", "is", "are", "a", "an", "the", "and", "or", "one", "for", "your", "our", "my", "also", "plus", "then"}
PRONOUNS = {"i", "ive", "im", "id", "we", "weve", "you", "youre", "they", "it", "this", "that", "these", "those", "he", "she", "me", "us", "them"}
FUNCTION = {"for", "as", "so", "but", "yes", "which", "let", "lets", "if", "when", "because", "to", "with", "of", "about", "in", "on", "at", "who"}
PAYOFF_PHRASES = {"all in one", "in one place", "from one platform", "all from one platform", "in one"}


def spoken_number(tok: str) -> int | None:
    """'fifty-five' -> 55, 'twelve' -> 12; Scribe often spells numbers out."""
    parts = norm(tok).replace("'", "").split("-") if "-" in tok else [norm(tok)]
    if all(p in NUMBER_WORDS for p in parts) and parts:
        return sum(NUMBER_WORDS[p] for p in parts)
    return None


def list_item(clause: list[dict], first: bool) -> list[dict] | None:
    """The noun phrase of 1 enumeration item, or None: 'we have a reply manager,' -> reply manager."""
    toks = list(clause)
    while toks and norm(toks[0]["w"]).replace("'", "") in LIST_PREFIX:
        toks = toks[1:]
    if first and len(toks) > 3:
        toks = toks[-2:]  # an enumeration can start mid-clause: "which is a database,"
        while toks and norm(toks[0]["w"]).replace("'", "") in LIST_PREFIX:
            toks = toks[1:]
    if not 1 <= len(toks) <= 3:
        return None
    bare_toks = [norm(t["w"]).replace("'", "") for t in toks]
    if any(t in PRONOUNS for t in bare_toks) or bare_toks[0] in FUNCTION or any(re.search(r"\d", t["w"]) for t in toks):
        return None
    return toks


def find_scenes(kept: list[dict], fixes: dict, sc: dict, duration: float, drop_at: list | None = None) -> list[dict]:
    """Blank-screen candidates from the words: a ring for a spoken percentage, a list for a spoken enumeration.

    Rules are strict on purpose (natural speech is full of commas): list items are
    short noun phrases without pronouns, at least 3, spoken within 2 s of each other.
    """
    scenes: list[dict] = []
    for i, w in enumerate(kept):
        pct = "%" in w["w"]
        nxt = kept[i + 1] if i + 1 < len(kept) else None
        if not pct and nxt and norm(nxt["w"]).startswith("percent") and spoken_number(w["w"]) is not None:
            fixes[w["w"]] = f"{spoken_number(w['w'])}%"  # "fifty-five percent" -> 55%
            if drop_at is not None:
                drop_at.append(nxt["s"])
            pct = True
        if pct and w["s"] > 3:
            lead = [x for x in kept[max(0, i - 2):i] if w["s"] - x["s"] < 1.0]
            after = [x for x in kept[i + 1:i + 5] if not norm(x["w"]).startswith("percent")][:3]
            tail = [x for x in after if x["s"] - w["e"] < 1.6]
            a0, a1 = (lead[0]["s"] if lead else w["s"]) - 0.25, (tail[-1]["e"] if tail else w["e"]) + 0.35
            scenes.append({"graphic": "ring", "at": a0, "dur": min(a1 - a0, sc.get("max_s", 5)), "cue": w["w"],
                           "heroes": [{"start": w["s"], "words": 1, "lead": len(lead), "tail": len(tail), "style": "number"}]})
    # Enumerations are spoken fast: split on every comma, pause or not.
    commas: list[list[dict]] = []
    cur: list[dict] = []
    for w in kept:
        cur.append(w)
        if re.search(r"[,.?!]$", w["w"]):
            commas.append(cur)
            cur = []
    if cur:
        commas.append(cur)
    k = 0
    while k < len(commas):
        run, j = [], k
        while j < len(commas) and commas[j][-1]["w"].endswith(","):
            item = list_item(commas[j], first=not run)
            if not item or (run and item[0]["s"] - run[-1][0]["s"] > 2.0):
                break
            run.append(item)
            j += 1
        pay: list[dict] = []
        if len(run) >= 2 and j < len(commas):  # the closing item: "and a LinkedIn writer." / "a workflow builder all in one."
            last = commas[j]
            toks = list(last)
            while toks and norm(toks[0]["w"]).replace("'", "") in LIST_PREFIX:
                toks = toks[1:]
            for cut_at in range(1, min(3, len(toks)) + 1):
                rest = " ".join(norm(t["w"]) for t in toks[cut_at:])
                if rest in PAYOFF_PHRASES:
                    pay = toks[cut_at:]
                    toks = toks[:cut_at]
                    break
            item = list_item(toks, first=False) if toks else None
            if item and item[0]["s"] - run[-1][0]["s"] <= 2.0:
                run.append(item)
                j += 1
        if len(run) >= 3:
            items = [{"start": r[0]["s"], "words": len(r)} for r in run]
            a0, a1 = run[0][0]["s"] - 0.3, (pay[-1]["e"] if pay else run[-1][-1]["e"]) + 0.4
            scene = {"graphic": "list", "at": a0, "dur": min(a1 - a0, sc.get("max_s", 5) + 2), "cue": run[0][0]["w"], "items": items}
            if pay:
                scene["payoff"] = {"start": pay[0]["s"], "words": len(pay)}
            scenes.append(scene)
            k = j
            continue
        k = max(k + 1, j)
    scenes.sort(key=lambda x: x["at"])
    kept_scenes, last_end = [], -99.0
    for x in scenes:
        if x["at"] - last_end >= sc.get("min_gap_s", 8) and x["at"] > 3.5 and x["at"] + x["dur"] < duration - 3:
            kept_scenes.append(x)
            last_end = x["at"] + x["dur"]
    scenes = kept_scenes
    for n_, x in enumerate(scenes):
        x["tone"] = sc.get("tones", ["dark"])[n_ % len(sc.get("tones", ["dark"]))]
    return scenes


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project", type=Path)
    ap.add_argument("--base", required=True, type=Path, help="the cut clip (upscale 9:16 sources below 1080 wide first)")
    ap.add_argument("--preset", default="clean")
    ap.add_argument("--variant", default="default", help="a key of the preset's variants")
    ap.add_argument("--name", default=None)
    ap.add_argument("--out", default="edit.json")
    a = ap.parse_args()

    project = a.project.expanduser().resolve()
    preset = json.loads((SKILL / "presets" / f"{a.preset}.json").read_text())
    variant = preset["variants"][a.variant]
    base = a.base.expanduser().resolve()
    width, height, duration = probe(base)
    portrait = height > width
    short = portrait or duration <= 120
    words = json.loads((project / "words_out.json").read_text())
    cap, hk, rf = preset["captions"], preset["hooks"], preset["reframes"]

    fixes, drop, drop_at, kept = clean_words(words, cap)
    sents = sentences(kept)
    clauses = sentences(kept, clauses=True)

    heroes: list[dict] = []
    if hk.get("open") and sents and sents[0][0]["s"] < 1.5:
        first = [w for w in sents[0] if w["s"] < hk["open_window_s"]] or sents[0]
        h = payoff(first, hk["open_lead_max"], number_ok=True)
        if h:
            if h["style"] == "number":  # finish the number: "400" + "leads per month"
                h["tail"] = min(hk.get("open_tail_max", 0), len(sents[0]) - h["_idx"] - 1)
            heroes.append(h)
    if short and hk.get("close") and len(clauses) > 1 and duration > 6:
        h = payoff(clauses[-1], hk["close_lead_max"], number_ok=False)
        if h and (not heroes or h["start"] > heroes[0]["start"] + 2):
            if portrait and hk.get("close_side"):
                h.update(place=hk["close_side"], y=hk["close_side_y"])
            heroes.append(h)
    if not short:
        t = hk["long_every_s"]
        for sent in sents[1:]:
            if sent[0]["s"] >= t and len(sent) >= 4:
                h = payoff(sent, 4, number_ok=True)
                if h:
                    heroes.append(h)
                    t = sent[-1]["e"] + hk["long_every_s"]
    sc = preset.get("scenes", {})
    scenes = find_scenes(kept, fixes, sc, duration, drop_at)
    word = lambda w: fixes.get(w["w"], w["w"])  # noqa: E731
    idx_of = {id(w): i for i, w in enumerate(kept)}
    busy = lambda a, b: any(x["at"] - 1.0 < b and a < x["at"] + x["dur"] + 1.0 for x in scenes)  # noqa: E731

    # A serif payoff about every 12 s through the middle, so the rhythm never flattens.
    if short and hk.get("mid_every_s"):
        t_next = (heroes[0]["start"] + hk["mid_every_s"]) if heroes else hk["mid_every_s"]
        close_t = heroes[-1]["start"] if len(heroes) > 1 else duration
        weak = {"too", "right", "it", "this", "that", "there", "here", "one", "thing", "things", "stuff", "meaning", "like", "way", "well"}
        for cl in sents:  # sentence ends only: a clause end is rarely a payoff
            if len(cl) < 5 or cl[-1]["e"] < t_next or cl[-1]["e"] > close_t - 6:
                continue
            h = payoff(cl, hk["mid_lead_max"], number_ok=False)
            if not h or norm(cl[min(len(cl) - 1, h["_idx"] + h["words"] - 1)]["w"]) in weak or len(norm(cl[h["_idx"]]["w"])) < 4:
                continue
            idx = h["_idx"]
            span = (cl[max(0, idx - h["lead"])]["s"], cl[min(len(cl) - 1, idx + h["words"] - 1)]["e"])
            if busy(*span) or re.search(r"\d", cl[idx]["w"]):
                continue
            heroes.append(h)
            t_next = span[1] + hk["mid_every_s"]
        heroes.sort(key=lambda h: h["start"])

    hero_span = []
    for h in heroes:
        idx = next(i for i, w in enumerate(kept) if abs(w["s"] - h["start"]) < 0.02)
        hero_span.append((kept[max(0, idx - h["lead"])]["s"], kept[min(len(kept) - 1, idx + h["words"] + h.get("tail", 0) - 1)]["e"]))

    # 1 accent marker on a long key word, clear of the hooks.
    highlight: list[str] = []
    if variant.get("highlightWords"):
        hl, last_t = preset["highlight"], -99.0
        for w in kept:
            d = fixes.get(w["w"], w["w"])
            if len(norm(d)) >= hl["min_letters"] and not re.search(r"\d", d) and not any(a - 0.3 <= w["s"] <= b + 0.3 for a, b in hero_span) and not busy(w["s"], w["e"]):
                if w["s"] - last_t >= hl["min_gap_s"]:
                    highlight.append({"start": w["s"], "words": 1})
                    last_t = w["s"]
                    if short and len(highlight) >= hl["max_in_short"]:
                        break

    # Hard reframes: after the opening hook, alternate tight and wide at phrase starts; punch in on the closing payoff.
    focus = rf["focus"]["portrait" if portrait else "landscape"]
    lo, hi = rf["short_every_s" if short else "long_every_s"]
    # Cut points: pauses and clause ends; a tight cut has few pauses, so any word start is the fallback.
    starts = [w["s"] - 0.05 for i, w in enumerate(kept) if i and (w["s"] - kept[i - 1]["e"] >= 0.25 or re.search(r"[,.?!]$", kept[i - 1]["w"]))]
    anywhere = [w["s"] - 0.05 for w in kept[1:]]
    t0 = hero_span[0][1] + 0.3 if heroes and heroes[0]["start"] < 6 else 1.5
    close = next((h for h in heroes if h.get("place")), heroes[-1] if short and len(heroes) > 1 else None)
    close_at = (close["start"] - 0.2) if close else duration
    cuts, t = [], t0
    while True:
        nxt = [s for s in starts if t + lo <= s <= t + hi]
        if not nxt:
            mid = t + (lo + hi) / 2
            nxt = sorted((s for s in anywhere if s > t + lo), key=lambda s: abs(s - mid))[:1]
        cand = nxt[0] if nxt else None
        cuts.append(t)
        if cand is None or cand >= close_at - rf["min_len_s"]:
            break
        t = cand
    zooms, n = [], 0
    for i, c in enumerate(cuts):
        end = min(cuts[i + 1] if i + 1 < len(cuts) else close_at, close_at)
        if i % 2 == 0 and end - c >= rf["min_len_s"]:
            cue = next((w["w"] for w in kept if w["s"] >= c), kept[-1]["w"])
            zooms.append({"id": f"z{len(zooms) + 1:02d}", "at": round(c, 2), "dur": round(end - c, 2),
                          "scale": rf["scales"][n % len(rf["scales"])], "focus": focus, "ease": 0, "cue": cue})
            n += 1
    trimmed = []
    for z in zooms:
        a0, a1 = z["at"], z["at"] + z["dur"]
        for x in scenes:
            if x["at"] <= a0 < x["at"] + x["dur"]:
                a0 = x["at"] + x["dur"]
            elif a0 < x["at"] < a1:
                a1 = x["at"]
        if a1 - a0 >= rf["min_len_s"]:
            trimmed.append({**z, "at": round(a0, 2), "dur": round(a1 - a0, 2),
                            "cue": next((w["w"] for w in kept if w["s"] >= a0), kept[-1]["w"])})
    zooms = [{**z, "id": f"z{i + 1:02d}"} for i, z in enumerate(trimmed)]
    if close and duration - close_at >= rf["min_len_s"]:
        side = close.get("place")
        zooms.append({"id": f"z{len(zooms) + 1:02d}", "at": round(close_at, 2), "dur": round(duration - close_at - 0.01, 2),
                      "scale": rf["payoff_scale"], "focus": hk["close_focus"] if side else focus, "ease": 0,
                      "cue": next(w["w"] for w in kept if abs(w["s"] - close["start"]) < 0.02)})

    m = preset["music"]
    sections = [[0, round(duration, 2)]] if short else [[0, round(min(40.0, duration), 2)], [round(max(0.0, duration - 20), 2), round(duration, 2)]]
    rel = lambda p: str(p.relative_to(project)) if p.is_relative_to(project) else str(p)  # noqa: E731
    edl = project / "edl.json"
    for h in heroes:
        h.pop("_idx", None)
    plan = {
        "version": 1,
        "preset": f"{a.preset}/{a.variant}",
        "base": rel(base),
        "edl": "edl.json" if edl.exists() and not base.name.startswith("base-") else None,
        "layout": {"cam": None},
        "output": {"name": a.name or project.name},
        "voice": {"clean": preset.get("voice", {}).get("clean", True)},
        "loudness": preset["loudness"],
        "music": {"file": str(music_file(m["file"])), "sections": sections, "gain_db": m["gain_db"], "fade": m["fade"]} if m.get("enabled", True) and m.get("file") else None,
        "overlays": [{
            "id": "c01", "template": "Captions", "at": 0.0, "dur": round(duration - 0.01, 2), "cue": kept[0]["w"],
            "props": {"fixes": fixes, "drop": drop, "drop_at": drop_at, "heroes": heroes, "highlight": highlight,
                      "mode": cap["mode"]["portrait" if portrait else "landscape"], "serif": cap["serif"]},
        }],
        "zooms": zooms,
    }
    for n_, x in enumerate(scenes):
        props = {"tone": x["tone"], "graphic": x["graphic"], "fixes": fixes, "drop": drop, "drop_at": drop_at}
        for key in ("heroes", "items", "payoff"):
            if key in x:
                props[key] = x[key]
        plan["overlays"].append({"id": f"s{n_ + 1:02d}", "template": "Interlude", "at": round(x["at"], 2),
                                 "dur": round(x["dur"], 2), "cue": x["cue"], "props": props})
    out = project / a.out
    out.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n")
    say = lambda ws: " ".join(fixes.get(w["w"], w["w"]) for w in ws)  # noqa: E731
    print(f"{out}  ({a.preset}/{a.variant}, {'short' if short else 'long'}, {width}x{height}, {duration:.1f}s)")
    for h in heroes:
        idx = next(i for i, w in enumerate(kept) if abs(w["s"] - h["start"]) < 0.02)
        lead, body = kept[max(0, idx - h["lead"]):idx], kept[idx:idx + h["words"]]
        print(f"  hook @{h['start']:.2f}  [{say(lead)}] -> {say(body)} ({h['style']}{', ' + h['place'] if h.get('place') else ''})")
    marks = [next((fixes.get(w["w"], w["w"]) for w in kept if abs(w["s"] - h["start"]) < 0.02), "?") for h in highlight]
    print(f"  highlight: {marks or 'none'}; dropped: {drop + [f'@{t:.2f}' for t in drop_at] or 'none'}")
    for x in scenes:
        def words_at(start: float, n: int) -> str:
            i0 = next(i for i, w in enumerate(kept) if abs(w["s"] - start) < 0.02)
            return " ".join(word(w) for w in kept[i0:i0 + n])
        what = " / ".join(words_at(it["start"], it["words"]) for it in x.get("items", [])) or x["cue"]
        pay = f" -> {words_at(x['payoff']['start'], x['payoff']['words'])}" if x.get("payoff") else ""
        print(f"  scene @{x['at']:.2f} {x['graphic']} ({x['tone']}, {x['dur']:.1f}s): {what}{pay}")
    beats = sorted([h["start"] for h in heroes] + [x["at"] for x in scenes] + [h["start"] for h in highlight] + [0.0, duration])
    gaps = [(b - a, a) for a, b in zip(beats, beats[1:]) if b - a > sc.get("max_beat_gap_s", 15)]
    if gaps:
        print("  flat stretches (add a flow scene, payoff or highlight in review): " + ", ".join(f"{a:.0f}-{a + g:.0f}s" for g, a in gaps))
    print(f"  reframes: {', '.join(f'{z['at']:.1f}s x{z['scale']}' for z in zooms) or 'none'}")


if __name__ == "__main__":
    main()
