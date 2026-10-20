# Sound effects

This folder ships empty. Add short MP3 files you have the rights to use, named after how the edit refers to them:

| File | Suggested use |
|---|---|
| `tap.mp3` | Keyword, Lower and List cards |
| `click.mp3` | Focus spotlights |
| `impact.mp3` | Chapter cards, at -14 dB |
| `publish.mp3` | Stat cards |
| `pings.mp3`, `cascade.mp3`, `typing.mp3` | Optional, for specific visual events |

An event's `sfx` field names a file here (without `.mp3`) or gives an absolute path. `build_edit.py check` fails when a named file is missing. Without files, leave `sfx` out of the plan: the edit works without sound effects.
