"""HooCode v2 launch score: synthesis engine.

Pure numpy + scipy, float64, 48 kHz. No samples: every sound in the films is built from the
oscillators, noise, filters and effects in this file. Signals are 1-D (mono) or shape (2, n)
(stereo, channels first). Deterministic: every noise source takes an explicit numpy Generator.
"""

from __future__ import annotations

import numpy as np
from scipy import signal
from scipy.ndimage import minimum_filter1d

SR = 48_000


# ----------------------------------------------------------------------------- helpers


def db(x):
    """dB -> linear gain."""
    return 10.0 ** (np.asarray(x, dtype=float) / 20.0)


def to_db(x, floor=1e-12):
    return 20.0 * np.log10(np.maximum(np.abs(x), floor))


def hz(midi):
    """MIDI note -> Hz, A4 = 440."""
    return 440.0 * 2.0 ** ((np.asarray(midi, dtype=float) - 69.0) / 12.0)


def ns(t):
    """Seconds -> whole samples (sample-exact grid: 120 BPM 16th = 6000 samples)."""
    return int(round(t * SR))


def tvec(n):
    return np.arange(n) / SR


def edge_fade(x, a_ms=0.0, r_ms=3.0):
    """Raised-cosine fade at the start/end of a one-shot so it begins and ends at exact zero."""
    x = np.array(x, dtype=float, copy=True)
    n = x.shape[-1]
    for ms, end in ((a_ms, False), (r_ms, True)):
        k = min(n, ns(ms / 1000.0))
        if k <= 1:
            continue
        w = 0.5 - 0.5 * np.cos(np.linspace(0.0, np.pi, k))
        if end:
            x[..., n - k:] *= w[::-1]
        else:
            x[..., :k] *= w
    return x


def pan(mono, p):
    """Constant-power pan, p in [-1, 1] -> (2, n)."""
    a = (np.clip(p, -1, 1) + 1.0) * np.pi / 4.0
    return np.stack([mono * np.cos(a), mono * np.sin(a)]) * np.sqrt(2.0)


def place(buf, sig, start):
    """Add sig (mono or (2,n)) into buf (same rank) at sample index start, clipped to buf."""
    n = buf.shape[-1]
    m = sig.shape[-1]
    s0, s1 = max(start, 0), min(start + m, n)
    if s1 <= s0:
        return
    buf[..., s0:s1] += sig[..., s0 - start:s1 - start]


def peak(x):
    return float(np.max(np.abs(x))) if x.size else 0.0


def normalize(x, peak_db):
    p = peak(x)
    return x if p == 0 else x * (db(peak_db) / p)


# ----------------------------------------------------------------------------- oscillators


def _phase(freq, n, phase0=0.0):
    f = np.broadcast_to(np.asarray(freq, dtype=float), (n,))
    dt = f / SR
    ph = (np.cumsum(dt) - dt + phase0) % 1.0
    return ph, dt


def _blep(t, dt):
    """PolyBLEP residual for a unit step at phase 0 (2-sample polynomial)."""
    y = np.zeros_like(t)
    m = t < dt
    x = t[m] / dt[m]
    y[m] = x + x - x * x - 1.0
    m = t > 1.0 - dt
    x = (t[m] - 1.0) / dt[m]
    y[m] = x * x + x + x + 1.0
    return y


def saw(freq, n, phase0=0.0):
    """Band-limited (PolyBLEP) sawtooth, -1..1, rising."""
    ph, dt = _phase(freq, n, phase0)
    return 2.0 * ph - 1.0 - _blep(ph, dt)


def square(freq, n, phase0=0.0):
    """Band-limited (PolyBLEP) 50% square."""
    ph, dt = _phase(freq, n, phase0)
    y = np.where(ph < 0.5, 1.0, -1.0)
    y += _blep(ph, dt)
    y -= _blep((ph + 0.5) % 1.0, dt)
    return y


def sine(freq, n, phase0=0.0):
    ph, _ = _phase(freq, n, phase0)
    return np.sin(2.0 * np.pi * ph)


def fm_bell(f, n, ratio, index_env, amp_env, os=4):
    """2-op FM (carrier f, modulator ratio*f), rendered at os x SR and decimated (no fold-over)."""
    m = n * os
    t = np.arange(m) / (SR * os)
    idx = np.interp(t, tvec(n), index_env)
    mod = np.sin(2 * np.pi * ratio * f * t)
    car = np.sin(2 * np.pi * f * t + idx * mod)
    y = signal.resample_poly(car, 1, os)[:n]
    return y * amp_env


# ----------------------------------------------------------------------------- envelopes


def adsr(n, a, d, s, r, gate=None):
    """Linear attack a (s); exponential decay (tau d) to sustain s; exponential release (tau r)
    from the gate time. Times in seconds."""
    t = tvec(n)
    if a > 0:
        e = np.where(t < a, t / a, s + (1.0 - s) * np.exp(-(t - a) / max(d, 1e-6)))
    else:
        e = s + (1.0 - s) * np.exp(-t / max(d, 1e-6))
    if gate is not None:
        g = ns(gate)
        if g < n:
            lvl = e[g]
            e[g:] = lvl * np.exp(-(t[g:] - gate) / max(r, 1e-6))
    return e


def perc(n, a, tau):
    """Linear attack, exponential decay."""
    return adsr(n, a, tau, 0.0, tau)


# ----------------------------------------------------------------------------- filters


def rbj(kind, fc, q=0.7071, gain_db=0.0):
    """RBJ cookbook biquad coefficients (b, a), normalised."""
    fc = float(np.clip(fc, 5.0, 0.47 * SR))
    w = 2 * np.pi * fc / SR
    cw, sw = np.cos(w), np.sin(w)
    al = sw / (2 * q)
    A = 10 ** (gain_db / 40)
    if kind == "lp":
        b = [(1 - cw) / 2, 1 - cw, (1 - cw) / 2]
        a = [1 + al, -2 * cw, 1 - al]
    elif kind == "hp":
        b = [(1 + cw) / 2, -(1 + cw), (1 + cw) / 2]
        a = [1 + al, -2 * cw, 1 - al]
    elif kind == "bp":  # constant 0 dB peak gain
        b = [al, 0.0, -al]
        a = [1 + al, -2 * cw, 1 - al]
    elif kind == "peak":
        b = [1 + al * A, -2 * cw, 1 - al * A]
        a = [1 + al / A, -2 * cw, 1 - al / A]
    elif kind in ("ls", "hs"):
        sq = 2 * np.sqrt(A) * al
        if kind == "ls":
            b = [A * ((A + 1) - (A - 1) * cw + sq), 2 * A * ((A - 1) - (A + 1) * cw),
                 A * ((A + 1) - (A - 1) * cw - sq)]
            a = [(A + 1) + (A - 1) * cw + sq, -2 * ((A - 1) + (A + 1) * cw),
                 (A + 1) + (A - 1) * cw - sq]
        else:
            b = [A * ((A + 1) + (A - 1) * cw + sq), -2 * A * ((A - 1) + (A + 1) * cw),
                 A * ((A + 1) + (A - 1) * cw - sq)]
            a = [(A + 1) - (A - 1) * cw + sq, 2 * ((A - 1) - (A + 1) * cw),
                 (A + 1) - (A - 1) * cw - sq]
    else:
        raise ValueError(kind)
    b = np.array(b) / a[0]
    a = np.array(a) / a[0]
    return b, a


def filt(x, kind, fc, q=0.7071, gain_db=0.0):
    b, a = rbj(kind, fc, q, gain_db)
    return signal.lfilter(b, a, x, axis=-1)


def butter(x, kind, fc, order=2):
    sos = signal.butter(order, fc, btype={"lp": "lowpass", "hp": "highpass", "bp": "bandpass"}[kind],
                        fs=SR, output="sos")
    return signal.sosfilt(sos, x, axis=-1)


def onepole_lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    return signal.lfilter([1 - a], [1, -a], x, axis=-1)


def tv_filt(x, kind, fc, q=0.7071, block=32, step=0.004):
    """Time-varying biquad (2-pole SVF-equivalent response). fc is an array (Hz per sample) or a
    scalar. Coefficients follow fc per block of `block` samples, quantised to `step` in log-Hz so
    runs of near-constant cutoff are filtered in one call. State carries over (DF2T)."""
    x = np.asarray(x, dtype=float)
    n = x.shape[-1]
    if np.isscalar(fc):
        return filt(x, kind, fc, q)
    fc = np.clip(np.asarray(fc, dtype=float), 5.0, 0.47 * SR)
    starts = np.arange(0, n, block)
    key = np.round(np.log(fc[starts]) / step).astype(np.int64)
    change = np.flatnonzero(np.diff(key)) + 1
    run_starts = np.concatenate([[0], starts[change]])
    run_ends = np.concatenate([starts[change], [n]])
    run_fc = np.exp(key[np.concatenate([[0], change])] * step)
    y = np.empty_like(x)
    zi = np.zeros(x.shape[:-1] + (2,))
    for s0, s1, f in zip(run_starts, run_ends, run_fc):
        b, a = rbj(kind, f, q)
        y[..., s0:s1], zi = signal.lfilter(b, a, x[..., s0:s1], axis=-1, zi=zi)
    return y


def ladder(x, fc, res=0.25):
    """4-pole resonant lowpass (two cascaded time-varying biquads tuned like a ladder)."""
    y = tv_filt(x, "lp", fc, q=0.54)
    return tv_filt(y, "lp", fc, q=0.707 + 1.6 * res)


def saturate(x, drive):
    return np.tanh(drive * x) / np.tanh(drive)


def bitcrush(x, bits, hold):
    q = 2.0 ** (bits - 1)
    y = np.round(x * q) / q
    idx = (np.arange(len(y)) // hold) * hold
    return y[idx]


# ----------------------------------------------------------------------------- effects


def allpass_chain(x, delays_ms=(4.7, 7.3, 11.9, 17.3, 23.1), g=0.6):
    """Cascade of Schroeder all-pass filters: flat magnitude, scrambled phase (a decorrelator)."""
    for d in delays_ms:
        D = ns(d / 1000.0)
        b = np.zeros(D + 1)
        a = np.zeros(D + 1)
        b[0], b[D] = -g, 1.0
        a[0], a[D] = 1.0, -g
        x = signal.lfilter(b, a, x, axis=-1)
    return x


def make_ir(rng, dur=3.4, rt_low=2.6, rt_high=0.8, predelay=0.020):
    """Stereo hall IR. One noise IR with frequency-dependent decay (RT60 rt_low at 200 Hz falling
    to rt_high at 12 kHz = progressive damping), pink-weighted with a gentle tilt above 2 kHz, plus
    24 smeared early reflections (~12% of the energy) and a pre-delay. The right channel is the
    left through an all-pass decorrelator: identical magnitude response (tonal sources sit centred
    and both sides decay alike) with a different phase (the image stays wide)."""
    n = ns(dur)
    t = tvec(n)
    edges = [40, 160, 400, 900, 1800, 3500, 6500, 11000, 18000]
    ir = np.zeros(n)
    for lo, hi in zip(edges[:-1], edges[1:]):
        fcg = np.sqrt(lo * hi)
        k = np.clip(np.log(fcg / 200.0) / np.log(12000.0 / 200.0), 0.0, 1.0)
        rt = rt_low * (rt_high / rt_low) ** k
        sos = signal.butter(3, [lo, hi], btype="bandpass", fs=SR, output="sos")
        band = signal.sosfilt(sos, rng.standard_normal(n))
        band /= np.sqrt(np.mean(band ** 2))
        w = np.sqrt(np.log2(hi / lo)) * (min(1.0, 2000.0 / fcg) ** 0.25)
        ir += w * band * 10 ** (-3.0 * t / rt)
    ir *= np.minimum(1.0, (t / 0.060)) ** 1.5  # diffuse build-up over the first 60 ms
    er = np.zeros(n)
    burst = np.hanning(ns(0.0015))
    for tt in np.sort(rng.uniform(0.005, 0.080, 24)):
        place(er, rng.choice([-1, 1]) * (1 - tt / 0.1) * burst, ns(tt))
    er = onepole_lp(er, 6000.0)
    ir = ir + er * np.sqrt(0.12 * np.sum(ir ** 2) / np.sum(er ** 2))
    ir = np.concatenate([np.zeros(ns(predelay)), ir])
    ir = np.stack([ir, allpass_chain(ir)])
    ir = edge_fade(ir, 0, 200)
    ir /= np.sqrt(np.sum(ir ** 2, axis=-1, keepdims=True))
    return ir


def reverb(send, ir, hp=220.0, lp=9500.0):
    """Mono-sum the (stereo or mono) send, convolve with the stereo IR, EQ the return. The return
    is slowly delay-modulated per channel (about +-8 cents, 0.47 / 0.61 Hz): a modulated hall, so
    the tail of a sustained tone does not lock into a fixed dry/wet interference on one side."""
    mono = send if send.ndim == 1 else 0.5 * (send[0] + send[1])
    n = mono.shape[-1]
    wet = np.stack([signal.oaconvolve(mono, ir[c])[:n] for c in range(2)])
    wet = np.stack([mod_delay(wet[0], 0.004, 0.0025, 0.47, 0.0),
                    mod_delay(wet[1], 0.004, 0.0025, 0.61, 1.9)])
    wet = butter(wet, "hp", hp, 2)
    return butter(wet, "lp", lp, 2)


def pingpong(x, time, fb, wet, hp=300.0, lp=5000.0, taps=9, first=0):
    """Ping-pong delay (wet only): echo k on side `first` for odd k, the other side for even k;
    each pass through the feedback path is band-limited HP/LP, so repeats darken and thin."""
    mono = x if x.ndim == 1 else 0.5 * (x[0] + x[1])
    n = mono.shape[-1]
    d = ns(time)
    out = np.zeros((2, n))
    sig = mono
    gain = 1.0
    sos = np.array([np.concatenate(rbj("hp", hp)), np.concatenate(rbj("lp", lp))])
    for k in range(1, taps + 1):
        if k * d >= n:
            break
        sig = signal.sosfilt(sos, sig[: n - k * d])
        out[(k + 1 + first) % 2, k * d:] += gain * sig
        gain *= fb
    return out * wet


def mod_delay(x, base, depth, rate, phase=0.0):
    n = x.shape[-1]
    t = tvec(n)
    d = (base + depth * np.sin(2 * np.pi * rate * t + phase)) * SR
    idx = np.arange(n) - d
    i0 = np.floor(idx).astype(np.int64)
    fr = idx - i0
    i0c = np.clip(i0, 0, n - 1)
    i1c = np.clip(i0 + 1, 0, n - 1)
    y = x[i0c] * (1 - fr) + x[i1c] * fr
    y[i0 < 0] = 0.0
    return y


def chorus(x, wet=0.4):
    """Stereo chorus: L 12 ms / R 17 ms, depth 2 ms, rates 0.30 / 0.37 Hz."""
    l = mod_delay(x[0], 0.012, 0.002, 0.30, 0.0)
    r = mod_delay(x[1], 0.017, 0.002, 0.37, 1.3)
    return np.stack([x[0] * (1 - 0.5 * wet) + wet * l, x[1] * (1 - 0.5 * wet) + wet * r])


def duck_curve(n, times, depth, tau, attack=0.004):
    """Sidechain gain: x (1 - depth * h(t - tk)) per trigger, h = smooth 4 ms dip then exp(-t/tau)."""
    g = np.ones(n)
    L = ns(tau * 6 + attack)
    tt = tvec(L)
    h = np.where(tt < attack, 0.5 - 0.5 * np.cos(np.pi * tt / attack), 1.0)
    shape = 1.0 - depth * h * np.exp(-np.maximum(tt - attack, 0) / tau)
    for t in times:
        s = ns(t) - ns(attack)
        s0, s1 = max(s, 0), min(s + L, n)
        if s1 > s0:
            g[s0:s1] *= shape[s0 - s:s1 - s]
    return g


def width(x, w):
    m = 0.5 * (x[0] + x[1])
    s = 0.5 * (x[0] - x[1]) * w
    return np.stack([m + s, m - s])


def mono_below(x, fc=120.0):
    """Keep the low end mono: high-pass the side channel."""
    m = 0.5 * (x[0] + x[1])
    s = butter(0.5 * (x[0] - x[1]), "hp", fc, 2)
    return np.stack([m + s, m - s])


# ----------------------------------------------------------------------------- dynamics


def glue_gain(x, thr_db=-18.0, ratio=2.0, att=0.010, rel=0.150, rms_t=0.030, hop=16, max_gr=4.0):
    """Bus compressor gain curve (linear, length n). RMS detector, feed-forward, linked stereo."""
    p = np.mean(x ** 2, axis=0)
    a = np.exp(-1.0 / (rms_t * SR))
    p = signal.lfilter([1 - a], [1, -a], p)
    lvl = 10 * np.log10(p[::hop] + 1e-20)
    gr = np.minimum(0.0, (thr_db - lvl) * (1 - 1 / ratio))
    gr = np.maximum(gr, -max_gr)
    ca = np.exp(-hop / (att * SR))
    cr = np.exp(-hop / (rel * SR))
    out = np.empty_like(gr)
    g = 0.0
    for i, v in enumerate(gr):
        c = ca if v < g else cr
        g = c * g + (1 - c) * v
        out[i] = g
    n = x.shape[-1]
    return db(np.interp(np.arange(n), np.arange(len(out)) * hop, out))


def true_peak_env(x, os=4):
    """Per-sample true-peak magnitude (max over channels and the os inter-sample points)."""
    up = signal.resample_poly(x, os, 1, axis=-1)
    m = np.max(np.abs(up), axis=0)
    n = x.shape[-1]
    return m[: n * os].reshape(n, os).max(axis=1)


def true_peak_db(x):
    return float(to_db(np.max(true_peak_env(x))))


def limiter_gain(x, ceiling_db=-1.0, look=0.005, rel=0.080, hop=8):
    """Look-ahead true-peak limiter gain curve: required gain from the 4x-oversampled peak,
    min-filtered over the look-ahead window and smoothed (attack = look-ahead, exp release)."""
    n = x.shape[-1]
    tp = true_peak_env(x)
    req = np.minimum(1.0, db(ceiling_db) / np.maximum(tp, 1e-12))
    L = ns(look)
    # g[k] = min(req[k .. k+2L]) then a centred-forward moving average over L: never above req.
    mn = minimum_filter1d(req, size=2 * L + 1, origin=-L, mode="nearest")
    ker = np.ones(L) / L
    sm = np.convolve(np.concatenate([np.ones(L - 1), mn]), ker, mode="valid")
    sm = np.minimum(sm, mn)
    # release: hop-decimated recursive smoother that may only rise slowly
    d = sm[::hop]
    cr = np.exp(-hop / (rel * SR))
    out = np.empty_like(d)
    g = 1.0
    for i, v in enumerate(d):
        g = v if v < g else cr * g + (1 - cr) * v
        out[i] = g
    full = np.interp(np.arange(n), np.arange(len(out)) * hop, out)
    return np.minimum(full, mn)


# K-weighting (ITU-R BS.1770-4) at 48 kHz
_K1 = (np.array([1.53512485958697, -2.69169618940638, 1.19839281085285]),
       np.array([1.0, -1.69065929318241, 0.73248077421585]))
_K2 = (np.array([1.0, -2.0, 1.0]), np.array([1.0, -1.99004745483398, 0.99007225036621]))


def _kweight(x):
    y = signal.lfilter(*_K1, x, axis=-1)
    return signal.lfilter(*_K2, y, axis=-1)


def block_loudness(x, win=0.4, hop=0.1):
    """Gated-block powers per BS.1770 (400 ms, 75% overlap). Returns (block_lufs, mean-square z)."""
    y = _kweight(x)
    W, H = ns(win), ns(hop)
    c = np.concatenate([np.zeros((y.shape[0], 1)), np.cumsum(y ** 2, axis=-1)], axis=1)
    starts = np.arange(0, y.shape[-1] - W + 1, H)
    z = (c[:, starts + W] - c[:, starts]) / W
    zs = z.sum(axis=0)
    return -0.691 + 10 * np.log10(zs + 1e-20), zs


def lufs(x):
    """Integrated loudness, ITU-R BS.1770-4 (absolute gate -70 LUFS, relative gate -10 LU)."""
    l, zs = block_loudness(x)
    m = l > -70.0
    if not np.any(m):
        return -np.inf
    rel = -0.691 + 10 * np.log10(np.mean(zs[m])) - 10.0
    m &= l > rel
    return float(-0.691 + 10 * np.log10(np.mean(zs[m])))


def short_term(x, t0, t1):
    """Ungated K-weighted loudness of a window (LUFS)."""
    seg = _kweight(x[:, ns(t0):ns(t1)])
    return float(-0.691 + 10 * np.log10(np.sum(np.mean(seg ** 2, axis=-1)) + 1e-20))
