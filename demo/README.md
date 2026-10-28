# HooCode demo assets

Launch-demo assets for HooCode, a terminal coding agent written in Rust. One static binary, any model provider, nothing applied without your say-so.

Files:

- `hoocode.tape`: VHS script. Runs the real `hoocode` binary against a scripted model and records `out/hoocode.mp4` and `out/hoocode.gif`.
- `scenario.json`: the scripted model turns (same format as `scripts/demo/demo.json`, `llm` list).
- `run-mock.sh`: starts the mock model and runs `hoocode` in `sample-repo`. The tape calls it.
- `reset-sample.sh`: restores `sample-repo` with `git checkout`, so each recording starts from the same file.
- `sample-repo/`: a small std-only Rust crate (`toolbox stats <file>`). The demo adds `--json` to it.
- `storyboard.md`: 45s launch film storyboard and a 15s social teaser cut list.
- `film/index.html`: HyperFrames-style composition (GSAP timeline, 1920x1080) that wraps the clip.
- `out/`: generated video and GIF (not committed).

## Prerequisites

- A HooCode binary built from the source clone. The clone is read-only for this work, so build it there, or in your own checkout:

  ```sh
  cd /home/user/kolisachint/hoocode
  cargo build --release -p hoocode-code-main --bin hoocode
  ```

- VHS >= 0.8 (`Wait+Screen` needs it). Install with `go install github.com/charmbracelet/vhs@latest` (tested with v0.12.1). VHS needs `ttyd` and `ffmpeg` on PATH.
- `bash`, `python3`, and `cargo` (with a Rust toolchain) on PATH. `run-mock.sh` runs `cargo test` in `sample-repo`, and `mockllm.py` is stdlib Python.
- The HooCode source clone, for `scripts/tui/mockllm.py`. Default `/home/user/kolisachint/hoocode`; set `HOOCODE_SRC` to change it.

## Record the terminal demo

From the repo root:

```sh
mkdir -p demo/out
HOOCODE_BIN=/home/user/kolisachint/hoocode/target/release/hoocode vhs demo/hoocode.tape
```

What happens:

1. The hidden setup runs `reset-sample.sh`, then defines `hoocode() { ../run-mock.sh "$@"; }` in the shell.
2. The visible command `hoocode "Add a --json flag to the stats command"` runs `run-mock.sh` with that task.
3. `run-mock.sh` builds the test binary once (outside the recording), starts `mockllm.py` on a free port with the turns from `scenario.json`, writes a throwaway `models.json` and `settings.json`, and runs `HOOCODE_BIN --offline --provider demo --model scripted-demo "<task>"` in `sample-repo` with the same env as `scripts/demo/record.py`. The mock is stopped when hoocode exits.
4. The tape waits for the plan, answers the two clearance cards with `y`, waits for `exit 0` and `LANDED`, then quits with Ctrl+D.

Only the model is scripted. The Edit changes `src/main.rs` and the Shell call runs `cargo test` for real.

To run the same setup by hand, without VHS (the TUI is interactive, so this shows the screen in your terminal):

```sh
HOOCODE_BIN=/home/user/kolisachint/hoocode/target/release/hoocode demo/run-mock.sh "Add a --json flag to the stats command"
```

Then `demo/reset-sample.sh` to restore the sample repo.

### How scenario.json maps to demo.json

| `scripts/demo/demo.json` | `demo/scenario.json` |
|---|---|
| `model`: provider `demo`, id `scripted-demo` | same |
| `prepare`: `cargo test --quiet --lib --no-run` | `cargo test --quiet --no-run` (the crate has no `--lib` target) |
| `llm`: turns, each with `text` and `tool_calls` | same format. Six turns: TodoWrite plan, Read, Edit, Shell `cargo test --quiet`, TodoWrite done, summary |
| Edit arguments: `path` and `edits` with `oldText`/`newText` | same. The five edits were checked to turn `sample-repo/src/main.rs` into the post-edit file exactly |
| Tool names `Read`, `Edit`, `Shell` | same. The plan uses `TodoWrite` (on by default, not approval-gated) so the FLIGHT PLAN panel fills |
| `files`, `git`, `steps`, `workspace`, `terminal` | left out. The sample repo is a committed directory, and the tape drives the screen steps |

## Preview the film

```sh
npx serve demo -l 5055
# open http://localhost:5055/film/index.html
# add ?autoplay to play on load; click or Space toggles play
```

The film's `<video>` points at `../out/hoocode.mp4`, so it plays only after the recording. Without the file, the demo scene is empty and the browser logs one 404.

## Render the film

Render with HyperFrames is not set up yet. See the first open question below.

## Open questions

- [ ] HyperFrames render command, flags, viewport, and fps. The HTML lists its assumptions (1920x1080, `data-composition-id="hoocode-launch"`, `data-duration="45"`, `window.__timeline` and `window.__timelines.main`), but the renderer has not been run.
- [ ] Caption timings (9.6, 17.4, 26.4 s in the film) are estimates. Set them after the first real recording, because the clip's clearance and test times depend on the machine.
- [ ] The first recording may need its `Wait+Screen` timeouts tuned, mainly the first `cargo test`, which can compile.
- [ ] Teaser credit: remove the "Made with huashu-motion" credit as requested, and check the Huashu Motion license before publishing.

Checked against the source, not yet by a recording: the TUI strings the tape waits for (`FLIGHT PLAN`, `CLEARANCE NEEDED`, `exit 0`, `LANDED`) are taken from the source, and the film's Playwright check passes (screens at 2, 4.5, 7.1, 20 and 40 s, no page errors).
