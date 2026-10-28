# HooCode launch film: storyboard (45s)

Status: DRAFT, facts checked against the HooCode source (v0.2.20). The clip footage is a scripted run (see the root `README.md`), so the on-screen strings are real. Caption timings were measured from the first real recording (clip 21.6 s).

Facts used: binary `hoocode` (the install script also adds `hoo`); install `curl -fsSL https://kolisachint.github.io/hoocode/install.sh | sh`; also `npm install -g hoocode` and `pip install hoocode`; version 0.2.20; tagline "nothing applied without your say-so".

## Main film (45s)

| Timecode | Scene | Visual | Caption / on-screen text | Audio note |
|---|---|---|---|---|
| 0:00–0:05 | 1. Wordmark intro | Near-black field (`#09090B`). The exact 3-row HooCode glyph assembles from its pieces, staggered from the centre, each column coloured from accent `#5cc8bb` to violet `#9b8cff`. Beside it, `hoocode` types in, then `coding agent · v0.2.20`. | `hoocode` · `coding agent · v0.2.20` | Low synth pad rising from silence; soft click as the glyph locks at ~0:04. |
| 0:05–0:09 | 2. Mission Control opening | Starfield drifts slowly. Heading "MISSION CONTROL" fades in; countdown `T-3` → `T-2` → `T-1` → `T-0` at 0:05.5, 0:06.4, 0:07.3, 0:08.2, each on screen ~0.8 s, then the scene fades out by 0:09. | `MISSION CONTROL`, `T-3`, `T-2`, `T-1`, `T-0` | Four countdown ticks, one per number (0:05.5, 0:06.4, 0:07.3, 0:08.2); pad swells into the cut at 0:09. |
| 0:09–0:36 | 3. Demo clip | `out/hoocode.mp4` (21.6s of footage at 1x: the scripted run in the real TUI) inside a terminal frame. Plays from 0:09 to 0:30.6; last frame holds to 0:36. Captions sit below the frame, one at a time. | 0:14.6–0:20.4 `01 plans the mission` · 0:21.2–0:25.0 `02 asks clearance before it acts` · 0:25.6–0:35.4 `03 runs the tests and lands it` | Keyboard typing SFX (light, dry) during the typed prompt; soft tick on each caption change; no music hits. |
| 0:36–0:45 | 4. Outro | The small wordmark sits at top-centre. The install line appears in a box, then `or npm i -g hoocode · pip install hoocode`, then `v0.2.20`, then the tagline. Hold on the end card. | `$ curl -fsSL https://kolisachint.github.io/hoocode/install.sh \| sh` · `or npm i -g hoocode · pip install hoocode` · `v0.2.20` · `nothing applied without your say-so` | Pad resolves to a single held tone at 0:36; silence for the last 1s. |

### What the clip shows (the scripted run)

The clip is the real TUI running `hoocode "Add a --json flag to the stats command"` in `recording/sample-repo`, against the scripted mock model. It shows, in order:

1. The plan: the model writes it with TodoWrite; the rail shows `TodoWrite  4 items` (clip 6.0s, film 15.0s).
2. `◎ CLEARANCE NEEDED` for the edit, `BUILD asks for Edit` (clip 11.8s, film 20.8s). The viewer sees the `y go, once` key answered.
3. A second clearance for `cargo test` through Shell, `BUILD asks for Shell` (clip 13.3s, film 22.3s), answered the same way.
4. The tool output `exit 0` (clip 16.3s, film 25.3s), then the turn ends with `● LANDED` (clip 18.8s, film 27.8s). The clip ends at clip 21.6s (film 30.6s).

HooCode does not open pull requests, so the film has no PR beat. The third caption is the test run and the landing.

### Timing notes

- Film time = clip time + 9s (the clip starts at 0:09).
- Caption windows are set in `trailer/index.html`: 14.6 s (01), 21.2 s (02), 25.6 s (03). Measured from the first real recording (`out/hoocode.mp4`, 21.6 s): plan 4 items at clip 6.0 s, Edit clearance at 11.8 s, Shell clearance at 13.3 s, exit 0 at 16.3 s, LANDED at 18.8 s. Film time = clip time + 9 s.
- The mission and intro scenes are independent of the clip.

## 15s teaser

See `teaser/` (the teaser cut list and its files live there). This storyboard covers the 45s trailer only.
