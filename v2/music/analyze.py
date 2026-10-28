#!/usr/bin/env python3
"""Check a rendered score: loudness, true peak, per-bar envelope/spectrum, DC, clicks, spectrogram.

    python3 v2/music/analyze.py out/v2/audio/trailer60.wav [--offset 0] [--png out.png]

Per bar (2.0 s from --offset): sample peak, RMS, ungated K-weighted loudness, spectral centroid,
energy share below 120 Hz and side/mid ratio. Clicks: samples where the 2nd difference of the
>8 kHz band jumps far above its local median (transient SFX show up too; check them against the
cue list). --png needs matplotlib.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import signal

sys.path.insert(0, str(Path(__file__).resolve().parent))
from synth import SR, lufs, short_term, true_peak_db  # noqa: E402


def clicks(x, top=12):
    m = x.mean(axis=0)
    hp = signal.sosfilt(signal.butter(4, 8000, "highpass", fs=SR, output="sos"), m)
    d = np.abs(np.diff(hp, 2))
    win = int(0.010 * SR)
    env = np.sqrt(np.maximum(signal.convolve(d ** 2, np.ones(win) / win, mode="same"), 0)) + 1e-9
    base = signal.medfilt(env[::64], 31).repeat(64)[: len(env)] + 1e-7
    ratio = d / base
    idx = np.argsort(ratio)[::-1]
    out, used = [], []
    for i in idx:
        if all(abs(i - u) > SR * 0.05 for u in used):
            used.append(i)
            out.append((i / SR, 20 * np.log10(ratio[i])))
        if len(out) >= top:
            break
    return sorted(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("wav")
    ap.add_argument("--offset", type=float, default=0.0)
    ap.add_argument("--png")
    a = ap.parse_args()
    x, sr = sf.read(a.wav, always_2d=True)
    x = x.T
    assert sr == SR
    n = x.shape[1]
    print(f"{a.wav}: {n} samples = {n / SR:.4f} s")
    print(f"integrated {lufs(x):.2f} LUFS, true peak {true_peak_db(x):.2f} dBTP, "
          f"DC L/R {x[0].mean():.1e}/{x[1].mean():.1e}, last 50 ms max {np.abs(x[:, -2400:]).max():.1e}")
    print(" bar   t0     peak   rms   LUFS  centroid  <120Hz  side/mid")
    starts = [0.0] if a.offset > 0 else []
    t = a.offset
    while t < n / SR - 1e-6:
        starts.append(t)
        t += 2.0
    for k, t0 in enumerate(starts):
        t1 = min(starts[k + 1] if k + 1 < len(starts) else n / SR, n / SR)
        s = x[:, int(t0 * SR):int(t1 * SR)]
        if s.shape[1] < 2048:
            continue
        pk = 20 * np.log10(np.abs(s).max() + 1e-12)
        rms = 10 * np.log10(np.mean(s ** 2) + 1e-20)
        st = short_term(x, t0, t1)
        f, p = signal.welch(s.mean(axis=0), SR, nperseg=8192)
        cen = np.sum(f * p) / (np.sum(p) + 1e-20)
        low = np.sum(p[f < 120]) / (np.sum(p) + 1e-20)
        mid = np.mean((0.5 * (s[0] + s[1])) ** 2)
        side = np.mean((0.5 * (s[0] - s[1])) ** 2)
        print(f"{k:4d} {t0:6.2f} {pk:6.1f} {rms:6.1f} {st:6.1f} {cen:8.0f} {100 * low:6.1f}% {10 * np.log10(side / (mid + 1e-20) + 1e-20):6.1f} dB")
    print("largest HF derivative spikes (t, dB over local median):")
    print("  " + ", ".join(f"{t:.3f}s {d:.0f}" for t, d in clicks(x)))
    if a.png:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(2, 1, figsize=(16, 8), sharex=True,
                               gridspec_kw={"height_ratios": [1, 3]})
        m = x.mean(axis=0)
        hop = 480
        env = np.sqrt(np.convolve(m ** 2, np.ones(hop) / hop, mode="same"))[::hop]
        tt = np.arange(len(env)) * hop / SR
        ax[0].plot(tt, 20 * np.log10(env + 1e-9), lw=0.6)
        pk = np.abs(x).max(axis=0)[: len(env) * hop].reshape(-1, hop).max(axis=1)
        ax[0].plot(tt[: len(pk)], 20 * np.log10(pk + 1e-9), lw=0.4, alpha=0.6)
        ax[0].set_ylim(-60, 0)
        ax[0].set_ylabel("dBFS")
        for s in starts:
            ax[0].axvline(s, color="k", lw=0.3)
            ax[1].axvline(s, color="w", lw=0.3, alpha=0.4)
        f, tt2, S = signal.spectrogram(m, SR, nperseg=4096, noverlap=3072)
        ax[1].pcolormesh(tt2, f, 10 * np.log10(S + 1e-14), vmin=-130, vmax=-30, shading="auto", cmap="magma")
        ax[1].set_yscale("symlog", linthresh=200)
        ax[1].set_ylim(20, 24000)
        ax[1].set_ylabel("Hz")
        ax[1].set_xlabel("s")
        fig.suptitle(Path(a.wav).name)
        fig.tight_layout()
        fig.savefig(a.png, dpi=90)
        print("wrote", a.png)


if __name__ == "__main__":
    main()
