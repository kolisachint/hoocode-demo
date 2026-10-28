# v2 recording: scenario, VHS settings, cues

One recording feeds all five films. Real `hoocode` binary (v0.2.20), real tool execution in
`recording/sample-repo` (the `toolbox` crate), scripted mock model (`scripts/tui/mockllm.py` from the
hoocode clone, via `recording/run-mock.sh`). Nothing is sent to a real model.

## 1. Story (what the viewer sees)

The user types `hoocode "Add a --json flag to the stats command"`. The agent:

1. writes a 4-item plan (TodoWrite, no approval),
2. reads `src/main.rs` (no approval),
3. edits it: `to_json`, the `--json` flag, a unit test. **Clearance card** `BUILD asks for Edit`,
   the user presses **`y`** (go, once),
4. runs `cargo test --quiet`. **Clearance card** `BUILD asks for Shell`, the user presses **`a`**
   (`always cargo in this session`). The test **fails**: `HIT` `exit 101`. The JSON has spaces after
   the colons; the test expects the compact form,
5. fixes `to_json` (one-line edit). **Clearance card** `BUILD asks for Edit`, the user presses **`y`**,
6. re-runs `cargo test --quiet`. **No card** this time (the `a` answer covers `cargo` for the
   session). `exit 0`, 2 passed,
7. marks the plan done (TodoWrite `4 items · 4 done`) and sums up. `● LANDED`.

Why the red step: it is realistic (the agent checks its own work), it shows the `a` key, and it
gives the edit and the score one tension → release. If the red step is unwanted, drop turns 5–6 below
and the films use the single run (`trailer-60.md` §5 notes the swap).

## 2. Scenario file

Write `v2/recording/scenario.json` in the `recording/scenario.json` format (same `model`, same
`prepare`). Make `run-mock.sh` take `SCENARIO="${SCENARIO:-$DEMO_DIR/scenario.json}"` so v1 still
works. The `llm` turns, in order (one per model request):

| # | `text` (streamed) | tool call |
|---|---|---|
| 1 | `Plan: read the \`stats\` command, add \`--json\` with a unit test, then run \`cargo test\`. The edit and the test run each wait for your clearance.` | `TodoWrite` with the 4 todos of v1 (first `in_progress`, rest `pending`): "Read the stats command in src/main.rs", "Add a --json flag that prints the counts as JSON", "Cover the JSON output with a unit test", "Run cargo test" |
| 2 | `Reading the file first.` | `Read` `{"path":"src/main.rs"}` |
| 3 | `I'll add a \`to_json\` helper, a \`--json\` flag and a test for the JSON line.` | `Edit` src/main.rs: the five edits of v1 turn 3, **except** the `to_json` body is `format!("{{\"lines\": {}, \"words\": {}}}", counts.lines, counts.words)` (a space after each colon and after the comma). The test still asserts `"{\"lines\":2,\"words\":3}"`. |
| 4 | `Running the tests.` | `Shell` `{"command":"cargo test --quiet"}` → fails, exit 101 |
| 5 | `The JSON has spaces after the colons; the test expects the compact form. Fixing \`to_json\`.` | `Edit` src/main.rs, one edit: oldText `format!("{{\"lines\": {}, \"words\": {}}}"` → newText `format!("{{\"lines\":{},\"words\":{}}}"` |
| 6 | `Running them again.` | `Shell` `{"command":"cargo test --quiet"}` → exit 0, 2 passed |
| 7 | `Tests pass. Marking the plan done.` | `TodoWrite`, all 4 `completed` |
| 8 | `Added \`--json\` to \`toolbox stats\`. It prints \`{"lines":N,"words":N}\` instead of the two lines, and \`to_json\` has a unit test. \`cargo test\` passes with 2 tests.` | none |

Check before recording: run the scenario once without VHS and confirm turn 4 really fails (cargo exits
101, the tool error ends `Command exited with code 101`, `crates/hoocode-code-tool-bash/src/tool.rs`)
and turn 6 passes. `recording/reset-sample.sh` must run first so `src/main.rs` is the committed one.

Path shown on screen: the startup header and HUD print the working folder. Copy `sample-repo` to
`$WORK/home/toolbox` in `run-mock.sh` and run there, so it reads `~/toolbox` instead of
`/home/user/hoocode-demo/recording/sample-repo` (verify on the first take; if the TUI does not
abbreviate `$HOME`, use `/tmp/toolbox`).

## 3. VHS tape: `v2/recording/hoocode-v2.tape`

Start from `recording/hoocode.tape`. Changes:

```
Output out/v2/hoocode-v2.mp4

Set Shell "bash"
Set FontFamily "JetBrains Mono"   # check: fc-list | grep -i "JetBrains Mono"
Set FontSize 40
Set LineHeight 1.2
Set Width 2880
Set Height 1620
Set Padding 36
Set Framerate 30
Set TypingSpeed 45ms
Set CursorBlink false
# no WindowBar line (v1 used "Colorful": traffic lights are not brand)
Set Theme { ...same as v1 (background #09090B, cursor #00F0FF)... }
```

This gives about 117 columns x 32 rows, the same grid as v1 (118 x 33), so the layout matches v1's
frames at 1.8x the pixels. Downscaled to 1920x1080, text is ~27 px. If VHS holds 30 fps at
3840x2160 / FontSize 53 (check: output duration equals the sum of the tape's waits), that is better
still; then all punch-ins are lossless. Do not change the column count: the films' zoom rects assume
~117 columns.

Script (after the hidden setup of v1, with `SCENARIO=../../v2/recording/scenario.json` exported in the
hidden part):

```
Show
Sleep 1s
Type 'hoocode "Add a --json flag to the stats command"'
Sleep 500ms
Enter

Wait+Screen@60s /TodoWrite\s+4 items/
Sleep 2s

Wait+Screen@60s /BUILD asks for Edit/          # card 1
Sleep 2500ms
Type "y"
Sleep 1s

Wait+Screen@90s /BUILD asks for Shell/         # card 2
Sleep 2500ms
Type "a"

Wait+Screen@180s /exit 101/                    # red
Sleep 2s

Wait+Screen@60s /BUILD asks for Edit/          # card 3 (the fix)
Sleep 1500ms
Type "y"

Wait+Screen@180s /exit 0\b/                    # green, no card
Sleep 1500ms
Wait+Screen@120s /LANDED/
Sleep 3s
```

End the tape there (no `Ctrl+D`: it opens the end-of-shift card, which no film uses). The Sleeps are
deliberate holds: the edit freezes or trims them. Expected clip length: about 32 s.

## 4. Cues

After recording, step through the clip (`ffmpeg -ss <t> -i out/v2/hoocode-v2.mp4 -frames:v 1 ...`, or
OCR every 0.1 s) and record the **first frame** where each string is fully drawn, in clip seconds, to
`v2/recording/cues.json` (`{"TUI": 1.43, "PLAN": 5.97, ...}`). Every film doc refers to these names.
Also note the y of the cue's text row as a fraction of frame height (`"PLAN_y": 0.71`): the zoom rects
anchor on it.

| Cue | Screen string (regex) | Where on screen | Source of the string |
|---|---|---|---|
| `ENTER` | the shell line disappears (TUI takes the screen) | whole frame | |
| `TUI` | `HOOCODE` in the HUD row | row 1 | `hud.rs` |
| `PLANTEXT` | `Plan: read the` | transcript | scenario turn 1 |
| `PLAN` | `TodoWrite\s+4 items · 0 done` | transcript step 01 | `tools/todo.rs` |
| `PANEL` | `Reading the stats command` (task panel, in progress mark) | above the comms frame | scenario |
| `READ` | `Read\s+src/main.rs` | transcript step 02 | `tools/read.rs` |
| `CARD1` | `BUILD asks for Edit` (first) | clearance card, bottom | `clearance_card.rs` |
| `KEYS` | `y go, once` | card row 4 | `clearance_card.rs` |
| `Y1` | first frame with card 1 gone | | |
| `CARD2` | `BUILD asks for Shell` | clearance card | `clearance_card.rs` |
| `ALWAYS` | `always cargo in this session` | card keys row | `clearance_card.rs` (`always {program} in this session`) |
| `A2` | first frame with card 2 gone | | |
| `HIT` | ` HIT ` chip and `exit 101` on step 04's header | transcript, right edge | `trajectory.rs` `hit_chip`; `tool_execution.rs` |
| `FAILED` | `test result: FAILED` | step 04 body | cargo |
| `FIXTEXT` | `The JSON has spaces` | transcript | scenario turn 5 |
| `CARD3` | `BUILD asks for Edit` (second) | clearance card | |
| `Y3` | first frame with card 3 gone | | |
| `EXIT0` | `exit 0` on step 06's header | transcript, right edge | `tool_execution.rs` |
| `OK` | `test result: ok. 2 passed` | step 06 body | cargo |
| `DONE` | `4 items · 4 done` | transcript step 07 | `tools/todo.rs` |
| `LANDED` | `● LANDED · ` (the transcript landing line, expected `● LANDED · 7 steps · 1 hit · …`) | transcript | `trajectory.rs` `landing_line` |
| `LANDFRAME` | `LANDED` in the comms frame title, and `name your mission` | bottom frame | `comms_frame.rs` |
| `END` | last frame | | |

Strings confirmed in the hoocode source (`crates/`): `◎ CLEARANCE NEEDED`, `{MODE} asks for {Tool}`,
`y go, once`, `always {program} in this session`, `always {Tool} in {MODE}`, `n abort + say why`,
`e edit first`, `or type a reply`, `REACH`, `N items · N done`, ` HIT `, `exit {code}`, `exit 0`,
`● LANDED`, `◐ IN FLIGHT`, `name your mission`, `type to queue the next mission`, `SHIP`, `FUEL`,
`FLIGHT PLAN`. The landing line's exact counts (`7 steps · 1 hit`) are expected, not verified: read
them off the first take.

## 5. Zoom-rect convention

The films give zoom rects as `Z(w, x0, anchor@p)`: a 16:9 crop of the source, `w` = width as a
fraction of the source (height = `w` too, since the source is 16:9), left edge at `x0`, placed so the
anchor cue's text row sits at fraction `p` of the crop's height. Clamp the crop inside the frame
(clamping wins over `p`). Zoom factor = 1/`w`. For non-16:9 windows (teaser) the docs give `w` and the
window's aspect; height = `w` x (16/9) / window aspect.

Reference geometry from v1 (same grid, so expect within ~1 row): HUD row y≈0.08; clearance card
y≈0.81–0.97; task panel y≈0.68–0.81 while in flight; plan item text ends x≈0.48; card keys row ends
x≈0.65; right-aligned step stats start x≈0.82.
