# v2 recording: reproduce the take

The v2 take is an asciinema cast rendered to 4K by xterm.js in headless Chromium. Spec and
reasons: `v2/recording.md` §3.

## Files

| File | What |
|---|---|
| `scenario.json` | the scripted model turns (`delay_s` holds the red beat, turn 5; the summary, turn 8) |
| `record_cast.py` | drives a 117x32 tmux pane and records `hoocode-v2.cast` with asciinema |
| `cast-rc.sh` | the bash rc inside the recording: prompt, env, `hoocode` function (not run by hand) |
| `hoocode-v2.cast` | the recording (asciinema v2, real timing) |
| `render_cast.mjs` | renders the cast to 4K PNG frames, encodes the mp4s, writes `cues.json` |
| `vendor/` | xterm.js 6.0.0, xterm.css, addon-webgl 0.19.0, with their MIT licenses |
| `cues.json` | cue times (exact, from the cast) and row fractions |
| `hoocode-v2.tape` | the VHS version (fallback only; not faithful timing) |

## Prerequisites

- `hoocode` release binary (`HOOCODE_BIN`) and the hoocode clone with `scripts/tui/mockllm.py`
  (`HOOCODE_SRC`). Default: `/home/user/hoocode/target/release/hoocode` and `/home/user/hoocode`.
- `tmux`, `ffmpeg`, `node` (22 or newer), and `pip install asciinema` (checked: 2.4.0 has `--cols`
  and `--rows`; `python3 -m asciinema --version`).
- The `playwright` package on the node module path, and a Chromium binary
  (default `/opt/pw-browsers/chromium-1243/chrome-linux64/chrome`, override with `CHROME`).

## Record

From the repo root (`/home/user/hoocode-demo`). Resets `recording/sample-repo` to the committed state,
then records. Takes about 35 s.

```bash
HOOCODE_BIN=/home/user/hoocode/target/release/hoocode HOOCODE_SRC=/home/user/hoocode \
  python3 v2/recording/record_cast.py
```

Output: `v2/recording/hoocode-v2.cast`. Check the first event is the prompt (`$ `) and the last
event is 3 s after `LANDED`.

## Render

```bash
RENDER_WORK=<scratch dir, e.g. the session scratchpad> node v2/recording/render_cast.mjs
```

Takes about 9 min (about 0.6 s per frame at 3840x2160, plus encoding). Output:

- `v2/recording/cues.json` (exact cue times from the cast; `*_y` row fractions of the 4K frame)
- `out/v2/hoocode-v2-4k.mp4` (3840x2160, 30 fps, H.264 crf 14)
- `out/v2/hoocode-v2.mp4` (1920x1080, 30 fps, H.264 crf 16)
- PNG frames in `$RENDER_WORK/frames/` (`f00000.png` ... one per frame)

`--max-frames N` renders the first N frames only (a test); `--no-encode` skips ffmpeg.

## Last frame

```bash
ffmpeg -y -sseof -0.1 -i out/v2/hoocode-v2-4k.mp4 -frames:v 1 v2/recording/last-frame.png
ffmpeg -y -i v2/recording/last-frame.png -vf scale=1920:-2:flags=lanczos v2/recording/last-frame-1080.png
```

## Reset

```bash
recording/reset-sample.sh      # git checkout of recording/sample-repo (tracked files only)
```
