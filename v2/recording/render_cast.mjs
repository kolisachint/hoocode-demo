#!/usr/bin/env node
// Render v2/recording/hoocode-v2.cast to 4K frames with xterm.js in headless Chromium,
// encode them with ffmpeg, and resolve the film cues from the terminal buffer.
//
// Frame i (t = i/30 s) shows the screen after every cast event with timestamp <= t. Events
// are written one at a time (each write awaited), so a cue's time is the timestamp of the
// first event after which the visible buffer matches. Frames are PNG (lossless) and go to
// $RENDER_WORK/frames; ffmpeg encodes them to out/v2.
//
// Usage (from the repo root; needs node, the playwright package, ffmpeg):
//   RENDER_WORK=<scratch dir> node v2/recording/render_cast.mjs [--max-frames N] [--no-encode]
//
// Env: RENDER_WORK  scratch dir for frames (default: <tmpdir>/hoocode-v2-render)
//      CHROME       chromium executable (default /opt/pw-browsers/chromium-1243/chrome-linux64/chrome)
import { createRequire } from 'node:module';
import { createServer } from 'node:http';
import { existsSync, mkdirSync, readFileSync, createReadStream, writeFileSync, rmSync, readdirSync, copyFileSync, statSync } from 'node:fs';
import { execFileSync, spawnSync } from 'node:child_process';
import { tmpdir } from 'node:os';
import { join, dirname, resolve, extname } from 'node:path';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '../..');
const REC = join(ROOT, 'v2/recording');
const VENDOR = join(REC, 'vendor');
const FONTS = join(ROOT, 'teaser/assets/fonts');
const CAST = join(REC, 'hoocode-v2.cast');
const TAPE = join(REC, 'hoocode-v2.tape');
const CUES = join(REC, 'cues.json');
const OUT = join(ROOT, 'out/v2');
const WORK = process.env.RENDER_WORK || join(tmpdir(), 'hoocode-v2-render');
const FRAMES = join(WORK, 'frames');
const CHROME = process.env.CHROME || '/opt/pw-browsers/chromium-1243/chrome-linux64/chrome';

const FPS = 30;
const COLS = 117;
const ROWS = 32;
const W = 3840;
const H = 2160;
const PAD_Y = 36; // top and bottom padding: the 32 rows fill H - 2 * PAD_Y

const argv = process.argv.slice(2);
const maxFramesArg = argv.indexOf('--max-frames');
const MAX_FRAMES = maxFramesArg >= 0 ? Number(argv[maxFramesArg + 1]) : Infinity;
const NO_ENCODE = argv.includes('--no-encode');

// The theme is the tape's `Set Theme` JSON, so the terminal and the tape agree.
const tapeTheme = JSON.parse(readFileSync(TAPE, 'utf8').match(/^Set Theme (\{.*\})\s*$/m)[1]);
const THEME = {
  background: tapeTheme.background,
  foreground: tapeTheme.foreground,
  cursor: tapeTheme.cursor,
  cursorAccent: tapeTheme.cursorAccent,
  selectionBackground: tapeTheme.selection,
  black: tapeTheme.black, red: tapeTheme.red, green: tapeTheme.green, yellow: tapeTheme.yellow,
  blue: tapeTheme.blue, magenta: tapeTheme.magenta, cyan: tapeTheme.cyan, white: tapeTheme.white,
  brightBlack: tapeTheme.brightBlack, brightRed: tapeTheme.brightRed, brightGreen: tapeTheme.brightGreen,
  brightYellow: tapeTheme.brightYellow, brightBlue: tapeTheme.brightBlue, brightMagenta: tapeTheme.brightMagenta,
  brightCyan: tapeTheme.brightCyan, brightWhite: tapeTheme.brightWhite,
};

const PAGE = `<!doctype html>
<html><head><meta charset="utf-8">
<link rel="stylesheet" href="/vendor/xterm.css">
<style>
@font-face { font-family: "JetBrains Mono"; src: url("/fonts/jetbrains-mono-latin-400-normal.woff") format("woff"); font-weight: 400; }
@font-face { font-family: "JetBrains Mono"; src: url("/fonts/jetbrains-mono-latin-700-normal.woff") format("woff"); font-weight: 700; }
html, body { margin: 0; padding: 0; background: ${THEME.background}; width: ${W}px; height: ${H}px; overflow: hidden; }
#term { position: absolute; left: 0; top: 0; }
</style></head>
<body><div id="term"></div>
<script src="/vendor/xterm.js"></script>
<script src="/vendor/addon-webgl.js"></script>
</body></html>`;

// ---- static server: the page, the vendored xterm files, the teaser JetBrains Mono fonts ----
const TYPES = { '.js': 'text/javascript', '.css': 'text/css', '.woff': 'font/woff', '.html': 'text/html' };
const server = createServer((req, res) => {
  if (req.url === '/') {
    res.setHeader('content-type', 'text/html; charset=utf-8');
    return res.end(PAGE);
  }
  const m = req.url.match(/^\/(vendor|fonts)\/([\w.-]+)$/);
  const file = m && join(m[1] === 'vendor' ? VENDOR : FONTS, m[2]);
  if (!file || !existsSync(file)) {
    res.statusCode = 404;
    return res.end();
  }
  res.setHeader('content-type', TYPES[extname(file)] || 'application/octet-stream');
  createReadStream(file).pipe(res);
});
await new Promise((ok) => server.listen(0, '127.0.0.1', ok));
const origin = `http://127.0.0.1:${server.address().port}`;

// ---- cast ----
const lines = readFileSync(CAST, 'utf8').split('\n').filter((l) => l.trim());
const header = JSON.parse(lines[0]);
if (header.width !== COLS || header.height !== ROWS) throw new Error(`cast is ${header.width}x${header.height}, want ${COLS}x${ROWS}`);
const events = lines.slice(1).map((l) => JSON.parse(l)).filter((e) => e[1] === 'o');
const lastT = events[events.length - 1][0];
const N = Math.ceil((lastT + 0.5) * FPS - 1e-9); // duration = last event + 0.5 s, whole frames
const FRAMES_TO_RENDER = Math.min(N, MAX_FRAMES);

// ---- cues: [name, mode, patterns, after] ----
// mode 'first': the first event after which every pattern matches (after the `after` cue fired).
// mode 'gone':  the first event after which the pattern, seen before, no longer matches.
const CUE_DEFS = [
  { name: 'ENTER', mode: 'gone', pats: [/^\$ hoocode "Add/m] },
  { name: 'TUI', mode: 'first', pats: [/HOOCODE/] },
  { name: 'PLANTEXT', mode: 'first', pats: [/Plan: read the/] },
  { name: 'PLAN', mode: 'first', pats: [/TodoWrite\s+4 items · 0 done/] },
  { name: 'PANEL', mode: 'first', pats: [/Reading the stats command/] },
  { name: 'READ', mode: 'first', pats: [/Read\s+src\/main\.rs/] },
  { name: 'CARD1', mode: 'first', pats: [/BUILD asks for Edit/] },
  { name: 'KEYS', mode: 'first', pats: [/y go, once/] },
  { name: 'Y1', mode: 'gone', pats: [/BUILD asks for Edit/], after: 'CARD1' },
  { name: 'CARD2', mode: 'first', pats: [/BUILD asks for Shell/], after: 'Y1' },
  { name: 'ALWAYS', mode: 'first', pats: [/always cargo in this session/], after: 'CARD2' },
  { name: 'A2', mode: 'gone', pats: [/BUILD asks for Shell/], after: 'CARD2' },
  { name: 'HIT', mode: 'first', pats: [/ HIT /], after: 'A2' },
  { name: 'EXIT101', mode: 'first', pats: [/exit 101/], after: 'A2' },
  { name: 'HIT_END', mode: 'gone', pats: [/exit 101/], after: 'EXIT101' },
  { name: 'FIXTEXT', mode: 'first', pats: [/The JSON has spaces/], after: 'EXIT101' },
  { name: 'CARD3', mode: 'first', pats: [/BUILD asks for Edit/], after: 'Y1' },
  { name: 'Y3', mode: 'gone', pats: [/BUILD asks for Edit/], after: 'CARD3' },
  { name: 'EXIT0', mode: 'first', pats: [/exit 0\b/], after: 'HIT_END' },
  { name: 'OK', mode: 'first', pats: [/test result: ok\. 2 passed/], after: 'EXIT0' },
  { name: 'DONE', mode: 'first', pats: [/4 items · 4 done/], after: 'EXIT0' },
  { name: 'LANDED', mode: 'first', pats: [/● LANDED/], after: 'EXIT0' },
  { name: 'LANDFRAME', mode: 'first', pats: [/LANDED/, /name your mission/], after: 'EXIT0' },
];
const NO_Y = new Set(['ENTER', 'Y1', 'A2', 'HIT_END', 'Y3']); // gone cues and text-only ones
const fired = {}; // name -> { t, y, row }
const seenGone = {};
const cueLog = [];

function checkCues(t, rowsText) {
  const text = rowsText.join('\n');
  for (const d of CUE_DEFS) {
    if (fired[d.name]) continue;
    if (d.after && !fired[d.after]) continue;
    const ok = d.pats.every((p) => p.test(text));
    if (d.mode === 'first') {
      if (!ok) continue;
      const row = rowsText.findIndex((line) => d.pats[0].test(line));
      fired[d.name] = { t, row, text: (rowsText[row] || '').trim() };
      cueLog.push(`${d.name} ${t.toFixed(3)}s row ${row}`);
    } else {
      if (ok) seenGone[d.name] = true;
      else if (seenGone[d.name]) {
        fired[d.name] = { t, row: -1 };
        cueLog.push(`${d.name} ${t.toFixed(3)}s (gone)`);
      }
    }
  }
}

function visibleRows(term) {
  const b = term.buffer.active;
  const out = [];
  for (let r = 0; r < ROWS; r++) out.push(b.getLine(b.viewportY + r)?.translateToString(true) ?? '');
  return out;
}

// ---- browser ----
const browser = await chromium.launch({
  executablePath: CHROME,
  args: ['--enable-webgl', '--ignore-gpu-blocklist', '--force-device-scale-factor=1'],
});
const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
page.on('pageerror', (e) => console.error('page error:', e.message));
await page.goto(origin + '/');

const setup = await page.evaluate(
  async ({ cols, rows, theme, fontFamily, padY, W, H }) => {
    await document.fonts.load('400 50px "JetBrains Mono"');
    await document.fonts.load('700 50px "JetBrains Mono"');
    await document.fonts.ready;
    const frame = () => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    const cell = (term) => term._core._renderService.dimensions.css.cell;

    // xterm rejects lineHeight < 1, and its cell height is ceil(glyph box x lineHeight). The
    // glyph box is ~1.32 em, so 32 rows at 53.7 px (cell 71 px, 2272 px tall) cannot fit in 2160 px.
    // The rows fill the height instead: lineHeight 1 and the font size solved so that
    // ceil(cell height) = floor((H - 2 padY) / rows). The 117 columns then span less than the width.
    const term = new window.Terminal({
      cols, rows, fontFamily, theme,
      fontSize: 50, lineHeight: 1, scrollback: 0, cursorBlink: false,
      allowProposedApi: true,
    });
    term.open(document.getElementById('term'));
    const targetCellH = Math.floor((H - 2 * padY) / rows);
    for (let k = 0; k < 5; k++) {
      await frame();
      term.options.fontSize = term.options.fontSize * ((targetCellH - 0.01) / cell(term).height);
    }
    await frame();

    let renderer = 'dom';
    try {
      const addon = new window.WebglAddon.WebglAddon();
      addon.onContextLoss(() => addon.dispose());
      term.loadAddon(addon);
      renderer = 'webgl';
    } catch (e) {
      renderer = 'dom (webgl failed: ' + e.message + ')';
    }
    await frame();

    const c = cell(term);
    const el = document.getElementById('term');
    const left = Math.round((W - cols * c.width) / 2 * 100) / 100;
    const top = Math.round((H - rows * c.height) / 2 * 100) / 100;
    el.style.left = left + 'px';
    el.style.top = top + 'px';
    await frame();
    window.__term = term;
    return {
      renderer, fontSize: term.options.fontSize, lineHeight: term.options.lineHeight,
      cellW: c.width, cellH: c.height, left, top,
      gridW: cols * c.width, gridH: rows * c.height,
    };
  },
  { cols: COLS, rows: ROWS, theme: THEME, fontFamily: '"JetBrains Mono", "DejaVu Sans Mono", monospace', padY: PAD_Y, W, H },
);
console.log('setup', JSON.stringify(setup));
const rowFrac = (row) => (setup.top + (row + 0.5) * setup.cellH) / H;

// ---- frames ----
rmSync(WORK, { recursive: true, force: true });
mkdirSync(FRAMES, { recursive: true });
const write = (data) => page.evaluate((d) => new Promise((r) => window.__term.write(d, r)), data);
const settle = () => page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));

const rowsNow = () => page.evaluate(() => {
  const b = window.__term.buffer.active;
  const out = [];
  for (let r = 0; r < window.__term.rows; r++) out.push(b.getLine(b.viewportY + r)?.translateToString(true) ?? '');
  return out;
});

let ei = 0;
let rowsLanded = [];
const t0 = Date.now();
for (let i = 0; i < FRAMES_TO_RENDER; i++) {
  const t = i / FPS;
  while (ei < events.length && events[ei][0] <= t + 1e-9) {
    const ev = events[ei];
    await write(ev[2]);
    // Cue times come from the cast: check the buffer after each event.
    const rows = await rowsNow();
    if (!fired.LANDED && rows.some((l) => /● LANDED/.test(l))) rowsLanded = rows;
    checkCues(ev[0], rows);
    ei++;
  }
  await page.evaluate(() => window.__term.refresh(0, window.__term.rows - 1));
  await settle();
  await page.screenshot({ path: join(FRAMES, `f${String(i).padStart(5, '0')}.png`), type: 'png' });
  if (i % 60 === 0) console.log(`frame ${i}/${FRAMES_TO_RENDER} t=${t.toFixed(2)}s`);
}
console.log(`rendered ${FRAMES_TO_RENDER} frames in ${((Date.now() - t0) / 1000).toFixed(1)} s`);
await browser.close();
server.close();

// ---- cues.json ----
if (FRAMES_TO_RENDER === N) {
  const cues = {};
  for (const d of CUE_DEFS) {
    const f = fired[d.name];
    if (!f) throw new Error(`cue ${d.name} never fired`);
    cues[d.name] = Math.round(f.t * 1000) / 1000;
    if (!NO_Y.has(d.name)) cues[`${d.name}_y`] = Math.round(rowFrac(f.row) * 1000) / 1000;
  }
  // The landing line as drawn (the transcript's last line, trimmed).
  const landedLine = rowsLanded.find((l) => /● LANDED/.test(l)) || '';
  cues.LANDED_text = landedLine.trim();
  cues.END = Math.round(((N - 1) / FPS) * 1000) / 1000;
  const duration = Math.round((N / FPS) * 1000) / 1000;
  cues.HIT_visible_s = Math.round((fired.HIT_END.t - fired.HIT.t) * 1000) / 1000;
  cues.clip_duration = duration;
  cues.fps = FPS;
  cues.size = [W, H];
  cues.notes = 'Times are clip seconds at the first cast event after which the visible terminal buffer matches (exact, from the cast). Gone cues (ENTER, Y1, A2, HIT_END, Y3) are the event where the text disappears. *_y is the row centre as a fraction of the 4K frame height, including the top padding. HIT_visible_s = HIT_END - HIT.';
  writeFileSync(CUES, JSON.stringify(cues, null, 2) + '\n');
  console.log(cueLog.join('\n'));
  console.log(`wrote ${CUES}`);
}

// ---- encode ----
if (!NO_ENCODE) {
  mkdirSync(OUT, { recursive: true });
  const seq = join(FRAMES, 'f%05d.png');
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(FPS), '-i', seq, '-r', String(FPS),
    '-c:v', 'libx264', '-crf', '14', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
    join(OUT, 'hoocode-v2-4k.mp4')], { stdio: 'inherit' });
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(FPS), '-i', seq, '-r', String(FPS),
    '-vf', 'scale=1920:1080:flags=lanczos', '-c:v', 'libx264', '-crf', '16', '-preset', 'slow', '-pix_fmt', 'yuv420p',
    '-movflags', '+faststart', join(OUT, 'hoocode-v2.mp4')], { stdio: 'inherit' });
  // A decode pass catches a broken encode (the first 4K encode here decoded with NAL errors).
  for (const f of ['hoocode-v2-4k.mp4', 'hoocode-v2.mp4']) {
    const r = spawnSync('ffmpeg', ['-v', 'error', '-i', join(OUT, f), '-f', 'null', '-'], { encoding: 'utf8' });
    if (r.status !== 0 || r.stderr.trim()) throw new Error(`${f} does not decode cleanly: ${r.stderr.slice(0, 300)}`);
  }
  console.log(`wrote ${join(OUT, 'hoocode-v2-4k.mp4')} and hoocode-v2.mp4 (decode checked)`);
}
