# HooCode launch film: storyboard (45s)

Status: DRAFT, facts checked against the HooCode source (v0.2.20). The clip footage is a scripted run (see `README.md`), so the on-screen strings are real. Caption timings are estimates until the first real recording.

Facts used: binary `hoocode` (the install script also adds `hoo`); install `curl -fsSL https://kolisachint.github.io/hoocode/install.sh | sh`; also `npm install -g hoocode` and `pip install hoocode`; version 0.2.20; tagline "nothing applied without your say-so".

## Main film (45s)

| Timecode | Scene | Visual | Caption / on-screen text | Audio note |
|---|---|---|---|---|
| 0:00–0:05 | 1. Wordmark intro | Near-black field (`#09090B`). The exact 3-row HooCode glyph assembles from its pieces, staggered from the centre, each column coloured from accent `#5cc8bb` to violet `#9b8cff`. Beside it, `hoocode` types in, then `coding agent · v0.2.20`. | `hoocode` · `coding agent · v0.2.20` | Low synth pad rising from silence; soft click as the glyph locks at ~0:04. |
| 0:05–0:09 | 2. Mission Control opening | Starfield drifts slowly. Heading "MISSION CONTROL" fades in; countdown `T-3` → `T-2` → `T-1` → `T-0`, one number per second, then fades. | `MISSION CONTROL`, `T-3`, `T-2`, `T-1`, `T-0` | Four countdown ticks, one per number; pad swells into the cut at 0:09. |
| 0:09–0:36 | 3. Demo clip | `demo/out/hoocode.mp4` (about 25s of footage: the scripted run in the real TUI) inside a terminal frame. Plays from 0:09 to ~0:34; last frame holds to 0:36. Captions sit below the frame, one at a time. | 0:09.6–0:16.5 `01 plans the mission` · 0:17.4–0:25.5 `02 asks clearance before it acts` · 0:26.4–0:35.4 `03 runs the tests and lands it` | Keyboard typing SFX (light, dry) during the typed prompt; soft tick on each caption change; no music hits. |
| 0:36–0:45 | 4. Outro | The small wordmark sits at top-centre. The install line appears in a box, then `or npm i -g hoocode · pip install hoocode`, then `v0.2.20`, then the tagline. Hold on the end card. | `$ curl -fsSL https://kolisachint.github.io/hoocode/install.sh \| sh` · `or npm i -g hoocode · pip install hoocode` · `v0.2.20` · `nothing applied without your say-so` | Pad resolves to a single held tone at 0:36; silence for the last 1s. |

### What the clip shows (the scripted run)

The clip is the real TUI running `hoocode "Add a --json flag to the stats command"` in `demo/sample-repo`, against the scripted mock model. It shows, in order:

1. The plan: the model writes it with TodoWrite, and the FLIGHT PLAN panel fills.
2. `◎ CLEARANCE NEEDED` for the edit (the card names the tool). The viewer sees the `y go, once` key answered.
3. A second clearance for `cargo test` through Shell, answered the same way.
4. The tool output `exit 0`, then the turn ends with `LANDED`.

HooCode does not open pull requests, so the film has no PR beat. The third caption is the test run and the landing.

### Timing notes

- Film time = clip time + 9s (the clip starts at 0:09).
- Caption windows are set in `film/index.html` (9.6, 17.4, 26.4 s starts). After the first recording, check that each caption lands on its beat, and move the three start times if not.
- The mission and intro scenes are independent of the clip.

## Social teaser cut list (15s, for Huashu Motion)

Notes:

- Do not imitate the HooCode UI. Use motion graphics and the wordmark, not a recreated TUI.
- Remove the "Made with huashu-motion" credit from the teaser. Before publishing, check the Huashu Motion license for any attribution it requires.

| Timecode | Cut | Visual | Caption | Audio |
|---|---|---|---|---|
| 0:00–0:02 | Hook | Wordmark fragments snap together (same build as the main film, 2s version). | `hoocode` | Pad hit at 0:01.5. |
| 0:02–0:05 | Promise | Full-frame text. | "Your terminal. Now with a plan." | Light typing SFX. |
| 0:05–0:10 | Plan | Clip 0:00–0:05 (task typed, plan appears). Tight crop, 1.2× speed. | `plans the mission` | Typing SFX. |
| 0:10–0:13 | Run and test | Clip 0:13–0:16 (the test run and LANDED). Crop to the status line. | `runs the tests and lands it` | Tick on the pass line. |
| 0:13–0:15 | End card | Wordmark, install line, `v0.2.20`. | `curl -fsSL https://kolisachint.github.io/hoocode/install.sh \| sh` | Pad resolves at 0:14. |
