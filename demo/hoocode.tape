# =====================================================================
# HooCode launch demo: VHS tape (https://github.com/charmbracelet/vhs)
#
# Run from the repo root:   vhs demo/hoocode.tape
# Needs: VHS >= 0.8 (for Wait+Screen), ttyd, ffmpeg, and `hoo` on PATH.
# Output dir must exist:    mkdir -p demo/out
#
# ---- EDITABLE VALUES (all PLACEHOLDERS, see demo/README.md TODO list) ----
# Binary name:         hoo                       (TODO: confirm)
# Sample repo:         demo/sample-repo          (TODO: create it; not in repo yet)
# Task 1 prompt:       Add a --json output flag to the stats command
# Task 2 (agent):      approve the plan with Enter; agent edits files, runs cargo test
# Task 3 prompt:       Open a pull request with these changes
# Quit key:            Ctrl+C                    (TODO: confirm real quit key)
# Screen strings we wait on: "Plan", "tests passed", "Pull request"  (TODO: confirm)
# Version shown in outro (film only): v0.1.25    (TODO: confirm)
#
# ---- TIMING MAP ----
# Clip time c maps to film time 9 + c (storyboard: VHS clip runs 0:09-0:36).
# The clip is ~25s of footage; the film holds the last frame for the rest.
# Wait+Screen durations vary by machine, so the clip times below are targets.
# =====================================================================

Output demo/out/hoocode.mp4
Output demo/out/hoocode.gif

Set Shell "bash"
Set FontSize 22
Set Width 1600
Set Height 900
Set Theme "Catppuccin Mocha"
Set TypingSpeed 45ms
Set Padding 24
Set WindowBar Colorful

Require hoo

# --- Setup (hidden, not recorded) ---------------------------------------
Hide
Type "cd demo/sample-repo"
Enter
Type "clear"
Enter
Show

# --- Scene A: launch (clip 0:00-0:02 / film 0:09-0:11) ------------------
# Storyboard: VHS clip begins at 0:09. Caption "01 plans the task" starts here.
Type "hoo"
Enter
Sleep 2s

# --- Scene B: task 1, plan (clip 0:02-0:08 / film 0:11-0:17) -----------
# Caption "01 plans the task" should stay up for this whole scene.
# Typing ~52 chars at 45ms per char is about 2.5s.
Type "Add a --json output flag to the stats command"
Sleep 500ms
Enter
Wait+Screen@30s /Plan/
Sleep 2s

# Approve the plan (TODO: confirm the approve key; Enter is a guess).
Enter

# --- Scene C: agent runs, edits, tests (clip 0:08-0:17 / film 0:17-0:26)
# Caption "02 runs the agent". Waiting on cargo test output, so allow time to compile.
Wait+Screen@90s /tests passed/
Sleep 1500ms

# --- Scene D: open PR (clip 0:17-0:25 / film 0:26-0:34, then hold to 0:36)
# Caption "03 opens the PR".
Type "Open a pull request with these changes"
Sleep 500ms
Enter
Wait+Screen@90s /Pull request/
Sleep 3s

# --- Outro in tape (not in film; film has its own outro) ---------------
Sleep 2s
Ctrl+C
