#!/usr/bin/env python3
"""A gentle voice chain for a quiet mic in a room, cut to an EDL.

Made for a recording that is very quiet (around -40 LUFS) with an audible room
floor. What worked, and what did not, when it was picked by ear:

- Blind denoising (afftdn tn=1) invents a burbling, artificial texture. Rejected.
- Dynamic loudnorm rides the gain per frame and pumps. Rejected.
- Chosen: high-pass 60 Hz, 1 constant gain that lands the true peak at -1.5 dBTP,
  then afftdn with a noise profile LEARNED from the longest silence in this very
  take (nr=12). It runs on the full take BEFORE the trims, because the silence it
  samples is exactly what the cut throws away.

Usage:
  python voice_print.py <raw take> <edl.json> <out.wav> [--nr 12]
Then swap it into the cut: ffmpeg -i base.mp4 -i out.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k base-voice.mp4
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path

import numpy as np

FADE = 0.03
TARGET_TP = -1.5


def find_silence(src: Path, min_len: float = 0.8) -> tuple[float, float]:
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(src), "-af", f"silencedetect=noise=-55dB:d={min_len}",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    starts = [float(m) for m in re.findall(r"silence_start: ([\d.]+)", err)]
    ends = [float(m) for m in re.findall(r"silence_end: ([\d.]+)", err)]
    best, blen = None, 0.0
    for s0, e0 in zip(starts, ends):
        a, b = s0 + 0.15, e0 - 0.15  # stay clear of word tails and breaths
        if b - a > blen:
            best, blen = (a, b), b - a
    if not best:
        raise SystemExit(f"no silence of {min_len}s to learn a noise print from in {src.name}")
    return best


def pcm(path: Path, ss: float, t: float) -> np.ndarray:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{ss:.3f}", "-t", f"{t:.3f}", "-i", str(path), "-ac", "1",
                          "-ar", "8000", "-af", "highpass=f=100", "-f", "s16le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.int16).astype(float)
    return (x - x.mean()) / (x.std() + 1e-9)


def latency(raw: Path, processed: Path, at: float) -> float:
    """Delay the FFT denoiser adds (about 25 ms), measured against the untouched take, so it can be taken back out."""
    ref, test = pcm(raw, at, 3.0), pcm(processed, at, 3.0)
    pad = 800  # search up to 100 ms either way
    c = np.correlate(test, ref[pad:-pad], mode="valid")
    return (np.argmax(c) - pad) / 8000


def trims(ranges: list[dict], label: str, fps: float, shift: float = 0.0) -> tuple[list[str], str]:
    parts, al = [], []
    for i, r in enumerate(ranges):
        s, e = float(r["start"]), float(r["end"])
        e = s + max(1, round((e - s) * fps)) / fps  # same frame snapping as render_cut.py, so lips stay in sync
        s, e = s + shift, e + shift
        d = e - s
        parts.append(f"[{label}{i}]atrim=start={s:.6f}:end={e:.6f},asetpts=PTS-STARTPTS,"
                     f"apad=whole_dur={d:.6f},atrim=duration={d:.6f},"
                     f"afade=t=in:st=0:d={FADE},afade=t=out:st={max(0.0, d - FADE):.4f}:d={FADE}[a{i}]")
        al.append(f"[a{i}]")
    parts.append(f"{''.join(al)}concat=n={len(ranges)}:v=0:a=1[ac]")
    return parts, "[ac]"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("raw", type=Path)
    ap.add_argument("edl", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--nr", type=int, default=12)
    ap.add_argument("--fps", type=float, default=30.0, help="frame rate of the cut, for segment snapping")
    a = ap.parse_args()
    ranges = json.loads(a.edl.read_text())["ranges"]
    n = len(ranges)

    # Pass 1: true peak of the cut after the high-pass, so 1 constant gain lands it at TARGET_TP.
    split = f"[0:a]highpass=f=60:poles=2,asplit={n}" + "".join(f"[p{i}]" for i in range(n))
    parts, out = trims(ranges, "p", a.fps)
    parts = [split] + parts + [f"{out}loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json[m]"]
    txt = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(a.raw), "-filter_complex", ";".join(parts),
                          "-map", "[m]", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = json.loads(txt[txt.rfind("{"):txt.rfind("}") + 1])
    gain = TARGET_TP - float(m["input_tp"])

    # Pass 2: learned noise print on the FULL take (the silence it samples is what the cut removes).
    s0, s1 = find_silence(a.raw)
    chain = (f"highpass=f=60:poles=2,volume={gain:.2f}dB,asendcmd={s0:.2f} afftdn sn start,"
             f"asendcmd={s1:.2f} afftdn sn stop,afftdn=nr={a.nr}:nf=-40")
    with tempfile.TemporaryDirectory() as tmp:
        full = Path(tmp) / "full.wav"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(a.raw), "-af", f"{chain},aresample=48000",
                        "-c:a", "pcm_s24le", str(full)], check=True)
        # Pass 3: take the denoiser's latency back out, then cut.
        longest = max(ranges, key=lambda r: float(r["end"]) - float(r["start"]))
        lat = latency(a.raw, full, float(longest["start"]) + 0.3)
        split = f"[0:a]asplit={n}" + "".join(f"[q{i}]" for i in range(n))
        parts, out = trims(ranges, "q", a.fps, shift=lat)
        parts = [split] + parts + [f"{out}aresample=48000[aout]"]
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(full), "-filter_complex", ";".join(parts),
                        "-map", "[aout]", "-c:a", "pcm_s24le", str(a.out)], check=True)
    print(f"{a.out}  gain {gain:+.1f} dB (TP {float(m['input_tp']):.1f} -> {TARGET_TP}), "
          f"noise print {s0:.2f}-{s1:.2f}s, nr={a.nr}, denoiser latency {lat * 1000:+.1f} ms removed")


if __name__ == "__main__":
    main()
