# cutdown30: the 30 s HooCode v2 cutdown

HyperFrames project (pinned `hyperframes@0.8.210`). 1920x1080, 30 fps, 30.0 s (900 frames).
Spec as built: [`../cutdown-30.md`](../cutdown-30.md); shared look and layouts:
[`../trailer-60.md`](../trailer-60.md), [`../direction.md`](../direction.md); music:
[`../score.md`](../score.md) §5.2.

Output: `out/v2/hoocode-trailer-30s.mp4` (H.264 High, yuv420p, CRF 16 + AAC-LC 320 kb/s 48 kHz).

## Files

Same layout as [`../trailer60/README.md`](../trailer60/README.md):

| File | What |
|---|---|
| `build.py` | The edit (footage segments), typed text timings, beats and SFX cues. Writes `edit.json`, `events.json`, the TIMING block in `index.html`; `--plate` bakes `out/v2/plates/cutdown30-plate.mp4` (4K, film time 2.0-14.0 s). |
| `edit.json`, `events.json` | Generated. |
| `index.html` | The composition (`data-composition-id="hoocode-cutdown-30"`). |
| `assets/footage.mp4` | Symlink to `out/v2/hoocode-v2-4k.mp4`. |
| `assets/plate.mp4` | Symlink to `out/v2/plates/cutdown30-plate.mp4`. |
| `assets/filmkit.js`, `assets/filmkit.css`, `assets/fonts`, `assets/brand` | Symlinks to the shared `v2/filmkit.*` and `v2/assets/*`. |

## Rebuild (from the repo root)

```bash
python3 v2/cutdown30/build.py --plate
python3 v2/music/score.py --film cutdown30 --events v2/cutdown30/events.json

cd v2/cutdown30
npx -y hyperframes@0.8.210 lint
PUPPETEER_EXECUTABLE_PATH=/opt/pw-browsers/chromium npx -y hyperframes@0.8.210 render \
  --output ../../out/v2/cutdown30-silent.mp4 --fps 30 --quality high --video-frame-format png
cd ../..

ffmpeg -y -i out/v2/cutdown30-silent.mp4 -i out/v2/audio/cutdown30.wav -map 0:v -map 1:a \
  -c:v libx264 -crf 16 -preset slow -profile:v high -pix_fmt yuv420p \
  -c:a aac -b:a 320k -ar 48000 -movflags +faststart -shortest out/v2/hoocode-trailer-30s.mp4
ffprobe -v error -show_entries stream=codec_type,duration -of compact out/v2/hoocode-trailer-30s.mp4
```

The render takes about 2-3 minutes on 4 cores; the score about 20 s.

## Changing the edit

Change `SEGMENTS` / `BEATS` in `build.py` and rebuild; see the trailer README for the camera-rect
convention and the clip frames that must not be shown.
