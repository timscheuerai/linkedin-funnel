import React from "react";
import { AbsoluteFill, Img, OffthreadVideo, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { Base, Card, Placed, useLife } from "../kit";
import { clamp, inOut, pal, ramp, tint, toneColors } from "../theme";

/*
 * Media: the real thing on screen. A screenshot of the repo, site, post or
 * product the speaker names, in a quiet window frame. Never an invented
 * graphic standing in for a real page.
 */
export type MediaProps = Base & { src: string; label?: string; width?: number; maxHeight?: number };
export const Media: React.FC<MediaProps> = ({ src, label, width = 900, maxHeight = 780, anchor = "right", tone = "light", offset }) => {
  const c = toneColors(tone);
  const { t, dur } = useLife();
  const push = interpolate(t, [0, dur], [1, 1.035], clamp);
  return (
    <Placed anchor={anchor} offset={offset}>
      <Card anchor={anchor} tone={tone} radius={18} padding={0} style={{ width, overflow: "hidden" }}>
        <div style={{ height: 50, display: "flex", alignItems: "center", gap: 9, padding: "0 18px", borderBottom: `1px solid ${tone === "light" ? tint(pal.dark, 10) : "rgb(255 255 255 / 12%)"}` }}>
          {[0, 1, 2].map((i) => (
            <div key={i} style={{ width: 13, height: 13, borderRadius: 13, background: tone === "light" ? tint(pal.dark, 16) : "rgb(255 255 255 / 22%)" }} />
          ))}
          {label ? (
            <div
              style={{
                margin: "0 auto",
                padding: "6px 18px",
                borderRadius: 9,
                fontSize: 19,
                fontWeight: 500,
                color: c.soft,
                background: tone === "light" ? tint(pal.dark, 6) : "rgb(255 255 255 / 8%)",
                transform: "translateX(-24px)",
              }}
            >
              {label}
            </div>
          ) : null}
        </div>
        <div style={{ maxHeight, overflow: "hidden" }}>
          <Img src={staticFile(src)} style={{ display: "block", width: "100%", transform: `scale(${push})`, transformOrigin: "50% 0%" }} />
        </div>
      </Card>
    </Placed>
  );
};

/*
 * Focus: points at a region of the recorded screen. `rect` is [x, y, w, h]
 * as fractions of the frame. The rest of the frame dims so the eye lands there.
 */
export type FocusProps = Base & { rect: [number, number, number, number]; label?: string; labelSide?: "top" | "bottom" | "right"; dim?: number };
export const Focus: React.FC<FocusProps> = ({ rect, label, labelSide = "bottom", dim = 0.42, tone = "dark" }) => {
  const { t, inP, outP } = useLife();
  const { width: W, height: H } = useVideoConfig();
  const c = toneColors(tone);
  const [x, y, w, h] = [rect[0] * W, rect[1] * H, rect[2] * W, rect[3] * H];
  const pad = 10;
  const grow = 1.08 - 0.08 * Math.min(inP, 1);
  const vis = Math.min(1, inP) * (1 - outP);
  const labelP = ramp(t, 8, 22) * (1 - outP);
  return (
    <AbsoluteFill>
      <div
        style={{
          position: "absolute",
          left: x - pad,
          top: y - pad,
          width: w + pad * 2,
          height: h + pad * 2,
          borderRadius: 16,
          boxShadow: `0 0 0 4000px ${tint(pal.ink, dim * vis * 100)}`,
          transform: `scale(${grow})`,
        }}
      />
      <div
        style={{
          position: "absolute",
          left: x - pad,
          top: y - pad,
          width: w + pad * 2,
          height: h + pad * 2,
          borderRadius: 16,
          border: `2px solid ${pal.caption}`,
          boxShadow: "0 0 24px rgb(0 0 0 / 18%)",
          opacity: vis,
          transform: `scale(${grow})`,
        }}
      />
      {label ? (
        <div
          style={{
            position: "absolute",
            left: labelSide === "right" ? x + w + pad + 26 : x - pad,
            top: labelSide === "bottom" ? y + h + pad + 18 : labelSide === "right" ? y + h / 2 : undefined,
            bottom: labelSide === "top" ? H - (y - pad) + 18 : undefined,
            // clean: cream type on the dimmed frame, no chip
            color: pal.caption,
            textShadow: "0 1px 10px rgb(0 0 0 / 35%)",
            fontFamily: pal.sans,
            fontSize: 34,
            fontWeight: 640,
            letterSpacing: "-0.035em",
            opacity: labelP,
            transform:
              labelSide === "right"
                ? `translate(${(1 - labelP) * -12}px, -50%)`
                : `translateY(${(1 - labelP) * (labelSide === "bottom" ? -12 : 12)}px)`,
            whiteSpace: "nowrap",
          }}
        >
          {label}
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

/*
 * Zoom: an opaque insert that replaces the base picture for its span.
 * Scales around `focus` ([x, y] fractions), which keeps the frame edges
 * inside the picture. `ease` seconds in and out; 0 is a hard punch-in.
 */
export type ZoomProps = { seconds: number; fps?: number; src: string; scale: number; focus: [number, number]; ease?: number };
export const Zoom: React.FC<ZoomProps> = ({ src, scale, focus, ease = 0.35 }) => {
  const t = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const e = Math.max(0, Math.round(ease * fps));
  const up = e === 0 ? 1 : interpolate(t, [0, e], [0, 1], { ...clamp, easing: inOut });
  const down = e === 0 ? 0 : interpolate(t, [durationInFrames - e, durationInFrames], [0, 1], { ...clamp, easing: inOut });
  const z = 1 + (scale - 1) * up * (1 - down);
  return (
    <AbsoluteFill style={{ background: "black", overflow: "hidden" }}>
      <AbsoluteFill style={{ transform: `scale(${z})`, transformOrigin: `${focus[0] * 100}% ${focus[1] * 100}%` }}>
        <OffthreadVideo src={staticFile(src)} muted style={{ width: "100%", height: "100%" }} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
