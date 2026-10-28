# =====================================================================
# HooCode v2 launch recording: VHS tape (https://github.com/charmbracelet/vhs)
#
# Record from the repo root (Output paths are relative to it):
#   mkdir -p out/v2 && vhs v2/recording/hoocode-v2.tape
#
# Same scripted run as v1 (recording/hoocode.tape), but the v2 scenario
# (v2/recording/scenario.json): the cargo test fails once (exit 101), the agent fixes
# to_json, and the second run passes (exit 0). The working folder shows as ~/toolbox
# (TOOLBOX=1). Nothing is sent to a real model. See v2/recording.md for the spec.
# =====================================================================

Output out/v2/hoocode-v2.mp4

Set Shell "bash"
Set FontFamily "JetBrains Mono"
Set FontSize 40
Set LineHeight 1.2
Set Width 2880
Set Height 1620
Set Padding 36
Set Framerate 30
Set TypingSpeed 45ms
Set CursorBlink false
# dark.json (crates/hoocode-code-tui-theme/themes/dark.json) on the brand background #09090B.
Set Theme { "name": "HooCode dark", "background": "#09090B", "foreground": "#FAFAFA", "selection": "#2a2a36", "cursor": "#00F0FF", "cursorAccent": "#09090B", "black": "#16161f", "red": "#d58181", "green": "#b5bd68", "yellow": "#f0c674", "blue": "#6e93ff", "magenta": "#9b8cff", "cyan": "#5cc8bb", "white": "#a8a8a8", "brightBlack": "#757575", "brightRed": "#e8a0a0", "brightGreen": "#c9d88a", "brightYellow": "#ffff00", "brightBlue": "#8fb0ff", "brightMagenta": "#b8acff", "brightCyan": "#7fe0d5", "brightWhite": "#FAFAFA" }

# --- Setup (hidden, not recorded) ---------------------------------------
Hide
Type 'export SCENARIO="$PWD/v2/recording/scenario.json" TOOLBOX=1 HOOCODE_BIN=/home/user/hoocode/target/release/hoocode HOOCODE_SRC=/home/user/hoocode'
Enter
Type "recording/reset-sample.sh && cd recording/sample-repo && PS1='$ ' && clear"
Enter
# The typed command runs the mock-backed launcher. Its args are the task text.
Type 'hoocode() { ../run-mock.sh "$@"; }'
Enter
Type "clear"
Enter
Show

Sleep 1s
Type 'hoocode "Add a --json flag to the stats command"'
Sleep 500ms
Enter

# The plan (TodoWrite runs without approval).
Wait+Screen@60s /TodoWrite\s+4 items/
Sleep 2s

# Clearance for the edit: "y go, once".
Wait+Screen@60s /BUILD asks for Edit/
Sleep 2500ms
Type "y"
Sleep 1s

# Clearance for cargo test: "a always cargo in this session".
Wait+Screen@90s /BUILD asks for Shell/
Sleep 2500ms
Type "a"

# The first run fails: HIT, exit 101.
Wait+Screen@180s /exit 101/
Sleep 2s

# Clearance for the one-line fix.
Wait+Screen@60s /BUILD asks for Edit/
Sleep 1500ms
Type "y"

# The second run passes: exit 0, no card.
Wait+Screen@180s /exit 0\b/
Sleep 1500ms
Wait+Screen@120s /LANDED/
Sleep 3s
