# Project for a clip that is already cut

`plan.py` and `build_edit.py` need a project folder with word timings on the clip's own timeline. When the clip came out of [talking-head-video-cut](../../talking-head-video-cut/SKILL.md), its project folder already has everything. For an older clip:

```
<session>/edit/video-editor/<slug>/
  transcripts/<source stem>.json   word-timed JSON of the source the clip was cut from
  edl.json                         the ranges of that source that make up the clip
  base-1080.mp4                    the clip, upscaled when it is below 1080 wide
```

`edl.json` in the talking-head-video-cut format:

```json
{
  "version": 1,
  "sources": { "main": "/abs/path/raw/2026-01-15 16-18-46.mov" },
  "ranges": [{ "source": "main", "start": 9.48, "end": 18.33 }],
  "settings": { "fps": "30/1", "width": 360, "height": 640 }
}
```

- Transcript JSON shape: `{"words": [{"text": "hello", "start": 0.12, "end": 0.41, "type": "word"}, ...]}`. ElevenLabs Scribe returns this shape; convert other word-timed output (Whisper with word timestamps, for example) to it. External transcription uploads the audio to a provider, so use it only when the author allows that.
- Cut decisions kept somewhere else: copy their ranges into `edl.json`.
- No transcript at all: transcribe the clip itself into `transcripts/`, and use 1 range from 0 to the clip's duration with the clip as the source.
- When `base` is an upscaled or graded copy, `plan.py` sets `"edl": null`, so the Resolve timeline uses the base as its only V1 clip.
