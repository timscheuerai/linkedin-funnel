// node scripts/render.mjs <jobs.json> [--still] [--only id,id]
//
// Renders overlay and zoom jobs for the video-editor skill. Bundles once,
// then renders each job at the footage size (design space 1920 x 1080, or
// 1080 x 1920 for vertical footage).
//   overlays -> ProRes 4444 with alpha (.mov), straight alpha
//   Zoom     -> ProRes 422 HQ, opaque (.mov)
//   --still  -> 1 transparent PNG per job at its fully built frame
//
// jobs.json: { width, height, fps, jobs: [{ id, template, seconds, props, out }] }
// Any absolute `props.src` is staged into public/.jobs/ and rewritten to a
// staticFile path, so media never needs to live inside this folder.
import { bundle } from "@remotion/bundler";
import { renderMedia, renderStill, selectComposition } from "@remotion/renderer";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const args = process.argv.slice(2);
const jobsPath = args.find((a) => !a.startsWith("--"));
if (!jobsPath) {
  console.error("usage: node scripts/render.mjs <jobs.json> [--still] [--only id,id]");
  process.exit(2);
}
const still = args.includes("--still");
const onlyArg = args[args.indexOf("--only") + 1];
const only = args.includes("--only") ? new Set(onlyArg.split(",")) : null;

const spec = JSON.parse(fs.readFileSync(jobsPath, "utf8"));
const { width, height } = spec;
const fps = spec.fps ?? 30;
// Landscape designs at 1920 x 1080, portrait (shorts) at 1080 x 1920.
const portrait = height > width;
if (Math.abs(Math.max(width, height) / Math.min(width, height) - 16 / 9) > 0.01) {
  throw new Error(`footage must be 16:9 or 9:16, got ${width}x${height}`);
}
const orientation = portrait ? "portrait" : "landscape";
const scale = (portrait ? height : width) / 1920;
const jobs = spec.jobs.filter((j) => !only || only.has(j.id));

// Stage media. Hard link when possible (same volume), copy otherwise.
const stage = path.join(root, "public", ".jobs");
fs.rmSync(stage, { recursive: true, force: true });
fs.mkdirSync(stage, { recursive: true });
for (const job of jobs) {
  const src = job.props?.src;
  if (typeof src === "string" && path.isAbsolute(src)) {
    if (!fs.existsSync(src)) throw new Error(`${job.id}: media not found ${src}`);
    const name = crypto.createHash("sha1").update(src).digest("hex").slice(0, 12) + path.extname(src);
    const dest = path.join(stage, name);
    if (!fs.existsSync(dest)) {
      try {
        fs.linkSync(src, dest);
      } catch {
        fs.copyFileSync(src, dest);
      }
    }
    job.props = { ...job.props, src: `.jobs/${name}` };
  }
}

const serveUrl = await bundle({ entryPoint: path.join(root, "src/index.ts"), webpackOverride: (c) => c });
// A long batch can lose its browser midway; retry a failed job once, finish the rest, then report.
const failed = [];
const renderJob = async (job) => {
  const inputProps = { ...job.props, seconds: job.seconds, fps, orientation };
  const composition = await selectComposition({ serveUrl, id: job.template, inputProps });
  fs.mkdirSync(path.dirname(job.out), { recursive: true });
  const zoom = job.template === "Zoom";
  if (still) {
    const frame = Math.max(0, composition.durationInFrames - 12);
    const out = job.out.replace(/\.[a-z0-9]+$/i, ".png");
    await renderStill({ serveUrl, composition, inputProps, frame, output: out, imageFormat: "png", scale });
    console.log(`still ${job.id} ${out}`);
    return;
  }
  let last = -1;
  await renderMedia({
    serveUrl,
    composition,
    inputProps,
    outputLocation: job.out,
    codec: "prores",
    proResProfile: zoom ? "hq" : "4444",
    // BT.709 so the files match the master's tags and Resolve reads the brand
    // colours exactly; PNG frames because JPEG plus bt709 decodes darker.
    imageFormat: "png",
    colorSpace: "bt709",
    pixelFormat: zoom ? "yuv422p10le" : "yuva444p10le",
    scale,
    muted: true,
    concurrency: 6,
    timeoutInMilliseconds: 240000,
    onProgress: ({ progress }) => {
      const p = Math.floor(progress * 4);
      if (p !== last) {
        last = p;
        if (p > 0) console.log(`${job.id} ${p * 25}%`);
      }
    },
  });
  console.log(`done ${job.id} ${job.out}`);
};
for (const job of jobs) {
  try {
    await renderJob(job);
  } catch (err) {
    console.error(`retry ${job.id}: ${String(err).split("\n")[0]}`);
    try {
      await renderJob(job);
    } catch (err2) {
      console.error(`FAILED ${job.id}: ${String(err2).split("\n")[0]}`);
      failed.push(job.id);
    }
  }
}
if (failed.length) {
  console.error(`failed jobs: ${failed.join(",")}`);
  process.exit(1);
}
