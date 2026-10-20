// Render the still of a diorama page: output/<page>.png (1x), @2x and -phone (390 px wide,
// how most people meet it in the feed). Uses a CPU WebGL context, because headless
// Chromium has none on many machines.
//   node render.mjs [page=scene.html]
import { chromium } from 'playwright';
import { mkdir } from 'fs/promises';
import { fileURLToPath } from 'url';
const page = process.argv[2] || 'scene.html';
const name = page.replace(/\.html$/, '');
const out = fileURLToPath(new URL('output/', import.meta.url));
await mkdir(out, { recursive: true });
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
for (const [scale, suffix] of [[1, ''], [2, '@2x'], [390 / 1080, '-phone']]) {
  const tab = await browser.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: scale });
  const errors = [];
  tab.on('pageerror', (e) => errors.push(e.message));
  await tab.goto(new URL(page, import.meta.url).href);
  await tab.evaluate(() => document.fonts.ready);
  if (errors.length) throw new Error(`${page}: ${errors.join('; ')}`);
  await tab.locator('.pb-art').screenshot({ path: `${out}${name}${suffix}.png` });
  await tab.close();
}
await browser.close();
console.log(`${name}: 1x, 2x and phone preview in ${out}`);
