# hoocode-demo

Launch assets for HooCode (`hoocode`, a terminal coding agent). The pipeline runs in three steps: record the terminal demo, render the 45s trailer around it, then render the 15s teaser.

## v2 (launch films with original score)

Everything for v2 lives in `v2/`; the finished films are committed in `out/v2/`.

| File | What it is |
|---|---|
| `out/v2/hoocode-trailer-60s.mp4` | 60 s trailer, 1920x1080, with score and SFX |
| `out/v2/hoocode-trailer-30s.mp4` | 30 s cutdown, 1920x1080 |
| `out/v2/hoocode-teaser-{9x16,1x1,16x9}.mp4` | 15 s teaser in three aspects (+ `-poster.png`) |
| `out/v2/hoocode-v2.mp4` | the 1080p demo recording (4K master is rebuilt by `v2/recording/`) |

Pipeline (each step has a README in its folder):

1. **Direction**: `v2/direction.md` (concept "Plans. Asks. Tests. Lands."), shot lists `v2/trailer-60.md`, `v2/cutdown-30.md`, `v2/teaser-15.md`.
2. **Recording**: `v2/recording/` records an asciinema cast of the real `hoocode` binary against the scripted model, then renders it to 4K/30 fps with xterm.js (`render_cast.mjs`) and writes exact cue times to `cues.json`.
3. **Score**: `v2/music/` synthesizes the original score in Python (no samples): `python3 v2/music/score.py --film <trailer60|cutdown30|teaser15> --events v2/<film>/events.json`. Spec in `v2/score.md`.
4. **Films**: HyperFrames projects in `v2/trailer60/`, `v2/cutdown30/`, `v2/teaser15/{9x16,1x1,16x9}/`. Each `build.py` turns `cues.json` into the edit, the SFX `events.json` and the timing block, so picture and sound cannot drift. Render, then mux with the score WAV.

Brand marks in `v2/assets/brand/` are copied from `hoo-brand/assets/`.

## Folders

| Path | What it is |
|---|---|
| `brand/` | Brand facts: `wordmark.txt` (the 3-row glyph), `brand.json` (colours, name, version, tagline, install lines). |
| `recording/` | VHS recording of the real `hoocode` binary against a scripted model. `hoocode.tape` is the script; `run-mock.sh` runs `hoocode` in `sample-repo/` against the mock model in `scenario.json`; `reset-sample.sh` restores `sample-repo/` first. |
| `trailer/` | 45s HyperFrames project (`index.html`, GSAP timeline). It wraps the recording with the intro, captions and outro. `storyboard.md` is the scene plan. |
| `out/` | Generated media: `hoocode.mp4` and `hoocode.gif` (from the recording), `trailer.mp4` (from the trailer), and teaser files. Only the files listed in `.gitignore` are committed. |
| `teaser/` | The 15s social teaser. Created by its own agent, documented in `teaser/`. |

## Pipeline

1. **Record**: `recording/hoocode.tape` writes `out/hoocode.mp4` and `out/hoocode.gif`.
2. **Render the trailer**: `trailer/` reads `out/hoocode.mp4` (through the symlink `trailer/assets/hoocode.mp4`) and writes `out/trailer.mp4`.
3. **Render the teaser**: see `teaser/`.

## Commands

Run from the repo root.

```sh
# One-time setup for VHS: chromium on PATH, and no sandbox (VHS runs as root here)
mkdir -p ~/bin && ln -sfn /opt/pw-browsers/chromium ~/bin/chromium
export PATH="$HOME/bin:/root/go/bin:$PATH" VHS_NO_SANDBOX=true

# 1. Record (needs a HooCode binary built from the source clone; see Prerequisites)
mkdir -p out
HOOCODE_BIN=/home/user/kolisachint/hoocode/target/release/hoocode vhs recording/hoocode.tape

# Check the tape without recording
vhs validate recording/hoocode.tape

# 2. Render the trailer (see trailer/README.md)
cd trailer && npx -y hyperframes lint && npx -y hyperframes render --output ../out/trailer.mp4 --fps 30 --quality draft && cd ..
```

### Prerequisites

- VHS >= 0.8 with `ttyd` and `ffmpeg` on PATH. The tape was run with VHS v0.12.1 (`go install github.com/charmbracelet/vhs@latest`).
- The chromium symlink above. VHS drives Chrome; `/opt/pw-browsers/chromium` is the Playwright Chrome for Testing build. `VHS_NO_SANDBOX=true` is needed because the sandbox does not run as root.
- A HooCode binary built from the source clone: `cd /home/user/kolisachint/hoocode && cargo build --release -p hoocode-code-main --bin hoocode`. `run-mock.sh` also reads `scripts/tui/mockllm.py` from that clone (set `HOOCODE_SRC` to change the path).
- `bash`, `python3`, `cargo` for `run-mock.sh`, which builds the sample test binary once before the recording starts.
- Node.js (`npx`) and `ffmpeg` for the trailer.

### Notes

- VHS resolves `Output` paths from the directory you run it in, so run `vhs` from the repo root and keep `out/` there.
- `recording/reset-sample.sh` runs `git checkout -- recording/sample-repo`, so each recording starts from the committed sample.
- The recorded footage shows the path it ran in. Re-record after moving the repo to avoid a stale path in the clip.
- Caption timings in `trailer/index.html` are measured from the recording. Re-check them after every re-record (see `trailer/README.md`).
