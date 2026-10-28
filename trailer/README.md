# trailer

The 45s HooCode launch trailer, as a HyperFrames project. It wraps `out/hoocode.mp4` (the VHS recording) with a wordmark intro, a mission countdown, three captions, and an outro with the install lines. The scene plan is in `storyboard.md`.

## Files

- `index.html`: the composition. Root `#stage` with `data-composition-id="hoocode-trailer"`, 1920x1080, 30 fps, 45 s. One paused GSAP timeline is registered on `window.__timelines["hoocode-trailer"]`.
- `assets/hoocode.mp4`: a symlink to `../out/hoocode.mp4`. HyperFrames needs media inside the project, and lint rejects `../` paths.
- `assets/last-frame.png`: the recording's last frame. It holds the recording's final frame from 30.6 s to 36 s. Regenerate it after a re-record (below).
- `AGENTS.md`, `CLAUDE.md`, `hyperframes.json`, `meta.json`, `package.json`: the HyperFrames project files, copied from `npx hyperframes init`. The scripts pin `hyperframes@0.8.210`.
- `storyboard.md`: the scene plan and caption cue times.

## Commands

Run from this folder (`trailer/`). Chrome needs the chromium symlink used for VHS (see the root README).

```sh
cd trailer

# Live preview in the browser (agent-safe: background mode)
npx hyperframes preview --background
npx hyperframes preview --status     # confirm it is listening
npx hyperframes preview --stop       # when finished

# Lint (structure), then the full check (lint + runtime, layout, motion, contrast)
npx hyperframes lint
PUPPETEER_EXECUTABLE_PATH=/opt/pw-browsers/chromium npx hyperframes check

# Render to ../out/trailer.mp4 (draft quality, 30 fps)
PUPPETEER_EXECUTABLE_PATH=/opt/pw-browsers/chromium npx hyperframes render --output ../out/trailer.mp4 --fps 30 --quality draft

# Stills at chosen seconds, to look at before rendering
npx hyperframes snapshot --at 2,15,27,40
```

The last render (draft) took about 5 minutes and produced a 2.0 MB, 45 s MP4 (`out/trailer.mp4`).

## After re-recording

When `recording/hoocode.tape` is run again:

1. `trailer/assets/hoocode.mp4` already points at the new file (symlink). Nothing to copy.
2. Regenerate the hold still from the new recording's last frame:
   ```sh
   ffmpeg -sseof -0.1 -i out/hoocode.mp4 -frames:v 1 -y trailer/assets/last-frame.png
   ```
3. Check the caption cue times in `index.html` (`cap-1` 14.6 s, `cap-2` 21.2 s, `cap-3` 25.6 s, and their ends) against the new clip. The clip plays from 9 s on the timeline. The times were measured from the first recording: plan at clip 6.0 s, Edit clearance at 11.8 s, Shell clearance at 13.3 s, `exit 0` at 16.3 s, `LANDED` at 18.8 s. Film time = clip time + 9 s. Update the cue times in `index.html` and `storyboard.md` if they move.
4. Run `lint` and `check`, then render `out/trailer.mp4` again.
