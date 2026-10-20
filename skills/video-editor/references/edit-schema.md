# edit.json

The plan the agent writes and `build_edit.py` builds. All times are seconds on the finished cut (`transcript_out.md`), snapped to frames at build time. Relative paths resolve against the project folder.

```json
{
  "version": 1,
  "base": "2026-01-15-demo-final.mp4",
  "edl": "edl.json",
  "layout": { "cam": [0.0, 0.645, 0.355, 0.355] },
  "output": { "name": "demo-edit" },
  "voice": { "clean": true },
  "loudness": { "i": -14, "tp": -1.5, "lra": 11 },
  "music": {
    "file": "/abs/path/licensed-music-bed.mp3",
    "sections": [[0, 39.4], [686.0, 704.6]],
    "gain_db": -16,
    "fade": 3
  },
  "overlays": [
    { "id": "o01", "template": "Keyword", "at": 8.8, "dur": 3.0, "cue": "generate leads", "sfx": "tap",
      "props": { "text": "Can this find *leads* for me?" } },
    { "id": "o14", "template": "Stat", "at": 219.0, "dur": 5.0, "cue": "fifty-five", "sfx": "publish",
      "source": "on-screen analytics: 20 replies, 55% reply rate",
      "props": { "value": "55%", "label": "Reply rate", "sub": "11 of 20 replies positive", "anchor": "right" } },
    { "id": "o08", "template": "Focus", "at": 114.0, "dur": 6.0, "cue": "outbound campaigns", "sfx": "click",
      "props": { "rect": [0.012, 0.195, 0.19, 0.445], "label": "The campaign list", "labelSide": "top" } }
  ],
  "zooms": [
    { "id": "z01", "at": 375.8, "dur": 5.0, "scale": 1.3, "focus": [0, 1], "ease": 0.3, "cue": "here's what I want" }
  ]
}
```

## Top level

| Field | Meaning |
| --- | --- |
| `base` | The cut MP4 from [talking-head-video-cut](../../talking-head-video-cut/SKILL.md). Its size and frame rate drive every render. |
| `edl` | The cut's `edl.json`; used for the Resolve timeline and the transcript mapping. `null` makes `base` the only V1 clip (a graded or upscaled cut). |
| `layout.cam` | Webcam box `[x, y, w, h]` as fractions of the frame, or `null`. |
| `output.name` | Basename for `out/<name>.mp4`, `.fcpxml`, `.otio`. |
| `voice.clean` | Voice EQ and compression before the mix (default `true`). |
| `loudness` | Target for the two-pass loudnorm. |
| `music` | `null` for none. `sections` are `[start, end]` on the cut; the file loops to fill. |

## Events

Common fields on overlays and zooms: `id` (unique), `at`, `dur`, `cue` (spoken words within 2 s of `at`, required), `sfx` (a file name in `overlays/public/sfx/` or an absolute path), `sfx_gain_db` (default -9), `sfx_at` (`"in"` or `"out"`), `sfx_offset` (seconds).

Overlay `props` by template. Every card also takes `tone` (`clean` default, `ink` on bright footage, `dark`, `light`) and `anchor` (`top-left`, `top-center`, `top-right`, `left`, `center`, `right`, `bottom-left`, `bottom-center`, `bottom-right`), `offset` `[x, y]` in design pixels.

| Template | Props |
| --- | --- |
| Keyword | `text` (`*word*` or `*several words*` for the serif accent), `size` (default 74) |
| Lower | `title`, `kicker` |
| Stat | `value` (leading number counts up), `label`, `sub`; event-level `source` when the number is not spoken |
| List | `title`, `items: [{ text, at }]` (`at` seconds from card start), `numbered` |
| Chapter | `number` ("01"), `title` |
| Media | `src` (screenshot path), `label` (URL bar text), `width` (design px, default 900), `maxHeight` |
| Focus | `rect [x, y, w, h]`, `label`, `labelSide` (`bottom` or `top`), `dim` (default 0.42) |
| Captions | filled from `words_out.json`: `fixes` (token to display form, `{"$1,800": "$1,800+"}`), `drop` (tokens to leave out: filler, stutters), `emphasis` (words set 1.35x), `heroes` (`[{ start, words, lead, tail, style, place, y, highlight }]`: `start` in cut seconds, `words` in the payoff, `lead` words before it on the small line, `tail` after it, `style` `serif`, `number` or `bold`, `place` `center`, `left` or `right`, `y` its line centre, `highlight` the accent marker on the payoff), `placements` (`[{ start, end, place, y }]` in cut seconds: body words beside the head), `highlight` (a word everywhere, or `{ start, words }` in cut seconds for exactly those spoken words; the translucent accent marker), `drop_at` (cut seconds of single tokens to drop), `serif` (`display` heavy italic, default, or `brand` for the accent serif in `overlays/src/theme.ts`), `y`, `size`, `mute` |
| Interlude | the same word props as Captions plus `tone` (`dark` or `light`); words after a hero sit below it as tiny support words |

Zoom fields: `scale` (1.05 to 2.5), `focus [x, y]` (the point that stays fixed), `ease` (seconds in and out; 0 is a hard punch).

## Outputs

```
edit.json                 the plan
work/overlays/*.mov       ProRes 4444 alpha, 1 per overlay
work/zooms/*.mov          ProRes 422 HQ inserts
work/voice.wav, music_stem.wav, sfx_stem.wav, mix.wav, sfx_hits.json
out/<name>.mp4            the master
out/<name>.fcpxml, .otio  the Resolve timeline
qa/stills/                stills sheets (pre-render review)
qa/frames/, qa/master-sheet-*.jpg, qa/report.md
```
