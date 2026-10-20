import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring } from "remotion";
import { Anchor, INK_HALO, MARGIN, TEXT_SHADOW, Tone, bare, clamp, inOut, out, pal, ramp, toneColors } from "./theme";
import { interpolate } from "remotion";

/* Shared props every overlay accepts. `seconds` and `fps` size the composition. */
export type Base = {
  seconds: number;
  fps?: number;
  anchor?: Anchor;
  tone?: Tone;
  offset?: [number, number];
};

export const ENTER = 16; // frames
export const EXIT = 8; // exits faster than entrances

/** Enter progress (spring, a hair of overshoot) and exit progress for the clip. */
export const useLife = () => {
  const t = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const inP = t <= 0 ? 0 : spring({ frame: t, fps, config: { damping: 20, stiffness: 190, mass: 0.8 } });
  const outP = interpolate(t, [durationInFrames - EXIT, durationInFrames - 1], [0, 1], { ...clamp, easing: inOut });
  return { t, fps, dur: durationInFrames, inP, outP };
};

const justify = (a: Anchor) => (a.endsWith("left") || a === "left" ? "flex-start" : a.endsWith("right") || a === "right" ? "flex-end" : "center");
const align = (a: Anchor) => (a.startsWith("top") ? "flex-start" : a.startsWith("bottom") ? "flex-end" : "center");

/** Direction the card travels in from: the nearest frame edge. */
export const enterVector = (a: Anchor): [number, number] => {
  if (a === "top-center") return [0, -1];
  if (a === "bottom-center") return [0, 1];
  if (a === "center") return [0, 0.6];
  if (a.endsWith("left") || a === "left") return [-1, 0];
  return [1, 0];
};

/** Positions its child inside the safe margin at the anchor. */
export const Placed: React.FC<{ anchor: Anchor; offset?: [number, number]; children: React.ReactNode }> = ({ anchor, offset = [0, 0], children }) => {
  const { width, height } = useVideoConfig();
  const portrait = height > width;
  // Vertical: keep clear of the Shorts, Reels and TikTok chrome (top 10%, bottom 22%)
  // and set cards 15% larger; they are read on a phone held upright.
  const padding = portrait ? `${height * 0.1}px ${MARGIN}px ${height * 0.22}px` : MARGIN;
  const zoom = portrait ? 1.15 : 1;
  return (
    <AbsoluteFill
      style={{
        padding,
        display: "flex",
        flexDirection: "row",
        justifyContent: justify(anchor),
        alignItems: align(anchor),
      }}
    >
      <div style={{ transform: `translate(${offset[0]}px, ${offset[1]}px)`, zoom }}>{children}</div>
    </AbsoluteFill>
  );
};

/** The overlay surface: opaque dark or light card with a glass rim and float shadow. */
export const Card: React.FC<{
  anchor: Anchor;
  tone: Tone;
  radius?: number;
  padding?: string | number;
  style?: React.CSSProperties;
  children: React.ReactNode;
}> = ({ anchor, tone, radius = 22, padding = "26px 34px", style, children }) => {
  const { inP, outP } = useLife();
  const [vx, vy] = enterVector(anchor);
  const c = toneColors(tone);
  const travel = 56;
  const x = vx * travel * (1 - inP) + vx * 14 * outP;
  const y = vy * travel * (1 - inP) + vy * 10 * outP;
  const scale = 0.94 + 0.06 * inP - 0.03 * outP;
  const blur = (1 - Math.min(inP, 1)) * 14 + outP * 10;
  return (
    <div
      style={{
        position: "relative",
        background: c.bg,
        color: c.fg,
        borderRadius: radius,
        padding,
        boxShadow: bare(tone) ? undefined : `${pal.shadowFloat}, inset 0 1px 0 rgb(255 255 255 / ${tone === "dark" ? 14 : 85}%)`,
        textShadow: tone === "clean" ? TEXT_SHADOW : tone === "ink" ? INK_HALO : undefined,
        opacity: Math.min(1, inP * 1.4) * (1 - outP),
        transform: `translate(${x}px, ${y}px) scale(${scale})`,
        transformOrigin: vx < 0 ? "left center" : vx > 0 ? "right center" : "center",
        filter: blur > 0.3 ? `blur(${blur}px)` : undefined,
        fontFamily: pal.sans,
        ...style,
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          borderRadius: radius,
          border: bare(tone) ? "none" : `1px solid rgb(255 255 255 / ${tone === "dark" ? 16 : 70}%)`,
          pointerEvents: "none",
        }}
      />
      {children}
    </div>
  );
};

/**
 * Words that blur into focus one by one. Wrap a word in *asterisks* for the
 * Instrument Serif italic accent. Never combine it with another highlight.
 */
export const Words: React.FC<{
  text: string;
  at?: number;
  stagger?: number;
  size: number;
  weight?: number;
  color: string;
  accent?: string;
  style?: React.CSSProperties;
}> = ({ text, at = 4, stagger = 3, size, weight = 600, color, accent, style }) => {
  const t = useCurrentFrame();
  // *spans* may cover several words: "A proper *MCP or CLI*".
  let open = false;
  const tokens = text
    .split(/\s+/)
    .filter(Boolean)
    .map((raw) => {
      const starts = raw.startsWith("*");
      const ends = /\*[.,!?:;]?$/.test(raw);
      const serif = open || starts;
      if (starts) open = true;
      if (ends) open = false;
      return { word: raw.replace(/\*/g, ""), serif };
    });
  return (
    <div style={{ fontSize: size, fontWeight: weight, letterSpacing: "-0.035em", lineHeight: 1.06, color, ...style }}>
      {tokens.map(({ word, serif }, i) => {
        const p = ramp(t, at + i * stagger, at + i * stagger + 14);
        return (
          <span
            key={i}
            style={{
              display: "inline-block",
              marginRight: "0.24em",
              opacity: p,
              transform: `translateY(${(1 - p) * 0.3}em)`,
              filter: p < 0.98 ? `blur(${(1 - p) * 10}px)` : undefined,
              fontFamily: serif ? pal.serif : undefined,
              fontStyle: serif ? "italic" : undefined,
              fontWeight: serif ? 400 : undefined,
              letterSpacing: serif ? "-0.01em" : undefined,
              color: serif && accent ? accent : undefined,
            }}
          >
            {word}
          </span>
        );
      })}
    </div>
  );
};

/** Rolls the leading number of a value ("47/70", "3x", "10'000") up from 0. */
export const CountUp: React.FC<{ value: string; at?: number; frames?: number }> = ({ value, at = 4, frames = 22 }) => {
  const t = useCurrentFrame();
  const m = value.match(/^([^\d]*)([\d][\d',.]*)(.*)$/);
  if (!m) return <>{value}</>;
  const [, pre, num, post] = m;
  const sep = num.includes("'") ? "'" : num.includes(",") && !num.includes(".") ? "," : "";
  const target = parseFloat(num.replace(/[',]/g, ""));
  const decimals = (num.split(".")[1] ?? "").length;
  const p = ramp(t, at, at + frames);
  const v = (target * p).toFixed(decimals);
  const withSep = sep ? v.replace(/\B(?=(\d{3})+(?!\d))/g, sep) : v;
  return (
    <>
      {pre}
      {withSep}
      {post}
    </>
  );
};

export const Dot: React.FC<{ color: string; size?: number }> = ({ color, size = 12 }) => {
  const t = useCurrentFrame();
  const pulse = 1 + 0.18 * Math.sin(t / 7);
  return <div style={{ width: size, height: size, borderRadius: size, background: color, transform: `scale(${pulse})`, flex: "none" }} />;
};

export { out, inOut, ramp };
