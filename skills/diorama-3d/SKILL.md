---
name: diorama-3d
description: Build a 3D diorama graphic in three.js that tells a system as a place (a room, a factory floor, a machine line), with the roles and tools as glossy toys, labels projected from 3D, a 2-second build-in and a seamless loop, exported as a 1080 x 1350 still, MP4 and GIF. Use for a 3D or animated system graphic for a post or lead magnet; flat posters stay in graphics-designer and editable process maps in flowchart.
---

# 3D diorama

A diorama tells a system as a place the reader understands in 2 seconds: a team as an office, outbound as a lead factory, a content workflow as a machine line. It earns its place when the story has stations, roles or a flow. Dense teaching content stays a flat graphic ([graphics-designer](../graphics-designer/SKILL.md)) or a flowchart ([flowchart](../flowchart/SKILL.md)).

## Ground the work

- Read [the brand page](../../context/brand/BRAND.md) for colours, fonts and logo rules, and [positioning](../../context/identity/positioning.md) and [the LinkedIn voice](../../context/voice/linkedin-voice.md) for the copy. Take numbers only from [proof](../../context/identity/proof.md); leave a number out rather than invent one.
- Roles, team members and tool names come from the real source. Never fill a station with an invented role.
- When the brief is open, offer 3 metaphors in 1 line each (for example a press, a greenhouse, a scroll stopper) and build the one the author picks. Then state the reading order: what enters, which stations change it, what comes out.

## Start from the starter

```sh
cp -R skills/diorama-3d/starter output/<asset-name>
npm install --no-save playwright@1.58.2 && npx playwright install chromium   # once, at the repository root
cd output/<asset-name> && ./build.sh
```

The starter renders as is: a slab, a diagonal belt, 3 stations with cards, toys and an in/out line, the header and a 2-step CTA. Replace `STATIONS` and the toys in `scene.js`, the copy and the author's photo in `scene.html`, and the palette and fonts in the `:root` block of `scene.css`. Node and ffmpeg are needed; esbuild runs through `npx`.

- **Plan in screen space.** `P(sx, h, y)`: sx runs left to right on screen, h from the back to the front. `S(s, off, y)` runs along the diagonal belt, which reads as a line from the back left to the front right. A group turned by `ROT` has its local x along the belt.
- **Camera.** Orthographic, about 40 degrees down from the front right (`CAM_DIR`), fitted by `fit(points)` to the corners and the room each card needs. Let walls run off the edges rather than shrinking everything to fit.
- **Toys.** Glossy rounded primitives (`RoundedBoxGeometry`, a clearcoat material) in brand colours. Build faces from the real marks of the tools in the story, as simple extrusions or voxels; put logos on signs as textures and respect their usage rules.
- **Words are HTML, never 3D text.** `label()` projects each label from a 3D anchor and nudges collisions upward with a leader line. Place signs first, then tags. Station cards carry a number, a name and up to 3 lines, each an instruction or a fact the reader can act on.
- **Light and colour.** RoomEnvironment for reflections, 1 soft shadow sun, a cool fill, and neutral tone mapping so brand colours land close to their values.

## What makes it work

- Understandable beats detailed. Fewer, bigger stations; every actor visible; the same nameplate style for every actor. Cut any prop that hides a label.
- Fast build: header, slab and stations arrive in reading order, each over 0.4 s with ease-out and no bounce, and the whole page including the CTA is on screen by about 2.3 s.
- Then the place works: belts fill from each machine's exit, machines move on a beat, toys bob, a short chat line can open above a speaker. Keep motion gentle, never blinking.
- The GIF restarts on the empty stage, so every play shows the build. The still is the fully built, running scene.
- A collab uses the partner's branding, with both faces large and on top.
- CTA: a real next action only. For a LinkedIn lead magnet, 2 steps: "1 Connect with me" (photo and button) and "2 Comment KEYWORD", because a DM usually needs a connection first. On X, "1 Follow me" and "2 Comment KEYWORD" (copy `scene.html` to `scene-x.html`).

## Render, capture, encode

- `./build.sh [page]` bundles `scene.js` with esbuild (module scripts do not load from `file://`) and renders `output/scene.png`, `@2x` and a phone-width preview with a CPU WebGL context.
- `node capture.mjs <frames-dir> 25 [scale] [page]` steps `window.renderAt(t)` from 0 to `T_END`. Draft at scale 1; scale 2 takes several minutes.
- `./encode.sh <frames-dir> <name>` writes the MP4 (1080 x 1350, H.264, for a LinkedIn video post) and a GIF (720 x 900 at 15 fps) that should stay under 5 MB.
- Every running motion repeats within `T_LOOP` (use divisors of it), so the loop has no seam. In `built()`, use `dyn: true` only for objects whose y `updateActors` sets every frame, or the drop accumulates.

## Inspect

Open the full-size still and the phone preview: headline, CTA, station names and the main actors must read at phone size. Make a filmstrip of the build and the loop, for example `ffmpeg -i frames/f%04d.png -vf "select='lte(n\,11)',scale=360:-1,tile=6x2" -frames:v 1 strip.png` after capturing at 4 fps. Check that frame 1 is the empty stage, everything sits by about 2.3 s, no label covers a toy or another label, and nothing jumps at the restart. Fix the biggest weakness and re-render. Do not claim a visual review from the source alone.

## Deliver

Return the still, MP4, GIF and the editable folder, with the dimensions and any known limitation. Keep a short README in the asset folder with the brief, the author's feedback per round and the rebuild commands. Posting needs the author's go.

## Third-party code

`starter/vendor/` holds three.js 0.170.0 and 2 of its addons under the MIT licence (`starter/vendor/three-LICENSE`).
