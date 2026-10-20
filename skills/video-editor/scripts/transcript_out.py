#!/usr/bin/env python3
"""Map word timings from a transcript through a cut EDL onto the output timeline.

Writes, next to edl.json:
  words_out.json      [{"w", "s", "e"}] in output seconds, used for cue checks
  transcript_out.md   phrases with output-time ranges, the planning artifact

Usage:
  python transcript_out.py <project-dir> [--silence 0.5]
Transcripts are read from <project-dir>/transcripts/<source stem>.json:
{"words": [{"text": "...", "start": 0.0, "end": 0.3, "type": "word"}, ...]}
(ElevenLabs Scribe JSON has this shape; convert other word-timed output to it).
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path


def edl_offsets(edl: dict) -> list[tuple[dict, float]]:
    """Output start of every EDL range, rounded to frames like render_cut.py."""
    fps = float(Fraction(edl["settings"]["fps"]))
    cursor = 0.0
    placed = []
    for item in edl["ranges"]:
        frames = max(1, round((float(item["end"]) - float(item["start"])) * fps))
        placed.append((item, cursor))
        cursor += frames / fps
    return placed


def map_words(project: Path, edl: dict) -> list[dict]:
    cache: dict[str, list[dict]] = {}
    out: list[dict] = []
    for item, offset in edl_offsets(edl):
        source_path = Path(edl["sources"][item["source"]])
        if item["source"] not in cache:
            transcript = project / "transcripts" / f"{source_path.stem}.json"
            if not transcript.exists():
                sys.exit(f"missing transcript {transcript}; transcribe the source with word timings first")
            cache[item["source"]] = [
                w for w in json.loads(transcript.read_text())["words"] if w.get("type", "word") == "word"
            ]
        start, end = float(item["start"]), float(item["end"])
        for w in cache[item["source"]]:
            if start <= float(w["start"]) < end:
                s = offset + float(w["start"]) - start
                e = offset + min(float(w["end"]), end) - start
                out.append({"w": w["text"].strip(), "s": round(s, 3), "e": round(e, 3)})
    return out


def phrases(words: list[dict], silence: float) -> list[tuple[float, float, str]]:
    groups: list[list[dict]] = []
    for w in words:
        if groups and w["s"] - groups[-1][-1]["e"] < silence:
            groups[-1].append(w)
        else:
            groups.append([w])
    return [(g[0]["s"], g[-1]["e"], " ".join(x["w"] for x in g)) for g in groups]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("project", type=Path)
    parser.add_argument("--silence", type=float, default=0.5)
    args = parser.parse_args()
    project = args.project.expanduser().resolve()
    edl = json.loads((project / "edl.json").read_text())
    words = map_words(project, edl)
    (project / "words_out.json").write_text(json.dumps(words) + "\n")
    lines = [
        "# Output-timeline transcript",
        "",
        "Times are seconds on the finished cut. Use them for `at` in edit.json.",
        "",
    ]
    for s, e, text in phrases(words, args.silence):
        lines.append(f"[{s:07.2f}-{e:07.2f}] {text}")
    (project / "transcript_out.md").write_text("\n".join(lines) + "\n")
    print(f"{len(words)} words -> {project / 'transcript_out.md'}")


if __name__ == "__main__":
    main()
