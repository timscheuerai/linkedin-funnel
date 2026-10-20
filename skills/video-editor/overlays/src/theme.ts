import { Easing, cancelRender, continueRender, delayRender, interpolate } from "remotion";
import sansFont from "../fonts/Geist-Variable.ttf";
import accentSerif from "../fonts/InstrumentSerif-Italic.ttf";
// Heavy italic for caption payoffs. Kit-local, OFL.
import dmSerifItalic from "../fonts/DMSerifDisplay-Italic.ttf";

/*
 * The palette for every overlay. Neutral defaults: replace the hex values with
 * the author's colours from context/brand/BRAND.md (and swap the font files in
 * ../fonts/ if the brand uses other faces). Overlays render on a transparent
 * canvas and are composited later, so backdrop blur has nothing to sample:
 * cards use opaque fills instead.
 */
export const palette = {
  dark: "#1C2026", // dark card and interlude ground, type on bright footage ("ink")
  light: "#FAFAF7", // light card and interlude ground
  white: "#FEFEFC", // type on dark grounds
  caption: "#F2EADB", // warm off-white caption type on footage
  accent: "#DCE3EC", // translucent marker behind 1 key word, accent numerals
  markerInk: "#6E86A8", // the marker on bright footage
  ink: "#16181C",
  secondary: "#5A606B",
  warm: "#F2F0EB",
} as const;

/** `#rrggbb` plus an opacity in percent as CSS `rgb(r g b / a%)`. */
export const tint = (hex: string, percent: number) => {
  const n = parseInt(hex.slice(1), 16);
  return `rgb(${(n >> 16) & 255} ${(n >> 8) & 255} ${n & 255} / ${percent}%)`;
};

export const pal = {
  ...palette,
  hairline: tint(palette.dark, 12),
  glassRim: "linear-gradient(135deg, rgb(255 255 255 / 85%), rgb(255 255 255 / 6%) 24%, rgb(255 255 255 / 2%) 56%, rgb(255 255 255 / 63%))",
  shadowFloat: "0 36px 70px -20px rgb(0 0 0 / 55%), 0 12px 28px -14px rgb(0 0 0 / 38%)",
  shadowOverlay: `0 8px 40px -12px ${tint(palette.dark, 20)}`,
  sans: "'Geist', system-ui, sans-serif",
  serif: "'Instrument Serif', Georgia, serif",
  display: "'DM Serif Display', Georgia, serif",
} as const;

/** Design space. Every template is laid out at 1920 x 1080; render.mjs scales to the footage. */
export const W = 1920;
export const H = 1080;
export const MARGIN = 76; // 4% safe margin at 1080 (HyperFrames layout heuristics)

/* "clean" is the house style: light type straight on the picture, no surface,
   a soft shadow for legibility, serif as the only accent. Dark and light cards
   remain for Media and for explicit requests. */
/* "ink" is the same idea for bright footage (screen recordings, white UI):
   dark type with a soft light halo. White on white UI is unreadable. */
export type Tone = "clean" | "ink" | "dark" | "light";
export const TEXT_SHADOW = "0 2px 18px rgb(0 0 0 / 32%), 0 1px 2px rgb(0 0 0 / 25%)";
export const INK_HALO = "0 0 22px rgb(254 254 252 / 95%), 0 0 6px rgb(254 254 252 / 90%)";
export const bare = (tone: Tone) => tone === "clean" || tone === "ink";
export const toneColors = (tone: Tone) =>
  tone === "clean"
    ? { bg: "transparent", fg: pal.white, soft: tint(pal.white, 78), accent: pal.white, chip: tint(pal.white, 16) }
    : tone === "ink"
      ? { bg: "transparent", fg: pal.dark, soft: tint(pal.dark, 72), accent: pal.dark, chip: tint(pal.dark, 12) }
    : tone === "dark"
      ? { bg: pal.dark, fg: pal.white, soft: tint(pal.white, 64), accent: pal.accent, chip: tint(pal.accent, 14) }
      : { bg: pal.white, fg: pal.ink, soft: pal.secondary, accent: pal.dark, chip: pal.accent };

export type Anchor =
  | "top-left" | "top-center" | "top-right"
  | "left" | "center" | "right"
  | "bottom-left" | "bottom-center" | "bottom-right";

export const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
export const out = Easing.bezier(0.16, 1, 0.3, 1);
export const inOut = Easing.bezier(0.65, 0, 0.35, 1);
export const ramp = (t: number, a: number, b: number, from = 0, to = 1, ease = out) =>
  interpolate(t, [a, b], [from, to], { ...clamp, easing: ease });

if (typeof document !== "undefined") {
  const handle = delayRender("Loading overlay fonts");
  const faces: [string, string, FontFaceDescriptors][] = [
    ["Geist", sansFont, { weight: "100 900" }],
    ["Instrument Serif", accentSerif, { style: "italic", weight: "400" }],
    ["DM Serif Display", dmSerifItalic, { style: "italic", weight: "400" }],
  ];
  Promise.all(
    faces.map(([family, src, desc]) => new FontFace(family, `url(${src})`, desc).load().then((f) => document.fonts.add(f))),
  ).then(
    () => continueRender(handle),
    (err) => cancelRender(err),
  );
}
