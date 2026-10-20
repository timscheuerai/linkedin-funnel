# Silver title text

A silver, slightly graded title that stands out over a face frame. The spec was measured pixel by pixel from a high-performing creator thumbnail, then made a little more contrasty (the chrome version). `../assets/silver-text.css` holds both as classes.

## The chrome version (default `.silver-text`)

- Fill: pure white `#FFFFFF` at the cap top to cool steel `#B3B9C2` at the baseline. 1 vertical gradient across the whole line, so lowercase letters pick up the same row value as capitals.
- Edge: no stroke, bevel or inner highlight. A tight contact shadow (`0 0.01em 0.015em`, black at 45%) gives a crisp edge, then 1 soft black shadow (`0 0.02em 0.115em`) at 60%. Full strength reads heavy over a light shirt.
- `padding-right: 0.08em` is required: with tight tracking the box ends inside the last letter and the fill slices it off.
- Type: a bold neo-grotesque with stems about 20% of the cap height and an x-height about 75% of it (Geist 700 fits), tracked so tight that round letters touch.
- Placement at 1280 x 720: about 210 px type (cap height about 148 px), centred, about 60% of the frame wide, low across the chest.
- Use it for the big title over a face frame: the tool or topic name, 1 or 2 words. It does not replace a different, approved hook style.

## Why it works

The shadow does the separation, not a border: the background right at the letter drops to about two thirds of its brightness and recovers over about 40 px. Over a white shirt that soft dark halo is what makes the silver read. Text over a dark area (a jacket, a laptop) pops even more.

## How to use it

```html
<div style="text-align:center; font-size:210px"><span class="silver-text">Tool Name</span></div>
```

- Everything is in `em`, so the shadow scales with the type.
- Keep `line-height: 1` and no vertical padding on the span; the gradient stops assume them.
- `silver-text--reference` gives the measured reference (lighter fill, shadow only) when a softer look fits.
- Check the last letter at full size: a clipped glyph means the padding was removed.
