# HooCode launch film: storyboard (45s)

Status: DRAFT. Binary name, install command, version, keys, and copy are placeholders. See the TODO list in `demo/README.md`.

## Main film (45s)

| Timecode | Scene | Visual | Caption / on-screen text | Audio note |
|---|---|---|---|---|
| 0:00–0:05 | 1. Wordmark intro | Black field. Block wordmark `HOO` assembles from fragments (`▟▀▀▀▙`, `█`, `▜▄▄▄▛`), staggered from the center, each glyph settling with a small overshoot. | `HOO` (wordmark only, no tagline) | Low synth pad rising from silence; soft click as the last glyph locks at ~0:04. |
| 0:05–0:09 | 2. Mission Control opening | Starfield drifts slowly. Heading "MISSION CONTROL" fades in; countdown `T-3` → `T-2` → `T-1` → `T-0`, one number per second, then fades. | `MISSION CONTROL`, `T-3`, `T-2`, `T-1`, `T-0` | Four countdown ticks, one per number; pad swells into the cut at 0:09. |
| 0:09–0:36 | 3. VHS demo clip | Clip `demo/out/hoocode.mp4` (about 25s of footage) inside a terminal-frame. Plays from 0:09 to ~0:34; last frame holds to 0:36. Captions sit below the frame, one at a time. | 0:09–0:17 `01 plans the task` · 0:17–0:26 `02 runs the agent` · 0:26–0:36 `03 opens the PR` | Keyboard typing SFX (light, dry) during the typed prompts; soft tick on each caption change; no music hits. |
| 0:36–0:45 | 4. Outro | Wordmark shrinks to top-center. Install line in monospace appears in a box, then `v0.1.25` fades in under it. Hold on the end card. | `$ curl -fsSL https://hoocode.dev/install.sh \| sh` · `v0.1.25` | Pad resolves to a single held tone at 0:36; silence for the last 1s. |

### Timing notes

- Film time = clip time + 9s (the clip starts at 0:09).
- Captions in the film: 0:09.6–0:16.8, 0:17.4–0:25.8, 0:26.4–0:35.6.
- Caption copy uses the storyboard's three phrases: "plans the task", "runs the agent", "opens the PR".

## Social teaser cut list (15s, for Huashu Motion)

Notes:

- Do not imitate the HooCode UI. Use motion graphics and the wordmark, not a recreated TUI.
- Remove the "Made with huashu-motion" credit from the teaser. Before publishing, check the Huashu Motion license for any attribution it requires.

| Timecode | Cut | Visual | Caption | Audio |
|---|---|---|---|---|
| 0:00–0:02 | Hook | Wordmark fragments snap together (same build as the main film, 2s version). | `HOO` | Pad hit at 0:01.5. |
| 0:02–0:05 | Promise | Full-frame text. | "Your terminal. Now with a plan." | Light typing SFX. |
| 0:05–0:10 | Plan | Clip 0:00–0:05 (task typed, plan appears). Tight crop, 1.2× speed. | `plans the task` | Typing SFX. |
| 0:10–0:13 | Run and test | Clip 0:13–0:16 (cargo test output). Crop to the status line. | `runs the agent` | Tick on the pass line. |
| 0:13–0:15 | End card | Wordmark, install line, `v0.1.25`. | `curl -fsSL https://hoocode.dev/install.sh \| sh` | Pad resolves at 0:14. |
