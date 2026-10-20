import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { clamp, pal, tint } from "../theme";

/*
 * Clean captions. Off-white type straight on the picture: no boxes,
 * no highlight, a shadow you can barely see.
 *
 * Body: 1 word at a time, lowercase, centred at 65% of the height. Filler
 *   words 0.85x, `emphasis` words 1.25x.
 * Hero unit (the hook and payoffs): a small lead line builds word by word
 *   while the block drifts up, then the hero lands right under it, in a heavy
 *   italic serif ("serif") or bold sans for a number ("number"). The block is
 *   set tight: lines nearly touch, word spaces are narrow.
 * Motion: every word rises a little out of a soft blur (4 frames body, 6 lead,
 *   16 hero, expo-out); a unit that ends in a pause blurs out over 6 frames.
 * Sizes at 1080 wide: body 68 px, lead 49,
 *   emphasis 85, hero 126. Lines sit at 0.82 leading and the hero overlaps
 *   the line above by a fifth of its size, like stacked caption blocks.
 * Placement varies: `placements` and `hero.place` move a unit beside the head
 *   ("left" or "right", default y 0.4) instead of under the chin.
 * `highlight` words (or `hero.highlight`) get a translucent accent marker that
 *   wipes in behind the caption type: specific words only, never whole lines.
 * Leading is compact everywhere: lines of small text almost touch.
 * Interlude reuses the same units on a flat dark or light frame.
 */
export const CREAM = pal.caption; // warm off-white caption type, set in theme.ts

export type Word = { w: string; s: number; e: number };
export type Place = "center" | "left" | "right";
export type Hero = {
  start: number;
  words?: number;
  lead?: number;
  tail?: number;
  style?: "serif" | "number" | "bold";
  place?: Place;
  y?: number;
  highlight?: boolean;
};
export type Placement = { start: number; end: number; place: Place; y?: number };
export type CaptionsProps = {
  seconds: number;
  fps?: number;
  words: Word[];
  heroes?: Hero[];
  emphasis?: string[];
  y?: number; // centre of the caption, fraction of frame height
  size?: number; // body size in px; default 3.55% of frame height
  serif?: "display" | "brand"; // heavy DM Serif Display italic, or the accent serif (Instrument Serif)
  mute?: [number, number][]; // seconds from overlay start (Interludes are muted automatically)
  placements?: Placement[]; // seconds from overlay start: body words beside the head
  highlight?: (string | { start: number; words?: number })[]; // a word everywhere, or specific spoken words by time
  mode?: "full" | "hooks"; // "hooks": only hero units and highlighted words show (long-form talking heads)
  tone?: "cream" | "ink"; // "ink" on bright footage (screen recordings)
};

type Unit =
  | { kind: "word"; word: Word; start: number; end: number; outro: boolean }
  | { kind: "hero"; lead: Word[]; hero: Word[]; tail: Word[]; style: Hero["style"]; spec: Hero; start: number; end: number; outro: boolean };

const FILLER = new Set(
  "a an the of to in on at for and or but so is are was were be been it its it's that this these those i me my we our us you your as with by from if then than just".split(" "),
);
const bare = (w: string) => w.toLowerCase().replace(/[^a-z0-9']/g, "");
const isFiller = (w: string) => FILLER.has(bare(w));
// Lowercase captions, but keep acronyms and names with inner capitals ("AI", "LinkedIn", "C-suites") and anything with digits or symbols.
const display = (w: string) => (/.[A-Z]/.test(w) || /^[A-Z]-/.test(w) || /[\d$€%]/.test(w) ? w : w.toLowerCase());
const expo = Easing.bezier(0.16, 1, 0.3, 1);

export const buildUnits = (words: Word[], heroes: Hero[] = []): Unit[] => {
  const role: (null | { h: number; part: "lead" | "hero" | "tail" })[] = words.map(() => null);
  heroes.forEach((h, hi) => {
    let i = 0;
    words.forEach((w, k) => {
      if (Math.abs(w.s - h.start) < Math.abs(words[i].s - h.start)) i = k;
    });
    const n = h.words ?? 1;
    for (let k = Math.max(0, i - (h.lead ?? 0)); k < i; k++) role[k] = { h: hi, part: "lead" };
    for (let k = i; k < Math.min(words.length, i + n); k++) role[k] = { h: hi, part: "hero" };
    for (let k = i + n; k < Math.min(words.length, i + n + (h.tail ?? 0)); k++) role[k] = { h: hi, part: "tail" };
  });
  const units: (Unit & { h?: number })[] = [];
  words.forEach((w, k) => {
    const r = role[k];
    if (!r) {
      units.push({ kind: "word", word: w, start: w.s - 0.04, end: 0, outro: false });
      return;
    }
    const last = units[units.length - 1];
    if (last && last.kind === "hero" && last.h === r.h) {
      last[r.part].push(w);
    } else {
      const u = { kind: "hero" as const, lead: [] as Word[], hero: [] as Word[], tail: [] as Word[], style: heroes[r.h].style ?? "serif", spec: heroes[r.h], start: w.s - 0.04, end: 0, outro: false, h: r.h };
      u[r.part].push(w);
      units.push(u);
    }
  });
  // Zero gap while speech runs; a unit that runs into a pause holds, then blurs out.
  units.forEach((u, i) => {
    const lastWord = u.kind === "word" ? u.word : [...u.lead, ...u.hero, ...u.tail].slice(-1)[0];
    const next = units[i + 1];
    const hold = lastWord.e + (u.kind === "word" ? 0.9 : 1.2);
    u.end = next ? Math.min(next.start, hold) : hold;
    u.outro = !next || next.start - u.end > 0.05;
  });
  return units;
};

type Kind = "body" | "filler" | "emph" | "lead" | "tiny" | "serif" | "number";
const SIZE: Record<Kind, number> = { body: 1, filler: 0.85, emph: 1.25, lead: 0.72, tiny: 0.55, serif: 1.85, number: 1.9 };
const IN_FRAMES: Record<Kind, number> = { body: 4, filler: 4, emph: 5, lead: 6, tiny: 6, serif: 16, number: 14 };

// Translucent accent marker; the type stays caption-coloured over it.
const ACCENT_WASH = tint(pal.accent, 30);

// Ink: dark type with a light halo, for bright footage (white UI). Its marker is a stronger accent wash.
const INK_HALO = "0 0 18px rgb(254 254 252 / 92%), 0 0 5px rgb(254 254 252 / 88%)";
const INK_WASH = tint(pal.markerInk, 26);

const Glyph: React.FC<{ w: string; t: number; s: number; size: number; kind: Kind; color: string; fps: number; shadow: boolean; serifFont: string; mark?: boolean; ink?: boolean }> = ({
  w,
  t,
  s,
  size,
  kind,
  color,
  fps,
  shadow,
  serifFont,
  mark,
  ink,
}) => {
  const hero = kind === "serif" || kind === "number";
  const p = interpolate(t, [s - 0.04, s - 0.04 + IN_FRAMES[kind] / fps], [0, 1], { ...clamp, easing: expo });
  const serif = kind === "serif";
  // Accent highlight: a square bar wipes in from the left just after the word lands.
  const wipe = mark ? interpolate(t, [s + 2 / fps, s + 11 / fps], [0, 1], { ...clamp, easing: expo }) : 0;
  const text = kind === "number" ? <NumberParts w={w} /> : display(w);
  return (
    <span
      style={{
        position: "relative",
        display: "inline-block",
        opacity: Math.min(1, p * 1.25),
        transform: `translateY(${(1 - p) * (hero ? 0.32 : 0.2)}em) scale(${hero ? 1.05 - 0.05 * p : 1})`,
        transformOrigin: "50% 100%",
        filter: p < 0.99 ? `blur(${(1 - p) * (hero ? 14 : 6)}px)` : undefined,
        fontFamily: serif ? serifFont : pal.sans,
        fontStyle: serif ? "italic" : undefined,
        fontWeight: serif ? 400 : kind === "number" ? 700 : kind === "lead" || kind === "tiny" ? 620 : 680,
        fontSize: size,
        letterSpacing: serif ? "-0.03em" : kind === "number" ? "-0.06em" : "-0.05em",
        lineHeight: "inherit", // the line sets the leading; a word must not hold lines apart
        color,
        textShadow: shadow && wipe < 0.99 ? (ink ? INK_HALO : "0 1px 10px rgb(0 0 0 / 16%)") : undefined,
        whiteSpace: "pre",
        padding: mark ? "0.02em 0.12em 0.06em" : undefined,
        margin: mark ? "-0.02em -0.12em -0.06em" : undefined,
      }}
    >
      {mark ? (
        // The marker: a translucent accent bar wipes in left to right behind the caption type.
        <span
          style={{
            position: "absolute",
            inset: 0,
            background: ink ? INK_WASH : ACCENT_WASH,
            transform: `scaleX(${wipe})`,
            transformOrigin: "0% 50%",
          }}
        />
      ) : null}
      <span style={{ position: "relative" }}>{text}</span>
    </span>
  );
};

/** "$1'800+" -> small "$", full digits, small "+" (the "90%" treatment). */
const NumberParts: React.FC<{ w: string }> = ({ w }) => {
  const m = w.match(/^([^\d]*)([\d][\d',.]*)(.*)$/);
  if (!m) return <>{w}</>;
  const small: React.CSSProperties = { fontSize: "0.5em", verticalAlign: "0.72em", letterSpacing: "-0.02em", marginInline: "0.03em" };
  return (
    <>
      {m[1] ? <span style={small}>{m[1]}</span> : null}
      {m[2]}
      {m[3] ? <span style={small}>{m[3]}</span> : null}
    </>
  );
};

export const TypeLayer: React.FC<{
  words: Word[];
  heroes?: Hero[];
  emphasis?: string[];
  y: number;
  size: number;
  color: string;
  shadow: boolean;
  serif?: "display" | "brand";
  tailKind?: Kind;
  mute?: [number, number][];
  placements?: Placement[];
  highlight?: (string | { start: number; words?: number })[];
  mode?: "full" | "hooks";
  ink?: boolean;
}> = ({ words, heroes, emphasis = [], y, size, color, shadow, serif = "display", tailKind = "lead", mute = [], placements = [], highlight = [], mode = "full", ink = false }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const t = frame / fps;
  if (mute.some(([a, b]) => t >= a && t < b)) return null;
  let units = buildUnits(words, heroes);
  if (mode === "hooks") {
    // Hooks mode shows hero units only, each held until the next hero (or 1.2 s after its last word),
    // so a blank screen never picks up the next spoken word on its own.
    const kept = units.filter((x) => x.kind === "hero" || highlight.some((h) => (typeof h === "string" ? x.kind === "word" && bare(h) === bare(x.word.w) : x.kind === "word" && Math.abs(h.start - x.word.s) < 0.05)));
    units = kept.map((x, i) => {
      const lastWord = x.kind === "word" ? x.word : [...x.lead, ...x.hero, ...x.tail].slice(-1)[0];
      const next = kept[i + 1];
      return { ...x, end: next ? Math.min(next.start, lastWord.e + 1.2) : lastWord.e + 1.2 };
    });
  }
  const u = units.find((x) => t >= x.start && t < x.end);
  if (!u) return null;
  const serifFont = serif === "brand" ? pal.serif : pal.display;
  const emph = new Set(emphasis.map(bare));
  const marked = new Set(highlight.filter((h): h is string => typeof h === "string").map(bare));
  // Time-anchored highlights mark exactly the spoken words they point at.
  const markedAt = new Set<number>();
  highlight.forEach((h) => {
    if (typeof h === "string") return;
    let i = 0;
    words.forEach((w, k) => {
      if (Math.abs(w.s - h.start) < Math.abs(words[i].s - h.start)) i = k;
    });
    for (let k = i; k < Math.min(words.length, i + (h.words ?? 1)); k++) markedAt.add(words[k].s);
  });
  // Where this unit sits: under the chin (centre) or beside the head.
  const spot = u.kind === "hero" && u.spec.place ? { place: u.spec.place, y: u.spec.y } : placements.find((p) => u.start >= p.start - 0.05 && u.start < p.end);
  const place: Place = spot?.place ?? "center";
  const side = place !== "center";
  const yy = spot?.y ?? (side ? 0.4 : y);
  const align = side ? place : "center";
  const markAll = u.kind === "hero" && u.spec.highlight;
  // Inline words in a balanced block, narrow word spaces, tight leading: a wrapped line splits evenly and the lines nearly touch.
  const line = (ws: Word[], kind: Kind, al: Place, maxW = 0.86) => (
    <div style={{ maxWidth: width * (side ? Math.min(maxW, 0.36) : maxW), textAlign: al, textWrap: "balance", lineHeight: kind === "serif" ? 0.8 : kind === "lead" || kind === "tiny" ? 0.7 : 0.84 } as React.CSSProperties}>
      {ws.map((w, i) => (
        <React.Fragment key={i}>
          <Glyph w={w.w} t={t} s={w.s} size={size * SIZE[kind]} kind={kind} color={color} fps={fps} shadow={shadow} serifFont={serifFont} ink={ink} mark={marked.has(bare(w.w)) || markedAt.has(w.s) || (markAll && (kind === "serif" || kind === "number" || kind === "emph"))} />
          {i < ws.length - 1 ? <span style={{ fontSize: size * SIZE[kind] * (kind === "lead" || kind === "tiny" ? 0.68 : 0.82), fontFamily: pal.sans, letterSpacing: 0 }}> </span> : null}
        </React.Fragment>
      ))}
    </div>
  );
  // The hook block drifts up as it builds (ease-out over 1.2 s); any unit that runs into a pause blurs out.
  const drift = u.kind === "hero" ? interpolate(t, [u.start, u.start + 1.2], [height * 0.03, 0], { ...clamp, easing: expo }) : 0;
  const out = u.outro ? interpolate(t, [u.end - 6 / fps, u.end], [0, 1], { ...clamp, easing: Easing.in(Easing.quad) }) : 0;
  const bodyKind = (w: string): Kind => (emph.has(bare(w)) ? "emph" : isFiller(w) ? "filler" : "body");
  const centred = !side && (u.kind === "word" || u.style === "number");
  const al: Place = side ? place : centred ? "center" : "left";
  // Payoff sits right under the lead: the serif's ascenders nearly touch it, the number's digits just clear it.
  const overlap = (k: Kind) => -size * SIZE[k] * (k === "serif" ? 0.14 : 0.0);
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div
        style={{
          position: "absolute",
          left: side ? (place === "left" ? width * 0.06 : "auto") : 0,
          right: side ? (place === "right" ? width * 0.06 : "auto") : 0,
          width: side ? width * 0.4 : undefined,
          top: height * yy,
          transform: `translateY(-50%) translateY(${drift - out * size * 0.2}px)`,
          opacity: 1 - out,
          filter: out > 0.01 ? `blur(${out * 8}px)` : undefined,
          display: "flex",
          justifyContent: align === "left" ? "flex-start" : align === "right" ? "flex-end" : "center",
        }}
      >
        {u.kind === "word" ? (
          line([u.word], bodyKind(u.word.w), al)
        ) : (
          <div style={{ display: "flex", flexDirection: "column", alignItems: al === "center" ? "center" : al === "right" ? "flex-end" : "flex-start" }}>
            {u.lead.length ? line(u.lead, "lead", al, 0.62) : null}
            {(() => {
              const k: Kind = u.style === "number" ? "number" : u.style === "bold" ? "emph" : "serif";
              return <div style={{ marginTop: u.lead.length ? overlap(k) : 0 }}>{line(u.hero, k, al)}</div>;
            })()}
            {u.tail.length ? <div style={{ marginTop: -size * 0.04 }}>{line(u.tail, tailKind, al, 0.62)}</div> : null}
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
};

export const Captions: React.FC<CaptionsProps> = ({ words, heroes, emphasis, y, size, serif, mute, placements, highlight, mode, tone = "cream" }) => {
  const { width, height } = useVideoConfig();
  const portrait = height > width;
  return (
    <TypeLayer
      words={words}
      heroes={heroes}
      emphasis={emphasis}
      y={y ?? (portrait ? 0.65 : 0.8)}
      size={size ?? Math.round(height * (portrait ? 0.0355 : 0.042))}
      color={tone === "ink" ? pal.dark : CREAM}
      shadow
      ink={tone === "ink"}
      serif={serif}
      mute={mute}
      placements={placements}
      highlight={highlight}
      mode={mode}
    />
  );
};

/*
 * Interlude: a full-frame beat on a flat dark (or light) ground, cut in hard. The
 * "blank screen" beat of clean talking-head edits. Without `graphic` it sets the words as
 * type units, centred (a number hero with tiny support words: "40% / of these
 * people"). With `graphic` it is a clean motion graphic that explains the words:
 *   ring  a number with a thin arc drawing to its percentage
 *   list  items stacking on their words; earlier items step back; optional serif payoff
 *   flow  steps joined by a line that draws down as each step is spoken
 * `items` and `payoff` point at spoken words by time (seconds from the overlay
 * start after build_edit.py shifts them), so every element lands on its word.
 */
export type Item = { start: number; words?: number; text?: string };
export type InterludeProps = Omit<CaptionsProps, "tone"> & {
  tone?: "dark" | "light";
  graphic?: "ring" | "list" | "flow" | "title";
  items?: Item[];
  payoff?: Item;
  kicker?: string; // "title": the small line, e.g. a chapter number
  title?: string; // "title": the chapter or section name, in the heavy serif
};

/** Chapter card: a small kicker, then the title rises in the heavy serif. Static text, not word-timed. */
const Title: React.FC<{ kicker?: string; title: string; color: string; size: number; serif?: "display" | "brand" }> = ({ kicker, title, color, size, serif }) => {
  const frame = useCurrentFrame();
  const { fps, width } = useVideoConfig();
  const t = frame / fps;
  const pk = rise(t, 0.08, fps, 8);
  const pt = rise(t, 0.22, fps, 16);
  return (
    <AbsoluteFill style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
      {kicker ? (
        <div style={{ fontFamily: pal.sans, fontWeight: 620, fontSize: size * 0.72, letterSpacing: "-0.02em", color, opacity: pk * 0.72, transform: `translateY(${(1 - pk) * size * 0.3}px)`, marginBottom: size * 0.1 }}>{kicker}</div>
      ) : null}
      <div style={{ maxWidth: width * 0.8, textAlign: "center", textWrap: "balance", fontFamily: serif === "brand" ? pal.serif : pal.display, fontStyle: "italic", fontSize: size * 1.85, lineHeight: 0.92, letterSpacing: "-0.03em", color, opacity: pt, transform: `translateY(${(1 - pt) * size * 0.5}px) scale(${1.04 - 0.04 * pt})`, filter: pt < 0.99 ? `blur(${(1 - pt) * 14}px)` : undefined } as React.CSSProperties}>
        {title}
      </div>
    </AbsoluteFill>
  );
};

const resolve = (words: Word[], it: Item) => {
  let i = 0;
  words.forEach((w, k) => {
    if (Math.abs(w.s - it.start) < Math.abs(words[i].s - it.start)) i = k;
  });
  const ws = words.slice(i, i + (it.words ?? 1));
  return { s: ws[0]?.s ?? it.start, text: it.text ?? ws.map((w) => display(w.w)).join(" ") };
};

const rise = (t: number, s: number, fps: number, frames = 8) =>
  interpolate(t, [s - 0.04, s - 0.04 + frames / fps], [0, 1], { ...clamp, easing: expo });

const Ring: React.FC<{ words: Word[]; heroes?: Hero[]; color: string; size: number; serif?: "display" | "brand" }> = ({ words, heroes, color, size, serif }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const t = frame / fps;
  const num = words.find((w) => /\d/.test(w.w));
  const pct = num ? Math.min(100, parseFloat(num.w.replace(/[^\d.]/g, ""))) : 0;
  const p = num ? interpolate(t, [num.s, num.s + 22 / fps], [0, 1], { ...clamp, easing: Easing.bezier(0.65, 0, 0.35, 1) }) : 0;
  const r = Math.min(width, height) * 0.27;
  const c = 2 * Math.PI * r;
  const stroke = Math.max(2, height * 0.0022);
  return (
    <AbsoluteFill>
      <svg width={width} height={height} style={{ position: "absolute", inset: 0 }}>
        <circle cx={width / 2} cy={height * 0.5} r={r} fill="none" stroke={color} strokeOpacity={0.14} strokeWidth={stroke} />
        <circle
          cx={width / 2}
          cy={height * 0.5}
          r={r}
          fill="none"
          stroke={color}
          strokeWidth={stroke * 1.6}
          strokeLinecap="round"
          strokeDasharray={`${(c * pct * p) / 100} ${c}`}
          transform={`rotate(-90 ${width / 2} ${height * 0.5})`}
        />
      </svg>
      <TypeLayer words={words} heroes={heroes} y={0.5} size={size} color={color} shadow={false} serif={serif} tailKind="tiny" mode="hooks" />
    </AbsoluteFill>
  );
};

const Stack: React.FC<{ words: Word[]; items: Item[]; payoff?: Item; color: string; size: number; flow: boolean; serif?: "display" | "brand" }> = ({
  words,
  items,
  payoff,
  color,
  size,
  flow,
  serif,
}) => {
  const frame = useCurrentFrame();
  const { fps, height } = useVideoConfig();
  const t = frame / fps;
  const list = items.map((it) => resolve(words, it));
  const pay = payoff ? resolve(words, payoff) : null;
  const current = list.reduce((k, it, i) => (t >= it.s - 0.04 ? i : k), -1);
  const fs = size * 1.18;
  const gap = flow ? fs * 1.05 : fs * 0.16;
  const dot = fs * 0.2;
  const stroke = Math.max(2, height * 0.0018);
  return (
    <AbsoluteFill style={{ display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ position: "relative", display: "flex", flexDirection: "column", alignItems: flow ? "flex-start" : "center", gap }}>
        {list.map((it, i) => {
          const p = rise(t, it.s, fps);
          // the newest item is full strength; earlier ones step back so the eye follows the speech
          const dim = i < current ? 0.42 : 1;
          const line = flow && i < list.length - 1 ? interpolate(t, [list[i + 1].s - 0.3, list[i + 1].s + 0.1], [0, 1], { ...clamp, easing: expo }) : 0;
          return (
            <div key={i} style={{ position: "relative", display: "flex", alignItems: "center", gap: fs * 0.42, opacity: p * dim, transform: `translateY(${(1 - p) * fs * 0.3}px)`, filter: p < 0.99 ? `blur(${(1 - p) * 8}px)` : undefined }}>
              {flow ? <div style={{ width: dot, height: dot, borderRadius: dot, background: color, flex: "none" }} /> : null}
              <span style={{ fontFamily: pal.sans, fontWeight: 660, fontSize: fs, letterSpacing: "-0.045em", lineHeight: 0.9, color, whiteSpace: "nowrap" }}>{it.text}</span>
              {flow && i < list.length - 1 ? (
                <div style={{ position: "absolute", left: dot / 2 - stroke / 2, top: fs * 0.5 + dot / 2, width: stroke, height: gap + fs * 0.9 - dot, background: color, opacity: 0.5, transform: `scaleY(${line})`, transformOrigin: "50% 0%" }} />
              ) : null}
            </div>
          );
        })}
        {pay ? (
          <div style={{ marginTop: fs * 0.25, alignSelf: "center" }}>
            {(() => {
              const p = rise(t, pay.s, fps, 16);
              return (
                <span style={{ display: "inline-block", fontFamily: serif === "brand" ? pal.serif : pal.display, fontStyle: "italic", fontSize: size * 1.85, letterSpacing: "-0.03em", lineHeight: 0.85, color, opacity: p, transform: `translateY(${(1 - p) * size * 0.5}px) scale(${1.05 - 0.05 * p})`, filter: p < 0.99 ? `blur(${(1 - p) * 14}px)` : undefined }}>
                  {pay.text}
                </span>
              );
            })()}
          </div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};

export const Interlude: React.FC<InterludeProps> = ({ words, heroes, emphasis, tone = "dark", size, serif, graphic, items = [], payoff, kicker, title }) => {
  const { height } = useVideoConfig();
  const color = tone === "dark" ? CREAM : pal.dark;
  const { width } = useVideoConfig();
  const base = size ?? Math.round(height * (height > width ? 0.038 : 0.062)); // landscape frames read from further away
  return (
    <AbsoluteFill style={{ background: tone === "dark" ? pal.dark : pal.light }}>
      {graphic === "title" ? (
        <Title kicker={kicker} title={title ?? ""} color={color} size={base} serif={serif} />
      ) : graphic === "ring" ? (
        <Ring words={words} heroes={heroes} color={color} size={base} serif={serif} />
      ) : graphic === "list" || graphic === "flow" ? (
        <Stack words={words} items={items} payoff={payoff} color={color} size={base} flow={graphic === "flow"} serif={serif} />
      ) : (
        <TypeLayer words={words} heroes={heroes} emphasis={emphasis} y={0.5} size={base} color={color} shadow={false} serif={serif} tailKind="tiny" mode="hooks" />
      )}
    </AbsoluteFill>
  );
};
