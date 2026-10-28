# v2 teaser, 15.0 s, three aspects

The HooCode v2 teaser as three HyperFrames projects (`hyperframes@0.8.210`) built from one source.
The timeline (`shared/teaser.js`), the footage edit and the SFX times are shared; only the layout CSS
differs per aspect. Spec: `../teaser-15.md` (timecodes as built), `../direction.md`, `../score.md`.

| Output | Size |
|---|---|
| `out/v2/hoocode-teaser-9x16.mp4` | 1080x1920 |
| `out/v2/hoocode-teaser-1x1.mp4` | 1080x1080 |
| `out/v2/hoocode-teaser-16x9.mp4` | 1920x1080 |
| `out/v2/hoocode-teaser-<aspect>-poster.png` | frame 0 (the owl), lossless |

All 15.000 s, 450 frames, 30 fps, H.264 yuv420p CRF 16, AAC-LC 320 kb/s 48 kHz stereo, one score
(`out/v2/audio/teaser15.wav`, -14 LUFS).

## Files

| Path | What |
|---|---|
| `build.py` | **The edit.** Footage in-points (from `v2/recording/cues.json`), freezes, typed-char frames, SFX events. Writes everything below. |
| `events.json` | Generated. SFX cues for `v2/music/score.py` (same numbers as the picture, so they cannot drift). |
| `shared/template.html` | The composition markup (one DOM for all aspects). |
| `shared/teaser.css` | Brand tokens, shared styles, and the three layouts (`.a9x16`, `.a1x1`, `.a16x9`). |
| `shared/teaser.js` | The one GSAP timeline: cuts, camera (crop maths from the terminal grid), brackets, keycap, spark, lockup, type-on. |
| `shared/beats.js` | Generated. The edit's times for `teaser.js`. |
| `shared/stills/` | Generated. 4K freeze frames (`asks` frame 450, `tests` frame 739). |
| `shared/gsap.min.js` | GSAP 3.14.2 (standard no-charge licence, `GSAP-LICENSE.txt`), as in v1's teaser. |
| `9x16/`, `1x1/`, `16x9/` | The projects. `index.html` is generated (template + inline brand SVGs + inlined `beats.js`/`teaser.js`); `assets/` holds symlinks: `footage.mp4` -> `out/v2/hoocode-v2-4k.mp4`, `fonts` -> `v2/assets/fonts`, `shared`, `stills`. |

Three thin projects rather than three entry files in one: `lint`, `check` and `snapshot` work on a
project's `index.html`. Do not edit the generated `index.html`, `beats.js` or `events.json`; edit
`build.py` or `shared/*` and rebuild.

Brand: the owl is drawn from `v2/assets/brand/owl.txt` as quadrant rects on the TUI cell (29 x 65),
body `#FAFAFA`, eyes `#27272A` on frame 0 and `#00F0FF` from 0.5 (the JetBrains Mono woff has no
block-element glyphs). `symbol.svg` and `hoocode.svg` are inlined by `build.py` (the lockup's
`<style>` with the CSS blink and its background `<rect>` are removed; the timeline drives `.cursor`).

## Footage geometry

`out/v2/hoocode-v2-4k.mp4` is 3840x2160: the xterm grid is 117 x 32 cells of 29 x 65 px with its origin
at (224, 40). `teaser.js` places every crop and bracket in those cell coordinates (`cells(c0, c1, r0, r1)`).
The window shows 1570 px of source width on 9:16 and 1:1 (terminal text about 32 px tall) and 1680 px
on 16:9 (about 30 px). Footage in-points are computed so each cue's first frame (frame i shows cast
events at t <= i/30) lands on its beat, plus 4 ms so floor- and round-based seeks agree.

## Rebuild

From the repo root (`/home/user/hoocode-demo`). Chromium for HyperFrames: `/opt/pw-browsers/chromium`.

```bash
# 1. Generate projects, events.json, beats.js, stills
python3 v2/teaser15/build.py

# 2. Score (about 12 s); prints loudness. Only the SFX depend on the edit.
python3 v2/music/score.py --film teaser15 --events v2/teaser15/events.json

# 3. Per aspect: lint/check, render silent (about 1 min each), mux, poster
export PUPPETEER_EXECUTABLE_PATH=/opt/pw-browsers/chromium
for a in 9x16 1x1 16x9; do
  (cd v2/teaser15/$a &&
   npx -y hyperframes@0.8.210 lint &&
   npx -y hyperframes@0.8.210 render --output ../../../out/v2/teaser-$a-silent.mp4 \
     --fps 30 --quality high --video-frame-format png &&
   npx -y hyperframes@0.8.210 snapshot --no-end --at 0 -o ../../../out/v2/.poster-$a)
  cp out/v2/.poster-$a/frame-00-at-0s.png out/v2/hoocode-teaser-$a-poster.png && rm -r out/v2/.poster-$a
  ffmpeg -y -i out/v2/teaser-$a-silent.mp4 -i out/v2/audio/teaser15.wav -map 0:v -map 1:a \
    -c:v libx264 -crf 16 -preset slow -pix_fmt yuv420p -c:a aac -b:a 320k -ar 48000 \
    -movflags +faststart -shortest out/v2/hoocode-teaser-$a.mp4
done

# Full gate (lint + runtime + layout + motion + contrast), per project
(cd v2/teaser15/9x16 && npx -y hyperframes@0.8.210 check)
```

`--video-frame-format png` keeps the terminal text crisp (the default may extract JPEG frames).
Check: `ffprobe` shows 450 video frames and 15.000 s for video and audio; `ffmpeg -i <mp4> -af
ebur128=peak=true -f null -` reads -14.0 LUFS.

Preview: `cd v2/teaser15/<aspect> && npx -y hyperframes@0.8.210 preview --background`
(`--status`, `--stop`). Stills: `npx -y hyperframes@0.8.210 snapshot --at 1.5,4.5,6,7.5`.

## After a re-record

`assets/footage.mp4` follows the symlink. Run `build.py` again: it re-reads `cues.json`, asserts
that card 1 is up at 3.0 and card 2 is not yet up at 4.8, re-extracts the stills (delete
`shared/stills/*.png` first) and rewrites `events.json`. Then re-check the crops and bracket cells in
`teaser.js` (`SHOTS`) against the new frame: they assume the rows of this take (plan panel rows
25-28, card rows 27-31, `exit 0` row 13, `● LANDED` row 23).
