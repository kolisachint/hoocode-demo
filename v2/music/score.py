#!/usr/bin/env python3
"""Render the HooCode v2 launch score (music on the 120 BPM bar grid + event-driven SFX).

    python3 v2/music/score.py --film trailer60|cutdown30|teaser15 [--events v2/<film>/events.json]
                              [--out out/v2/audio] [--stems]

Writes <out>/<film>.wav (48 kHz, 24-bit stereo, -14 LUFS, <= -1 dBTP, exact film length, last
50 ms digital zero) and the stems <film>-music.wav and <film>-sfx.wav (32-bit float; music + sfx
== mix to float precision). --stems also writes <film>-stems/{bass,drums,pluck,pad,fx,sfx}.wav.
Source of truth for the arrangement and the sounds: v2/score.md.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from synth import (SR, adsr, bitcrush, butter, chorus, db, duck_curve, edge_fade, filt, fm_bell,  # noqa: E402
                   glue_gain, hz, ladder, limiter_gain, lufs, make_ir, mono_below, normalize, ns,
                   pan, peak, perc, pingpong, place, reverb, saturate, saw, sine, square,
                   true_peak_db, tv_filt, tvec)

SEED = 20261028
BEAT, BAR, STEP = 0.5, 2.0, 0.125
REPO = Path(__file__).resolve().parents[2]

# ----------------------------------------------------------------------------- harmony (§2)

CHORDS = {
    "Dm9": ([50, 53, 57, 60, 64], 38, [62, 65, 69, 72, 76]),
    "Bbmaj9": ([46, 50, 53, 57, 60], 34, [58, 62, 65, 69, 72]),
    "Fmaj9": ([53, 57, 60, 64, 67], 41, [65, 69, 72, 76, 79]),
    "Csus2": ([48, 50, 55, 60, 62], 36, [60, 62, 67, 72, 74]),
    "Gm7/Bb": ([46, 50, 53, 55, 62], 34, [58, 62, 65, 67, 74]),
    "A7sus4": ([45, 50, 52, 55, 64], 33, [57, 62, 64, 67, 76]),
    "A7": ([45, 49, 52, 55, 64], 33, [57, 61, 64, 67, 76]),
    "Dadd9": ([50, 57, 62, 64, 66, 69], 38, [62, 66, 69, 74, 76]),
}
D5, F5, A5, C6, D6 = 74, 77, 81, 84, 86  # spark motif: plans, asks, tests, lands, logo

# ----------------------------------------------------------------------------- films (§5)
# Each bar: (section, chord or [(beat, chord), ...], options). Bar N starts at offset + (N-1)*BAR.

RISE_CH = [(0, "A7sus4"), (2, "A7")]
FEAT = ["Dm9", "Bbmaj9", "Fmaj9", "Csus2"]

FILMS = {
    "trailer60": dict(
        length=60.0, offset=0.0, pickup=None, fade=(58.5, 59.95),
        bars=[
            ("INTRO", "Dm9", {}),
            ("TYPE", "Dm9", {}),
            ("PLANS", "Dm9", {"motif": [(0, D5, "bell")]}),
            ("PLANS", "Bbmaj9", {}),
            ("ASKS", "Fmaj9", {"motif": [(0, F5, "bell")]}),
            ("ASKS", "Csus2", {}),
            ("ASKS", "Dm9", {}),
            ("ASKS", "Bbmaj9", {"fill": True}),
            ("RED", "Gm7/Bb", {"motif": [(0, A5, "red")]}),
            ("RED", "Gm7/Bb", {}),
            ("RISE", RISE_CH, {"roll": "full"}),
            ("DROP", "Dm9", {}),
            ("DROP", "Bbmaj9", {}),
            ("DROP", "Fmaj9", {"motif": [(0, C6, "bell")]}),
            ("BREATH", "Csus2", {}),
            ("BREATH", "Bbmaj9", {"motif": [(0, D5, "dry"), (1, F5, "dry"), (2, A5, "dry"), (3, C6, "dry")]}),
        ] + [("FEATURES", c, {}) for c in FEAT * 2] + [
            ("LOCKUP", "Dm9", {}),
            ("LOCKUP", "Bbmaj9", {}),
            ("INSTALL", "Fmaj9", {}),
            ("INSTALL", "Csus2", {}),
            ("END", "Dadd9", {}),
            ("END", "Dadd9", {}),
        ]),
    "cutdown30": dict(
        length=30.0, offset=0.0, pickup=None, fade=(28.5, 29.95),
        bars=[
            ("OPEN", "Dm9", {}),
            ("PLANS", "Dm9", {"motif": [(0, D5, "bell")]}),
            ("PLANS", "Bbmaj9", {}),
            ("ASKS", "Fmaj9", {"motif": [(0, F5, "bell")]}),
            ("RISE", RISE_CH, {"roll": "half", "asks_head": True, "riser_from": 2}),
            ("DROP", "Dm9", {"motif": [(0, A5, "bell")]}),
            ("DROP", "Bbmaj9", {"motif": [(0, C6, "bell")]}),
            ("BREATH", "Csus2", {}),
            ("FEATURES", "Dm9", {}),
            ("FEATURES", "Bbmaj9", {}),
            ("FEATURES", "Csus2", {}),
            ("LOCKUP", "Dm9", {}),
            ("LOCKUP", "Bbmaj9", {}),
            ("END", "Dadd9", {}),
            ("END", "Dadd9", {}),
        ]),
    "teaser15": dict(
        length=15.0, offset=1.0, pickup="Dm9", fade=(13.5, 14.95),
        bars=[
            ("PLANS", "Dm9", {"motif": [(0, D5, "bell")]}),
            ("ASKS", "Bbmaj9", {"motif": [(0, F5, "bell")], "asks_full": True}),
            ("RISE", RISE_CH, {"motif": [(0, A5, "bell")], "roll": "half"}),
            ("DROP", "Dm9", {"motif": [(0, C6, "bell")]}),
            ("BREATH", "Bbmaj9", {}),
            ("LOCKUP", [(0, "Fmaj9"), (2, "Csus2")], {}),
            ("END", "Dadd9", {}),
        ]),
}


# Section mix automation (dB per track group; a (start, end) pair ramps across the section run).
# This is what shapes the film's dynamics: PLANS/ASKS build, RED thins out, DROP is the peak before
# the logo, LOCKUP makes room for the spark-sting, INSTALL/END settle.
SECTION_MIX = {
    "INTRO": {},
    "OPEN": {},
    "TYPE": {},
    "PLANS": dict(drums=-6, bass=-5.5, pluck=-3, pad=-2),
    "ASKS": dict(drums=(-5.5, -3), bass=(-5, -3), pluck=-2, pad=-3),
    "RED": dict(drums=-1, bass=-1, pad=-1.5),
    "RISE": dict(drums=(-7, 0), bass=(-6, 0), pad=(-5, 0)),
    "DROP": dict(drums=0.5, bass=2.5, pluck=3, pad=-1),
    "BREATH": dict(bass=-3, pad=-1),
    "FEATURES": dict(drums=-2.5, bass=-2.5, pluck=-1, pad=-3),
    "LOCKUP": dict(drums=-4, bass=-4, pluck=-3, pad=-3.5),
    "INSTALL": dict(drums=-4, bass=-4, pluck=0, pad=-1),
    "END": dict(bass=-3, pad=-1.5),
}


# ----------------------------------------------------------------------------- arrangement


class Arr:
    """Note/hit lists produced from the bar table; instruments render from these."""

    def __init__(self):
        self.kick, self.sub, self.clap, self.hat = [], [], [], []
        self.bass, self.pluck, self.strum, self.lead = [], [], [], []
        self.pad, self.padfc, self.padfade = [], [], []
        self.riser, self.glitch, self.swell, self.gaps, self.endsub = [], [], [], [], []
        self.bars = []  # (t0, section, index in run, run length)


def chord_at(chords, beat):
    if isinstance(chords, str):
        return chords
    cur = chords[0][1]
    for b, c in chords:
        if b <= beat + 1e-9:
            cur = c
    return cur


ARP_IDX = [0, 2, 4, 2, 3, 2, 4, 1]
ARP_VEL = [1.0, 0.6, 0.8, 0.6, 0.9, 0.6, 0.8, 0.6]


def arrange(film):
    F = FILMS[film]
    A = Arr()
    bars = F["bars"]
    off = F["offset"]
    # runs of consecutive bars with the same section
    run_id, runs = [], []
    for i, (sec, _, _) in enumerate(bars):
        if i == 0 or bars[i - 1][0] != sec:
            runs.append([i])
        else:
            runs[-1].append(i)
        run_id.append(len(runs) - 1)

    if F["pickup"]:
        A.swell.append((off, F["pickup"]))

    for i, (sec, chords, o) in enumerate(bars):
        t0 = off + i * BAR
        run = runs[run_id[i]]
        k, nrun = run.index(i), len(run)
        first, last = k == 0, k == nrun - 1
        ch0 = chord_at(chords, 0)
        A.bars.append((t0, sec, k, nrun))
        st = lambda s: t0 + s * STEP  # noqa: E731
        half = lambda s: (k * 16 + s) / (nrun * 16) >= 0.5  # noqa: E731  (second half of run)

        # pad segments: per chord change inside the bar
        chs = [(0, chords)] if isinstance(chords, str) else chords
        groove = sec in ("PLANS", "ASKS", "DROP", "FEATURES", "RISE", "LOCKUP", "INSTALL")
        for j, (b, c) in enumerate(chs):
            b1 = chs[j + 1][0] if j + 1 < len(chs) else 4
            att = {"INTRO": 1.2, "OPEN": 0.5, "END": 0.05}.get(sec, 0.3 if groove else 0.8)
            rel = 3.0 if sec == "END" else (0.45 if groove else 1.2)
            A.pad.append(dict(t0=t0 + b * BEAT, t1=t0 + b1 * BEAT, chord=c, att=att, rel=rel,
                              retrig=(sec == "END" and first and j == 0)))

        for m in o.get("motif", []):
            A.lead.append((t0 + m[0] * BEAT, m[1], m[2]))

        def bass_pulse(base, env, chord_fn=lambda s: ch0, vel=1.0, upto=16):
            for s in range(0, upto, 2):
                c = chord_fn(s)
                root = CHORDS[c][1] + (12 if s == 14 else 0)
                v = (1.0 if s in (0, 8) else 0.75) * vel
                A.bass.append(dict(t=st(s), gate=0.175, midi=root, vel=v, base=base, env=env))

        def bass_pedal(base=220, env=250, vel=0.85, lfo=None, midi=None):
            A.bass.append(dict(t=t0, gate=1.9, midi=midi or CHORDS[ch0][1], vel=vel, base=base, env=env,
                               lfo=lfo, lfo_t0=t0))

        def arp(vel, fc0=5000.0, sparse=False):
            if sparse:
                for q, idx in enumerate([4, 2, 3, 1]):
                    c = chord_at(chords, q)
                    A.pluck.append((t0 + q * BEAT, CHORDS[c][2][idx], 0.6 * vel, fc0))
                return
            for e in range(8):
                c = chord_at(chords, e / 2)
                A.pluck.append((t0 + e * 2 * STEP, CHORDS[c][2][ARP_IDX[e]], ARP_VEL[e] * vel, fc0))

        def hats(pattern, vel=1.0, from_step=0, to_step=16):
            for s in range(from_step, to_step):
                if pattern == "OFF8" and s in (2, 6, 10, 14):
                    A.hat.append((st(s), 0.7 * vel, False))
                elif pattern == "16":
                    op = s in (6, 14)
                    A.hat.append((st(s), (0.8 if s % 2 == 0 else 0.4) * vel, op))
                elif pattern == "OFF8G":  # off-8ths + 16th ghosts
                    if s in (2, 6, 10, 14):
                        A.hat.append((st(s), 0.7 * vel, False))
                    elif s % 2 == 1:
                        A.hat.append((st(s), 0.25 * vel, False))

        def roll(kind, gap_at=15.0):
            hits = []
            if kind == "full":
                hits += [0, 2, 4, 6]
            hits += [8, 9, 10, 11]
            hits += [12 + 0.5 * j for j in range(int((gap_at - 12) * 2))]
            n = len(hits)
            for j, s in enumerate(hits):
                x = j / max(n - 1, 1)
                A.clap.append((st(s), 0.3 + 0.7 * x, 1000.0 + 2500.0 * x))

        def gap():
            A.gaps.append((st(15), t0 + BAR))

        if sec == "INTRO":
            A.padfc.append((t0, t0 + BAR, 500, 1100))
            A.padfade.append((t0, 1.5))
        elif sec == "OPEN":
            A.padfc.append((t0, t0 + BAR, 600, 1100))
            A.padfade.append((t0, 0.5))
            bass_pedal(base=150, env=120, vel=0.5)
            A.riser.append((t0 + 2 * BEAT, t0 + BAR, 1.0))
        elif sec == "TYPE":
            A.padfc.append((t0, t0 + BAR, 1100, 1100))
            bass_pedal(base=150, env=120, vel=0.5)
            A.riser.append((t0, t0 + BAR, 1.0))
        elif sec == "PLANS":
            A.padfc.append((t0, t0 + BAR, 1400, 1400))
            if first:
                A.sub.append((t0, 1.0))
            A.kick += [(st(s), 1.0) for s in (0, 8)]
            bass_pulse(220, 900)
            arp(0.6)
        elif sec == "ASKS":
            f0 = 1400 + 400 * k / nrun
            A.padfc.append((t0, t0 + BAR, f0, f0 + 400 / nrun))
            for s in (0, 4, 8, 12):
                if o.get("asks_full") or half(s) or s in (0, 8):
                    A.kick.append((st(s), 1.0))
            for s in (4, 12):
                if o.get("asks_full") or half(s):
                    A.clap.append((st(s), 0.9, 1200.0))
            hats("OFF8")
            bass_pulse(260, 1000)
            arp(0.85)
            if o.get("fill"):
                for j, s in enumerate((12, 13, 14, 15)):
                    A.clap.append((st(s), 0.45 + 0.15 * j, 1200.0 + 300 * j))
        elif sec == "RED":
            A.padfc.append((t0, t0 + BAR, 800, 800))
            bass_pedal(base=150, env=0, vel=1.0, lfo=(4.0, 120.0))
            hats("16", 0.3)
            rng = np.random.default_rng([SEED, 4, i])
            pos = np.sort(rng.choice(32, 6, replace=False))
            A.glitch += [(t0 + p * STEP / 2, int(rng.integers(1 << 30))) for p in pos]
        elif sec == "RISE":
            A.padfc.append((t0, t0 + BAR, 1500, 2600))
            if o.get("asks_head"):
                A.kick += [(st(0), 1.0), (st(4), 1.0)]
                A.clap.append((st(4), 0.9, 1200.0))
                hats("OFF8", 1.0, 0, 8)
            bass_pulse(260, 1100, chord_fn=lambda s: chord_at(chords, s / 4), upto=15)
            roll(o.get("roll", "full"))
            A.riser.append((t0 + o.get("riser_from", 0) * BEAT, st(15), 1.0))
            gap()
        elif sec == "DROP":
            A.padfc.append((t0, t0 + BAR, 2200, 2200))
            if first:
                A.sub.append((t0, 1.0))
            A.kick += [(st(s), 1.0) for s in (0, 4, 8, 12)]
            A.clap += [(st(s), 1.0, 1200.0) for s in (4, 12)]
            hats("16")
            bass_pulse(400, 1600)
            arp(1.0)
            A.pluck += [(t, m + 12, v * 0.4, fc) for t, m, v, fc in A.pluck[-8:]]  # octave lift
        elif sec == "BREATH":
            A.padfc.append((t0, t0 + BAR, 1400, 1400))
            bass_pedal(base=240, env=200, vel=0.75)
            if last:
                A.riser.append((t0 + 3 * BEAT, t0 + BAR, 0.6))
        elif sec == "FEATURES":
            second = nrun >= 4 and k >= nrun // 2
            f = 1700 if not second else 2000
            A.padfc.append((t0, t0 + BAR, f, f))
            A.kick += [(st(0), 1.0), (st(8), 1.0), (st(11), 0.8)]
            A.clap += [(st(s), 0.95, 1200.0) for s in (4, 12)]
            for s in (2, 6, 10, 14):
                A.bass.append(dict(t=st(s), gate=0.15, midi=CHORDS[ch0][1], vel=0.9, base=300, env=900))
            if last:
                hats("OFF8G", 1.0, 0, 8)
                roll("half")
                A.riser.append((t0, st(15), 1.0))
                gap()
            else:
                hats("OFF8G", 1.1 if second else 1.0)
            arp(1.0 if second else 0.9)
        elif sec == "LOCKUP":
            A.padfc.append((t0, t0 + BAR, 2200, 2200))
            A.kick.append((t0, 1.0))
            bass_pedal(base=260, env=300, vel=0.85)
            arp(1.0, sparse=True)
        elif sec == "INSTALL":
            A.padfc.append((t0, t0 + BAR, 1400, 1400))
            bass_pedal(base=220, env=200, vel=0.75)
            for e in range(8):
                x = (k * 8 + e) / (nrun * 8 - 1)
                c = chord_at(chords, e / 2)
                A.pluck.append((t0 + e * 2 * STEP, CHORDS[c][2][ARP_IDX[e]], ARP_VEL[e] * 0.4,
                                5000.0 - 2500.0 * x))
            if first:
                hats("OFF8", 0.5)
        elif sec == "END":
            A.padfc.append((t0, t0 + BAR, 1800, 1500))
            if first:
                A.sub.append((t0, db(-6)))
                for j, m in enumerate(CHORDS["Dadd9"][2]):
                    A.strum.append((t0 + 0.03 * j, m, 0.85 - 0.06 * j))
                A.bass.append(dict(t=t0, gate=3.6, midi=38, vel=0.8, base=260, env=300, rel=0.6))
                A.endsub.append(t0)
        else:
            raise ValueError(sec)
    return A


# ----------------------------------------------------------------------------- instruments (§3)


def kick_one(rng):
    n = ns(0.5)
    t = tvec(n)
    body = sine(45 + 105 * np.exp(-t / 0.035), n) * np.exp(-t / 0.32)
    k = ns(0.002)
    click = butter(butter(rng.standard_normal(k), "hp", 2000, 2), "lp", 9000, 2) * np.exp(-tvec(k) / 0.0007) * db(-16)
    body[:k] += click
    return edge_fade(np.tanh(1.5 * body), 0.2, 40)


def sub_one(rng):
    n = ns(2.0)
    t = tvec(n)
    y = sine(38 + 42 * np.exp(-t / 0.08), n) * perc(n, 0.002, 0.6)
    y[: ns(0.5)] += kick_one(rng) * 0.9
    k = ns(0.08)
    y[:k] += butter(rng.standard_normal(k), "lp", 800, 2) * np.exp(-tvec(k) / 0.025) * db(-18)
    return edge_fade(y, 0, 150)


def clap_one(rng, fc):
    n = ns(0.45)
    t = tvec(n)
    x = np.zeros(n)
    for off in (0.0, 0.010, 0.020):
        s, k = ns(off), ns(0.008)
        x[s:s + k] += rng.standard_normal(k) * np.exp(-tvec(k) / 0.003)
    s = ns(0.020)
    x[s:] += 0.55 * rng.standard_normal(n - s) * np.exp(-tvec(n - s) / 0.09)
    y = filt(x, "bp", fc, 1.2)
    y = y / peak(y)
    y += db(-10) * sine(190.0, n) * np.exp(-t / 0.04)
    return edge_fade(y / peak(y), 0, 20)


def hat_one(rng, open_):
    tau = 0.12 if open_ else 0.018
    n = ns(tau * 7)
    y = filt(filt(rng.standard_normal(n), "hp", 7000, 0.707), "hp", 7000, 0.707)
    y *= perc(n, 0.0005, tau)
    return edge_fade(y / peak(y), 0, 5)


def bass_note(rng, f, gate, vel, base, env, lfo=None, lfo_off=0.0, rel=0.04):
    n = ns(gate + max(0.25, rel * 6))
    t = tvec(n)
    p = rng.random(2)
    osc = 0.5 * saw(f * 2 ** (6 / 1200), n, p[0]) + 0.5 * saw(f * 2 ** (-6 / 1200), n, p[1])
    osc += 0.5 * square(f / 2, n, 0.0)
    x = saturate(0.7 * osc, 1.8)
    fenv = np.where(t < 0.002, t / 0.002, np.exp(-(t - 0.002) / 0.14))
    fc = base + env * fenv
    if lfo:
        rate, depth = lfo
        fc = fc + depth * np.cos(2 * np.pi * rate * (t + lfo_off))
    y = ladder(x, np.maximum(fc, 30.0), 0.25)
    y *= adsr(n, 0.003, 0.12, 0.7, rel, gate)
    return edge_fade(y * vel, 0, 5)


def pluck_note(rng, f, vel, fc0, tau=0.22, length=1.0):
    n = ns(length)
    t = tvec(n)
    osc = saw(f, n, rng.random()) + 0.3 * square(f * 2 ** (5 / 1200), n, rng.random())
    fc = 700 + (fc0 - 700) * np.exp(-t / 0.09)
    y = tv_filt(osc, "lp", fc, 1.0)
    return edge_fade(y * perc(n, 0.002, tau) * vel, 0, 30)


def lead_note(f, mode):
    n = ns(3.5)
    t = tvec(n)
    amp = perc(n, 0.001, 0.9)
    y = fm_bell(f, n, 2.0, 4 * np.exp(-t / 0.08) + 0.6, amp)
    y += db(-14) * sine(2 * f, n) * amp
    if mode == "red":
        y = butter(y, "lp", 1500, 2)
    return edge_fade(y, 0, 300)


def riser_one(rng, dur, top=1.0):
    n = ns(dur)
    t = tvec(n)
    x = t / dur
    fc = 300 * (8000 / 300) ** x
    noise = tv_filt(rng.standard_normal((2, n)), "bp", fc, 2.0)
    noise /= peak(noise)
    sw = db(-20) * sine(220 * 8 ** x, n)
    g = db(-40 + 34 * x ** 3) * top
    y = (noise + sw) * g
    return edge_fade(y, 0, 5)


def glitch_one(seed, card=False):
    rng = np.random.default_rng(seed)
    n = ns(0.004)
    f = rng.uniform(3000, 6000)
    y = bitcrush(sine(f, n) * np.hanning(n + 2)[1:-1] ** 0.3, 6, 4)
    if card:
        m = ns(0.06)
        z = np.zeros(m)
        z[:n] += y
        k = ns(0.002)
        z[:k] += butter(rng.standard_normal(k), "hp", 4000, 2) * 0.8 * np.exp(-tvec(k) / 0.0005)
        z += 0.6 * sine(2400.0, m) * perc(m, 0.001, 0.010) * (tvec(m) < 0.030)
        y = z
    y = edge_fade(y, 0, 1)
    return pan(y / peak(y), rng.uniform(-0.6, 0.6) if not card else 0.0)


# ----------------------------------------------------------------------------- render music


def render_pad(A, n, rng):
    # merge segments into per-pitch lanes (common tones are held through chord changes)
    lanes, active = [], {}
    prev_end, prev_rel = None, 1.0
    for seg in sorted(A.pad, key=lambda s: s["t0"]):
        notes = CHORDS[seg["chord"]][0]
        if prev_end is not None and (abs(seg["t0"] - prev_end) > 1e-6 or seg["retrig"]):
            for m, (ton, att) in active.items():
                lanes.append((m, ton, seg["t0"] if seg["retrig"] else prev_end, att, prev_rel))
            active = {}
        for m in list(active):
            if m not in notes:
                ton, att = active.pop(m)
                lanes.append((m, ton, seg["t0"], att, prev_rel))
        for m in notes:
            if m not in active:
                active[m] = (seg["t0"], seg["att"])
        prev_end, prev_rel = seg["t1"], seg["rel"]
    for m, (ton, att) in active.items():
        lanes.append((m, ton, prev_end, att, prev_rel))

    out = np.zeros((2, n))
    envsum = np.zeros(n)
    for j, (m, ton, toff, att, rel) in enumerate(sorted(lanes, key=lambda l: (l[1], l[0]))):
        s = ns(ton)
        L = min(ns(toff - ton + rel * 5), n - s)
        if L <= 0:
            continue
        f = hz(m)
        osc = sum(saw(f * 2 ** (c / 1200), L, rng.random()) for c in (-9, 0, 9)) * db(-10)
        env = adsr(L, att, 1.0, 0.8, rel, toff - ton)
        env = edge_fade(env, 0, 20)
        place(out, pan(osc * env, 0.3 if m % 2 else -0.3), s)
        envsum[s:s + L] += env
    # cutoff automation (log-linear per bar, glided) + LFO 0.125 Hz +-200 Hz
    t = tvec(n)
    lf = np.full(n, np.log(1100.0))
    for t0, t1, f0, f1 in sorted(A.padfc):
        a, b = ns(t0), min(ns(t1), n)
        lf[a:b] = np.linspace(np.log(f0), np.log(f1), b - a)
        lf[b:] = np.log(f1)
    lf = filt(lf - lf[0], "lp", 4.0, 0.5) + lf[0]
    fc = np.exp(lf) + 200 * np.sin(2 * np.pi * 0.125 * t)
    out = tv_filt(out, "lp", fc, 0.7, block=64)
    # air layer
    air = filt(rng.standard_normal((2, n)), "bp", 7000, 0.8)
    air *= envsum / max(peak(envsum), 1e-9)
    out += air * db(-32) / max(peak(air), 1e-9) * peak(out)
    out = filt(filt(out, "hp", 150, 0.6), "peak", 330, 0.8, -3.0)  # clear the bass / low-mid
    out = chorus(out, 0.4)
    # fades
    g = np.ones(n)
    for t0, dur in A.padfade:
        a, b = ns(t0), ns(t0 + dur)
        g[:a] = 0
        g[a:b] = np.linspace(0, 1, b - a) ** 2
    return out * g


def render_swell(t_end, chord, ir, rng, n):
    L = ns(1.0)
    f = hz(np.array(CHORDS[chord][0]))
    dry = np.zeros(L)
    for m in f:
        dry += sum(saw(m * 2 ** (c / 1200), L, rng.random()) for c in (-9, 0, 9))
    dry = filt(dry, "lp", 2400, 0.7) * edge_fade(np.ones(L), 0, 30)
    k = ns(0.05)
    dry[:k] += rng.standard_normal(k) * 2.0 * np.exp(-tvec(k) / 0.015)
    pad_in = np.concatenate([dry, np.zeros(ns(1.5))])
    wet = reverb(pad_in, ir, hp=150)
    tail = wet[:, L:2 * L][:, ::-1]
    tail *= np.linspace(0, 1, L) ** 0.5
    out = np.zeros((2, n))
    place(out, edge_fade(tail, 0, 4), ns(t_end) - L)
    return out


def render_music(film, A, n, ir):
    """Returns dict of dry tracks: name -> (stereo signal, reverb send, delay send)."""
    tr = {}
    R = lambda i: np.random.default_rng(SEED + i)  # noqa: E731 (per-stem rng)

    # drums (stem 1)
    rng = R(1)
    kick = np.zeros(n)
    ks = kick_one(rng)
    for t, v in A.kick:
        place(kick, ks * v, ns(t))
    sub = np.zeros(n)
    for t, v in A.sub:
        place(sub, sub_one(rng) * v, ns(t))
    clap = np.zeros(n)
    for t, v, fc in A.clap:
        place(clap, clap_one(rng, fc) * v, ns(t))
    hat = np.zeros(n)
    hits = sorted(A.hat)
    for j, (t, v, op) in enumerate(hits):
        h = hat_one(rng, op) * v
        if op and j + 1 < len(hits):  # choke on the next hit
            k = ns(hits[j + 1][0] - t)
            if k < len(h):
                h = edge_fade(h[:k], 0, 4)
        place(hat, h, ns(t))
    tr["kick"] = (pan(normalize(kick, -8), 0), 0.0, 0.0, "drums", "drums")
    tr["sub"] = (pan(normalize(sub, -7), 0), 0.0, 0.0, "drums", None)
    tr["clap"] = (pan(normalize(clap, -13), 0), 0.25, 0.0, "drums", "drums")
    tr["hat"] = (pan(normalize(hat, -20), 0.2), 0.08, 0.0, "drums", "drums")

    # bass (stem 0), sidechained from kick + sub hits
    rng = R(0)
    bass = np.zeros(n)
    for b in A.bass:
        y = bass_note(rng, hz(b["midi"]), b["gate"], b["vel"], b["base"], b["env"], b.get("lfo"),
                      b["t"] - b.get("lfo_t0", b["t"]), b.get("rel", 0.04))
        place(bass, y, ns(b["t"]))
    for t in A.endsub:
        m = ns(4.0)
        place(bass, edge_fade(sine(hz(26), m) * perc(m, 0.005, 1.5), 0, 200) * 0.6, ns(t))
    bass = butter(bass, "hp", 30, 2)
    duck_t = [t for t, _ in A.kick] + [t for t, _ in A.sub]
    bass *= duck_curve(n, duck_t, 0.5, 0.09)
    tr["bass"] = (pan(normalize(bass, -8), 0), 0.0, 0.0, "bass", "bass")

    # pad (stem 3)
    pad = render_pad(A, n, R(3))
    pad *= duck_curve(n, duck_t, 0.2, 0.15)
    tr["pad"] = (normalize(pad, -11), 0.35, 0.0, "pad", "pad")

    # pluck + lead (stem 2)
    rng = R(2)
    pl = np.zeros((2, n))
    for j, (t, m, v, fc0) in enumerate(sorted(A.pluck)):
        place(pl, pan(pluck_note(rng, hz(m), v, fc0), 0.25 if j % 2 else -0.25), ns(t))
    tr["pluck"] = (normalize(pl, -14), 0.20, 0.22, "pluck", "pluck")
    stm = np.zeros((2, n))
    for j, (t, m, v) in enumerate(A.strum):
        place(stm, pan(pluck_note(rng, hz(m), v, 4200, tau=0.9, length=3.5), -0.3 + 0.15 * j), ns(t))
    tr["strum"] = (normalize(stm, -15), 0.30, 0.12, "pluck", None)
    for mode, send, dl in (("bell", 0.30, 0.15), ("red", 0.30, 0.15), ("dry", 0.10, 0.0)):
        ld = np.zeros((2, n))
        for j, (t, m, md) in enumerate(A.lead):
            if md == mode:
                y = pan(lead_note(hz(m), md), 0.0)
                y = np.concatenate([y, np.zeros((2, ns(3.0)))], axis=1)
                if dl:  # ping-pong starting on alternate sides per motif note
                    y = y + pingpong(y, 0.375, 0.32, dl, first=j % 2)
                place(ld, y, ns(t))
        if peak(ld) > 0:
            lvl = {"bell": -17.5, "red": -18.5, "dry": -15.5}[mode]
            tr["lead_" + mode] = (normalize(ld, lvl), send, 0.0, "pluck", None)

    # fx (stem 4)
    rng = R(4)
    rs = np.zeros((2, n))
    for t0, t1, top in A.riser:
        place(rs, riser_one(rng, t1 - t0, top), ns(t0))
    tr["riser"] = (normalize(rs, -13), 0.15, 0.0, "fx", None)
    gl = np.zeros((2, n))
    for t, seed in A.glitch:
        place(gl, glitch_one(seed), ns(t))
    tr["glitch"] = (normalize(gl, -20), 0.20, 0.0, "fx", None)
    sw = np.zeros((2, n))
    for t, c in A.swell:
        sw += render_swell(t, c, ir, rng, n)
    tr["swell"] = (normalize(sw, -9), 0.0, 0.0, "fx", None)
    return tr


# ----------------------------------------------------------------------------- SFX (§6)

CUES = ["key-tick", "key-tick-soft", "key-enter", "key-press", "blip-eye", "blip-card",
        "spark-micro", "spark-sting", "spark-sting-short", "hit-buzz", "chime-landed",
        "whoosh-in", "whoosh-out", "glitch-tick", "card-tick"]
ALIASES = {
    "landed-chime": "chime-landed", "card-blip": "blip-card", "eye-blip": "blip-eye",
    "spark-sting-full": "spark-sting", "sting": "spark-sting", "enter": "key-enter",
    "confirm-y": ["key-press", "spark-micro"], "always-a": ["key-press", "spark-micro"],
}
SFX_PEAK = {"key-tick": -24, "key-tick-soft": -31, "key-enter": -18, "key-press": -16,
            "blip-eye": -20, "blip-card": -18, "spark-micro": -16, "spark-sting": -7,
            "spark-sting-short": -14, "hit-buzz": -14, "chime-landed": -14, "whoosh-in": -20,
            "whoosh-out": -22, "glitch-tick": -20, "card-tick": -15}
SFX_SEND = {"blip-eye": 0.2, "blip-card": 0.15, "spark-micro": 0.25, "spark-sting": 0.3,
            "spark-sting-short": 0.3, "hit-buzz": 0.1, "chime-landed": 0.3, "whoosh-in": 0.1,
            "whoosh-out": 0.1, "glitch-tick": 0.2, "card-tick": 0.15, "key-enter": 0.05,
            "key-press": 0.08}
TICK_MIN_GAP = 0.024  # key ticks closer than this to the previous tick are skipped


def load_events(path, length):
    data = json.loads(Path(path).read_text())
    placeholder = False
    if isinstance(data, dict):
        placeholder = bool(data.get("_placeholder", False))
        data = data["events"]
    out = []
    for e in data:
        cue = str(e["cue"]).strip().lower().replace("_", "-")
        cue = ALIASES.get(cue, cue)
        for c in cue if isinstance(cue, list) else [cue]:
            if c not in CUES:
                raise SystemExit(f"unknown cue {e['cue']!r} in {path}; known: {', '.join(CUES)}")
            t = float(e["t"])
            if not 0 <= t < length:
                print(f"  warn: {c} at {t:.3f}s is outside the film, skipped")
                continue
            out.append(dict(e, cue=c, t=t))
    out.sort(key=lambda e: (e["t"], e["cue"]))
    # thin dense type-on ticks
    kept, last = [], -1.0
    for e in out:
        if e["cue"].startswith("key-tick"):
            if e["t"] - last < TICK_MIN_GAP:
                continue
            last = e["t"]
        kept.append(e)
    return kept, placeholder


def diamond(t0_list=(0, 0.025, 0.05, 0.075), pans=(-0.6, 0.6, -0.3, 0.3)):
    n = ns(0.3)
    y = np.zeros((2, n))
    k = ns(0.04)
    g = sine(2349.3, k) * perc(k, 0.001, 0.015)
    g = edge_fade(g, 0, 5)
    for t, p in zip(t0_list, pans):
        place(y, pan(g, p), ns(t))
    return y


def sfx_one(cue, rng, ev, ir):
    """Returns (stereo dry one-shot normalised to the cue's peak, start offset in s, presuck)."""
    presuck = None
    off = 0.0
    ref = None  # peak the cue level refers to (default: the whole one-shot)
    if cue in ("key-tick", "key-tick-soft"):
        n = ns(0.03)
        k = ns(0.006)
        x = np.zeros(n)
        x[:k] = rng.standard_normal(k)
        y = filt(x, "bp", rng.uniform(3000, 4500), 1.5) * perc(n, 0.0002, 0.002)
        c = ns(0.002)
        y[:c] += butter(butter(rng.standard_normal(c), "hp", 4000, 2), "lp", 9000, 2) * 0.3 * np.exp(-tvec(c) / 0.0004)
        y = pan(edge_fade(y, 0, 5), rng.uniform(-0.15, 0.15)) * db(rng.uniform(-3, 3))
        return normalize(y, SFX_PEAK[cue] + rng.uniform(-3, 0)), off, None
    if cue in ("key-enter", "key-press"):
        n = ns(0.2)
        k = ns(0.014)
        x = np.zeros(n)
        x[:k] = rng.standard_normal(k) * np.exp(-tvec(k) / 0.005)
        y = filt(x, "bp", 1800 if cue == "key-enter" else 2400, 1.5)
        y = y / peak(y) + 0.8 * sine(120 * (1 + 0.5 * np.exp(-tvec(n) / 0.01)), n) * perc(n, 0.001, 0.03)
        y = pan(edge_fade(y, 0, 20), 0.0)
    elif cue == "blip-eye":
        n = ns(0.45)
        y = np.zeros(n)
        for f, t in ((1760.0, 0.0), (2349.3, 0.055)):
            m = n - ns(t)
            y[ns(t):] += sine(f, m) * perc(m, 0.001, 0.06)
        y = pan(edge_fade(y, 0, 30), 0.0)
    elif cue == "blip-card":
        n = ns(0.5)
        y = np.zeros(n)
        a = ns(0.05)
        y[:a] = square(659.26, a) * adsr(a, 0.001, 0.08, 0.0, 0.004, 0.046)
        m = n - a
        y[a:] += square(880.0, m) * perc(m, 0.001, 0.08)
        y = pan(edge_fade(butter(y, "lp", 3000, 2), 0, 30), 0.0)
    elif cue == "spark-micro":
        n = ns(1.2)
        t = tvec(n)
        y = fm_bell(2349.3, n, 1.5, 2 * np.exp(-t / 0.03), perc(n, 0.001, 0.25))
        y = pan(edge_fade(y, 0, 50), 0.0)
        d = diamond()
        y[:, : d.shape[1]] += d * db(-12)
    elif cue in ("spark-sting", "spark-sting-short"):
        full = cue == "spark-sting"
        n = ns(4.5 if full else 3.0)
        t = tvec(n)
        tau = 1.6 if full else 0.9
        bells = np.zeros((2, n))
        for f, p in ((1174.66, -0.15), (1760.0, 0.15)):
            b = fm_bell(f, n, 2.0, (4.4 if full else 2.4) * np.exp(-t / 0.06) + 0.6, perc(n, 0.001, tau))
            bells += pan(b, p)
        d = diamond()
        bells[:, : d.shape[1]] += d * (1.2 if full else 0.4)
        m = ns(2.0)
        sh = butter(rng.standard_normal((2, m)), "hp", 8000, 2) * perc(m, 0.002, 0.4)
        sh *= peak(bells) / np.sqrt(np.mean(sh[:, : ns(0.4)] ** 2))  # shimmer RMS re bell peak:
        bells[:, :m] += sh * db(-18 if full else -30)  # -18 dB (full) / -30 dB (short)
        y = bells
        if full:
            # pre-suck: the sting's own reverb tail, reversed, rising into t0
            wet = reverb(np.concatenate([bells, np.zeros((2, ns(1.0)))], axis=1), ir)
            L = ns(0.5)
            ps = wet[:, : ns(1.0)][:, ::-1][:, -L:].copy()
            ps *= np.linspace(0, 1, L) ** 2
            presuck = edge_fade(ps, 0, 3)
            # sub layer: normalised separately (SFX_PEAK applies to the bells; sub sits 2 dB under)
            ref = peak(bells)
            sub = pan(sub_one(rng), 0.0)
            y = bells.copy()
            place(y, sub * db(-2) * ref / peak(sub), 0)
        y = edge_fade(y, 0, 300)
    elif cue == "hit-buzz":
        n = ns(0.5)
        k = ns(0.18)
        x = np.zeros(n)
        x[:k] = (square(55.0, k) + square(58.27, k)) * 0.5 * edge_fade(np.ones(k), 0, 6)
        x = butter(x, "lp", 900, 2)
        x = bitcrush(x / peak(x), 5, 1) * perc(n, 0.001, 0.12)
        x = butter(x, "lp", 5000, 2)
        x += kick_one(rng)[:n] * db(-6)
        y = pan(edge_fade(x, 0, 20), 0.0)
    elif cue == "chime-landed":
        n = ns(4.0)
        y = np.zeros((2, n))
        for f, dt, p in ((1174.66, 0, -0.3), (1760.0, 0.04, 0.3), (2349.3, 0.08, -0.15), (2637.0, 0.12, 0.15)):
            m = n - ns(dt)
            tt = tvec(m)
            b = fm_bell(f, m, 3.5, 1.5 * np.exp(-tt / 0.1), perc(m, 0.001, 1.4))
            place(y, pan(b, p), ns(dt))
        y = edge_fade(y, 0, 300)
    elif cue in ("whoosh-in", "whoosh-out"):
        dur = float(ev.get("dur", 0.4))
        n = ns(dur)
        x = tvec(n) / dur
        fc = 400 * (3500 / 400) ** x
        g = x ** 2
        nz = tv_filt(rng.standard_normal(n), "bp", fc, 1.4)
        y = nz * g
        pp = -0.5 + x
        if cue == "whoosh-out":
            y = y[::-1]
            pp = pp[::-1]
        a = (np.clip(pp, -1, 1) + 1) * np.pi / 4
        y = np.stack([y * np.cos(a), y * np.sin(a)]) * np.sqrt(2)
        y = edge_fade(y, 20 if cue == "whoosh-out" else 5, 20 if cue == "whoosh-in" else 40)
    elif cue == "glitch-tick":
        y = glitch_one(int(rng.integers(1 << 30)))
    elif cue == "card-tick":
        y = glitch_one(int(rng.integers(1 << 30)), card=True)
    else:
        raise ValueError(cue)
    pk = ref or peak(y)
    g = db(SFX_PEAK[cue] + float(ev.get("gain_db", 0.0))) / pk
    return y * g, off, (presuck * g * db(-12) / peak(presuck) * pk if presuck is not None else None)


def render_sfx(events, n, ir):
    dry = np.zeros((2, n))
    send = np.zeros((2, n))
    post = np.zeros((2, n))
    for k, ev in enumerate(events):
        rng = np.random.default_rng([SEED + 5, k])
        y, off, ps = sfx_one(ev["cue"], rng, ev, ir)
        s = ns(ev["t"] + off)
        place(dry, y, s)
        place(send, y * SFX_SEND.get(ev["cue"], 0.0), s)
        if ps is not None:
            place(post, ps, s - ps.shape[1])
    wet = reverb(send, ir) if peak(send) > 0 else np.zeros((2, n))
    return dry + wet, post


# ----------------------------------------------------------------------------- master (§7)


def gap_curve(n, gaps, ramp=0.005):
    g = np.ones(n)
    r = ns(ramp)
    w = 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, r))
    for a, b in gaps:
        A, B = ns(a), ns(b)
        g[A:B - r] = 0.0
        g[A:A + r] = np.minimum(g[A:A + r], w)
        g[B - r:B] = np.minimum(g[B - r:B], w[::-1])
    return g


def fade_curve(n, fade):
    g = np.ones(n)
    a, b = ns(fade[0]), ns(fade[1])
    g[a:b] = 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, b - a))
    g[b:] = 0.0
    k = ns(0.003)
    g[:k] *= np.linspace(0, 1, k)
    return g


def master(stems, post, film, target=-14.0, ceiling=-1.5):
    """stems: dict name -> (2, n). Every bus stage is either linear per stem (HPF, mono-bass) or a
    shared gain curve, so the processed stems still sum exactly to the mix."""
    F = FILMS[film]
    n = next(iter(stems.values())).shape[1]
    gaps = gap_curve(n, ARR_GAPS[film])
    proc = {}
    for k, x in stems.items():
        x = mono_below(butter(x, "hp", 25, 2), 120.0)
        x = filt(x, "hs", 5000, 0.7, 2.0)  # +2 dB air shelf
        x = x * gaps
        if k == "sfx":
            x = x + mono_below(butter(post, "hp", 25, 2), 120.0)  # pre-suck bypasses the gaps
        proc[k] = x
    mix = sum(proc.values())
    g0 = db(-16.0 - lufs(mix))
    comp = glue_gain(mix * g0)
    fade = fade_curve(n, F["fade"])
    G = g0 * comp
    gain = db(target - lufs(mix * G * fade))
    lim = np.ones(n)
    ceil_try = ceiling - 0.05
    for _ in range(10):
        y = mix * G * gain
        lim = limiter_gain(y, ceil_try)
        z = y * lim * fade
        L, TP = lufs(z), true_peak_db(z)
        if abs(L - target) <= 0.05 and TP <= ceiling - 0.05:
            break
        if TP > ceiling - 0.05:
            ceil_try -= TP - (ceiling - 0.1)
        gain *= db(target - L)
    total = G * gain * lim * fade
    out = {k: x * total for k, x in proc.items()}
    info = dict(comp_max_gr=float(-20 * np.log10(np.min(comp))),
                lim_max_gr=float(-20 * np.log10(np.min(lim))))
    return out, info


ARR_GAPS = {}


def mix_curve(A, grp, n, ramp=0.02):
    """Gain curve for a track group from SECTION_MIX, stepping on downbeats with 20 ms ramps."""
    g = np.zeros(n)
    for t0, sec, k, nrun in A.bars:
        v = SECTION_MIX[sec].get(grp, 0.0)
        if isinstance(v, tuple):
            a, b = v
            v0, v1 = a + (b - a) * k / nrun, a + (b - a) * (k + 1) / nrun
        else:
            v0 = v1 = v
        s0, s1 = ns(t0), min(ns(t0 + BAR), n)
        g[s0:s1] = np.linspace(v0, v1, s1 - s0)
        g[s1:] = v1
    if A.bars and ns(A.bars[0][0]) > 0:
        g[: ns(A.bars[0][0])] = g[ns(A.bars[0][0])]
    k = ns(ramp)
    g = np.convolve(np.concatenate([np.full(k, g[0]), g]), np.ones(k) / k, mode="valid")[:n]
    return db(g)


def write_float(path, x):
    """32-bit float WAV without libsndfile's PEAK chunk (it holds a timestamp, which would make
    identical renders differ byte-wise)."""
    sf.write(path, x.T, SR, subtype="FLOAT")
    raw = Path(path).read_bytes()
    out, i = [raw[:12]], 12
    while i + 8 <= len(raw):
        cid, size = raw[i:i + 4], int.from_bytes(raw[i + 4:i + 8], "little")
        end = i + 8 + size + (size & 1)
        if cid != b"PEAK":
            out.append(raw[i:end])
        i = end
    body = b"".join(out)
    Path(path).write_bytes(body[:4] + (len(body) - 8).to_bytes(4, "little") + body[8:])


def render(film, events_path, out_dir, all_stems=False):
    t_start = time.time()
    F = FILMS[film]
    n = ns(F["length"])
    A = arrange(film)
    ARR_GAPS[film] = A.gaps
    ir = make_ir(np.random.default_rng(SEED + 99))

    tracks = render_music(film, A, n, ir)
    stems = {s: np.zeros((2, n)) for s in ("bass", "drums", "pluck", "pad", "fx")}
    sends = {s: np.zeros((2, n)) for s in stems}
    autos = {}
    for name, (x, rv, dl, stem, grp) in tracks.items():
        if grp:
            if grp not in autos:
                autos[grp] = mix_curve(A, grp, n)
            x = x * autos[grp]
        stems[stem] += x
        if rv:
            sends[stem] += x * rv
        if dl:
            stems[stem] += pingpong(x, 0.375, 0.32, dl)
    for s in stems:
        if peak(sends[s]) > 0:
            stems[s] += reverb(sends[s], ir)

    events, placeholder = load_events(events_path, F["length"])
    sfx, post = render_sfx(events, n, ir)
    stems["sfx"] = sfx

    out, info = master(stems, post, film)
    zeros_from = ns(F["length"] - 0.05)
    # Quantise to the 24-bit grid: the delivery precision, and it makes the files bit-identical
    # run to run (numpy's SIMD reductions can move a gain by one ulp with memory alignment).
    # The mix is the exact sum of the two quantised stems.
    q = lambda x: np.round(x * 2.0 ** 23) / 2.0 ** 23  # noqa: E731
    out = {k: q(v) for k, v in out.items()}
    music = q(sum(v for k, v in out.items() if k != "sfx"))
    sfx = out["sfx"]
    for x in (music, sfx, *out.values()):
        x[:, zeros_from:] = 0.0
    mix = music + sfx

    out_dir.mkdir(parents=True, exist_ok=True)
    sf.write(out_dir / f"{film}.wav", mix.T, SR, subtype="PCM_24")
    write_float(out_dir / f"{film}-music.wav", music)
    write_float(out_dir / f"{film}-sfx.wav", sfx)
    if all_stems:
        d = out_dir / f"{film}-stems"
        d.mkdir(exist_ok=True)
        for k, v in out.items():
            write_float(d / f"{k}.wav", v)

    # re-measure the file as written (24-bit)
    written, _ = sf.read(out_dir / f"{film}.wav", always_2d=True)
    w = written.T
    L, TP = lufs(w), true_peak_db(w)
    tail = np.max(np.abs(w[:, zeros_from:]))
    print(f"{film}: {w.shape[1]} samples ({w.shape[1] / SR:.3f} s), events {len(events)}"
          f"{' (PLACEHOLDER events.json)' if placeholder else ''}")
    print(f"  integrated {L:.2f} LUFS, true peak {TP:.2f} dBTP, sample peak {20 * np.log10(np.max(np.abs(w))):.2f} dBFS,"
          f" last 50 ms max {tail:.1e}, DC {np.mean(w):.1e}")
    print(f"  glue max GR {info['comp_max_gr']:.1f} dB, limiter max GR {info['lim_max_gr']:.1f} dB,"
          f" render {time.time() - t_start:.1f} s -> {out_dir / (film + '.wav')}")
    return L, TP


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--film", required=True, choices=list(FILMS))
    ap.add_argument("--events", help="events.json (default v2/<film>/events.json)")
    ap.add_argument("--out", default=str(REPO / "out" / "v2" / "audio"))
    ap.add_argument("--stems", action="store_true", help="also write the six per-instrument stems")
    a = ap.parse_args()
    ev = Path(a.events) if a.events else REPO / "v2" / a.film / "events.json"
    render(a.film, ev, Path(a.out), a.stems)


if __name__ == "__main__":
    main()
