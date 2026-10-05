# Editorial rules

## Take selection

For repeated takes, prefer the last attempt that actually completes the thought. A trailing fragment such as “So…”, “and…”, or a cut-off word is not a take. Fall back to the previous complete version.

Preserve the narrative order unless the user asks for restructuring. For timestamped OBS recordings, chronological file order is the default when no other sequence is specified.

## Boundary timing

Word starts from Scribe are dependable enough to locate phrases. Word ends often extend into silence and can produce false alarms. Use transcript timing to choose content, then use the audio waveform to decide where silence begins and ends.

Pad a selected take by about 60 ms before its first word and 150 ms after its last word. Use a wider pad only when plosives, breaths, or room acoustics require it.

## Pause removal

Use `silencedetect` on the audio. A good OBS starting point is a −45 dB threshold and 600 ms minimum duration. Remove the middle of a qualifying pause and retain about 180 ms total, usually 90 ms on each side. This keeps speech from sounding machine-cut.

Do not remove every short gap. Pauses below 600 ms usually carry phrasing, emphasis, or breath. After rendering, remaining silence up to roughly 600 ms is acceptable when it reads as natural cadence.

## Manual drops

Acoustic detection cannot identify every editorial transition. Mark these explicitly in the plan:

- searching for a page, file, workflow, or tab;
- waiting for an interface to load;
- a spoken “Exactly”, “Lovely”, or similar marker followed by a setup change;
- repeated scene setup that restates the next clip's opening;
- false starts with audible speech;
- accidental selection, menus, or cursor setup that adds no explanation.

Cut manual drops on complete word boundaries. Keep the screen change if it helps the viewer understand where the next explanation happens.

## Audio and picture

Apply 30 ms audio fades at every kept-segment edge. This prevents clicks without creating an audible crossfade.

Encode each segment once with the final picture settings, then concatenate compatible segments with stream copy. Do not encode the finished master again just to merge it.

For a plain edit, preserve the original frame, frame rate, and screen content. Do not add grading, captions, music, compression, zooms, or overlays unless requested.

## QA

Inspect a filmstrip plus waveform at every output-timeline join, not merely every source join. Confirm:

- no black or single-frame flash;
- no clipped consonant or word;
- no audio spike or click at the boundary;
- no long dead-air gap;
- the screen jump matches the spoken thought;
- opening and closing frames are intentional.

Also decode the full output with ffmpeg, run black-frame and silence detection, verify codec metadata, and inspect the opening, midpoint, and ending frames. Rebuild when evidence finds an issue.
