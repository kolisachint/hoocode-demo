# v2 launch films: score and SFX

Original music and sound effects for the three v2 films, synthesized entirely in code (numpy +
scipy; no samples, no downloaded audio). The spec and source of truth is [`../score.md`](../score.md);
this page is the how-to.

| File | What |
|---|---|
| `synth.py` | Engine: PolyBLEP saw/square, sine, 4x-oversampled FM, envelopes, RBJ biquads (static and time-varying, the "SVF"), 4-pole ladder-style lowpass, saturation, bit-crush, synthesized stereo hall IR + convolution reverb, ping-pong delay, chorus, sidechain duck curves, M/S width and mono-bass, bus compressor, look-ahead true-peak limiter, BS.1770-4 loudness and true peak. |
| `score.py` | Harmony, instruments, the three arrangements on the bar grid, the SFX cues, the master bus, file writing. |
| `analyze.py` | Checks a render: loudness, true peak, DC, per-bar peak/RMS/loudness/centroid/low-share/stereo, HF spike (click) report, optional spectrogram PNG (needs matplotlib). |

## Render

```bash
python3 v2/music/score.py --film trailer60    # also: cutdown30, teaser15
python3 v2/music/score.py --film teaser15 --events v2/teaser15/events.json --stems
```

`--events` defaults to `v2/<film>/events.json`, `--out` to `out/v2/audio`. Python 3 with numpy,
scipy and soundfile. Render time: about 50 s (trailer), 18 s (cutdown) and 10 s (teaser) on 4 cores.
The renderer prints the measured result:

```
trailer60: 2880000 samples (60.000 s), events 115 (PLACEHOLDER events.json)
  integrated -14.03 LUFS, true peak -1.60 dBTP, sample peak -1.61 dBFS, last 50 ms max 0.0e+00, DC 5.3e-06
```

Outputs, all exactly the film length at 48 kHz stereo:

| File | Content |
|---|---|
| `out/v2/audio/<film>.wav` | Final mix, 24-bit PCM. −14.0 LUFS integrated, ≤ −1.5 dBTP (4x oversampled), last 50 ms digital zero. |
| `out/v2/audio/<film>-music.wav` | Everything on the bar grid: bass, drums (kick, clap, hats, rolls, sub hits), pluck + strum + lead motif, pad, fx (risers, reverse swell, RED glitch ticks), each with its reverb/delay. 32-bit float. |
| `out/v2/audio/<film>-sfx.wav` | Everything triggered by `events.json`: keys, blips, spark-micro, spark-stings (with their sub hit and pre-suck), chime, whooshes, hit-buzz, glitch/card ticks, with their reverb. 32-bit float. |
| `out/v2/audio/<film>-stems/*.wav` | `--stems` only: `bass`, `drums`, `pluck`, `pad`, `fx`, `sfx` (32-bit float). |

The bus is linear per stem or one shared gain curve, so the stems carry the final processing:
`music + sfx` equals the mix sample for sample (all files sit on the 24-bit grid). Renders are
deterministic: the same code and events give byte-identical files.

Check a render (`analyze.py` also works on the stems):

```bash
ffmpeg -i out/v2/audio/trailer60.wav -af ebur128=peak=true -f null -    # I: -14.0 LUFS, Peak: -1.6 dBFS
python3 v2/music/analyze.py out/v2/audio/trailer60.wav --png /tmp/trailer60.png
python3 v2/music/analyze.py out/v2/audio/teaser15.wav --offset 1.0      # teaser bars start at 1.0
```

The AAC-LC 320 kb/s encode for the mux measures −14.0 LUFS and −1.5 dBTP (the WAV ceiling is
−1.5 dBTP so the codec's overshoot stays under −1.0).

## The pieces

One family: D minor (Dm9 · Bbmaj9 · Fmaj9 · Csus2), 120 BPM, the same instruments, and the **spark
motif**: one FM-bell note per verb, D5 (plans) → F5 (asks) → A5 (tests) → C6 (lands), resolving to
D6/A6 in the spark-sting on the logo and to D major add9 on the end card ("landed").

- **Trailer 60 s.** A pad breathes in under the owl; the typed task is a rain of soft key ticks over
  a riser. `plans.` lands with a sub hit and a half-time pulse; `asks.` builds to four-on-the-floor
  with hats and clap. The failing test drops the kick: a dark Bb pedal with a wobbling filter and
  glitch ticks, then an A7sus4 → A7 roll and riser into a hard air gap, and the **drop** on the
  passing run (the loudest moment before the logo), crowned by the chime and C6 on `● LANDED`.
  A drumless breath plays the four-note motif dry, then a lighter half-time groove carries the
  eight feature cards (card tick on each cut), fills into a second gap and the **full spark-sting**
  on the lockup (the brightest moment). The install card settles to a filtered arp; the end card
  resolves on D add9 and fades to digital silence.
- **Cutdown 30 s.** The same story compressed: owl and typing in one bar, plans, asks, a one-bar
  rise into the gap, a two-bar drop (A5 on `exit 0`, C6 on `LANDED`), breath, three feature bars
  with fill and gap, the full sting at 22.0, the resolve.
- **Teaser 15 s.** A reverse swell pulls into bar 1; one bar per verb (plans, asks, tests with the
  roll and gap, lands on the drop); the sting's pre-suck rises under the end of the drop into the
  spark at 9.0, then lockup and the D major end chord.

## SFX cue vocabulary

`events.json` is either a bare list or `{"_placeholder": true, "events": [...]}`. Each event is
`{"t": seconds, "cue": "<name>"}`, with optional `"dur"` (whooshes) and `"gain_db"`. Names are
case-insensitive and `_` = `-` (so `key_tick` works).

| Cue | Sound | Used for | Peak dBFS |
|---|---|---|---|
| `key-tick` | 6 ms band-passed noise tick + tiny click, seeded pitch/level/pan | each typed character of the task | −24 |
| `key-tick-soft` | same, quieter | banner and install-line type-on | −31 |
| `key-enter` | noise click + 120 Hz thump | Enter on the typed task | −18 |
| `key-press` | brighter keycap click + thump | `y` / `a` keycap answers | −16 |
| `blip-eye` | two sine pings A6 → D7 | owl eyes light | −20 |
| `blip-card` | square E5 → A5, low-passed | clearance card appears | −18 |
| `spark-micro` | FM ping at D7 + 4 diamond grains | the small spark on every `y`/`a`, end-card cursor | −16 |
| `spark-sting` | pre-suck (0.5 s before `t`), FM bells D6 + A6, diamond grains, shimmer, sub hit | the logo spark (full) | −7 (bells) |
| `spark-sting-short` | darker bells, no pre-suck, no sub | the breath-card spark | −14 |
| `hit-buzz` | crushed A1 + Bb1 squares + kick | `HIT exit 101` (test fail) | −14 |
| `chime-landed` | four FM bells D6 A6 D7 E7, staggered 40 ms | `● LANDED` | −14 |
| `whoosh-in` | band-pass sweep up, L → R, `t` = start, lands at `t + dur` (0.4 s) | camera push-in | −20 |
| `whoosh-out` | the reverse, `t` = start of the pull-back | camera pull-back | −22 |
| `glitch-tick` | 4 ms bit-crushed sine | teaser `exit 0` | −20 |
| `card-tick` | glitch tick + click + 2.4 kHz blip | each feature card's downbeat | −15 |

Aliases: `landed-chime`, `card-blip`, `eye-blip`, `spark-sting-full`, `sting`, `enter`, and the
composites `confirm-y` / `always-a` (= `key-press` + `spark-micro`). Key ticks closer than 24 ms to
the previous one are skipped, so a fast type-on (the install line at about 21 ms per character)
does not turn into a buzz.

**Placeholders.** `v2/{trailer60,cutdown30,teaser15}/events.json` hold the intended cue times from
the film docs and are marked `"_placeholder": true` (the renderer says so). When
`v2/recording/cues.json` exists and the edit is locked, rewrite each file's events from the resolved
picture times (one `key-tick` per typed character at its on-screen frame, etc.), drop the flag and
re-render. Only the SFX move; the music is on the fixed grid and does not change.

## Bar → timecode

120 BPM, bar = 2.0 s = 96 000 samples. Music hits only; the SFX times are in `events.json` and in
`score.md` §5. Generated from `FILMS` / `arrange()` in `score.py`.

### Trailer 60 s (`trailer60`)

| Bar | Time | Section | Chord | Music on the grid |
|---|---|---|---|---|
| 1 | 0.0 | INTRO | Dm9 | pad fades in over 1.5 s |
| 2 | 2.0 | TYPE | Dm9 | bass pedal; riser 2–4 |
| 3 | 4.0 | PLANS | Dm9 | sub hit; motif D5 4.0 |
| 4 | 6.0 | PLANS | Bbmaj9 | |
| 5 | 8.0 | ASKS | Fmaj9 | motif F5 8.0; hats in |
| 6 | 10.0 | ASKS | Csus2 | |
| 7 | 12.0 | ASKS | Dm9 | kick FOUR + clap (second half) |
| 8 | 14.0 | ASKS | Bbmaj9 | clap 16ths on beat 4 |
| 9 | 16.0 | RED | Gm7/Bb | motif A5 (filtered) 16.0; kick out |
| 10 | 18.0 | RED | Gm7/Bb | |
| 11 | 20.0 | RISE | A7sus4 → A7 | snare roll; riser 20–21.875; **gap 21.875–22.0** |
| 12 | 22.0 | DROP | Dm9 | **sub hit (the drop)** |
| 13 | 24.0 | DROP | Bbmaj9 | |
| 14 | 26.0 | DROP | Fmaj9 | motif C6 26.0 |
| 15 | 28.0 | BREATH | Csus2 | drums out |
| 16 | 30.0 | BREATH | Bbmaj9 | motif D5 F5 A5 C6 (dry) 30.0 / 30.5 / 31.0 / 31.5; riser 31.5–32 |
| 17–23 | 32.0–46.0 | FEATURES | Dm9 Bbmaj9 Fmaj9 Csus2 Dm9 Bbmaj9 Fmaj9 | half-time groove; brighter from bar 21 (40.0) |
| 24 | 46.0 | FEATURES | Csus2 | snare roll beats 3–4; riser 46–47.875; **gap 47.875–48.0** |
| 25 | 48.0 | LOCKUP | Dm9 | (spark-sting is an SFX cue) |
| 26 | 50.0 | LOCKUP | Bbmaj9 | |
| 27 | 52.0 | INSTALL | Fmaj9 | arp darkens across the section |
| 28 | 54.0 | INSTALL | Csus2 | |
| 29 | 56.0 | END | Dadd9 | final chord, strum, sub hit (−6 dB) |
| 30 | 58.0 | END | (held) | fade 58.5 → 59.95; digital zero to 60.0 |

### Cutdown 30 s (`cutdown30`)

| Bar | Time | Section | Chord | Music on the grid |
|---|---|---|---|---|
| 1 | 0.0 | OPEN | Dm9 | pad fades in over 0.5 s; bass pedal; riser 1–2 |
| 2 | 2.0 | PLANS | Dm9 | sub hit; motif D5 2.0 |
| 3 | 4.0 | PLANS | Bbmaj9 | |
| 4 | 6.0 | ASKS | Fmaj9 | motif F5 6.0 |
| 5 | 8.0 | RISE | A7sus4 → A7 | ASKS kick/clap/hats on beats 1–2; snare roll beats 3–4; riser 9–9.875; **gap 9.875–10.0** |
| 6 | 10.0 | DROP | Dm9 | **sub hit (the drop)**; motif A5 10.0 |
| 7 | 12.0 | DROP | Bbmaj9 | motif C6 12.0 |
| 8 | 14.0 | BREATH | Csus2 | riser 15.5–16 |
| 9 | 16.0 | FEATURES | Dm9 | |
| 10 | 18.0 | FEATURES | Bbmaj9 | |
| 11 | 20.0 | FEATURES | Csus2 | snare roll beats 3–4; riser 20–21.875; **gap 21.875–22.0** |
| 12 | 22.0 | LOCKUP | Dm9 | (spark-sting is an SFX cue) |
| 13 | 24.0 | LOCKUP | Bbmaj9 | |
| 14 | 26.0 | END | Dadd9 | final chord, strum, sub hit (−6 dB) |
| 15 | 28.0 | END | (held) | fade 28.5 → 29.95; digital zero to 30.0 |

### Teaser 15 s (`teaser15`, bar N at 1.0 + (N−1)·2.0 s)

| Bar | Time | Section | Chord | Music on the grid |
|---|---|---|---|---|
| pickup | 0.0 | REVERSE SWELL | Dm9 | swell ends exactly on 1.0 |
| 1 | 1.0 | PLANS | Dm9 | sub hit; motif D5 1.0 |
| 2 | 3.0 | ASKS | Bbmaj9 | motif F5 3.0; kick FOUR, hats, clap from the start |
| 3 | 5.0 | RISE | A7sus4 → A7 | motif A5 5.0; snare roll 6.0–6.875; riser 5–6.875; **gap 6.875–7.0** |
| 4 | 7.0 | DROP | Dm9 | **sub hit (the drop)**; motif C6 7.0 |
| 5 | 9.0 | BREATH | Bbmaj9 | (spark-sting 9.0 is an SFX cue); riser 10.5–11 |
| 6 | 11.0 | LOCKUP | Fmaj9 → Csus2 | |
| 7 | 13.0 | END | Dadd9 | final chord, strum, sub hit; fade 13.5 → 14.95; digital zero to 15.0 |

## Measured (current placeholder events)

| Film | Integrated | True peak | ffmpeg ebur128 | pyloudnorm | Loudest bar before the logo |
|---|---|---|---|---|---|
| trailer60 | −14.03 LUFS | −1.60 dBTP | −14.0 LUFS / −1.6 dBFS | −14.06 | DROP 26.0 (−11.3), logo 48.0 (−11.9) |
| cutdown30 | −14.04 LUFS | −1.60 dBTP | −14.0 LUFS / −1.6 dBFS | −14.08 | DROP 12.0 (−11.6), logo 22.0 (−12.5) |
| teaser15 | −14.01 LUFS | −1.60 dBTP | −14.0 LUFS / −1.6 dBFS | −14.05 | DROP 7.0 (−11.6), sting 9.0 (−12.9) |

Per-bar values are ungated K-weighted loudness. Also checked: no DC (|mean| < 4e-5), no clipping,
low end near-mono (side 26 dB under mid below 120 Hz), L/R correlation above 300 Hz median 0.6
(0.2–0.74 per 2 s window), and no off-grid HF spikes above −50 dBFS
apart from deliberate transients. The full spark-sting is the brightest second of each film; in
the cutdown it is close to the short sting at 14.0, which sits over a drumless bar.
