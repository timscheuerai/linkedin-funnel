#!/usr/bin/env python3
"""Learn a grade from a graded clip and its ungraded source, and bake it as a .cube LUT.

Grade 1 clip of a session by hand; this carries that exact look to every other
take shot in the same light. It samples aligned
frames, fits a second-order colour polynomial per channel (least squares), checks
the fit, and writes a 33-point 3D LUT for ffmpeg's lut3d.

Usage:
  python match_grade.py <ungraded source> <graded clip> --offset <source seconds at graded 0> --out look.cube
Apply:
  ffmpeg -i in.mp4 -vf "lut3d=file=look.cube" ...
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import numpy as np

W, H = 180, 320  # sampling size; the fit is colour only, so resolution does not matter


def frame(path: Path, t: float, w: int, h: int) -> np.ndarray:
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", str(path), "-frames:v", "1",
         "-vf", f"scale={w}:{h}:flags=area", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        check=True, capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(h, w, 3).astype(np.float64) / 255.0


def duration(path: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         check=True, capture_output=True, text=True).stdout
    return float(out)


def features(rgb: np.ndarray) -> np.ndarray:
    r, g, b = rgb[:, 0], rgb[:, 1], rgb[:, 2]
    return np.stack([np.ones_like(r), r, g, b, r * r, g * g, b * b, r * g, r * b, g * b], axis=1)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", type=Path)
    ap.add_argument("graded", type=Path)
    ap.add_argument("--offset", type=float, required=True, help="source time that corresponds to graded time 0")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--frames", type=int, default=10)
    a = ap.parse_args()

    d = duration(a.graded)
    times = np.linspace(0.3, d - 0.3, a.frames)
    xs, ys = [], []
    for t in times:
        src, grd = frame(a.source, a.offset + t, W, H), frame(a.graded, t, W, H)
        # Alignment guard: the luma of both frames must correlate, or the offset is wrong.
        c = np.corrcoef(src.mean(axis=2).ravel(), grd.mean(axis=2).ravel())[0, 1]
        if c < 0.9:
            raise SystemExit(f"frames at {t:.2f}s do not line up (correlation {c:.2f}); check --offset")
        xs.append(src.reshape(-1, 3))
        ys.append(grd.reshape(-1, 3))
    x, y = np.concatenate(xs), np.concatenate(ys)
    X = features(x)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    err = np.abs(X @ beta - y).mean() * 255
    print(f"fit on {len(x)} pixels from {len(times)} frames: mean error {err:.2f} / 255")

    n = 33
    grid = np.linspace(0, 1, n)
    b_, g_, r_ = np.meshgrid(grid, grid, grid, indexing="ij")  # .cube: red varies fastest
    rgb = np.stack([r_.ravel(), g_.ravel(), b_.ravel()], axis=1)
    lut = np.clip(features(rgb) @ beta, 0, 1)
    lines = [f"TITLE \"matched from {a.graded.name}\"", f"LUT_3D_SIZE {n}", "DOMAIN_MIN 0 0 0", "DOMAIN_MAX 1 1 1"]
    lines += [f"{v[0]:.6f} {v[1]:.6f} {v[2]:.6f}" for v in lut]
    a.out.write_text("\n".join(lines) + "\n")
    print(a.out)


if __name__ == "__main__":
    main()
