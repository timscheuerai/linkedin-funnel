# Cut plan schema

`render_cut.py` accepts JSON with ordered sources, keep windows, optional manual drops, silence settings, and output settings.

```json
{
  "sources": [
    {
      "id": "intro",
      "path": "/absolute/path/recording.mov",
      "keep": [[54.06, 125.21]],
      "drop": [
        {
          "start": 90.0,
          "end": 92.5,
          "reason": "screen search transition"
        }
      ]
    }
  ],
  "silence": {
    "threshold_db": -45,
    "min_seconds": 0.6,
    "retain_seconds": 0.18
  },
  "output": {
    "path": "/absolute/project/path/final.mp4",
    "crf": 18,
    "preset": "medium",
    "audio_bitrate": "192k"
  }
}
```

Rules:

- `sources` order is the merge order.
- `id` values must be unique.
- `keep` ranges are source-timeline seconds and may contain more than 1 window.
- `drop` ranges are source-timeline seconds. The renderer intersects them with keep windows.
- Paths should be absolute so the project remains reproducible from any working directory.
- Omitted silence and output settings use the measured defaults from `SKILL.md`.
- The renderer writes `edl.json`, `segments/`, `concat.txt`, and the final MP4 next to `plan.json` unless `output.path` overrides the final location.
