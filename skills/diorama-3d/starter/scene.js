// 3D diorama starter: a slab, 1 belt, 3 stations, 1 worker toy per station and HTML labels
// projected from 3D anchors. Copy the folder, then replace STATIONS, the copy in scene.html
// and the toys. renderAt(t) poses any frame: the header, the slab, the stations and the CTA
// build in reading order by B.cta + IN (about 2.3 s), then the line runs on a seamless T_LOOP.
// The still is renderAt(STILL_T); the GIF plays 0 to T_END and restarts on the empty stage.
// Lineage: the 3D lead-magnet graphics behind LinkedIn Funnel (a team room, a lead factory, a graphics press).
import * as THREE from 'three';
import { RoundedBoxGeometry } from './vendor/RoundedBoxGeometry.js';
import { RoomEnvironment } from './vendor/RoomEnvironment.js';

// ---------- what the diorama says: 1 entry per station, left to right along the belt ----------
const STATIONS = [
  { name: 'Collect', lines: ['Pull the raw list', 'Keep the source on every row'] },
  { name: 'Qualify', lines: ['Score fit with evidence', 'Drop what does not fit'] },
  { name: 'Reach out', lines: ['Draft in your voice', 'Send after your OK'] },
];

const stage = document.querySelector('.stage');
const W = stage.clientWidth, H = stage.clientHeight;
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(W, H);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.NeutralToneMapping; // keeps brand hex close to the token
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
stage.prepend(renderer.domElement);
const scene = new THREE.Scene();
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
scene.environmentIntensity = 0.5;

// ---------- palette: read from scene.css, so the 3D matches the type ----------
const css = getComputedStyle(document.documentElement);
const tok = (name, fallback) => css.getPropertyValue(name).trim() || fallback;
const C = {
  ink: tok('--d-ink', '#1F2622'), accent: tok('--d-accent', '#18392A'), soft: tok('--d-accent-soft', '#E1EADB'),
  slab: tok('--d-slab', '#FCFBF8'), raw: tok('--d-raw', '#C9CCC8'), steel: tok('--d-steel', '#3A4741'),
  belt: tok('--d-belt', '#2D3D35'), toy: tok('--d-toy', '#D97757'),
};

// ---------- helpers ----------
const std = (color, o = {}) => new THREE.MeshStandardMaterial({ color, roughness: 0.55, metalness: 0, ...o });
const gloss = (color) => new THREE.MeshPhysicalMaterial({ color, roughness: 0.4, clearcoat: 0.4, clearcoatRoughness: 0.25 });
function add(mesh, x, y, z, parent = scene) {
  mesh.position.set(x, y, z); mesh.castShadow = true; mesh.receiveShadow = true; parent.add(mesh); return mesh;
}
function box(w, h, d, mat, x, y, z, r = 0.04, parent) {
  const g = r > 0 ? new RoundedBoxGeometry(w, h, d, 3, Math.min(r, w / 2, h / 2, d / 2)) : new THREE.BoxGeometry(w, h, d);
  return add(new THREE.Mesh(g, typeof mat === 'string' ? std(mat) : mat), x, y, z, parent);
}
function cyl(rt, rb, h, mat, x, y, z, seg = 32, parent) {
  return add(new THREE.Mesh(new THREE.CylinderGeometry(rt, rb, h, seg), typeof mat === 'string' ? std(mat) : mat), x, y, z, parent);
}
function canvasTex(w, h, draw) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t;
}
function seeded(seed) { return () => (seed = (seed * 16807) % 2147483647) / 2147483647; }
// a screen of code-like lines on dark glass; emissive so it glows
function screenTex(seed, bg = '#132019', ink = ['#9FD3A9', '#E1EADB', '#6FAF82']) {
  const rnd = seeded(seed);
  return canvasTex(256, 160, (g, w, h) => {
    g.fillStyle = bg; g.fillRect(0, 0, w, h);
    for (let y = 18; y < h - 10; y += 16) {
      let x = 16 + Math.floor(rnd() * 3) * 14;
      for (let i = 0, n = 1 + Math.floor(rnd() * 3); i < n; i++) {
        const len = 20 + rnd() * 70; g.fillStyle = ink[Math.floor(rnd() * ink.length)];
        g.globalAlpha = 0.85; g.fillRect(x, y, len, 6); x += len + 10;
      }
    }
  });
}

// ---------- plan in screen space: sx runs left to right on screen, h from the back (-) to the front (+) ----------
const CAM_DIR = new THREE.Vector3(0.492, 0.643, 0.587).normalize(); // from the front right, about 40 degrees down
const AZ = Math.atan2(CAM_DIR.x, CAM_DIR.z), CA = Math.cos(AZ), SA = Math.sin(AZ);
const P = (sx, h, y = 0) => new THREE.Vector3(CA * sx + SA * h, y, -SA * sx + CA * h);
const FACE = AZ * 0.85; // toys and products turn most of the way to the viewer
// the line runs diagonally, from the back left to the front right: S(s, off, y) is s along the belt
// and off across it (+ toward the viewer); a group turned by ROT has its local x along the belt
const SPAN = 11, PHI = 0.42, CP = Math.cos(PHI), SP = Math.sin(PHI);
const S = (s, off = 0, y = 0) => P(-CP * SPAN / 2 + CP * s - SP * off, -SP * SPAN / 2 + SP * s + CP * off, y);
const ROT = AZ - PHI;

// ---------- the build: when each part arrives (s); RUN is when the line starts ----------
const T_LOOP = 6; // the period of every running motion (use divisors of it for faster beats)
const B = { slab: 0.3, belt: 0.5, st: STATIONS.map((_, i) => 0.7 + i * 0.25), run: 1.5, cta: 1.9 };
const IN = 0.4; // how long each part takes to arrive
const T_END = B.run + T_LOOP; // the GIF: build, 1 full loop, restart on the empty stage
const STILL_T = B.run + T_LOOP * 0.6;
const ease = (u) => { u = Math.min(1, Math.max(0, u)); return 1 - Math.pow(1 - u, 3); }; // ease-out, no bounce
const BUILD = [];
// dyn: updateActors sets the object's y every frame before applyBuild, which then adds the drop;
// leave it false when only a child moves, or the drop accumulates frame after frame
function built(obj, t, { drop = 1.4, dyn = false } = {}) { BUILD.push({ obj, t, drop, dyn, y: obj.position.y, s: obj.scale.clone() }); return obj; }
function applyBuild(t) {
  for (const b of BUILD) {
    const p = ease((t - b.t) / IN);
    b.obj.visible = p > 0.001;
    if (!b.dyn) b.obj.position.y = b.y;
    b.obj.position.y += (1 - p) * b.drop;
    b.obj.scale.copy(b.s).multiplyScalar(Math.max(0.001, 0.35 + 0.65 * p));
  }
}

// ---------- the slab: a diorama base under the whole line ----------
const SLAB = { w: SPAN + 2.2, d: 3.3, off: 0.25 };
const slab = new THREE.Group(); scene.add(slab);
box(SLAB.w, 0.5, SLAB.d, C.slab, 0, -0.25, 0, 0.12, slab);
box(SLAB.w + 0.04, 0.08, SLAB.d + 0.04, C.soft, 0, -0.52, 0, 0.04, slab);
slab.position.copy(S(SPAN / 2, SLAB.off)); slab.rotation.y = ROT;
built(slab, B.slab, { drop: 0.8 });

// ---------- the belt and what rides it ----------
const BELT_Y = 0.62;
const LINE = [S(0), S(SPAN)];
const pathLen = (pts) => pts.reduce((s, p, i) => (i ? s + p.distanceTo(pts[i - 1]) : 0), 0);
function along(points, d) {
  for (let i = 0; i < points.length - 1; i++) {
    const a = points[i], b = points[i + 1], L = a.distanceTo(b);
    if (d <= L || i === points.length - 2) return { p: a.clone().lerp(b, Math.min(1, d / L)), dir: b.clone().sub(a).normalize() };
    d -= L;
  }
}
function conveyor(points, w = 0.62, y = BELT_Y) {
  const out = new THREE.Group(); scene.add(out);
  for (let i = 0; i < points.length - 1; i++) {
    const a = points[i], b = points[i + 1], d = b.clone().sub(a), L = Math.hypot(d.x, d.z);
    const g = new THREE.Group(); g.position.set((a.x + b.x) / 2, 0, (a.z + b.z) / 2); g.rotation.y = Math.atan2(-d.z, d.x); out.add(g);
    box(L + w, 0.1, w, C.belt, 0, y, 0, 0.03, g);
    for (const s of [-1, 1]) box(L + w, 0.07, 0.06, C.ink, 0, y + 0.08, s * (w / 2 + 0.02), 0.02, g);
    for (let k = 0, n = Math.max(1, Math.round(L / 1.3)); k <= n; k++) {
      for (const s of [-1, 1]) box(0.06, y, 0.06, C.steel, -L / 2 + (L * k) / n, y / 2, s * (w / 2 - 0.06), 0.02, g);
    }
  }
  return out;
}
built(conveyor(LINE), B.belt, { drop: 0.6 });

// products change colour at each station: raw, then the soft accent, then the accent
const STAGE_COLOURS = [C.raw, C.soft, C.accent, C.accent];
function product(colour) { const g = new THREE.Group(); box(0.34, 0.26, 0.34, gloss(colour), 0, 0.13, 0, 0.05, g); scene.add(g); return g; }
const items = [];
const GAP = 1.1, SPEED = (SPAN * 2) / T_LOOP; // 2 belt lengths a loop keeps the stream seamless
const N = Math.round((SPEED * T_LOOP) / GAP);
for (let i = 0; i < N; i++) items.push(STAGE_COLOURS.map((c) => product(c)));
const stationAt = STATIONS.map((_, i) => (SPAN * (i + 1)) / (STATIONS.length + 1)); // s of each station
function updateStreams(t) {
  const tr = t - B.run; // the belt starts empty and fills from the left
  items.forEach((variants, i) => {
    const d = (((SPEED * tr - i * GAP) % (N * GAP)) + N * GAP) % (N * GAP);
    const on = tr > 0 && d <= SPEED * tr && d < SPAN;
    const k = stationAt.filter((s) => d > s).length; // stations passed so far
    variants.forEach((m, j) => {
      m.visible = on && j === k;
      if (!m.visible) return;
      m.position.copy(S(d, 0, BELT_Y + 0.05)); m.rotation.y = FACE;
    });
  });
}

// ---------- the stations: a machine and a worker toy each ----------
const machines = [], toys = [];
function machine(i) {
  const g = new THREE.Group(); g.position.copy(S(stationAt[i], -0.15)); g.rotation.y = ROT; scene.add(g);
  box(1.5, 2.1, 0.3, C.slab, 0, 1.05, -0.62, 0.08, g); // back wall
  box(1.5, 0.8, 1.3, C.slab, 0, 1.6, -0.1, 0.1, g); // the hood: products pass underneath
  box(1.54, 0.14, 1.34, C.accent, 0, 2.07, -0.1, 0.05, g);
  const tex = screenTex(11 + i * 7);
  const scr = new THREE.Mesh(new THREE.PlaneGeometry(0.9, 0.5),
    new THREE.MeshStandardMaterial({ map: tex, emissive: '#ffffff', emissiveMap: tex, emissiveIntensity: 0.9, roughness: 0.3 }));
  scr.position.set(0, 1.6, 0.56); g.add(scr);
  const lamp = cyl(0.12, 0.12, 0.14, new THREE.MeshStandardMaterial({ color: C.soft, emissive: C.soft, emissiveIntensity: 0.6 }), 0.5, 2.22, 0.3, 24, g);
  machines.push({ g, lamp });
  built(g, B.st[i]);
}
// a glossy toy with 2 eyes; swap for the real marks of the agents or tools in the story
function toy(colour, scale = 1) {
  const g = new THREE.Group(); const body = new THREE.Group(); g.add(body);
  box(0.62, 0.7, 0.5, gloss(colour), 0, 0.5, 0, 0.22, body);
  const eye = std('#141414', { roughness: 0.3 });
  for (const x of [-0.12, 0.12]) box(0.07, 0.14, 0.04, eye, x, 0.6, 0.26, 0.02, body);
  g.scale.setScalar(scale); scene.add(g);
  return { g, body };
}
STATIONS.forEach((_, i) => {
  machine(i);
  const t = toy(C.toy, 0.9); t.g.position.copy(S(stationAt[i] + 0.55, 1.25)); t.g.rotation.y = FACE;
  toys.push(t); built(t.g, B.st[i] + 0.2, { drop: 1.2 }); // updateActors moves t.body, not t.g
});

function updateActors(t) {
  const T = Math.max(0, t - B.run); // the line moves once it runs
  toys.forEach((k, i) => {
    const ph = T * (Math.PI * 2 / (T_LOOP / 3)) + i * 1.3; // 3 beats a loop: seamless
    k.body.position.y = Math.max(0, Math.sin(ph)) * 0.08;
    k.body.rotation.x = Math.sin(ph) * 0.06;
  });
  machines.forEach((m, i) => { m.lamp.material.emissiveIntensity = 0.5 + 0.5 * Math.max(0, Math.sin(T * Math.PI * 2 / (T_LOOP / 2) + i)); });
}

// ---------- light ----------
scene.add(new THREE.HemisphereLight('#FFFFFF', '#BDBDBD', 0.95));
const sun = new THREE.DirectionalLight('#FFFFFF', 2.0);
sun.position.set(-8, 17, 9); scene.add(sun.target);
sun.castShadow = true; sun.shadow.mapSize.set(4096, 4096);
Object.assign(sun.shadow.camera, { left: -13, right: 13, top: 13, bottom: -13, near: 1, far: 60 });
sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.02; sun.shadow.radius = 4;
scene.add(sun);
const fill = new THREE.DirectionalLight('#F3F0FF', 0.5); fill.position.set(12, 7, 10); scene.add(fill);

// ---------- camera: orthographic, fitted to the points that must show ----------
const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.1, 200);
camera.position.copy(CAM_DIR).multiplyScalar(60); camera.lookAt(0, 0, 0); camera.updateMatrixWorld();
function fit(points, pad = 0.2) {
  const v = points.map((p) => p.clone().applyMatrix4(camera.matrixWorldInverse));
  const l = Math.min(...v.map((p) => p.x)) - pad, r = Math.max(...v.map((p) => p.x)) + pad;
  const b = Math.min(...v.map((p) => p.y)) - pad, t = Math.max(...v.map((p) => p.y)) + pad;
  const cx = (l + r) / 2, cy = (b + t) / 2;
  let hw = (r - l) / 2, hh = (t - b) / 2;
  if (hw / hh > W / H) hh = hw * H / W; else hw = hh * W / H;
  Object.assign(camera, { left: cx - hw, right: cx + hw, top: cy + hh, bottom: cy - hh });
  camera.updateProjectionMatrix();
}
{ // the slab's corners, its underside, and room above each station for its card
  const pts = [];
  for (const a of [-1, 1]) for (const b of [-1, 1]) pts.push(S(SPAN / 2 + a * SLAB.w / 2, SLAB.off + b * SLAB.d / 2, -0.55));
  stationAt.forEach((s) => pts.push(S(s, -0.15, 3.6)));
  fit(pts);
}

// ---------- labels: every word is HTML, projected from a 3D anchor and nudged apart ----------
const layer = document.querySelector('.labels');
const leaders = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
leaders.setAttribute('class', 'leaders'); leaders.setAttribute('viewBox', `0 0 ${W} ${H}`); layer.appendChild(leaders);
const proj = (v) => { const p = v.clone().project(camera); return [(p.x + 1) / 2 * W, (1 - p.y) / 2 * H]; };
const placed = [], HTML_AT = []; // [element, time it arrives]
function label(t, html, cls, pt, anchor = 'bottom', [dx, dy] = [0, 0], avoid = true) {
  const [ax, ay] = proj(pt);
  const el = document.createElement('div'); el.className = `lbl ${cls} a-${anchor}`; el.innerHTML = html; layer.appendChild(el);
  const w = el.offsetWidth + 6, h = el.offsetHeight + 4;
  let px = ax + dx, py = ay + dy;
  const rect = () => {
    const l = anchor === 'right' ? px - w : anchor === 'left' ? px : px - w / 2;
    const tp = anchor === 'top' ? py : anchor === 'bottom' ? py - h : py - h / 2;
    return [l, tp, l + w, tp + h];
  };
  const hits = () => placed.some((q) => { const r = rect(); return r[0] < q[2] && r[2] > q[0] && r[1] < q[3] && r[3] > q[1]; });
  if (avoid) for (let k = 0; k < 40 && hits(); k++) py -= 5;
  placed.push(rect());
  el.style.left = px + 'px'; el.style.top = py + 'px';
  if (Math.abs(py - (ay + dy)) > 6) { // moved: draw a leader back to the anchor
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    Object.entries({ x1: ax, y1: ay + dy, x2: px, y2: py }).forEach(([k, v]) => line.setAttribute(k, v));
    const dot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    Object.entries({ cx: ax, cy: ay + dy, r: 3 }).forEach(([k, v]) => dot.setAttribute(k, v));
    leaders.append(line, dot);
  }
  HTML_AT.push([el, t]);
  return el;
}
const card = (n, s) => `<i>${n}</i><div><b>${s.name}</b><ul>${s.lines.map((l) => `<li>${l}</li>`).join('')}</ul></div>`;
STATIONS.forEach((s, i) => label(B.st[i] + 0.15, card(i + 1, s), 'station', S(stationAt[i], -0.15, 2.45), 'bottom', [0, -6]));
label(B.belt + 0.2, 'in', 'tag', S(0, 0, BELT_Y + 0.2), 'right', [-10, 0], false);
label(B.belt + 0.2, 'out', 'tag', S(SPAN, 0, BELT_Y + 0.2), 'left', [10, 0], false);
// the page around the stage builds too: header first, the CTA last
[...document.querySelectorAll('[data-build]')].forEach((el) => HTML_AT.push([el, el.dataset.build === 'cta' ? B.cta : Number(el.dataset.build)]));
function updateHTML(t) {
  for (const [el, t0] of HTML_AT) { const p = ease((t - t0) / IN); el.style.opacity = p; el.style.translate = `0 ${(1 - p) * 16}px`; }
  leaders.style.opacity = ease((t - B.cta) / IN);
}

window.renderAt = (t) => { updateStreams(t); updateActors(t); applyBuild(t); updateHTML(t); renderer.render(scene, camera); };
window.T_END = T_END;
window.renderAt(STILL_T);
