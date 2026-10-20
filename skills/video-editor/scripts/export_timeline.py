#!/usr/bin/env python3
"""Export the edit as a DaVinci Resolve timeline: out/<name>.fcpxml and out/<name>.otio.

Tracks (FCPXML lanes in brackets):
  V1 [spine]  source clips, 1 per EDL range, so every cut stays editable
  V2 [1]      zoom inserts (delete one to remove that zoom)
  V3+ [2+]    overlays, ProRes 4444 with straight alpha
  A1          source audio (linked to V1)
  A2 [-1]     music stem, already ducked under the voice
  A3+ [-2]    sound effects, 1 clip per hit
Markers carry every event id and cue. Import in Resolve with
File > Import > Timeline. Media paths are absolute.

Usage:
  python export_timeline.py <edit.json>
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from fractions import Fraction
from pathlib import Path
from urllib.parse import quote
from xml.sax.saxutils import escape, quoteattr

try:
    import opentimelineio as otio
except ImportError:
    otio = None
    if not os.environ.get("VE_NO_REEXEC") and shutil.which("uv"):
        os.environ["VE_NO_REEXEC"] = "1"
        os.execvp("uv", ["uv", "run", "--quiet", "--with", "opentimelineio", "python", __file__, *sys.argv[1:]])

sys.path.insert(0, str(Path(__file__).parent))
from build_edit import Ctx, probe  # noqa: E402

if len(sys.argv) != 2 or sys.argv[1] in ("-h", "--help"):
    sys.exit(__doc__)


def lanes_for(items: list[tuple[int, int]]) -> list[int]:
    """Greedy lane per (start, length) so nothing overlaps within a lane."""
    ends: list[int] = []
    out = []
    for start, length in items:
        for k, end in enumerate(ends):
            if start >= end:
                ends[k] = start + length
                out.append(k)
                break
        else:
            ends.append(start + length)
            out.append(len(ends) - 1)
    return out


def build_model(ctx: Ctx) -> dict:
    fps = ctx.fps
    spine = []
    if ctx.edl:
        rec = 0
        for item in ctx.edl["ranges"]:
            src = Path(ctx.edl["sources"][item["source"]])
            frames = max(1, round((float(item["end"]) - float(item["start"])) * fps))
            spine.append({"path": src, "src_in": round(float(item["start"]) * fps), "rec": rec, "len": frames})
            rec += frames
    else:
        spine.append({"path": ctx.base, "src_in": 0, "rec": 0, "len": ctx.frames(ctx.duration)})

    video = []
    for z in ctx.zooms:
        video.append({"path": ctx.work / "zooms" / f"{z['id']}.mov", "rec": ctx.frames(z["at"]),
                      "len": ctx.frames(z["dur"]), "name": z["id"], "lane": 1})
    overlays = [(ctx.frames(o["at"]), ctx.frames(o["dur"])) for o in ctx.overlays]
    for o, lane in zip(ctx.overlays, lanes_for(overlays)):
        video.append({"path": ctx.work / "overlays" / f"{o['id']}.mov", "rec": ctx.frames(o["at"]),
                      "len": ctx.frames(o["dur"]), "name": f"{o['id']} {o['template']}", "lane": 2 + lane})

    audio = []
    if ctx.edit.get("music"):
        audio.append({"path": ctx.work / "music_stem.wav", "rec": 0, "len": ctx.frames(ctx.duration),
                      "name": "music (ducked)", "lane": -1, "role": "music"})
    hits_file = ctx.work / "sfx_hits.json"
    hits = json.loads(hits_file.read_text()) if hits_file.exists() else []
    placed = []
    for h in hits:
        length = max(1, int(probe(Path(h["file"]))["duration"] * fps))
        placed.append((ctx.frames(h["t"]), length, h))
    for (rec, length, h), lane in zip(placed, lanes_for([(r, n) for r, n, _ in placed])):
        audio.append({"path": Path(h["file"]), "rec": rec, "len": length, "name": Path(h["file"]).stem,
                      "lane": -2 - lane, "role": "effects", "gain_db": h["gain_db"]})

    markers = [{"rec": ctx.frames(e["at"]), "name": f"{e['id']} {e.get('template', 'Zoom')}",
                "note": e.get("cue", "")} for e in ctx.events()]
    return {"spine": spine, "video": video, "audio": audio, "markers": markers}


# ---------------------------------------------------------------- FCPXML

def write_fcpxml(ctx: Ctx, model: dict, path: Path) -> None:
    fps = ctx.fps
    fd = Fraction(fps.denominator, fps.numerator)

    def rt(frames: int) -> str:
        v = frames * fd
        return f"{v.numerator}s" if v.denominator == 1 else f"{v.numerator}/{v.denominator}s"

    formats: dict[tuple, str] = {}
    assets: dict[str, dict] = {}
    res: list[str] = []

    def fmt(w: int, h: int) -> str:
        key = (w, h)
        if key not in formats:
            formats[key] = f"r{len(formats) + 1}"
            res.append(f'<format id="{formats[key]}" frameDuration="{rt(1)}" width="{w}" height="{h}" '
                       f'colorSpace="1-1-1 (Rec. 709)"/>')
        return formats[key]

    seq_fmt = fmt(ctx.w, ctx.h)

    def asset(p: Path) -> str:
        key = str(p)
        if key in assets:
            return assets[key]["id"]
        info = probe(p)
        aid = f"a{len(assets) + 1}"
        frames = int(info["duration"] * fps)
        attrs = [f'id="{aid}"', f"name={quoteattr(p.stem)}", 'start="0s"', f'duration="{rt(frames)}"']
        if "width" in info:
            attrs += ['hasVideo="1"', f'format="{fmt(info["width"], info["height"])}"']
        if info["audio"]:
            attrs += ['hasAudio="1"', 'audioSources="1"', 'audioChannels="2"', 'audioRate="48000"']
        url = "file://" + quote(str(p.resolve()))
        res.append(f'<asset {" ".join(attrs)}><media-rep kind="original-media" src={quoteattr(url)}/></asset>')
        assets[key] = {"id": aid}
        return aid

    def parent_of(rec: int) -> int:
        for k, c in enumerate(model["spine"]):
            if c["rec"] <= rec < c["rec"] + c["len"]:
                return k
        return len(model["spine"]) - 1

    children: dict[int, list[str]] = {k: [] for k in range(len(model["spine"]))}
    for m in model["markers"]:
        k = parent_of(m["rec"])
        c = model["spine"][k]
        local = c["src_in"] + m["rec"] - c["rec"]
        children[k].append(f'<marker start="{rt(local)}" duration="{rt(1)}" value={quoteattr(m["name"])} '
                           f'note={quoteattr(m["note"])}/>')
    for item in model["video"] + model["audio"]:
        k = parent_of(item["rec"])
        c = model["spine"][k]
        local = c["src_in"] + item["rec"] - c["rec"]
        aid = asset(item["path"])
        role = f' audioRole="{item["role"]}"' if item.get("role") else ""
        vol = f'<adjust-volume amount="{item["gain_db"]:+.1f}dB"/>' if "gain_db" in item else ""
        children[k].append(f'<asset-clip ref="{aid}" lane="{item["lane"]}" offset="{rt(local)}" '
                           f'name={quoteattr(item["name"])} start="0s" duration="{rt(item["len"])}"{role}>{vol}</asset-clip>')

    spine_xml = []
    for k, c in enumerate(model["spine"]):
        aid = asset(c["path"])
        spine_xml.append(
            f'<asset-clip ref="{aid}" offset="{rt(c["rec"])}" name={quoteattr(c["path"].stem)} start="{rt(c["src_in"])}" '
            f'duration="{rt(c["len"])}" tcFormat="NDF" audioRole="dialogue">' + "".join(children[k]) + "</asset-clip>"
        )
    total = model["spine"][-1]["rec"] + model["spine"][-1]["len"]
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE fcpxml>\n<fcpxml version="1.9">\n'
        "<resources>\n" + "\n".join(res) + "\n</resources>\n"
        f'<library><event name={quoteattr(ctx.name)}><project name={quoteattr(ctx.name)}>'
        f'<sequence format="{seq_fmt}" duration="{rt(total)}" tcStart="0s" tcFormat="NDF" audioLayout="stereo" audioRate="48k">'
        "<spine>\n" + "\n".join(spine_xml) + "\n</spine></sequence></project></event></library>\n</fcpxml>\n"
    )
    path.write_text(xml)


# ---------------------------------------------------------------- OTIO

def write_otio(ctx: Ctx, model: dict, path: Path) -> None:
    rate = float(ctx.fps)
    RT, TR = otio.opentime.RationalTime, otio.opentime.TimeRange

    def ref(p: Path) -> "otio.schema.ExternalReference":
        frames = int(probe(p)["duration"] * rate)
        return otio.schema.ExternalReference(target_url="file://" + quote(str(p.resolve())),
                                             available_range=TR(RT(0, rate), RT(frames, rate)))

    def track(name: str, kind, items: list[dict], src_key: str | None = None):
        tr = otio.schema.Track(name=name, kind=kind)
        cursor = 0
        for it in sorted(items, key=lambda i: i["rec"]):
            if it["rec"] > cursor:
                tr.append(otio.schema.Gap(source_range=TR(RT(0, rate), RT(it["rec"] - cursor, rate))))
            start = it.get(src_key, 0) if src_key else 0
            tr.append(otio.schema.Clip(name=it.get("name", it["path"].stem), media_reference=ref(it["path"]),
                                       source_range=TR(RT(start, rate), RT(it["len"], rate))))
            cursor = it["rec"] + it["len"]
        return tr

    tl = otio.schema.Timeline(name=ctx.name, global_start_time=RT(0, rate))
    v1 = track("V1 cut", otio.schema.TrackKind.Video, model["spine"], "src_in")
    for m in model["markers"]:
        v1.markers.append(otio.schema.Marker(name=m["name"], marked_range=TR(RT(m["rec"], rate), RT(1, rate)),
                                             metadata={"note": m["note"]}))
    tl.tracks.append(v1)
    for lane in sorted({v["lane"] for v in model["video"]}):
        label = "V2 zooms" if lane == 1 else f"V{lane + 1} overlays"
        tl.tracks.append(track(label, otio.schema.TrackKind.Video, [v for v in model["video"] if v["lane"] == lane]))
    tl.tracks.append(track("A1 voice", otio.schema.TrackKind.Audio, model["spine"], "src_in"))
    for lane in sorted({a["lane"] for a in model["audio"]}, reverse=True):
        label = "A2 music" if lane == -1 else f"A{1 - lane} sfx"
        tl.tracks.append(track(label, otio.schema.TrackKind.Audio, [a for a in model["audio"] if a["lane"] == lane]))
    otio.adapters.write_to_file(tl, str(path))


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    ctx = Ctx(Path(sys.argv[1]).expanduser())
    model = build_model(ctx)
    ctx.out.mkdir(parents=True, exist_ok=True)
    fcpxml = ctx.out / f"{ctx.name}.fcpxml"
    write_fcpxml(ctx, model, fcpxml)
    print(f"export: {fcpxml}")
    if otio:
        path = ctx.out / f"{ctx.name}.otio"
        write_otio(ctx, model, path)
        print(f"export: {path}")
    else:
        print("export: opentimelineio unavailable, skipped .otio")


if __name__ == "__main__":
    main()
