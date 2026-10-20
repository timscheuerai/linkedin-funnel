# Designed intro, clip-only tutorial

Use this when the video opens with the author speaking to camera and then becomes a screen demonstration that should stay visually clean.

## Plan from speech and picture

1. Transcribe with word timing. Mark the hook, each claim that deserves a visual, the first tutorial frame and the closing transition. Write exact source in and out ranges and the reason for every removal.
2. Match support to the spoken beat. A launch page, logo or number appears when the author names it and leaves after about 1.5 to 3 seconds. Use the real source visual, never an invented card.
3. Make the intro worth watching on mute while the author stays the main subject: short phrase captions, comfortable size, clear of the face, gentle framing changes at phrase boundaries.

## Proof moments

- Count up a number only to its real value, and let the counter, the chart and any arrow share 1 reveal so they agree on every frame.
- Show analytics screenshots full frame, labelled with their own numbers; do not caption a different, rounder number on top.
- Name the time window ("last 7 days") when the number has one.

## Treatment

- 1 calm visual system for the whole intro: a neutral ground, a few translucent panels, precise type, 1 accent colour.
- Avoid large uniform captions, oversized slabs, cheap wipes and bouncy transitions.
- The tutorial body has no captions, overlays, chapter interruptions or zooms. Repair timing and stutters there by cutting source ranges.

## Layout variety and attention

A long intro with every graphic on the same side reads as monotone. Edit for attention:

- Alternate the frame: a side card on the left, a full frame, a card on the right, a full frame, a split screen. Shift the camera framing away from the card's side, and use denser glass where the background behind the text is dark or busy.
- Make full-frame moments frosted glass over the author's own footage rather than a flat ground, and rack the blur in and out by animating the frost's `backdrop-filter` and a separate tint layer. Never fade the overlay's parent: a parent below opacity 1 switches the blur off, so it pops in late. A frosted full frame also hides a jump cut.
- No talking stretch longer than about 7 seconds without a visual change. For a long one, snap-punch in on the key phrase or use a split screen: the author in a rounded window on one side, a diagram building on the other at the same height.
- Move from frame 1 (a slight zoom that settles), and push in on the last line into the cut to the tutorial.
- Related numbers each get their own beat; a comparison becomes columns, not 1 crowded card.

## Render checks

- Every element starts hidden before its entrance and is gone before the last intro frame, so the cut into the body is invisible. Check descendants too: a child forced visible can outlive its timed parent and leave a panel on screen.
- Run the motion tool's check, render, then inspect a timed contact sheet and the actual MP4 before assembly.
- Review the intro-to-tutorial seam and the closing cut frame by frame.
- Sound design, when the brief asks for it: a few quiet cues tied to clear motion events (a panel entering, landing, a reveal), the original voice kept, no repeated click pattern. Mix by listening against the words as well as measuring the export.
