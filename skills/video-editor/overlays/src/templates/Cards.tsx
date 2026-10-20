import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { Base, Card, CountUp, Dot, Placed, Words, useLife } from "../kit";
import { MARGIN, bare, pal, ramp, toneColors } from "../theme";

/* Lower: who or what is on screen. Kicker is optional context, title is the name. */
export type LowerProps = Base & { kicker?: string; title: string };
export const Lower: React.FC<LowerProps> = ({ kicker, title, anchor = "bottom-right", tone = "clean", offset }) => {
  const c = toneColors(tone);
  const t = useCurrentFrame();
  return (
    <Placed anchor={anchor} offset={offset}>
      <Card anchor={anchor} tone={tone} padding="20px 34px 22px 22px">
        <div style={{ display: "flex", alignItems: "center", gap: 22 }}>
          {bare(tone) ? null : (
            <div style={{ width: 58, height: 58, borderRadius: 15, background: c.chip, display: "grid", placeItems: "center", flex: "none" }}>
              <Dot color={c.accent} size={14} />
            </div>
          )}
          <div>
            {kicker ? (
              <div style={{ fontSize: 22, fontWeight: 500, color: c.soft, marginBottom: 2, opacity: ramp(t, 6, 18) }}>{kicker}</div>
            ) : null}
            <Words text={title} size={42} color={c.fg} accent={c.accent} at={5} />
          </div>
        </div>
      </Card>
    </Placed>
  );
};

/* Stat: 1 number from the transcript or cleared proof, with what it measures. */
export type StatProps = Base & { value: string; label: string; sub?: string };
export const Stat: React.FC<StatProps> = ({ value, label, sub, anchor = "top-right", tone = "clean", offset }) => {
  const c = toneColors(tone);
  const t = useCurrentFrame();
  return (
    <Placed anchor={anchor} offset={offset}>
      <Card anchor={anchor} tone={tone} padding="30px 40px 32px" style={{ minWidth: 380 }}>
        <div style={{ fontSize: 132, fontWeight: 600, letterSpacing: "-0.055em", lineHeight: 0.95, fontVariantNumeric: "tabular-nums" }}>
          <CountUp value={value} at={5} />
        </div>
        <div style={{ height: 3, borderRadius: 3, background: c.accent, margin: "20px 0 16px", width: `${ramp(t, 10, 30) * 100}%`, opacity: 0.9 }} />
        <Words text={label} size={32} weight={560} color={c.fg} accent={c.accent} at={12} stagger={2} />
        {sub ? <div style={{ fontSize: 22, color: c.soft, marginTop: 6, opacity: ramp(t, 18, 30) }}>{sub}</div> : null}
      </Card>
    </Placed>
  );
};

/* Keyword: the 1 idea of the sentence, 1 to 6 words, *serif* accent optional. */
export type KeywordProps = Base & { text: string; size?: number };
export const Keyword: React.FC<KeywordProps> = ({ text, size = 74, anchor = "top-center", tone = "clean", offset }) => {
  const c = toneColors(tone);
  const { width } = useVideoConfig();
  return (
    <Placed anchor={anchor} offset={offset}>
      <Card anchor={anchor} tone={tone} radius={30} padding="22px 40px 28px" style={{ maxWidth: Math.min(1300, width - 2 * MARGIN) }}>
        <Words text={text} size={size} color={c.fg} accent={c.accent} at={4} stagger={4} style={{ textAlign: "center" }} />
      </Card>
    </Placed>
  );
};

/* List: items build in sync with speech. `at` is seconds from the overlay start. */
export type ListProps = Base & { title?: string; items: { text: string; at?: number }[]; numbered?: boolean };
export const List: React.FC<ListProps> = ({ title, items, numbered = false, anchor = "right", tone = "clean", offset }) => {
  const c = toneColors(tone);
  const { t, fps } = useLife();
  return (
    <Placed anchor={anchor} offset={offset}>
      <Card anchor={anchor} tone={tone} padding="28px 36px 30px" style={{ width: 560 }}>
        {title ? <Words text={title} size={30} weight={560} color={c.soft} at={3} stagger={2} style={{ marginBottom: 16 }} /> : null}
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {items.map((item, i) => {
            const at = Math.round((item.at ?? 0.35 + i * 0.6) * fps);
            const p = ramp(t, at, at + 12);
            const flash = ramp(t, at, at + 6) * (1 - ramp(t, at + 10, at + 30));
            return (
              <div
                key={i}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 16,
                  opacity: p,
                  transform: `translateX(${(1 - p) * 26}px)`,
                  filter: p < 0.98 ? `blur(${(1 - p) * 8}px)` : undefined,
                }}
              >
                {bare(tone) ? (
                  <div style={{ width: 36, flex: "none", fontSize: 22, fontWeight: 600, color: c.soft, fontVariantNumeric: "tabular-nums" }}>
                    {String(i + 1).padStart(2, "0")}
                  </div>
                ) : (
                  <div
                    style={{
                      width: 36,
                      height: 36,
                      borderRadius: 10,
                      flex: "none",
                      display: "grid",
                      placeItems: "center",
                      fontSize: 19,
                      fontWeight: 600,
                      color: tone === "dark" ? pal.dark : pal.white,
                      background: c.accent,
                      transform: `scale(${1 + flash * 0.18})`,
                    }}
                  >
                    {numbered ? i + 1 : <Check color={tone === "dark" ? pal.dark : pal.white} />}
                  </div>
                )}
                <div style={{ fontSize: 33, fontWeight: 520, letterSpacing: "-0.025em", lineHeight: 1.15 }}>{item.text}</div>
              </div>
            );
          })}
        </div>
      </Card>
    </Placed>
  );
};

const Check: React.FC<{ color: string }> = ({ color }) => (
  <svg width="18" height="18" viewBox="0 0 18 18">
    <path d="M3.5 9.5l3.4 3.2L14.5 5" fill="none" stroke={color} strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

/* Chapter: section change. Number in the serif accent, title in the sans. */
export type ChapterProps = Base & { number?: string; title: string };
export const Chapter: React.FC<ChapterProps> = ({ number, title, anchor = "top-left", tone = "clean", offset }) => {
  const c = toneColors(tone);
  const t = useCurrentFrame();
  return (
    <Placed anchor={anchor} offset={offset}>
      <Card anchor={anchor} tone={tone} radius={26} padding="22px 40px 26px 30px">
        <div style={{ display: "flex", alignItems: "center", gap: 26 }}>
          {number ? (
            <div style={{ fontFamily: pal.serif, fontStyle: "italic", fontSize: 92, lineHeight: 0.9, color: c.accent, opacity: ramp(t, 3, 14), transform: `translateY(${(1 - ramp(t, 3, 18)) * 18}px)` }}>
              {number}
            </div>
          ) : null}
          {number ? <div style={{ width: 2, alignSelf: "stretch", background: c.chip, transform: `scaleY(${ramp(t, 6, 20)})` }} /> : null}
          <Words text={title} size={54} color={c.fg} accent={c.accent} at={8} stagger={3} style={{ maxWidth: 900 }} />
        </div>
      </Card>
    </Placed>
  );
};
