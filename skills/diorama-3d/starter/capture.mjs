// Capture the build and the loop frame by frame through window.renderAt, for encode.sh:
//   node capture.mjs <frames-dir> [fps=25] [scale=1] [page=scene.html]
// Draft at scale 1; scale 2 is sharper and takes about 4 min for 10 s on CPU WebGL.
import { mkdir } from 'fs/promises';
import { chromium } from 'playwright';
const [dir, fps = '25', scale = '1', page = 'scene.html'] = process.argv.slice(2);
if (!dir) { console.error('usage: node capture.mjs <frames-dir> [fps] [scale] [page]'); process.exit(1); }
await mkdir(dir, { recursive: true });
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const tab = await browser.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: Number(scale) });
await tab.goto(new URL(page, import.meta.url).href);
await tab.evaluate(() => document.fonts.ready);
const n = Math.round((await tab.evaluate(() => window.T_END)) * Number(fps));
const art = tab.locator('.pb-art');
for (let i = 0; i < n; i++) {
  await tab.evaluate((t) => window.renderAt(t), i / Number(fps));
  await art.screenshot({ path: `${dir}/f${String(i).padStart(4, '0')}.png` });
}
await browser.close();
console.log(`${n} frames in ${dir}`);
