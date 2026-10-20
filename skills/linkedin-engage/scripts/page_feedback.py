#!/usr/bin/env python3
"""What the author did on the LinkedIn Comment Queue page, read back from its database.

Optional. When the page is published as a Claude Artifact with a `db`
capability, it saves 1 document per card in its `feedback` collection: which
draft the author took (Copy, or Copy & open), their final text, whether they
edited it, or why they skipped the card. Read the collection into files first
with the ArtifactData tool (action "list", the page url, collection
"feedback", out_dir <scratch>/page-feedback), then:

  python3 page_feedback.py <scratch>/page-feedback/feedback \
    --append-golden skills/linkedin-engage/references/golden-comments.md

It prints each card and the totals across all runs: how often each move was
shown and taken, draft A against B, how much the author edits and how their
final text differs in length, and the skip reasons. With --append-golden,
every comment they took is added once to the golden set the drafting reads as
its best examples. It writes only the golden file.
"""
import argparse, json, re, sys
from collections import Counter, defaultdict
from pathlib import Path


def load(folder):
    docs = []
    for f in sorted(Path(folder).glob("*.json")):
        try:
            obj = json.loads(f.read_text())
        except Exception:
            continue
        body = obj.get("data") if isinstance(obj.get("data"), dict) else obj
        if body.get("run_id") and body.get("item_id"):
            docs.append({**body, "_id": f.stem})
    return docs


def words(t):
    return len(re.findall(r"\S+", t or ""))


def one_line(t):
    return " / ".join(p.strip() for p in re.split(r"\n\s*\n|\n", (t or "").strip()) if p.strip())


def letter(k, n):
    return "" if k is None or n < 2 else ("AB"[k] if k < 2 else str(k + 1))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("folder", help="the folder of feedback documents ArtifactData wrote")
    ap.add_argument("--append-golden", help="references/golden-comments.md: add every comment the author took, once")
    a = ap.parse_args()
    docs = load(a.folder)
    if not docs:
        sys.exit(f"no feedback documents in {a.folder}")

    shown, taken, by_slot = Counter(), Counter(), Counter()
    reasons, edits, lengths = Counter(), [], []
    runs = defaultdict(list)
    for d in docs:
        runs[d["run_id"]].append(d)
        vs = d.get("variants") or []
        for v in vs:
            shown[v.get("label") or v.get("move") or "?"] += 1
        state, k = d.get("state"), d.get("picked")
        if state in ("copied", "opened") and k is not None and k < len(vs):
            taken[vs[k].get("label") or vs[k].get("move") or "?"] += 1
            by_slot[letter(k, len(vs)) or "only"] += 1
            edits.append(bool(d.get("edited")))
            lengths.append((words(d.get("draft")), words(d.get("final"))))
        elif state == "skipped":
            reasons[d.get("skip_reason") or "no reason"] += 1

    for run in sorted(runs):
        print(f"## Run {run}")
        for d in sorted(runs[run], key=lambda d: d.get("updated_at") or ""):
            vs, k, state = d.get("variants") or [], d.get("picked"), d.get("state")
            who = d.get("name") or d.get("author")
            if state in ("copied", "opened"):
                move = vs[k].get("label") if k is not None and k < len(vs) else "?"
                how = "Copy & open" if state == "opened" else "Copy"
                tag = letter(k, len(vs))
                line = f"- {who}: took {tag + ' ' if tag else ''}({move}) with {how}"
                if d.get("edited"):
                    line += f', edited\n  draft: "{one_line(d.get("draft"))}"\n  final: "{one_line(d.get("final"))}"'
                else:
                    line += f', as drafted: "{one_line(d.get("final"))}"'
            elif state == "skipped":
                line = f"- {who}: skipped ({d.get('skip_reason') or 'no reason'})"
            else:
                line = f"- {who}: opened the card, nothing taken yet"
            print(line)
        print()

    took = sum(taken.values())
    print("## Totals")
    print(f"- cards with an action: {len(docs)}, taken: {took}, skipped: {sum(reasons.values())}")
    if by_slot:
        print("- taken by slot: " + ", ".join(f"{s} {n}" for s, n in sorted(by_slot.items())))
    print("- moves (taken of shown): " + ", ".join(f"{m} {taken[m]}/{n}" for m, n in shown.most_common()))
    if edits:
        dw = sum(f - d for d, f in lengths) / len(lengths)
        print(f"- edited {sum(edits)} of {len(edits)} taken; final vs draft length {dw:+.1f} words on average")
    if reasons:
        print("- skip reasons: " + ", ".join(f"{r} {n}" for r, n in reasons.most_common()))

    if a.append_golden:
        g = Path(a.append_golden)
        text = g.read_text() if g.exists() else (
            "# Golden comments\n\n"
            "The comments the author took from the LinkedIn Comment Queue, with their edits, newest at the bottom.\n\n")
        added = 0
        for d in sorted(docs, key=lambda d: d.get("updated_at") or ""):
            if d.get("state") not in ("copied", "opened") or f"doc:{d['_id']}" in text:
                continue
            vs, k = d.get("variants") or [], d.get("picked")
            move = vs[k].get("label") if k is not None and k < len(vs) else "?"
            when = (d.get("updated_at") or d["run_id"])[:10]
            text += (f"- {when}, {d.get('name') or d.get('author')} ({move}{', edited' if d.get('edited') else ''}): "
                     f"\"{one_line(d.get('final'))}\" <!-- doc:{d['_id']} -->\n")
            added += 1
        g.write_text(text)
        print(f"\n{added} new comments added to {g}")


if __name__ == "__main__":
    main()
