#!/usr/bin/env python3
"""Render an OBS talking-head cut from a small JSON plan."""

from __future__ import annotations

import argparse
from fractions import Fraction
import json
import re
import subprocess
import sys
from pathlib import Path


def command(args: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, check=True, text=True, capture_output=capture)


def probe(path: Path) -> dict:
    result = command(
        [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height,avg_frame_rate",
            "-of", "json", str(path),
        ],
        capture=True,
    )
    stream = json.loads(result.stdout)["streams"][0]
    fps_fraction = Fraction(stream["avg_frame_rate"])
    return {
        "width": int(stream["width"]),
        "height": int(stream["height"]),
        "fps_fraction": fps_fraction,
        "fps_filter": f"{fps_fraction.numerator}/{fps_fraction.denominator}",
    }


def detect_silences(path: Path, threshold_db: float, min_seconds: float) -> list[tuple[float, float]]:
    result = subprocess.run(
        [
            "ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
            "-af", f"silencedetect=noise={threshold_db}dB:d={min_seconds}",
            "-f", "null", "-",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    starts = [float(value) for value in re.findall(r"silence_start: ([0-9.]+)", result.stderr)]
    ends = [float(value) for value in re.findall(r"silence_end: ([0-9.]+)", result.stderr)]
    return list(zip(starts, ends))


def merge_drops(drops: list[tuple[float, float, str]]) -> list[tuple[float, float, str]]:
    merged: list[tuple[float, float, str]] = []
    for start, end, reason in sorted(drops):
        if end <= start:
            continue
        if merged and start <= merged[-1][1]:
            old_start, old_end, old_reason = merged[-1]
            merged[-1] = (old_start, max(old_end, end), f"{old_reason}; {reason}")
        else:
            merged.append((start, end, reason))
    return merged


def subtract_drops(
    keep_start: float,
    keep_end: float,
    drops: list[tuple[float, float, str]],
) -> list[tuple[float, float, str]]:
    kept: list[tuple[float, float, str]] = []
    cursor = keep_start
    for drop_start, drop_end, reason in drops:
        start = max(keep_start, drop_start)
        end = min(keep_end, drop_end)
        if end <= cursor or start >= keep_end:
            continue
        if start - cursor >= 0.25:
            kept.append((cursor, start, reason))
        cursor = max(cursor, end)
    if keep_end - cursor >= 0.25:
        kept.append((cursor, keep_end, "end of keep window"))
    return kept


def validate_plan(plan: dict) -> None:
    sources = plan.get("sources")
    if not isinstance(sources, list) or not sources:
        raise SystemExit("plan.sources must be a non-empty ordered list")
    ids = [source.get("id") for source in sources]
    if any(not value for value in ids) or len(ids) != len(set(ids)):
        raise SystemExit("every source needs a unique non-empty id")
    for source in sources:
        path = Path(source.get("path", "")).expanduser()
        if not path.is_absolute() or not path.exists():
            raise SystemExit(f"source path must exist and be absolute: {path}")
        keep = source.get("keep")
        if not isinstance(keep, list) or not keep:
            raise SystemExit(f"source {source['id']} needs at least 1 keep range")
        for item in keep:
            if len(item) != 2 or float(item[1]) <= float(item[0]):
                raise SystemExit(f"invalid keep range for {source['id']}: {item}")


def build_edl(plan: dict, specs: dict[str, dict]) -> dict:
    silence = plan.get("silence", {})
    threshold_db = float(silence.get("threshold_db", -45))
    min_seconds = float(silence.get("min_seconds", 0.6))
    retain_seconds = float(silence.get("retain_seconds", 0.18))
    if retain_seconds < 0 or retain_seconds >= min_seconds:
        raise SystemExit("silence.retain_seconds must be >= 0 and below min_seconds")

    ranges: list[dict] = []
    selected_duration = 0.0
    removed_duration = 0.0

    for source in plan["sources"]:
        source_id = source["id"]
        path = Path(source["path"])
        acoustic = detect_silences(path, threshold_db, min_seconds)
        manual = [
            (float(item["start"]), float(item["end"]), item.get("reason", "manual drop"))
            for item in source.get("drop", [])
        ]

        for keep in source["keep"]:
            keep_start, keep_end = map(float, keep)
            selected_duration += keep_end - keep_start
            drops = list(manual)
            half = retain_seconds / 2
            for silence_start, silence_end in acoustic:
                overlap_start = max(keep_start, silence_start)
                overlap_end = min(keep_end, silence_end)
                if overlap_end - overlap_start < min_seconds:
                    continue
                cut_start = overlap_start + half
                cut_end = overlap_end - half
                if cut_end > cut_start:
                    drops.append((cut_start, cut_end, "long acoustic pause"))

            merged = merge_drops(drops)
            for drop_start, drop_end, _ in merged:
                overlap = max(0.0, min(keep_end, drop_end) - max(keep_start, drop_start))
                removed_duration += overlap
            for start, end, boundary_reason in subtract_drops(keep_start, keep_end, merged):
                ranges.append(
                    {
                        "source": source_id,
                        "start": round(start, 3),
                        "end": round(end, 3),
                        "reason": boundary_reason,
                    }
                )

    total = sum(item["end"] - item["start"] for item in ranges)
    first = plan["sources"][0]["id"]
    spec = specs[first]
    return {
        "version": 1,
        "sources": {source["id"]: source["path"] for source in plan["sources"]},
        "ranges": ranges,
        "settings": {
            "silence_threshold_db": threshold_db,
            "minimum_silence_seconds": min_seconds,
            "silence_retained_seconds": retain_seconds,
            "audio_fade_seconds": 0.03,
            "width": spec["width"],
            "height": spec["height"],
            "fps": spec["fps_filter"],
        },
        "selected_duration_s": round(selected_duration, 3),
        "removed_duration_s": round(removed_duration, 3),
        "total_duration_s": round(total, 3),
    }


def render(plan: dict, edl: dict, project: Path, output_override: Path | None) -> Path:
    output_config = plan.get("output", {})
    output = output_override or Path(output_config.get("path", project / "final.mp4")).expanduser()
    if not output.is_absolute():
        output = (project / output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    segments_dir = project / "segments"
    segments_dir.mkdir(parents=True, exist_ok=True)

    width = edl["settings"]["width"]
    height = edl["settings"]["height"]
    fps = edl["settings"]["fps"]
    fps_value = float(Fraction(fps))
    crf = str(output_config.get("crf", 18))
    preset = str(output_config.get("preset", "medium"))
    audio_bitrate = str(output_config.get("audio_bitrate", "192k"))
    fade = float(edl["settings"]["audio_fade_seconds"])
    video_filter_base = (
        f"scale={width}:{height}:force_original_aspect_ratio=decrease:flags=lanczos,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,"
        f"fps={fps},setsar=1,format=yuv420p"
    )

    rendered: list[Path] = []
    for index, item in enumerate(edl["ranges"]):
        source = Path(edl["sources"][item["source"]])
        start = float(item["start"])
        requested_duration = float(item["end"]) - start
        duration = max(1, round(requested_duration * fps_value)) / fps_value
        out = segments_dir / f"segment-{index:03d}.mp4"
        fade_duration = min(fade, duration / 3)
        fade_out = max(0.0, duration - fade_duration)
        video_filter = f"trim=duration={duration:.9f},setpts=PTS-STARTPTS,{video_filter_base}"
        audio_filter = (
            f"atrim=duration={duration:.9f},asetpts=PTS-STARTPTS,"
            f"apad=whole_dur={duration:.9f},atrim=duration={duration:.9f},"
            f"afade=t=in:st=0:d={fade_duration:.3f},"
            f"afade=t=out:st={fade_out:.3f}:d={fade_duration:.3f}"
        )
        command(
            [
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-ss", f"{start:.3f}", "-i", str(source), "-t", f"{duration:.9f}",
                "-map", "0:v:0", "-map", "0:a:0",
                "-vf", video_filter, "-af", audio_filter,
                "-c:v", "libx264", "-preset", preset, "-crf", crf,
                "-profile:v", "high", "-pix_fmt", "yuv420p",
                "-color_primaries", "bt709", "-color_trc", "bt709",
                "-colorspace", "bt709", "-color_range", "tv",
                "-c:a", "aac", "-b:a", audio_bitrate, "-ar", "48000", "-ac", "2",
                "-movflags", "+faststart", str(out),
            ]
        )
        rendered.append(out)
        print(f"[{index + 1:02d}/{len(edl['ranges']):02d}] {item['source']} {start:.2f}-{item['end']:.2f}")

    concat_file = project / "concat.txt"
    concat_file.write_text("".join(f"file '{path.resolve()}'\n" for path in rendered))
    command(
        [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-f", "concat", "-safe", "0", "-i", str(concat_file),
            "-c", "copy", "-movflags", "+faststart", str(output),
        ]
    )
    command(["ffmpeg", "-v", "error", "-i", str(output), "-f", "null", "-"])
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path, help="JSON cut plan")
    parser.add_argument("--output", type=Path, default=None, help="Override final MP4 path")
    parser.add_argument("--edl-only", action="store_true", help="Write edl.json without rendering")
    args = parser.parse_args()

    plan_path = args.plan.expanduser().resolve()
    if not plan_path.exists():
        sys.exit(f"plan not found: {plan_path}")
    plan = json.loads(plan_path.read_text())
    validate_plan(plan)
    specs = {source["id"]: probe(Path(source["path"])) for source in plan["sources"]}
    edl = build_edl(plan, specs)
    edl_path = plan_path.parent / "edl.json"
    edl_path.write_text(json.dumps(edl, indent=2) + "\n")
    print(
        f"selected={edl['selected_duration_s']:.2f}s "
        f"removed={edl['removed_duration_s']:.2f}s "
        f"output={edl['total_duration_s']:.2f}s "
        f"segments={len(edl['ranges'])}"
    )
    if args.edl_only:
        print(edl_path)
        return
    output = render(plan, edl, plan_path.parent, args.output)
    print(output)


if __name__ == "__main__":
    main()
