#!/usr/bin/env python3
"""Drive the v2 take in a detached tmux pane and record it with asciinema.

Writes v2/recording/hoocode-v2.cast (asciinema v2 format, 117x32). The timing follows
hoocode-v2.tape: 1 s idle, the command typed at 45 ms per char, then holds and waits on
screen text (polled with `tmux capture-pane`). The cast keeps real timing, so nothing is
retimed later.

Usage: python3 v2/recording/record_cast.py   (from the repo root; needs tmux and asciinema)
"""
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REC = ROOT / "v2/recording"
CAST = REC / "hoocode-v2.cast"
RC = REC / "cast-rc.sh"
SESSION = "hcrec"
COLS, ROWS = 117, 32
TASK = 'hoocode "Add a --json flag to the stats command"'


def tmux(*args: str) -> str:
    return subprocess.run(["tmux", *args], check=True, capture_output=True, text=True).stdout


def screen() -> str:
    return tmux("capture-pane", "-p", "-t", SESSION)


def wait_for(pattern: str, timeout: float = 240.0, after: str | None = None) -> None:
    """Poll the pane until `pattern` matches. With `after`, the match must come after
    `after` has been seen first (for texts that also appear in earlier screens)."""
    rx = re.compile(pattern, re.M)
    deadline = time.monotonic() + timeout
    seen_gate = after is None
    while time.monotonic() < deadline:
        text = screen()
        if not seen_gate and re.search(after, text, re.M):
            seen_gate = True
        elif seen_gate and rx.search(text):
            return
        time.sleep(0.03)
    raise SystemExit(f"timed out waiting for {pattern!r}")


def hold(seconds: float) -> None:
    time.sleep(seconds)


def send(keys: str) -> None:
    tmux("send-keys", "-t", SESSION, "-l", keys)


def enter() -> None:
    tmux("send-keys", "-t", SESSION, "Enter")


def main() -> None:
    subprocess.run([str(ROOT / "recording/reset-sample.sh")], check=True, cwd=ROOT)
    subprocess.run(["tmux", "kill-session", "-t", SESSION], capture_output=True)
    CAST.unlink(missing_ok=True)

    rec = " ".join(
        [
            "env", "TERM=xterm-256color", "COLORTERM=truecolor",
            "python3", "-m", "asciinema", "rec", "--overwrite", "-y", "-q",
            "--cols", str(COLS), "--rows", str(ROWS),
            "-c", shlex.quote(f"bash --rcfile {shlex.quote(str(RC))} -i"),
            shlex.quote(str(CAST)),
        ]
    )
    tmux("new-session", "-d", "-s", SESSION, "-x", str(COLS), "-y", str(ROWS),
         "-c", str(ROOT), rec)
    wait_for(r"^\$", timeout=30)
    pane_pid = int(tmux("display-message", "-p", "-t", SESSION, "#{pane_pid}").strip())

    hold(1.0)  # idle before typing
    start = time.monotonic()
    for k, ch in enumerate(TASK):  # fixed schedule: 45 ms per char, no drift from send-keys
        time.sleep(max(0.0, start + k * 0.045 - time.monotonic()))
        send(ch)
    hold(0.5)
    enter()

    wait_for(r"TodoWrite\s+4 items")
    hold(2.0)

    wait_for(r"BUILD asks for Edit")
    hold(2.5)
    send("y")

    wait_for(r"BUILD asks for Shell")
    hold(2.5)
    send("a")

    wait_for(r"exit 101")
    wait_for(r"BUILD asks for Edit", after=r"exit 101")
    hold(1.5)
    send("y")

    wait_for(r"exit 0\b", after=r"exit 101")
    wait_for(r"LANDED", after=r"exit 0\b")
    hold(3.0)

    # Stop the recording: SIGINT to asciinema (the pane's process), then wait for it to exit.
    subprocess.run(["kill", "-INT", str(pane_pid)], check=False)
    for _ in range(100):
        if subprocess.run(["kill", "-0", str(pane_pid)], capture_output=True).returncode != 0:
            break
        time.sleep(0.1)
    subprocess.run(["tmux", "kill-session", "-t", SESSION], capture_output=True)
    add_final_hold(CAST, hold_s=3.0)
    print(f"wrote {CAST}")


def add_final_hold(cast: Path, hold_s: float) -> None:
    """The screen is static after LANDED, so asciinema writes no event for the 3 s hold.
    Append an empty output event at (LANDED draw time + hold_s) so the cast keeps the hold."""
    import json
    lines = cast.read_text(encoding="utf-8").splitlines()
    landed = next(
        json.loads(l)[0] for l in lines[1:]
        if l.strip() and "LANDED" in json.loads(l)[2]
    )
    lines.append(json.dumps([round(landed + hold_s, 6), "o", ""], ensure_ascii=False))
    cast.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
