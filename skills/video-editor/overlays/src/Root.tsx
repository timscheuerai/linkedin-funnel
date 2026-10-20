import React from "react";
import { CalculateMetadataFunction, Composition } from "remotion";
import "./theme";
import { Captions, Interlude } from "./templates/Captions";
import { Chapter, Keyword, List, Lower, Stat } from "./templates/Cards";
import { Focus, Media, Zoom } from "./templates/Screen";
import { H, W } from "./theme";

// Landscape designs at 1920 x 1080, portrait (shorts) at 1080 x 1920.
type Timed = Record<string, unknown> & { seconds?: number; fps?: number; orientation?: "landscape" | "portrait" };
const timed: CalculateMetadataFunction<Timed> = ({ props }) => {
  const fps = props.fps ?? 30;
  const portrait = props.orientation === "portrait";
  return {
    fps,
    durationInFrames: Math.max(1, Math.round((props.seconds ?? 3) * fps)),
    width: portrait ? H : W,
    height: portrait ? W : H,
  };
};

// Studio samples. Remotion merges these under the render props, so they hold
// ONLY required fields: an optional field here would leak sample text into a
// real render whenever a plan leaves it out.
const templates = [
  { id: "Lower", component: Lower, defaultProps: { seconds: 4, title: "Sample name" } },
  { id: "Stat", component: Stat, defaultProps: { seconds: 4, value: "00", label: "Sample label" } },
  { id: "Keyword", component: Keyword, defaultProps: { seconds: 3, text: "Sample *keyword*" } },
  {
    id: "List",
    component: List,
    defaultProps: {
      seconds: 6,
      items: [{ text: "Sample item" }, { text: "Sample item" }, { text: "Sample item" }],
    },
  },
  { id: "Chapter", component: Chapter, defaultProps: { seconds: 3, title: "Sample chapter" } },
  { id: "Media", component: Media, defaultProps: { seconds: 5, src: "sample/screenshot.png" } },
  { id: "Focus", component: Focus, defaultProps: { seconds: 4, rect: [0.1, 0.2, 0.3, 0.3] } },
  { id: "Zoom", component: Zoom, defaultProps: { seconds: 3, src: "sample/clip.mp4", scale: 1.6, focus: [0.7, 0.3], ease: 0.35 } },
  {
    id: "Interlude",
    component: Interlude,
    defaultProps: {
      seconds: 3,
      words: [
        { w: "90%", s: 0.2, e: 0.8 },
        { w: "of", s: 1.0, e: 1.2 },
        { w: "people", s: 1.3, e: 1.8 },
      ],
    },
  },
  {
    id: "Captions",
    component: Captions,
    defaultProps: {
      seconds: 4,
      words: [
        { w: "Sample", s: 0.2, e: 0.6 },
        { w: "caption", s: 0.7, e: 1.2 },
        { w: "words", s: 1.3, e: 2.0 },
      ],
    },
  },
] as const;

export const Root: React.FC = () => (
  <>
    {templates.map((t) => (
      <Composition
        key={t.id}
        id={t.id}
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        component={t.component as React.FC<any>}
        width={W}
        height={H}
        fps={30}
        durationInFrames={90}
        defaultProps={t.defaultProps as unknown as Timed}
        calculateMetadata={timed}
      />
    ))}
  </>
);
