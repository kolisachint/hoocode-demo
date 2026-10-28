# =====================================================================
# HooCode launch demo: VHS tape (https://github.com/charmbracelet/vhs)
#
# Record (from the repo root, with a HooCode binary built from the clone):
#   HOOCODE_BIN=/home/user/kolisachint/hoocode/target/release/hoocode vhs demo/hoocode.tape
#
# The run is deterministic: `hoocode` here is demo/run-mock.sh, which starts the
# scripted mock LLM (scripts/tui/mockllm.py, turns in demo/scenario.json) and runs the
# real binary against it in demo/sample-repo. Nothing is sent to a real model.
# demo/reset-sample.sh restores the sample repo first, so every recording starts the same.
#
# Needs: VHS >= 0.8 (Wait+Screen), ttyd, ffmpeg, bash, cargo, python3.
# Output dir must exist: mkdir -p demo/out
#
# Timing map: clip time c is film time 9 + c (see demo/storyboard.md). The clip times in
# the comments are estimates until the first real recording; the film's caption times are
# set in film/index.html. The Wait+Screen timeouts are generous.
# =====================================================================

Output demo/out/hoocode.mp4
Output demo/out/hoocode.gif

Set Shell "bash"
Set FontSize 22
Set Width 1600
Set Height 900
Set Padding 24
Set WindowBar Colorful
Set TypingSpeed 45ms
# dark.json (crates/hoocode-code-tui-theme/themes/dark.json) on the brand background #09090B.
Set Theme { "name": "HooCode dark", "background": "#09090B", "foreground": "#FAFAFA", "selection": "#2a2a36", "cursor": "#00F0FF", "cursorAccent": "#09090B", "black": "#16161f", "red": "#d58181", "green": "#b5bd68", "yellow": "#f0c674", "blue": "#6e93ff", "magenta": "#9b8cff", "cyan": "#5cc8bb", "white": "#a8a8a8", "brightBlack": "#757575", "brightRed": "#e8a0a0", "brightGreen": "#c9d88a", "brightYellow": "#ffff00", "brightBlue": "#8fb0ff", "brightMagenta": "#b8acff", "brightCyan": "#7fe0d5", "brightWhite": "#FAFAFA" }

# --- Setup (hidden, not recorded) ---------------------------------------
Hide
Type "demo/reset-sample.sh && cd demo/sample-repo && PS1='$ ' && clear"
Enter
# The typed command runs the mock-backed launcher. Its args are the task text.
Type 'hoocode() { ../run-mock.sh "$@"; }'
Enter
Type "clear"
Enter
Show

# --- Scene A: launch (clip 0-1s; film 9-10s, caption "01 plans the mission" from film 9.6s) ---
Sleep 1s
Type 'hoocode "Add a --json flag to the stats command"'
Sleep 500ms
Enter

# --- Scene B: plan (clip 2-8s; film 11-17s, caption 01 on screen) ------------
# The scripted turn 1 writes the plan with TodoWrite, which fills the FLIGHT PLAN panel.
Wait+Screen@60s /FLIGHT PLAN|Plan/
Sleep 2s

# --- Scene C: clearance for the edit (clip 8-12s; caption 02 from film 17.4s) ---
# Read runs without approval. The Edit waits for "y go, once".
Wait+Screen@60s /CLEARANCE NEEDED/
Sleep 2s
Type "y"
Sleep 1s

# --- Scene D: clearance for cargo test (clip 12-16s; caption 02 still on screen) ---
Wait+Screen@90s /CLEARANCE NEEDED/
Sleep 2s
Type "y"

# --- Scene E: the test run and the landing (clip 16-26s; caption 03 from film 26.4s) ---
Wait+Screen@180s /exit 0/
Sleep 1500ms
Wait+Screen@120s /LANDED/
Sleep 3s

Ctrl+D
