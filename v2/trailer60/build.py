#!/usr/bin/env python3
"""Trailer 60 s: the edit, the SFX events and the composition timing, from one description.

    python3 v2/trailer60/build.py            # edit.json, events.json, TIMING block in index.html
    python3 v2/trailer60/build.py --plate    # also bake out/v2/plates/trailer60-plate.mp4 (4K, ~1 min)

Then: python3 v2/music/score.py --film trailer60 --events v2/trailer60/events.json, render, mux
(README.md).
"""
import sys

sys.dont_write_bytecode = True
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import filmkit as fk  # noqa: E402

HERE = Path(__file__).resolve().parent
F = fk.FPS


def s(t):
    """film seconds -> film frame"""
    return round(t * F)


# ---- footage edit (film frames -> clip frames). Clip frame n shows clip time n/30. -------------
CARD1, Y1, CARD2, A2 = fk.cue_frame("CARD1"), fk.cue_frame("Y1"), fk.cue_frame("CARD2"), fk.cue_frame("A2")
HIT, CARD3, Y3 = fk.cue_frame("HIT"), fk.cue_frame("CARD3"), fk.cue_frame("Y3")
EXIT0, DONE, LANDED = fk.cue_frame("EXIT0"), fk.cue_frame("DONE"), fk.cue_frame("LANDED")
# EXIT0 is drawn mid-scroll; the transcript settles 5 frames later (scroll at clip 23.4 s).
EXIT0_SETTLED = EXIT0 + 5
# The re-run shows a transient "exit 0" from clip frame Y3 + 7 (23.0 s): the slow-motion RISE
# stops one frame earlier, so `exit 0` is first seen on the drop.
RERUN_LAST = Y3 + 5
# Clip frames A2+1 .. HIT-1 show the first run's transient "exit 0": never shown.
TUI0 = 134  # clip 4.45 s: TUI drawn; the task panel then lands on film 6.0 s

SEGMENTS = [
    fk.seg(s(4.0), s(8.0), TUI0, TUI0 + s(4.0) - 1, "plans: TUI, plan, task panel (1x)"),
    fk.seg(s(8.0), s(10.0), TUI0 + s(4.0), CARD1 - 1, "asks: read + edit diff streaming (1.9x)"),
    fk.seg(s(10.0), s(12.5), Y1 - s(2.5), Y1 - 1, "card 1, Edit (1x); y lands on 12.5"),
    fk.seg(s(12.5), s(13.0), Y1, CARD2 - 1, "card 1 answered (slow)"),
    fk.seg(s(13.0), s(15.5), CARD2, A2 - 1, "card 2, Shell (1x); a lands on 15.5"),
    fk.seg(s(15.5), s(16.0), A2, None, "hold: card 2 answered"),
    fk.seg(s(16.0), s(19.0), HIT, CARD3 - 1, "tests: HIT exit 101, the fix text (1.14x)"),
    fk.seg(s(19.0), s(20.5), CARD3, Y3 - 1, "card 3, the fix (1x); y lands on 20.5"),
    fk.seg(s(20.5), s(21.875), Y3, RERUN_LAST, "the re-run, no card (slow, RISE)"),
    fk.seg(s(21.875), s(22.0), RERUN_LAST, None, "air gap: hold"),
    fk.seg(s(22.0), s(24.0), EXIT0_SETTLED, DONE - 1, "exit 0, test result ok (0.72x)"),
    fk.seg(s(24.0), s(26.0), DONE, LANDED - 1, "plan done, summary (0.88x)"),
    fk.seg(s(26.0), s(28.0), LANDED, LANDED + s(2.0) - 1, "LANDED (1x)"),
]

# ---- typed text --------------------------------------------------------------------------------
BANNER = "hoo│code"
TASK = 'hoocode "Add a --json flag to the stats command"'
INSTALL = "curl -fsSL https://kolisachint.github.io/hoocode/install.sh | sh"
banner_t = fk.type_times(BANNER, 1.05, 0.05)
task_t = fk.type_times(TASK, 2.05, 0.032)
install_t = fk.type_times(INSTALL, 52.0, 1.4 / len(INSTALL))

# ---- picture events (film seconds) -------------------------------------------------------------
BEATS = {
    "eye": 1.0, "enter": 3.95,
    "push_plan": 5.6, "pull_plan": 7.6, "push_card1": 9.6,
    "card1": 10.0, "y1": 12.5, "card2": 13.0, "a2": 15.5,
    "hit": 16.0, "fix": 18.0, "card3": 19.0, "y3": 20.5,
    "pull_rerun": 20.6, "gap": 21.875, "exit0": 22.0,
    "push_landed": 25.6, "landed": 26.0,
    "breath": 28.0, "verbs": 30.0, "features": 32.0, "lockup": 48.0, "tagline": 50.0,
    "install": 52.0, "end": 56.0,
}

events = [{"t": BEATS["eye"], "cue": "blip-eye"}]
events += fk.tick_events(banner_t, "key-tick-soft", text=BANNER)
events += fk.tick_events(task_t, "key-tick", text=TASK)
events += [
    {"t": BEATS["enter"], "cue": "key-enter"},
    {"t": BEATS["push_plan"], "cue": "whoosh-in", "dur": 0.4},
    {"t": BEATS["pull_plan"], "cue": "whoosh-out", "dur": 0.4},
    {"t": BEATS["push_card1"], "cue": "whoosh-in", "dur": 0.4, "gain_db": -3},
    {"t": BEATS["card1"], "cue": "blip-card"},
    {"t": BEATS["y1"], "cue": "key-press"}, {"t": BEATS["y1"], "cue": "spark-micro"},
    {"t": BEATS["card2"], "cue": "blip-card"},
    {"t": BEATS["a2"], "cue": "key-press"}, {"t": BEATS["a2"], "cue": "spark-micro"},
    {"t": BEATS["hit"], "cue": "hit-buzz"},
    {"t": BEATS["card3"], "cue": "blip-card"},
    {"t": BEATS["y3"], "cue": "key-press"}, {"t": BEATS["y3"], "cue": "spark-micro"},
    {"t": BEATS["pull_rerun"], "cue": "whoosh-out", "dur": 0.4, "gain_db": -3},
    {"t": BEATS["push_landed"], "cue": "whoosh-in", "dur": 0.4, "gain_db": -3},
    {"t": BEATS["landed"], "cue": "chime-landed"},
    {"t": BEATS["breath"], "cue": "spark-sting-short"},
]
events += [{"t": 32.0 + 2.0 * i, "cue": "card-tick"} for i in range(8)]
events += [{"t": BEATS["lockup"], "cue": "spark-sting"}]
events += fk.tick_events(install_t, "key-tick-soft", text=INSTALL)
events += [{"t": BEATS["end"], "cue": "spark-micro"}]

if __name__ == "__main__":
    fm = fk.write_edit(HERE, SEGMENTS)
    fk.write_events(HERE, events,
                    "Generated by v2/trailer60/build.py from v2/recording/cues.json and the edit "
                    "(edit.json). Film seconds. Cue vocabulary: v2/music/README.md.")
    timing = {
        "banner": banner_t, "task": task_t, "install": install_t, "beats": BEATS,
        "plate": {"start": fm[0][0] / F, "end": (fm[-1][0] + 1) / F},
    }
    fk.inject_timing(HERE / "index.html", timing)
    print(f"events: {len(events)}; footage {timing['plate']}")
    if "--plate" in fk.main_flags():
        fk.build_plate(HERE / "assets" / "footage.mp4", fk.REPO / "out" / "v2" / "plates" / "trailer60-plate.mp4", fm)
