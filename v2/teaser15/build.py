#!/usr/bin/env python3
"""Build the v2 HooCode teaser (15.0 s) projects from one source.

One timeline, three HyperFrames projects (9x16/, 1x1/, 16x9/) that differ only in layout CSS.
This script is the single source of the edit's times. It writes:

  shared/beats.js         timeline data for shared/teaser.js (footage in-points, typed-char frames)
  events.json             SFX cues for v2/music/score.py (same times, so picture and sound cannot drift)
  shared/stills/*.png     4K freeze frames pulled from the footage
  <aspect>/index.html     the composition per aspect (shared/template.html + inline brand SVGs)
  <aspect>/assets/*       symlinks: footage.mp4 -> out/v2/hoocode-v2-4k.mp4, fonts, shared, stills

Run from anywhere:  python3 v2/teaser15/build.py
Footage cue times come from v2/recording/cues.json (clip seconds).
"""
import json
import math
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
V2 = os.path.dirname(HERE)
REPO = os.path.dirname(V2)
FOOTAGE = os.path.join(REPO, "out", "v2", "hoocode-v2-4k.mp4")
CUES = json.load(open(os.path.join(V2, "recording", "cues.json")))
FPS = 30
FRAME = 1.0 / FPS
SAFE = 0.004  # seconds past a frame boundary, so floor- and round-based seeks pick the same frame

ASPECTS = {
    "9x16": (1080, 1920),
    "1x1": (1080, 1080),
    "16x9": (1920, 1080),
}


def first_frame(cue):
    """Index of the first footage frame that shows a cue (frame i shows events at t <= i/30)."""
    return math.ceil(CUES[cue] * FPS - 1e-9)


def media_start(cue, film_t, act_start):
    """Media in-point so the cue's first frame is on screen at film time film_t."""
    return round(first_frame(cue) / FPS - (film_t - act_start) + SAFE, 4)


# ---- the edit (film seconds) -------------------------------------------------------------
# Grid: 120 BPM, beat 0.5 s, 2-beat pickup 0.0-1.0, bar N at 1.0 + (N-1) * 2.0.

ACTS = []


def video(start, end, media):
    return dict(kind="video", start=start, end=end, media=round(media, 4))


def still(frame, start, end):
    return dict(kind="still", frame=frame, start=start, end=end)


# 1 plans.  1.0-3.0  The task panel (the plan) appears on beat 2 (1.5); brackets land on it.
ACTS.append(dict(id="plans", start=1.0, end=3.0,
                 clips=[video(1.0, 3.0, media_start("PANEL", 1.5, 1.0))]))

# 2 asks.   3.0-5.0  Card 1 is up at the cut; keycap y at 4.5; the card leaves (Y1) at 4.6.
#           Hold the post-Y1 frame from 4.8 (CARD2 would appear at 4.83).
m2 = media_start("Y1", 4.6, 3.0)
ACTS.append(dict(id="asks", start=3.0, end=5.0,
                 clips=[video(3.0, 4.8, m2), still(first_frame("CARD2") - 1, 4.8, 5.0)]))
assert math.floor((m2 + (4.8 - 3.0)) * FPS) < first_frame("CARD2")
assert math.floor((m2 + 0.0) * FPS) >= first_frame("CARD1")

# 3 tests.  5.0-7.0  Red, then green. 5.0: hold the first frame after card 3 leaves (Y3): the
#           failed run's `Command exited with code 101` and the fix diff. 5.467 (frame 164, the
#           closest frame to beat 2 the take allows): the re-run lands (EXIT0, the screen scrolls)
#           and plays live; push 5.6-6.0 onto `test result: ok. 2 passed`; freeze 6.875-7.0.
RED_FRAME = first_frame("Y3")
EXIT0_FILM = 164 / FPS
m3 = round(first_frame("EXIT0") / FPS + SAFE, 4)
ACTS.append(dict(id="tests", start=5.0, end=7.0, red_frame=RED_FRAME,
                 clips=[still(RED_FRAME, 5.0, EXIT0_FILM), video(EXIT0_FILM, 6.875, m3),
                        still(math.floor((m3 + 6.875 - EXIT0_FILM) * FPS), 6.875, 7.0)]))

# 4 lands.  7.0-9.0  `● LANDED` is on screen on the drop's first frame.
ACTS.append(dict(id="lands", start=7.0, end=9.0,
                 clips=[video(7.0, 9.0, media_start("LANDED", 7.0, 7.0))]))

for a in ACTS:
    for c in a["clips"]:
        if c["kind"] == "video":
            assert c["media"] + (c["end"] - c["start"]) <= CUES["clip_duration"], a

# Install line type-on 12.0-12.9: char k shows on frame 360 + floor(k * 27 / n).
INSTALL_CMD = "curl -fsSL https://kolisachint.github.io/hoocode/install.sh | sh"
TYPE_START_F, TYPE_FRAMES = 360, 27
TYPE_FRAMES_LIST = [TYPE_START_F + (k * TYPE_FRAMES) // len(INSTALL_CMD) for k in range(len(INSTALL_CMD))]

BEATS = dict(
    fps=FPS,
    duration=15.0,
    acts=ACTS,
    exit0_film=round(EXIT0_FILM, 4),
    eyes=0.5,
    keycap=4.5,
    spark=9.0,
    tagline=9.5,
    lockup=11.0,
    subline=11.5,
    install_cmd=INSTALL_CMD,
    install_frames=TYPE_FRAMES_LIST,
    end=13.0,
    cursor_solid=14.0,
)

# ---- SFX events (v2/music/README.md vocabulary) -------------------------------------------
events = [
    {"t": 0.5, "cue": "blip-eye"},                 # owl eyes light
    {"t": 3.0, "cue": "blip-card"},                # clearance card on the cut
    {"t": 4.5, "cue": "key-press"},                # keycap y
    {"t": 4.5, "cue": "spark-micro"},              # the say-so spark
    {"t": 5.0, "cue": "hit-buzz", "gain_db": -3.0},  # tests. opens on the red run (exit 101)
    {"t": round(EXIT0_FILM, 4), "cue": "glitch-tick"},  # re-run lands green; chip flips to exit 0
    {"t": 7.0, "cue": "chime-landed"},             # ● LANDED on the drop
    {"t": 9.0, "cue": "spark-sting"},              # Symbol C spark (pre-suck 8.5-9.0)
]
for f in TYPE_FRAMES_LIST:                          # one per typed char, at its frame
    events.append({"t": round(f / FPS, 4), "cue": "key-tick-soft"})
events.append({"t": 13.0, "cue": "spark-micro"})   # end card: npm/pip + version, diamond pulse

EVENTS = {
    "_note": "Generated by v2/teaser15/build.py from the teaser edit (do not hand-edit). "
             "Film seconds; cue vocabulary in v2/music/README.md. key-tick-soft: one per typed "
             "install character at its on-screen frame (score.py skips ticks < 24 ms apart).",
    "events": events,
}


# ---- brand SVGs ----------------------------------------------------------------------------
def brand(name):
    return open(os.path.join(V2, "assets", "brand", name)).read()


def lockup_svg():
    s = brand("hoocode.svg")
    s = re.sub(r"<style>.*?</style>\s*", "", s, flags=re.S)       # no CSS keyframes: timeline drives .cursor
    s = re.sub(r"<title[^>]*>.*?</title>\s*", "", s, flags=re.S)
    s = re.sub(r'<rect width="274" height="80" rx="16" fill="#09090B"/>\s*', "", s)
    s = s.replace('role="img" aria-labelledby="hoocode-title"', 'id="lockup" role="img" aria-label="HooCode"')
    s = re.sub(r'\swidth="274" height="80"', "", s, count=1)
    # Tag the parts the timeline animates (order as in the file).
    parts = ["lk-stem", "lk-arch", "lk-n1", "lk-n2", "lk-spark", "lk-arc", "lk-div", "lk-code"]
    out, i = [], 0
    for line in s.split("\n"):
        if i < len(parts) and re.match(r"\s*<(line|path|circle|polygon)\b", line) and 'class="cursor"' not in line:
            line = re.sub(r"<(line|path|circle|polygon)\b", r'<\1 class="%s"' % parts[i], line, count=1)
            i += 1
        out.append(line)
    s = "\n".join(out)
    s = s.replace('<path class="cursor"', '<path class="cursor" id="lk-cursor"')
    return s


def symbol_svg():
    s = brand("symbol.svg")
    s = re.sub(r"<title[^>]*>.*?</title>\s*", "", s, flags=re.S)
    s = s.replace('role="img" aria-labelledby="hoo-symbol-title"', 'id="symbol" role="img" aria-label="Hoo symbol"')
    s = re.sub(r'\swidth="168" height="80"', "", s, count=1)
    s = s.replace('<path d="M40,72', '<path class="sy-arc sy-arc-l" d="M40,72', 1)
    s = s.replace('<path d="M160,72', '<path class="sy-arc sy-arc-r" d="M160,72', 1)
    s = s.replace('<circle cx="70"', '<circle class="sy-node" cx="70"', 1)
    s = s.replace('<circle cx="130"', '<circle class="sy-node" cx="130"', 1)
    s = s.replace("<polygon ", '<polygon class="sy-spark" ', 1)
    return s


# Quadrant blocks: bits (UL, UR, LL, LR).
QUAD = {"▟": (0, 1, 1, 1), "▀": (1, 1, 0, 0), "▙": (1, 0, 1, 1), "▌": (1, 0, 1, 0), "▐": (0, 1, 0, 1),
        "▜": (1, 1, 0, 1), "▄": (0, 0, 1, 1), "▛": (1, 1, 1, 0), " ": (0, 0, 0, 0)}


def owl_svg():
    """owl.txt as quadrant rects on the terminal cell (29 x 65 at 4K, so the owl keeps its TUI shape).
    Body #FAFAFA, eye glyphs (row 2, cols 1-2 and 4-5, from owl.ans) class "eye"."""
    rows = [r for r in open(os.path.join(V2, "assets", "brand", "owl.txt")).read().split("\n") if r]
    qw, qh = 29, 65  # half a cell each way, in 2x units: cell 58 x 130
    rects = []
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            bits = QUAD[ch]
            eye = r == 1 and c in (1, 2, 4, 5)
            for q, on in enumerate(bits):
                if not on:
                    continue
                x = c * 2 * qw + (q % 2) * qw
                y = r * 2 * qh + (q // 2) * qh
                rects.append((x, y, eye))
    w, h = len(rows[0]) * 2 * qw, len(rows) * 2 * qh
    body = "".join('<rect x="%d" y="%d" width="%d" height="%d"/>' % (x, y, qw + 0.6, qh + 0.6)
                   for x, y, e in rects if not e)
    eyes = "".join('<rect x="%d" y="%d" width="%d" height="%d"/>' % (x, y, qw + 0.6, qh + 0.6)
                   for x, y, e in rects if e)
    return ('<svg id="owl" viewBox="0 0 %d %d" role="img" aria-label="HooCode owl" shape-rendering="crispEdges">'
            '<g class="owl-body" fill="#FAFAFA">%s</g><g class="owl-eyes">%s</g></svg>') % (w, h, body, eyes)


# ---- write -----------------------------------------------------------------------------------
def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)


def link(target, path):
    if os.path.islink(path) or os.path.exists(path):
        os.remove(path)
    os.symlink(os.path.relpath(target, os.path.dirname(path)), path)


def main():
    shared = os.path.join(HERE, "shared")
    write(os.path.join(shared, "beats.js"),
          "// Generated by v2/teaser15/build.py. Do not edit.\nwindow.TEASER_BEATS = "
          + json.dumps(BEATS, indent=1, ensure_ascii=False) + ";\n")
    write(os.path.join(HERE, "events.json"), "{\n  \"_note\": %s,\n  \"events\": [\n%s\n  ]\n}\n" % (
        json.dumps(EVENTS["_note"]), ",\n".join("    " + json.dumps(e) for e in events)))

    stills = os.path.join(shared, "stills")
    os.makedirs(stills, exist_ok=True)
    for a in ACTS:
        for c in a["clips"]:
            if c["kind"] != "still":
                continue
            out = os.path.join(stills, "f%04d.png" % c["frame"])
            c["src"] = "assets/stills/" + os.path.basename(out)
            if not os.path.exists(out):
                subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", FOOTAGE, "-vf",
                                "select=eq(n\\,%d)" % c["frame"], "-frames:v", "1", out], check=True)
    # beats.js again with still paths
    write(os.path.join(shared, "beats.js"),
          "// Generated by v2/teaser15/build.py. Do not edit.\nwindow.TEASER_BEATS = "
          + json.dumps(BEATS, indent=1, ensure_ascii=False) + ";\n")

    tpl = open(os.path.join(shared, "template.html")).read()
    acts_html = []
    # Clips start CLIP_LEAD before their frame time, so a start like 5.4667 (frame 164 = 5.46666...)
    # is already active on its frame; their ends stay put. Media in-points carry SAFE, so the lead
    # does not change which footage frame shows.
    CLIP_LEAD = 0.002
    for a in ACTS:
        clips = ""
        for k, c in enumerate(a["clips"]):
            c = dict(c, start=c["start"] - CLIP_LEAD,
                     media=c["media"] - CLIP_LEAD if c["kind"] == "video" else None)
            if c["kind"] == "video":
                clips += ('<video id="foot-%s-%d" class="clip foot" data-start="%g" data-duration="%g" '
                          'data-media-start="%g" src="assets/footage.mp4" muted playsinline preload="auto"></video>'
                          % (a["id"], k, round(c["start"], 6), round(c["end"] - c["start"], 6), round(c["media"], 6)))
            else:
                clips += ('<img id="hold-%s-%d" class="clip foot" data-start="%g" data-duration="%g" src="%s" alt="">'
                          % (a["id"], k, round(c["start"], 6), round(c["end"] - c["start"], 6), c["src"]))
        acts_html.append(
            '<div class="act" id="act-%s"><div class="push"><div class="cam">%s</div>'
            '<div class="brackets"><i class="tl"></i><i class="tr"></i><i class="bl"></i><i class="br"></i></div></div></div>'
            % (a["id"], clips))
    # Line breaks ride on the char after them (shown with it): nl1 after "-fsSL " (9:16, 1:1),
    # nl2 after "github.io/" (9:16 only, so the end card can use a larger size).
    brk = {INSTALL_CMD.index("-fsSL") + len("-fsSL "): " nl1",
           INSTALL_CMD.index("github.io/") + len("github.io/"): " nl2"}
    install = "".join('<span class="ch%s">%s</span>' % (brk.get(k, ""), c if c != " " else "&#32;")
                      for k, c in enumerate(INSTALL_CMD))
    for name, (w, h) in ASPECTS.items():
        html = (tpl.replace("{{ASPECT}}", name).replace("{{W}}", str(w)).replace("{{H}}", str(h))
                .replace("{{OWL}}", owl_svg()).replace("{{SYMBOL}}", symbol_svg())
                .replace("{{LOCKUP}}", lockup_svg()).replace("{{ACTS}}", "\n      ".join(acts_html))
                .replace("{{INSTALL}}", install)
                .replace("{{BEATS}}", open(os.path.join(shared, "beats.js")).read().strip())
                .replace("{{SCRIPT}}", open(os.path.join(shared, "teaser.js")).read().strip()))
        pdir = os.path.join(HERE, name)
        write(os.path.join(pdir, "index.html"), html)
        write(os.path.join(pdir, "meta.json"), json.dumps(
            {"id": "hoocode-teaser-" + name, "name": "hoocode-teaser-" + name}, indent=2) + "\n")
        write(os.path.join(pdir, "hyperframes.json"), json.dumps({
            "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
            "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
            "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
            "media": {"autoProxy": True}}, indent=2) + "\n")
        write(os.path.join(pdir, "package.json"), json.dumps({
            "name": "hoocode-teaser-" + name, "private": True, "type": "module",
            "scripts": {
                "dev": "npx --yes hyperframes@0.8.210 preview",
                "check": "npx --yes hyperframes@0.8.210 check",
                "render": "npx --yes hyperframes@0.8.210 render --output ../../../out/v2/teaser-%s-silent.mp4 --fps 30 --quality high" % name,
            }}, indent=2) + "\n")
        assets = os.path.join(pdir, "assets")
        os.makedirs(assets, exist_ok=True)
        link(FOOTAGE, os.path.join(assets, "footage.mp4"))
        link(os.path.join(V2, "assets", "fonts"), os.path.join(assets, "fonts"))
        link(shared, os.path.join(assets, "shared"))
        link(stills, os.path.join(assets, "stills"))
    print("acts:")
    for a in ACTS:
        print("  %-6s film %.3f-%.3f" % (a["id"], a["start"], a["end"]))
        for c in a["clips"]:
            print("      %-5s %.4f-%.4f %s" % (c["kind"], c["start"], c["end"],
                  "media-start %.4f" % c["media"] if c["kind"] == "video" else "frame %d" % c["frame"]))
    print("exit 0 appears at film %.3f" % EXIT0_FILM)
    print("events: %d -> %s" % (len(events), os.path.join(HERE, "events.json")))


if __name__ == "__main__":
    sys.exit(main())
