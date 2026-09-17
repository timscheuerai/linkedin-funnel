# Visual grammar and drawing helpers

## Compose for scanning

Start an operation card with an icon and plain-language title. Follow with left-aligned labeled rows and a separate output strip. Use labels that fit: Input, Find, Check, Match, Write or Route. Do not paste a centered paragraph into every box.

The helper starts with a 72px title band, 34px icon, 26px title, 18px body, 13px field labels and 22px padding. These are working-canvas starting values. Card height grows with explicit line breaks. Actual font measurement must confirm the width.

Distinguish functions and skills by shape, label and contrast, so color is not the sole signal. A function can call a model and still have a defined input/output contract. A skill can choose or combine functions. Neither distinction means one is always deterministic.

Use a quiet reference panel for files, a list/tree for taxonomy, a diamond for decisions and a larger number for an evidenced result. Variation should tell the reader what kind of thing they are looking at.

## Routes

Trace the successful path first. Add failure paths and outside return loops next. Label decision exits. Return a retry to the work it repeats. Two columns do not imply parallel execution.

A feedback line must start at a real source of feedback and end at the context or step that changes. Do not connect a sales result directly to a raw source file as if immutable evidence were rewritten.

Keep connectors outside cards and text. Bind actual endpoints, not nearby unrelated shapes. Native icon strokes are lines, not process arrows. For complex diagrams, keep a short edge checklist or structural assertions alongside the generator.

## Python API

Copy or import both files from this skill's `scripts/` directory. The helper has no external package dependency.

```python
from pathlib import Path
import sys

# Run the generator with the kit root as the working directory:
repo = Path.cwd()
sys.path.insert(0, str(repo / 'skills/flowchart/scripts'))
from flowchart import Flowchart

f = Flowchart()  # neutral grays, standard Excalidraw font slot 2
check = f.action('check', 80, 120, 480, 'Review request', 'verify',
                 [('Input', 'Request + criteria')], 'Decision + reason')
gate = f.gate('eligible', 220, 380, 200, 100, 'ready?')
proceed = f.node('proceed', 660, 390, 320, 80, 'Continue')
hold = f.node('hold', 80, 560, 480, 80, 'Request missing information')
f.arrow([(320, check['y']+check['height']), (320, 380)], a=check, b=gate)
f.arrow([(420, 430), (660, 430)], a=gate, b=proceed)
f.text(470, 400, 'YES', size=15)
f.arrow([(320, 480), (320, 560)], a=gate, b=hold)
f.text(342, 508, 'NO', size=15)
f.write(Path(__file__).with_name('request-flow.excalidraw'))
```

| Method | Purpose |
| --- | --- |
| `Flowchart(theme=None, font_family=2, center_x=920)` | Independent scene; optional color roles and native font slot |
| `action(key,x,y,w,title,glyph,rows,output,kind='function')` | Returns the outer card with its computed height; kind can be skill |
| `node(key,x,y,w,h,title,body=None,kind='card')` | Compact reference, hold or result |
| `gate(key,x,y,w,h,label)` | Decision diamond; add labels and outgoing arrows |
| `icon(name,x,y,size=36,color=None)` | Editable grouped line icon |
| `arrow(points,a=None,b=None,dashed=False)` | Native connector with reciprocal endpoint bindings |
| `stage(key,y,h,top,bottom,title)` / `end_stage()` | Grouped rectangular or narrowing stage |
| `embed_image(path,x,y,width,height)` | Embedded image bytes; caller preserves aspect ratio |
| `write(path,name=None)` | Native scene; writes only the specified path |

Theme roles: canvas, surface, muted, text, accent, secondary, connector, border and tint. Pass values from the client's existing tokens; no brand root or machine-specific path is required.

Icons: company, company-enrich, score, person, person-search, person-enrich, person-score, brain, waterfall, verify, rank, split, mail-ai, send, chart, tools, file, microphone, book, calendar, pen, message, layers and eye.

Keys and parent groups identify placements. Add a parent to the front of `f.groups` while building its contents, then remove it. For multiple scenes on one canvas, prefix every ID, group ID, binding reference and frame reference to avoid collisions.

## Rendering and validation

The helper outputs editable scene JSON, not a rendered image. Use the installed editor's native export, an available connector, or the project's existing renderer. The template does not require a particular hosted service or bundle a browser.

Measure text with the font actually used by the editor. Correct centering after measuring. Check the title, each field and the output strip against the card bounds. Confirm no connector intersects text, and that an arrow's binding is reciprocated by its destination shape.

Decode embedded images and check aspect ratio and visible pixels. Use authentic logos only when relevant and supplied; keep each placement in its own group. A logo does not need a vendor hyperlink.

Reopen/import the saved scene and compare it with the export. Verify the served URL returns the delivered scene. Keep an original before regenerating an edited diagram. Record what was checked and any limitation; a successful JSON parse is not a successful visual review.
