#!/usr/bin/env python3
"""Build a finished edit from edit.json.

Stages (run all by default, or name them):
  check    validate the plan against the style rules (no rendering)
  stills   fully built frame of every overlay over the cut, for design review
  assets   render changed overlays and zoom inserts (Remotion kit)
  audio    voice clean-up, music bed with ducking, SFX, two-pass loudness
  master   composite the finished MP4
  export   Resolve timeline (.fcpxml and .otio) via export_timeline.py
  qa       decode, loudness, black frames, 1 frame per event, contact sheets

Usage:
  python build_edit.py <edit.json> [stage ...]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
KIT = SKILL / "overlays"  # the Remotion overlay kit bundled with this skill
SFX_DIR = KIT / "public" / "sfx"  # your own licensed sound effects, see its README

TEMPLATES = {
    "Lower": {"req": ["title"], "dur": (2.5, 6.0), "anchor": "bottom-right", "size": (0.36, 0.16)},
    "Stat": {"req": ["value", "label"], "dur": (3.0, 6.0), "anchor": "top-right", "size": (0.27, 0.36)},
    "Keyword": {"req": ["text"], "dur": (1.5, 4.0), "anchor": "top-center", "size": (0.6, 0.15)},
    "List": {"req": ["items"], "dur": (3.0, 18.0), "anchor": "right", "size": (0.31, 0.46)},
    "Chapter": {"req": ["title"], "dur": (2.0, 4.0), "anchor": "top-left", "size": (0.46, 0.17)},
    "Media": {"req": ["src"], "dur": (3.0, 9.0), "anchor": "right", "size": (0.47, 0.8)},
    "Focus": {"req": ["rect"], "dur": (1.5, 6.0), "anchor": None, "size": None},
    "Captions": {"req": [], "dur": (1.0, 600.0), "anchor": None, "size": None},
    "Interlude": {"req": [], "dur": (0.8, 6.0), "anchor": None, "size": None},
}
MX, MY = 76 / 1920, 76 / 1080  # safe margin, 4% of the frame


# ---------------------------------------------------------------- helpers

def run(args: list[str], capture: bool = False, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(args, check=True, text=True, capture_output=capture, cwd=cwd)


def probe(path: Path) -> dict:
    out = run(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=codec_type,width,height,avg_frame_rate:format=duration", "-of", "json", str(path)],
        capture=True,
    ).stdout
    data = json.loads(out)
    video = next((s for s in data["streams"] if s["codec_type"] == "video"), None)
    info = {"duration": float(data["format"]["duration"]),
            "audio": any(s["codec_type"] == "audio" for s in data["streams"])}
    if video:
        info.update(width=int(video["width"]), height=int(video["height"]), fps=Fraction(video["avg_frame_rate"]))
    return info


class Ctx:
    def __init__(self, edit_path: Path):
        self.edit_path = edit_path.resolve()
        self.edit = json.loads(self.edit_path.read_text())
        self.project = Path(self.edit.get("project") or self.edit_path.parent).expanduser()
        self.base = self.path(self.edit["base"])
        # `"edl": null` makes the base itself the only V1 clip (e.g. a graded or upscaled cut).
        edl = self.edit.get("edl", "edl.json")
        self.edl_path = self.path(edl) if edl else None
        self.edl = json.loads(self.edl_path.read_text()) if self.edl_path and self.edl_path.exists() else None
        info = probe(self.base)
        self.w, self.h, self.fps, self.duration = info["width"], info["height"], info["fps"], info["duration"]
        self.work = self.project / "work"
        self.qa = self.project / "qa"
        self.out = self.project / "out"
        self.name = self.edit.get("output", {}).get("name", self.project.name)
        words = self.project / "words_out.json"
        self.words = json.loads(words.read_text()) if words.exists() else []
        self.overlays = sorted(self.edit.get("overlays", []), key=lambda o: o["at"])
        self.zooms = sorted(self.edit.get("zooms", []), key=lambda z: z["at"])
        self.cam = (self.edit.get("layout") or {}).get("cam")

    def path(self, p: str) -> Path:
        q = Path(p).expanduser()
        return q if q.is_absolute() else self.project / q

    def frames(self, seconds: float) -> int:
        return round(seconds * self.fps)

    def secs(self, frames: int) -> float:
        return float(frames / self.fps)

    def events(self) -> list[dict]:
        return sorted(
            [dict(o, kind="overlay") for o in self.overlays] + [dict(z, kind="zoom", template="Zoom") for z in self.zooms],
            key=lambda e: e["at"],
        )


def anchor_box(template: str, props: dict) -> tuple[float, float, float, float] | None:
    spec = TEMPLATES[template]
    if template == "Focus":
        x, y, w, h = props["rect"]
        side = props.get("labelSide", "bottom")
        label_h = 0.07 if props.get("label") else 0
        return (x, y - (label_h + 0.02 if side == "top" else 0), w, h + label_h + 0.02)
    w, h = spec["size"]
    if template == "Media" and props.get("width"):
        w = props["width"] / 1920
    anchor = props.get("anchor") or spec["anchor"]
    x = MX if "left" in anchor else 1 - MX - w if "right" in anchor else (1 - w) / 2
    y = MY if anchor.startswith("top") else 1 - MY - h if anchor.startswith("bottom") else (1 - h) / 2
    ox, oy = props.get("offset", [0, 0])
    return (x + ox / 1920, y + oy / 1080, w, h)


def zoom_view(scale: float, focus: list[float]) -> tuple[float, float, float, float]:
    """Visible region of a zoom that scales around `focus`, as x, y, w, h fractions."""
    fx, fy = focus
    return (fx - fx / scale, fy - fy / scale, 1 / scale, 1 / scale)


def overlap(a, b) -> float:
    dx = min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])
    dy = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
    return max(0.0, dx) * max(0.0, dy)


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def sfx_path(name: str) -> Path:
    p = Path(name).expanduser()
    return p if p.is_absolute() else SFX_DIR / (name if name.endswith(".mp3") else f"{name}.mp3")


# ---------------------------------------------------------------- check

def check(ctx: Ctx) -> bool:
    errors: list[str] = []
    warnings: list[str] = []
    ids = [e["id"] for e in ctx.events()]
    if len(ids) != len(set(ids)):
        errors.append("event ids must be unique")

    for o in ctx.overlays:
        if o.get("draft"):
            errors.append(f"{o['id']}: drafted by the planner, not reviewed yet (write the title, then remove \"draft\")")
    for e in ctx.events():
        eid, at, dur = e["id"], float(e["at"]), float(e["dur"])
        if at < 0 or at + dur > ctx.duration + 0.01:
            errors.append(f"{eid}: {at:.2f}+{dur:.2f}s runs outside the cut ({ctx.duration:.2f}s)")
        # Cue: the spoken words the event hangs on must be near `at`.
        cue = e.get("cue")
        if not cue:
            errors.append(f"{eid}: needs a `cue`, the spoken words it is anchored to")
        elif ctx.words:
            window = " ".join(w["w"] for w in ctx.words if at - 2.0 <= w["s"] <= at + 2.5)
            if norm(cue) not in norm(window):
                warnings.append(f"{eid}: cue '{cue}' is not spoken within 2 s of at={at:.2f}")
        if e.get("sfx") and not sfx_path(e["sfx"]).exists():
            errors.append(f"{eid}: sfx not found {sfx_path(e['sfx'])}")

        if e["kind"] == "zoom":
            if not 1.05 <= float(e.get("scale", 0)) <= 2.5:
                errors.append(f"{eid}: zoom scale must be 1.05 to 2.5")
            if dur < 1.2:
                warnings.append(f"{eid}: zoom shorter than 1.2 s reads as a glitch")
            if ctx.cam:
                view = zoom_view(float(e["scale"]), e.get("focus", [0.5, 0.5]))
                seen = overlap(view, ctx.cam) / (ctx.cam[2] * ctx.cam[3])
                if 0.02 < seen < 0.98:
                    errors.append(f"{eid}: zoom slices the camera ({seen:.0%} visible); keep it fully in or fully out")
            continue

        template = e.get("template")
        if template in ("Captions", "Interlude"):
            continue
        if template not in TEMPLATES:
            errors.append(f"{eid}: unknown template {template}; menu is {', '.join(TEMPLATES)}")
            continue
        props = e.get("props", {})
        for key in TEMPLATES[template]["req"]:
            if key not in props:
                errors.append(f"{eid}: {template} needs props.{key}")
        lo, hi = TEMPLATES[template]["dur"]
        if not lo <= dur <= hi:
            warnings.append(f"{eid}: {template} for {dur:.1f}s, the rule is {lo} to {hi}s")
        if template == "Media":
            src = ctx.path(props.get("src", ""))
            if not src.exists():
                errors.append(f"{eid}: Media src not found {src}")
        if template == "List":
            for item in props.get("items", []):
                if item.get("at") is not None and item["at"] > dur - 0.8:
                    errors.append(f"{eid}: list item '{item['text']}' starts after the card has almost gone")
        if template == "Stat" and ctx.words:
            digits = re.sub(r"[^0-9]", "", props.get("value", ""))[:2]
            near = " ".join(w["w"] for w in ctx.words if at - 20 <= w["s"] <= at + 20)
            if digits and digits not in re.sub(r"[^0-9 ]", "", near) and not e.get("source"):
                warnings.append(f"{eid}: {props.get('value')} is not spoken nearby; add `source` (proof.md or on-screen)")
        if all(k in props for k in TEMPLATES[template]["req"]) and ctx.cam:
            box = anchor_box(template, props)
            if box and overlap(box, ctx.cam) > 0.002:
                errors.append(f"{eid}: {template} at {props.get('anchor') or TEMPLATES[template]['anchor']} covers the camera")

    # Pacing: no stacked cards, breathing room, density by runtime.
    cards = [o for o in ctx.overlays if o.get("template") not in ("Focus", "Captions", "Interlude")]
    for a, b in zip(cards, cards[1:]):
        gap = b["at"] - (a["at"] + a["dur"])
        if gap < 0:
            errors.append(f"{a['id']} and {b['id']} overlap; 1 card on screen at a time")
        elif gap < 1.0:
            warnings.append(f"{a['id']} -> {b['id']}: {gap:.1f}s gap, give the speaker 1 s")
    sfx_times = sorted(e["at"] for e in ctx.events() if e.get("sfx"))
    for a, b in zip(sfx_times, sfx_times[1:]):
        if b - a < 1.5:
            warnings.append(f"2 sound effects within {b - a:.1f}s at {a:.1f}s; keep 1 per visual hit")
    minutes = ctx.duration / 60
    pace = (6, 8) if minutes < 1 else (8, 12) if minutes < 3 else (12, 20) if minutes < 10 else (20, 35) if minutes < 30 else (30, 60)
    expected = (ctx.duration / pace[1], ctx.duration / pace[0])
    count = len([o for o in ctx.overlays if o.get("template") != "Captions"])  # cards; punch-ins keep their own rhythm
    captioned = any(o.get("template") == "Captions" and o.get("props", {}).get("mode", "full") == "full" for o in ctx.overlays)
    if count < expected[0] * 0.6 and not captioned:  # full captions carry the rhythm on their own
        warnings.append(f"{count} cards for {minutes:.1f} min is sparse; rule of thumb {expected[0]:.0f} to {expected[1]:.0f}")
    if count > expected[1] * 1.4:
        warnings.append(f"{count} cards for {minutes:.1f} min is busy; rule of thumb {expected[0]:.0f} to {expected[1]:.0f}")
    biggest_gap = max(
        [b["at"] - (a["at"] + a["dur"]) for a, b in zip(ctx.events(), ctx.events()[1:])] or [0]
    )
    if biggest_gap > 60:
        warnings.append(f"{biggest_gap:.0f}s without any visual change; break the pattern about every 30 s")

    print(f"{ctx.name}: {ctx.w}x{ctx.h} @ {float(ctx.fps):g} fps, {ctx.duration:.1f}s, "
          f"{len(ctx.overlays)} overlays, {len(ctx.zooms)} zooms")
    for w in warnings:
        print(f"  warn  {w}")
    for e in errors:
        print(f"  ERROR {e}")
    print("check: " + ("FAILED" if errors else f"ok ({len(warnings)} warnings)"))
    return not errors


# ---------------------------------------------------------------- assets

def caption_props(ctx: Ctx, o: dict, props: dict) -> dict:
    """Fill caption words from the transcript: relative times, `fixes` applied, `drop` removed.

    `fixes` maps a transcript token to its display form ({"$1,800": "$1'800+"}); `drop`
    lists tokens to leave out (filler, stutters); `mute` ranges (seconds from the
    overlay start) hide captions while a card carries the words. Captions show 70 to
    85% of the words.
    """
    if "words" in props:
        return props
    fixes, drop = props.pop("fixes", {}), set(props.pop("drop", []))
    drop_at = props.pop("drop_at", [])  # cut seconds of single tokens to drop (stutters, false starts)
    # Heroes are planned in cut time like everything else; the template wants overlay time.
    props["heroes"] = [{**h, "start": round(h["start"] - o["at"], 3)} for h in props.get("heroes", [])]
    props["items"] = [{**it, "start": round(it["start"] - o["at"], 3)} for it in props.get("items", [])]
    if props.get("payoff"):
        props["payoff"] = {**props["payoff"], "start": round(props["payoff"]["start"] - o["at"], 3)}
    props["highlight"] = [
        {**h, "start": round(h["start"] - o["at"], 3)} if isinstance(h, dict) else h for h in props.get("highlight", [])
    ]
    props["placements"] = [
        {**p, "start": round(p["start"] - o["at"], 3), "end": round(p["end"] - o["at"], 3)} for p in props.get("placements", [])
    ]
    if o["template"] == "Captions":
        # An Interlude owns the screen: captions step aside for its span.
        props["mute"] = props.get("mute", []) + [
            [round(i["at"] - o["at"], 3), round(i["at"] + i["dur"] - o["at"], 3)]
            for i in ctx.overlays if i.get("template") == "Interlude"
        ]
    mute = props.get("mute", [])
    words = []
    for w in ctx.words:
        muted = any(a <= w["s"] - o["at"] < b for a, b in mute)
        dropped = w["w"] in drop or any(abs(w["s"] - t) < 0.02 for t in drop_at)
        if o["at"] <= w["s"] < o["at"] + o["dur"] and not dropped and not muted:
            words.append({"w": fixes.get(w["w"], w["w"]), "s": round(w["s"] - o["at"], 3), "e": round(w["e"] - o["at"], 3)})
    return {**props, "words": words}


def job_list(ctx: Ctx) -> list[dict]:
    jobs = []
    for o in ctx.overlays:
        props = dict(o.get("props", {}))
        if o["template"] in ("Captions", "Interlude"):
            props = caption_props(ctx, o, props)
        props.setdefault("anchor", TEMPLATES[o["template"]]["anchor"])
        if props["anchor"] is None:
            props.pop("anchor")
        if "src" in props:
            props["src"] = str(ctx.path(props["src"]))
        jobs.append({"id": o["id"], "template": o["template"], "seconds": ctx.secs(ctx.frames(o["dur"])),
                     "props": props, "out": str(ctx.work / "overlays" / f"{o['id']}.mov")})
    for z in ctx.zooms:
        jobs.append({"id": z["id"], "template": "Zoom", "seconds": ctx.secs(ctx.frames(z["dur"])),
                     "props": {"src": str(ctx.work / "zsrc" / f"{z['id']}.mp4"), "scale": z["scale"],
                               "focus": z.get("focus", [0.5, 0.5]), "ease": z.get("ease", 0.35)},
                     "out": str(ctx.work / "zooms" / f"{z['id']}.mov"), "at": z["at"]})
    return jobs


def job_hash(ctx: Ctx, job: dict) -> str:
    stamp = {k: v for k, v in job.items() if k != "out"}
    src = job["props"].get("src")
    if src and Path(src).exists():
        stat = Path(src).stat()
        stamp["src_stat"] = [stat.st_size, int(stat.st_mtime)]
    stamp["kit"] = sorted(
        (str(p.relative_to(KIT)), int(p.stat().st_mtime)) for p in (KIT / "src").rglob("*.tsx")
    )
    stamp["size"] = [ctx.w, ctx.h, str(ctx.fps)]
    return hashlib.sha1(json.dumps(stamp, sort_keys=True).encode()).hexdigest()


def cut_zoom_sources(ctx: Ctx) -> None:
    (ctx.work / "zsrc").mkdir(parents=True, exist_ok=True)
    for z in ctx.zooms:
        out = ctx.work / "zsrc" / f"{z['id']}.mp4"
        start, frames = ctx.secs(ctx.frames(z["at"])), ctx.frames(z["dur"])
        marker = out.with_suffix(".range")
        key = f"{start:.4f}:{frames}:{ctx.base.stat().st_mtime}"
        if out.exists() and marker.exists() and marker.read_text() == key:
            continue
        run(["ffmpeg", "-y", "-v", "error", "-ss", f"{start:.4f}", "-i", str(ctx.base), "-frames:v", str(frames),
             "-an", "-c:v", "libx264", "-crf", "10", "-preset", "fast", "-g", "15", "-pix_fmt", "yuv420p", str(out)])
        marker.write_text(key)


def render_jobs(ctx: Ctx, jobs: list[dict], still: bool = False) -> None:
    if not jobs:
        return
    ctx.work.mkdir(parents=True, exist_ok=True)
    spec = {"width": ctx.w, "height": ctx.h, "fps": float(ctx.fps), "jobs": jobs}
    path = ctx.work / ("stills.json" if still else "jobs.json")
    path.write_text(json.dumps(spec, indent=2) + "\n")
    if not (KIT / "node_modules").exists():
        run(["npm", "install", "--no-audit", "--no-fund"], cwd=KIT)
    run(["node", "scripts/render.mjs", str(path)] + (["--still"] if still else []), cwd=KIT)


def assets(ctx: Ctx) -> None:
    cut_zoom_sources(ctx)
    hashes_path = ctx.work / "render-hashes.json"
    hashes = json.loads(hashes_path.read_text()) if hashes_path.exists() else {}
    todo = []
    for job in job_list(ctx):
        h = job_hash(ctx, job)
        if hashes.get(job["id"]) != h or not Path(job["out"]).exists():
            todo.append(job)
            hashes[job["id"]] = h
    print(f"assets: {len(todo)} to render, {len(job_list(ctx)) - len(todo)} unchanged")
    render_jobs(ctx, [{k: v for k, v in j.items() if k != "at"} for j in todo])
    hashes_path.write_text(json.dumps(hashes, indent=2) + "\n")


def stills(ctx: Ctx) -> None:
    """Fully built frame of each overlay over the cut at that moment, before any video render."""
    jobs = [j for j in job_list(ctx) if j["template"] != "Zoom"]
    for j in jobs:
        j["out"] = str(ctx.qa / "stills" / (j["id"] + ".mov"))
    render_jobs(ctx, jobs, still=True)
    frames = []
    for o in ctx.overlays:
        png = ctx.qa / "stills" / f"{o['id']}.png"
        t = ctx.secs(ctx.frames(o["at"]) + ctx.frames(o["dur"]) - 12)
        out = ctx.qa / "stills" / f"{o['id']}.jpg"
        run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.3f}", "-i", str(ctx.base), "-i", str(png),
             "-filter_complex", "[0:v][1:v]overlay=format=auto", "-frames:v", "1", "-q:v", "3", str(out)])
        frames.append((out, f"{o['id']} {o['template']} @{o['at']:.1f}s"))
    sheets(frames, ctx.qa / "stills", "stills")


# ---------------------------------------------------------------- audio

def measure(src: Path) -> dict:
    """Integrated loudness and true peak of a file (analysis only, nothing is changed)."""
    txt = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(src), "-af", "loudnorm=print_format=json", "-f", "null", "-"],
        text=True, capture_output=True, check=True).stderr
    return json.loads(txt[txt.rindex("{"):txt.rindex("}") + 1])


def level(src: Path, dst: Path, target: dict) -> dict:
    """Constant gain to the loudness target, then a limiter that only touches peaks.

    Not dynamic loudnorm: it rides the gain per frame and audibly pumps on speech,
    and its linear mode silently turns dynamic when the peak
    would pass the ceiling. 1 multiplier keeps the tone; the limiter catches the few
    peaks that end up above the ceiling.
    """
    i, tp = target.get("i", -14), target.get("tp", -1.5)
    m = measure(src)
    gain = i - float(m["input_i"])
    ceiling = 10 ** ((tp - 0.5) / 20)  # headroom for AAC inter-sample peaks
    run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-af",
         f"volume={gain:.2f}dB,alimiter=limit={ceiling:.4f}:attack=1:release=60:level=false",
         "-ar", "48000", "-c:a", "pcm_s24le", str(dst)])
    return m


def audio(ctx: Ctx) -> None:
    ctx.work.mkdir(parents=True, exist_ok=True)
    dur = f"{ctx.duration:.3f}"
    voice = ctx.work / "voice.wav"
    clean = (ctx.edit.get("voice") or {}).get("clean", True)
    # HyperFrames voice order: rumble and mud first, then presence, then level. Limiter is the final loudnorm.
    chain = ("highpass=f=80,equalizer=f=250:t=q:w=1.2:g=-3,equalizer=f=3000:t=q:w=1:g=2.5,"
             "acompressor=threshold=-20dB:ratio=3:attack=5:release=120:makeup=2") if clean else "anull"
    pre = ctx.work / "voice_pre.wav"
    run(["ffmpeg", "-y", "-v", "error", "-i", str(ctx.base), "-vn", "-af", chain,
         "-ar", "48000", "-ac", "2", "-c:a", "pcm_s24le", str(pre)])
    # Level the voice to -16 LUFS with 1 constant gain before the mix, so the music bed's gain means the same on every recording.
    level(pre, voice, {"i": -16, "tp": -1.0})

    music = ctx.edit.get("music")
    music_stem = ctx.work / "music_stem.wav"
    if music and music.get("sections"):
        src = ctx.path(music["file"])
        fade = float(music.get("fade", 1.5))
        gain = float(music.get("gain_db", -16))
        inputs, parts, labels = [], [], []
        for n, (s, e) in enumerate(music["sections"]):
            length = float(e) - float(s)
            inputs += ["-stream_loop", "-1", "-i", str(src)]
            delay = int(float(s) * 1000)
            parts.append(
                f"[{n}:a]aformat=sample_rates=48000:channel_layouts=stereo,loudnorm=I=-14:TP=-2,"
                f"atrim=0:{length:.3f},asetpts=PTS-STARTPTS,afade=t=in:d={min(fade, length / 3):.2f},"
                f"afade=t=out:st={length - min(fade, length / 3):.3f}:d={min(fade, length / 3):.2f},"
                f"adelay={delay}|{delay}[m{n}]"
            )
            labels.append(f"[m{n}]")
        k = len(music["sections"])
        inputs += ["-i", str(voice)]
        # Carve room for the voice (1 to 2.5 kHz), set the bed, then duck under speech.
        parts.append(
            f"{''.join(labels)}amix=inputs={k}:normalize=0,apad=whole_dur={dur},atrim=0:{dur},"
            f"equalizer=f=1000:t=q:w=2:g=-4,equalizer=f=1600:t=q:w=2:g=-6,equalizer=f=2500:t=q:w=2:g=-4,"
            f"volume={gain}dB[bed]"
        )
        parts.append(f"[bed][{k}:a]sidechaincompress=threshold=0.03:ratio=8:attack=200:release=400[out]")
        run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(parts), "-map", "[out]",
             "-t", dur, "-ar", "48000", "-c:a", "pcm_s24le", str(music_stem)])
    else:
        run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", dur,
             "-c:a", "pcm_s24le", str(music_stem)])

    sfx_stem = ctx.work / "sfx_stem.wav"
    hits = []
    for e in ctx.events():
        if not e.get("sfx"):
            continue
        t = ctx.secs(ctx.frames(e["at"])) + float(e.get("sfx_offset", 0))
        if e.get("sfx_at") == "out":
            t = ctx.secs(ctx.frames(e["at"]) + ctx.frames(e["dur"])) - 0.3
        hits.append((max(0.0, t), sfx_path(e["sfx"]), float(e.get("sfx_gain_db", -9))))
    if hits:
        inputs, parts = [], []
        for n, (t, path, gain) in enumerate(hits):
            inputs += ["-i", str(path)]
            d = int(t * 1000)
            parts.append(f"[{n}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={gain}dB,adelay={d}|{d}[s{n}]")
        parts.append(f"{''.join(f'[s{n}]' for n in range(len(hits)))}amix=inputs={len(hits)}:normalize=0,"
                     f"apad=whole_dur={dur},atrim=0:{dur}[out]")
        run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(parts), "-map", "[out]",
             "-ar", "48000", "-c:a", "pcm_s24le", str(sfx_stem)])
    else:
        run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", dur,
             "-c:a", "pcm_s24le", str(sfx_stem)])
    (ctx.work / "sfx_hits.json").write_text(
        json.dumps([{"t": round(t, 3), "file": str(p), "gain_db": g} for t, p, g in hits], indent=2) + "\n"
    )

    raw = ctx.work / "mix_raw.wav"
    run(["ffmpeg", "-y", "-v", "error", "-i", str(voice), "-i", str(music_stem), "-i", str(sfx_stem),
         "-filter_complex", "[0:a][1:a][2:a]amix=inputs=3:normalize=0[a]", "-map", "[a]",
         "-c:a", "pcm_s24le", str(raw)])
    m = level(raw, ctx.work / "mix.wav", ctx.edit.get("loudness", {}))
    print(f"audio: mix measured {m['input_i']} LUFS, normalised to {ctx.edit.get('loudness', {}).get('i', -14)}; "
          f"{len(hits)} sound effects; music {'on' if music else 'off'}")


# ---------------------------------------------------------------- master

def master(ctx: Ctx) -> Path:
    ctx.out.mkdir(parents=True, exist_ok=True)
    inputs = ["-i", str(ctx.base)]
    parts, cur, n = [], "0:v", 1
    fps = ctx.fps
    layers = [(z, ctx.work / "zooms" / f"{z['id']}.mov") for z in ctx.zooms] + \
             [(o, ctx.work / "overlays" / f"{o['id']}.mov") for o in ctx.overlays]
    for i, (e, path) in enumerate(layers):
        if not path.exists():
            sys.exit(f"missing {path}; run the assets stage")
        inputs += ["-i", str(path)]
        start = ctx.frames(e["at"])
        parts.append(f"[{n}:v]setpts=PTS-STARTPTS+({start}*{fps.denominator}/{fps.numerator})/TB[l{i}]")
        parts.append(f"[{cur}][l{i}]overlay=format=auto:eof_action=pass:repeatlast=0[v{i}]")
        cur, n = f"v{i}", n + 1
    parts.append(f"[{cur}]format=yuv420p[vout]")
    inputs += ["-i", str(ctx.work / "mix.wav")]
    out = ctx.out / f"{ctx.name}.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-stats", *inputs, "-filter_complex", ";".join(parts),
         "-map", "[vout]", "-map", f"{n}:a", "-t", f"{ctx.duration:.3f}",
         "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-profile:v", "high", "-pix_fmt", "yuv420p",
         "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
         "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-movflags", "+faststart", str(out)])
    print(f"master: {out}")
    return out


# ---------------------------------------------------------------- qa

def sheets(frames: list[tuple[Path, str]], folder: Path, prefix: str, per: int = 6) -> None:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("qa: Pillow missing, frames written without contact sheets")
        return
    font = None
    for f in ["/System/Library/Fonts/SFNS.ttf", "/System/Library/Fonts/Helvetica.ttc"]:
        try:
            font = ImageFont.truetype(f, 22)
            break
        except OSError:
            continue
    portrait = frames and Image.open(frames[0][0]).height > Image.open(frames[0][0]).width
    tw, th, cols = (432, 768, 4) if portrait else (960, 540, 2)
    per = 8 if portrait else per
    for s in range(0, len(frames), per):
        chunk = frames[s:s + per]
        tiles = []
        for path, label in chunk:
            im = Image.open(path).convert("RGB").resize((tw, th))
            d = ImageDraw.Draw(im)
            d.rectangle([0, 0, tw, 34], fill=(28, 32, 38))
            d.text((12, 5), label, fill=(254, 254, 252), font=font)
            tiles.append(im)
        rows = (len(tiles) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * tw, rows * th), (252, 251, 248))
        for k, im in enumerate(tiles):
            sheet.paste(im, ((k % cols) * tw, (k // cols) * th))
        out = folder / f"{prefix}-sheet-{s // per + 1:02d}.jpg"
        sheet.save(out, quality=88)
        print(f"sheet {out}")


def qa(ctx: Ctx) -> None:
    final = ctx.out / f"{ctx.name}.mp4"
    frames_dir = ctx.qa / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    report = [f"# QA {ctx.name}", ""]
    decode = subprocess.run(["ffmpeg", "-v", "error", "-i", str(final), "-f", "null", "-"],
                            text=True, capture_output=True)
    report.append(f"- decode errors: {len(decode.stderr.strip().splitlines())}")
    info = probe(final)
    report.append(f"- duration {info['duration']:.2f}s vs cut {ctx.duration:.2f}s, {info['width']}x{info['height']}")
    ebu = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(final), "-af", "ebur128=peak=true",
                          "-f", "null", "-"], text=True, capture_output=True).stderr
    li = re.findall(r"I:\s+(-?[\d.]+) LUFS", ebu)
    tp = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", ebu)
    report.append(f"- loudness {li[-1] if li else '?'} LUFS integrated, true peak {tp[-1] if tp else '?'} dBFS")
    black = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(final), "-vf",
                            "blackdetect=d=0.10:pix_th=0.05", "-an", "-f", "null", "-"],
                           text=True, capture_output=True).stderr
    report.append(f"- black segments: {black.count('black_start')}")
    target = ctx.edit.get("loudness", {})
    ok = (li and abs(float(li[-1]) - target.get("i", -14)) <= 1.0 and tp and float(tp[-1]) <= target.get("tp", -1.5)
          and not decode.stderr.strip() and abs(info["duration"] - ctx.duration) < 0.1 and "black_start" not in black)
    report.insert(2, f"- automatic checks: {'PASS' if ok else 'FAIL'}")
    frames = []
    for e in ctx.events():
        t = e["at"] + min(e["dur"] * 0.6, e["dur"] - 0.45)
        if e.get("template") == "List":
            t = e["at"] + e["dur"] - 0.5
        out = frames_dir / f"{e['id']}.jpg"
        run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.3f}", "-i", str(final), "-frames:v", "1",
             "-vf", "scale='if(gt(iw,ih),960,432)':-2", "-q:v", "3", str(out)])
        label = e.get("props", {}).get("title") or e.get("props", {}).get("text") or e.get("props", {}).get("value") or ""
        frames.append((out, f"{e['id']} {e['template']} @{e['at']:.1f}s {label}"[:70]))
    sheets(frames, ctx.qa, "master")
    titles = [o for o in ctx.overlays if o.get("props", {}).get("graphic") == "title"]
    if titles:
        stamp = lambda t: f"{int(t // 60):02d}:{int(t % 60):02d}"  # noqa: E731
        lines = [] if titles[0]["at"] < 1 else ["00:00 Intro"]
        lines += [f"{stamp(o['at'])} {o['props'].get('title', '')}" for o in titles]
        (ctx.out / "chapters.txt").write_text("\n".join(lines) + "\n")
        report.append(f"- chapters: {len(lines)} written to out/chapters.txt")
    report += ["", "Review every sheet: overlay legible, nothing on the face, the frame matches the words, "
               "no 2 cards at once, zoom lands on the thing being shown."]
    (ctx.qa / "report.md").write_text("\n".join(report) + "\n")
    print("\n".join(report))


# ---------------------------------------------------------------- main

STAGES = ["check", "stills", "assets", "audio", "master", "export", "qa"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("edit", type=Path)
    parser.add_argument("stages", nargs="*", help=f"any of {', '.join(STAGES)}; default all but stills")
    args = parser.parse_args()
    ctx = Ctx(args.edit.expanduser())
    stages = args.stages or [s for s in STAGES if s != "stills"]
    for stage in stages:
        if stage not in STAGES:
            sys.exit(f"unknown stage {stage}")
    if not check(ctx):
        sys.exit(1)
    for stage in stages:
        if stage == "check":
            continue
        if stage == "export":
            run([sys.executable, str(Path(__file__).with_name("export_timeline.py")), str(ctx.edit_path)])
        else:
            globals()[stage](ctx)


if __name__ == "__main__":
    main()
