# trailer60: the 60 s HooCode v2 launch trailer

HyperFrames project (pinned `hyperframes@0.8.210`). 1920x1080, 30 fps, 60.0 s (1800 frames).
Spec as built: [`../trailer-60.md`](../trailer-60.md); look: [`../direction.md`](../direction.md);
music: [`../score.md`](../score.md).

Output: `out/v2/hoocode-trailer-60s.mp4` (H.264 High, yuv420p, CRF 16 + AAC-LC 320 kb/s 48 kHz).

## Files

| File | What |
|---|---|
| `build.py` | The single description of the edit: footage segments (film frame -> clip frame), typed text timings, picture beats and SFX cues. Writes `edit.json`, `events.json` and the TIMING block in `index.html`; `--plate` bakes the footage plate. |
| `edit.json` | Generated. The footage edit, per segment: film frames, clip frames, speed. |
| `events.json` | Generated. SFX cues for `v2/music/score.py` (film seconds). |
| `index.html` | The composition. Root `#stage`, `data-composition-id="hoocode-trailer-60"`. One paused GSAP timeline. The camera over the footage is the `#cam` transform (rects in source-frame pixels at 1080p scale). |
| `assets/footage.mp4` | Symlink to `out/v2/hoocode-v2-4k.mp4` (the 4K recording, 3840x2160). Source of the plate. |
| `assets/plate.mp4` | Symlink to `out/v2/plates/trailer60-plate.mp4`: the 4K footage re-timed onto film time 4.0-28.0 s (cuts, speed ramps, holds; frame exact). HyperFrames has no playback-rate control, so the retime is baked by `build.py --plate`. |
| `assets/filmkit.js`, `assets/filmkit.css` | Symlinks to `v2/filmkit.*`: shared builders (owl, type-on, camera, brackets, verb plates, keycaps, spark) and styles, also used by `v2/cutdown30`. |
| `assets/fonts`, `assets/brand` | Symlinks to `v2/assets/{fonts,brand}` (Inter var, JetBrains Mono 400/500/700). The lockup (`hoocode.svg`) and Symbol C (`symbol.svg`) are inlined so their parts can animate; the owl is drawn from `owl.txt` as rects (the brand fonts have no block glyphs). |

## Rebuild (from the repo root)

```bash
# 1. edit + events + composition timing (+ the 4K plate, ~40 s)
python3 v2/trailer60/build.py --plate

# 2. score (music on the fixed 120 BPM grid + SFX from events.json), ~50 s
python3 v2/music/score.py --film trailer60 --events v2/trailer60/events.json

# 3. picture (silent), ~3-4 min on 4 cores
cd v2/trailer60
npx -y hyperframes@0.8.210 lint
PUPPETEER_EXECUTABLE_PATH=/opt/pw-browsers/chromium npx -y hyperframes@0.8.210 render \
  --output ../../out/v2/trailer60-silent.mp4 --fps 30 --quality high --video-frame-format png
cd ../..

# 4. mux (video re-encoded at CRF 16 to the delivery spec)
ffmpeg -y -i out/v2/trailer60-silent.mp4 -i out/v2/audio/trailer60.wav -map 0:v -map 1:a \
  -c:v libx264 -crf 16 -preset slow -profile:v high -pix_fmt yuv420p \
  -c:a aac -b:a 320k -ar 48000 -movflags +faststart -shortest out/v2/hoocode-trailer-60s.mp4

# check: 60.000 s video, audio within one AAC frame
ffprobe -v error -show_entries stream=codec_type,duration -of compact out/v2/hoocode-trailer-60s.mp4
```

Stills before rendering: `npx -y hyperframes@0.8.210 snapshot --at 10,16,22,26,48,59.9` (needs
`PUPPETEER_EXECUTABLE_PATH=/opt/pw-browsers/chromium`).

## Changing the edit

Change `SEGMENTS` / `BEATS` in `build.py` only, then run steps 1-4. Events, plate and the
composition's TIMING block are regenerated from the same numbers, so picture and sound stay in
sync. Camera rects and bracket boxes (`R`, `BOX` in `index.html`) are in source-frame pixels at
1080p scale (terminal grid x 112..1808, row r centre y = 36.25 + 32.5 r); check them with
snapshots if the recording changes.

Clip frames that must never be shown (the product briefly draws `exit 0` on a running shell step):
clip 527-533 (first run, before `HIT`) and 690-696 (re-run, before the result settles). The edit
skips them; keep it that way after a re-record (check with frame strips).
