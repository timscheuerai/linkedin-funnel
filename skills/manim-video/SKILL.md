---
name: manim-video
description: Create an explanatory animation in Manim from a precise concept, scene plan and verified local renderer.
---

# Animate an explanation

Read the underlying concept and audience brief. Define what should become clear through motion: a transformation, dependency, construction or changing quantity. A decorative animation is not a substitute for the explanation.

Inspect the installed Manim version and current official documentation before writing version-dependent code. Manim and its rendering dependencies are not bundled in this kit.

Plan scenes with narration/caption, objects, spatial relationships, transformations and intended duration. Check mathematical statements and labels before animating. Use camera motion only when it helps explain scale or structure.

Implement in an editable Python project with explicit output directory and supplied brand tokens when available. Keep data and equations as source values. Render a low-cost preview to check pacing, text bounds, labels, camera and object continuity.

Render the requested final resolution and inspect the actual output. Check transitions and synchronize with narration if included. Use `shorts-qa` for applicable export checks.

Deliver scene source, rendered file, environment/version notes and any unverified dependencies. If rendering is unavailable, deliver the source as unrendered and identify the exact missing step.
