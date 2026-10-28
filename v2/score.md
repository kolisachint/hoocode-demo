# Score and SFX: synthesis spec

Original score, synthesized in code (Python 3 + numpy, scipy allowed for filters/convolution). No
samples, no sample packs, no presets. Engine `v2/music/synth.py`; renderer
`python3 v2/music/score.py --film {trailer60,cutdown30,teaser15} [--events v2/<film>/events.json] [--stems]`
writes `out/v2/audio/<film>.wav` (final mix) plus the stems `out/v2/audio/<film>-music.wav` and
`<film>-sfx.wav`; `--stems` adds `out/v2/audio/<film>-stems/{bass,drums,pluck,pad,fx,sfx}.wav`.
How to render, the cue vocabulary and the bar→timecode maps: `v2/music/README.md`.
The teaser WAV is shared by all three teaser aspects.

**Music vs SFX.** The music (everything in §2–§5) sits on the fixed 120 BPM bar grid and does not
depend on footage timings. Everything tied to a picture event (keys, blips, sparks, stings, chime,
whooshes, hit-buzz, card ticks) is an SFX cue triggered from `v2/<film>/events.json` (§6), so the
footage edit can move without touching the music.

Mood: premium dev-tool launch. Minimal, confident, electronic. Pulsing analog-style bass, clean plucks,
an airy pad, sub hits on the big moments, glitch ticks as "signal". Dark (D minor) for the work,
resolving to D major on the end card ("landed").

## 1. Global

| Item | Value |
|---|---|
| Tempo | 120 BPM, 4/4. Beat = 0.5 s = 24 000 samples = 15 frames. Bar = 2.0 s = 96 000 samples. 16th = 6 000 samples. |
| Sample rate / format | 48 000 Hz. Work in float64; write 24-bit PCM stereo WAV (stems 32-bit float). |
| Length | Exactly film length: 60.000 s = 2 880 000 samples; 30.000 s = 1 440 000; 15.000 s = 720 000. |
| Key | D minor (D Aeolian), final chord D major add9. Tuning A4 = 440 Hz, f = 440·2^((m−69)/12). |
| Randomness | `numpy.random.default_rng(20261028 + i)` per music stem (bass 0, drums 1, pluck 2, pad 3, fx 4); `default_rng([20261028 + 5, k])` per SFX event k (sorted order); reverb IR `default_rng(20261028 + 99)`; RED glitch positions `default_rng([20261028, 4, bar])`. Same inputs → byte-identical files (stems are quantised to the 24-bit grid; float WAVs carry no PEAK/timestamp chunk). |
| Source of event times | `v2/<film>/events.json` (§6.1): the SFX trigger list, from the film docs' cue tables now (`"_placeholder": true`), from `v2/recording/cues.json` once the recording exists. The music does not read it. |

## 2. Harmony

Chord table (MIDI notes). Pad = sustained voicing; bass = root for the bass synth; pluck = the 5 tones
the arpeggio walks (index 0–4).

| Name | Pad | Bass | Pluck tones |
|---|---|---|---|
| Dm9 | 50 53 57 60 64 | 38 (D2, 73.42 Hz) | 62 65 69 72 76 |
| Bbmaj9 | 46 50 53 57 60 | 34 (Bb1, 58.27) | 58 62 65 69 72 |
| Fmaj9 | 53 57 60 64 67 | 41 (F2, 87.31) | 65 69 72 76 79 |
| Csus2 | 48 50 55 60 62 | 36 (C2, 65.41) | 60 62 67 72 74 |
| Gm7/Bb | 46 50 53 55 62 | 34 (Bb1) | 58 62 65 67 74 |
| A7sus4 | 45 50 52 55 64 | 33 (A1, 55.00) | 57 62 64 67 76 |
| A7 | 45 49 52 55 64 | 33 | 57 61 64 67 76 |
| Dadd9 (final) | 50 57 62 64 66 69 | 38 + 26 (D1 sub) | strum 62 66 69 74 76 |

Spark motif (lead, one note per verb): plans D5 (74), asks F5 (77), tests A5 (81), lands C6 (84),
logo/end D6 (86). The rising minor-7th arpeggio resolving up to the octave is the film's signature.

## 3. Instruments

All envelopes: A = linear attack, D/R = exponential with the given time constant τ unless stated.
"Band-limited saw/square" = PolyBLEP. "SVF" = a time-varying RBJ biquad (the same 2-pole response),
coefficients updated every 32 samples; the "ladder" = two cascaded time-varying biquads (Q 0.54 and
0.707 + 1.6·resonance). FM sounds are rendered at 4x and decimated (no fold-over). Every one-shot
starts and ends at exact zero (raised-cosine edge fades).

| Instrument | Recipe |
|---|---|
| **PAD "air"** | Per note: 3 band-limited saws at −9, 0, +9 cents, each −10 dB. Notes common to two chords are held through the change (per-pitch lanes), so only moving voices re-attack. Mix → 2-pole SVF lowpass, cutoff per section (default 1400 Hz, glided between bars), Q 0.7, cutoff LFO sine 0.125 Hz ±200 Hz; then HPF 150 Hz (Q 0.6) and −3 dB bell at 330 Hz (Q 0.8) to keep the bass and low-mids clear. Amp ADSR A 1.2 s (INTRO) / 0.5 s (OPEN) / 0.3 s (groove sections) / 0.8 s (others) / 0.05 s (END), D 1.0 s, S 0.8; release τ 0.45 s in groove sections, 1.2 s elsewhere, 3.0 s on the END chord. Air layer: white noise → bandpass 7 kHz, Q 0.8, −32 dB under the pad, following the summed note envelope. Notes panned ±0.3 by pitch parity. Stereo chorus: two modulated delays 12 ms / 17 ms, depth 2 ms, rates 0.30 / 0.37 Hz, L/R, wet 0.4. Sidechain from kicks and sub hits, depth 0.2, τ 0.15 s. Reverb send 0.35. |
| **BASS "pulse"** | 2 band-limited saws ±6 cents + square one octave down at 0.5. Saturate `tanh(1.8x)/tanh(1.8)`. 4-pole ladder lowpass, resonance 0.25, cutoff = base + env·amount; filter env A 2 ms, τ 140 ms, no sustain. Amp: A 3 ms, τ_D 120 ms to S 0.7, R 40 ms. Gate per pattern. HPF 30 Hz. Mono. Sidechain from kicks and sub hits: gain × (1 − 0.5·e^(−t/0.09)) after each, entered over a 4 ms raised-cosine (no click). PEDAL defaults: base 220 Hz, env +250 Hz (TYPE/OPEN: 150 / +120 at −6 dB; BREATH 240 / +200; LOCKUP 260 / +300; RED 150 Hz, no env, LFO 4 Hz ±120 Hz phase-locked to the bar). |
| **KICK** | Sine, f(t) = 45 + 105·e^(−t/0.035) Hz; amp e^(−t/0.32); length 0.5 s (40 ms fade-out). Click: 2 ms white noise, HPF 2 kHz + LPF 9 kHz, τ 0.7 ms, at −16 dB. Soft clip tanh(1.5x). |
| **SUB HIT** | Sine, f(t) = 38 + 42·e^(−t/0.08) Hz (80 → 38 Hz); A 2 ms, amp e^(−t/0.6); length 2.0 s. Layer one KICK at t0 and 80 ms of noise LPF 800 Hz at −18 dB. |
| **CLAP** | Three noise bursts at 0, 10, 20 ms (each 8 ms, τ 3 ms), then a tail τ 90 ms; bandpass 1.2 kHz Q 1.2; body sine 190 Hz τ 40 ms at −10 dB. Reverb send 0.25. |
| **HAT** | White noise → 2nd-order HPF 7 kHz. Closed τ 18 ms, open τ 120 ms. Pan +0.2. Velocity per step. |
| **PLUCK "signal"** | Band-limited saw + square (0.3, +5 cents). 2-pole LP, cutoff env 5000 → 700 Hz, τ 90 ms, Q 1.0. Amp A 2 ms, τ 220 ms, length 1.0 s (30 ms fade-out, so the tail is at −39 dB when it ends). Ping-pong delay 0.375 s (dotted 8th), feedback 0.32, wet 0.22, delay path HPF 300 Hz / LPF 5 kHz (filtered again on every repeat). Reverb send 0.20. Notes alternately panned ±0.25. END strum: same voice, τ 0.9 s, length 3.5 s, cutoff start 4200 Hz, panned −0.3 → +0.3 across the 5 notes. |
| **LEAD "spark" (motif)** | FM bell: carrier sine f, modulator sine 2f, index I(t) = 4·e^(−t/0.08) + 0.6. Amp A 1 ms, τ 0.9 s, length 3.5 s. Plus a sine at 2f, −14 dB. Ping-pong delay wet 0.15, starting on alternate sides for successive motif notes (a delay that always starts left pulls the image left). Reverb send 0.30 (BREATH motif: 0.10 and no delay, "dry"). Filtered variant (RED): LPF 1.5 kHz. |
| **RISER** | White noise → bandpass, centre swept exponentially 300 → 8000 Hz over its length, Q 2. Plus sine sweep 220 → 1760 Hz at −20 dB. Gain curve −40 → −6 dB with a cubic ease-in. Stops dead at its end time (5 ms ramp). |
| **SNARE ROLL** | CLAP hits: 8ths on beats 1–2, 16ths on beat 3, 32nds on beat 4 until the air gap. Velocity ramps 0.3 → 1.0; its bandpass centre ramps 1.0 → 3.5 kHz. |
| **REVERSE SWELL** | Render the target chord (3 saws per note, LPF 2.4 kHz, 1.0 s) plus a 50 ms noise burst through the reverb, take the 1.0 s of wet tail after the chord ends, reverse it, shape with √ramp, place it to end exactly on the target downbeat. Peak −9 dBFS (fx stem). |
| **GLITCH TICK** | 4 ms sine burst at a seeded frequency 3–6 kHz, bit-crushed to 6 bits with sample-and-hold ×4; −20 dB; seeded pan ±0.6. "Card tick": the same plus a 2 ms click and a 30 ms 2.4 kHz sine, centred, used on feature-card downbeats (an SFX cue, §6). |
| **REVERB** | Convolution with a synthesized stereo IR, 3.4 s + 20 ms pre-delay. Diffuse part: white noise split into 8 bands (40 Hz–18 kHz), each with its own decay, RT60 2.6 s at 200 Hz falling log-linearly to 0.8 s at 12 kHz (progressive damping), pink-weighted with −1.5 dB/oct above 2 kHz, 60 ms build-up. 24 early reflections (5–80 ms, 1.5 ms smeared bursts, LPF 6 kHz) carry about 12% of the energy. The right channel is the left through 5 Schroeder all-passes (4.7–23.1 ms, g 0.6): identical magnitude response on both sides (tonal sources stay centred), different phase (L/R correlation ≈ −0.15, wide). Return: per-channel slow delay modulation (4 ± 2.5 ms at 0.47 / 0.61 Hz, about ±8 cents, a modulated hall, so a sustained tone's tail cannot lock into a one-sided dry/wet interference), HPF 220 Hz, LPF 9.5 kHz. The send is mono-summed. Reverb is applied per stem with the same IR (linear, so equal to one shared bus) so each stem carries its own wet signal. |

### Patterns (16 steps per bar, step 0 = downbeat)

| Pattern | Steps / rule |
|---|---|
| Kick HALF | 0, 8 |
| Kick FOUR | 0, 4, 8, 12 |
| Kick GROOVE-B | 0, 8, 11 |
| Kick ONE | 0 |
| Clap | 4, 12 |
| Hats OFF8 | 2, 6, 10, 14 (closed, vel 0.7) |
| Hats 16 | all steps, vel 0.8 on even, 0.4 on odd; open hat on 6 and 14 |
| Bass PULSE | every 8th (steps 0,2,…,14), gate 70% (0.175 s), last 8th of each bar +12 st, accent (vel 1.0) on 0 and 8, else 0.75 |
| Bass OFFBEAT | steps 2, 6, 10, 14, gate 60% |
| Bass PEDAL | one note per bar, gate 95% |
| Pluck ARP | 8ths walking tone indices 0,2,4,2,3,2,4,1; velocities 1.0,0.6,0.8,0.6,0.9,0.6,0.8,0.6 |
| Pluck SPARSE | quarters walking 4,2,3,1 at vel 0.6 |

## 4. Sections

Each section = bars of chords + which parts play. Levels are relative to the part's nominal level (§7).

| Section | Parts |
|---|---|
| INTRO | PAD only, cutoff ramps 500 → 1100 Hz over the bar, fades in from −∞ over 1.5 s. |
| TYPE | PAD (1100 Hz); BASS PEDAL at −6 dB, cutoff 150 Hz; RISER over the bar, ending on the next downbeat. |
| OPEN (cutdown) | INTRO + TYPE in one bar: PAD fades in over 0.5 s; RISER over beats 3–4. |
| PLANS | SUB HIT at start; Kick HALF; BASS PULSE base 220 Hz, env +900 Hz; Pluck ARP vel ×0.6; PAD 1400 Hz; LEAD motif note at start. |
| ASKS | Kick HALF (first half of section) → FOUR (second half); BASS PULSE base 260 Hz, env +1000; Hats OFF8; Clap in the second half (half/four decided per beat across the run, so a 1-bar ASKS is HALF on beats 1–2, FOUR on 3–4; teaser bar 2 is FOUR + clap throughout); Pluck ARP vel ×0.85; PAD 1400 → 1800 Hz across the run; LEAD motif at start. |
| RED | Kick out, clap out. BASS PEDAL on Bb1, ladder cutoff 150 Hz with an LFO at 4 Hz (8ths) ±120 Hz; PAD cutoff 800 Hz; Hats 16 at vel ×0.3; 6 GLITCH TICKs per bar on seeded 32nd positions; LEAD motif (filtered) at start. |
| RISE | Chord A7sus4 for beats 1–2, A7 for beats 3–4; BASS PULSE on A1 (base 260 Hz, env +1100, stops before the gap); PAD cutoff 1500 → 2600 Hz; SNARE ROLL; RISER over the bar, stopping dead at the gap; crescendo by mix automation (§4.1); **air gap** on the last 16th: master gain to 0 with 5 ms ramps (tails are cut on purpose). |
| DROP | SUB HIT at start; Kick FOUR; BASS PULSE base 400 Hz, env +1600; Clap; Hats 16; Pluck ARP full plus the same arp an octave up at vel ×0.4 (the "lift"); PAD 2200 Hz; LEAD motif per film table. |
| BREATH | All drums out. PAD 1400 Hz; BASS PEDAL; LEAD motif dry on the cues in the film table; a 0.5 s RISER (top −4.4 dB) into the downbeat after the last BREATH bar. |
| FEATURES | Kick GROOVE-B (step 11 at vel 0.8); BASS OFFBEAT base 300 Hz, env +900; Clap; Hats OFF8 + 16th ghosts at vel 0.25; Pluck ARP vel ×0.9; PAD 1700 Hz. Second half of an 8-bar run: PAD 2000 Hz, hats ×1.1, pluck ×1.0. Card ticks come from the events (§6). Last bar: hats on beats 1–2 only, SNARE ROLL on beats 3–4 + 1-bar RISER, air gap on the last 16th. |
| LOCKUP | Spark-sting full at start (SFX cue `spark-sting`, with its own sub hit); Kick ONE; BASS PEDAL; PAD 2200 Hz; Pluck SPARSE. |
| INSTALL | PAD 1400 Hz; BASS PEDAL; Pluck ARP vel ×0.4 with the pluck's cutoff env start lowered 5000 → 2500 Hz across the section; Hats OFF8 in the first bar only at vel ×0.5. |
| END | Final chord Dadd9 at start: PAD (A 0.05 s, retriggered, cutoff 1800 → 1500 Hz), PLUCK strum (5 notes, 30 ms apart, upward), SUB HIT at −6 dB, BASS D2 (gate 3.6 s, base 260 Hz) + D1 sine sub (τ 1.5 s); `spark-micro` is an SFX cue. Nothing else. Master fade (§7). |

### 4.1 Section mix automation

Track levels (§7) are offset per section, in dB, per group (drums = kick, clap, hats; sub hits,
lead, strum and fx are not automated). A pair ramps linearly across the section's run of bars.
Steps fall on downbeats with 20 ms ramps. This is what shapes the dynamics: PLANS/ASKS build, RED
thins out, RISE swells into the gap, DROP is the loudest moment before the logo, LOCKUP makes room
for the spark-sting, INSTALL/END settle.

| Section | drums | bass | pluck | pad |
|---|---|---|---|---|
| INTRO / OPEN / TYPE | 0 | 0 | 0 | 0 |
| PLANS | −6 | −5.5 | −3 | −2 |
| ASKS | −5.5 → −3 | −5 → −3 | −2 | −3 |
| RED | −1 | −1 | 0 | −1.5 |
| RISE | −7 → 0 | −6 → 0 | 0 | −5 → 0 |
| DROP | +0.5 | +2.5 | +3 | −1 |
| BREATH | 0 | −3 | 0 | −1 |
| FEATURES | −2.5 | −2.5 | −1 | −3 |
| LOCKUP | −4 | −4 | −3 | −3.5 |
| INSTALL | −4 | −4 | 0 | −1 |
| END | 0 | −3 | 0 | −1.5 |

Measured result (trailer, ungated loudness per bar after mastering): INTRO −20, TYPE −16, PLANS
−14/−16, ASKS −13…−15, RED −14/−15, RISE −16 (rising), **DROP −12/−12/−11**, BREATH −14,
FEATURES −14…−15, **LOCKUP (sting) −12**, INSTALL −15/−16, END −13 then the fade.

## 5. Arrangements (bar → timecode maps)

The "Hit points / cues" column mixes music hits (sub hits, motif notes, risers, rolls, gaps: on the
grid, in `score.py`) and SFX cues (`events.json`, §6). The placeholder `events.json` files carry the
SFX times listed here; the trailer also has `key-tick-soft` on the banner type-on (1.05–1.40) and
`card-tick` on every feature card (trailer 32–46, cutdown 16–20). Bar → timecode for the teaser is
offset by its 1.0 s pickup.

### 5.1 Trailer 60 s (30 bars, bar N at (N−1)·2.0 s)

| Bar | Time | Section | Chord | Hit points / cues |
|---|---|---|---|---|
| 1 | 0.0 | INTRO | Dm9 | blip-eye 1.0 |
| 2 | 2.0 | TYPE | Dm9 | key-tick ×48 2.05–3.55; key-enter 3.95; riser → 4.0 |
| 3 | 4.0 | PLANS | Dm9 | SUB HIT; motif D5 |
| 4 | 6.0 | PLANS | Bbmaj9 | whoosh-in 5.6–6.0 |
| 5 | 8.0 | ASKS | Fmaj9 | motif F5; whoosh-out 7.6–8.0 |
| 6 | 10.0 | ASKS | Csus2 | blip-card 10.0; key-press + spark-micro 11.5 |
| 7 | 12.0 | ASKS | Dm9 | blip-card 12.0; key-press + spark-micro 13.5; whoosh-out 13.6 |
| 8 | 14.0 | ASKS | Bbmaj9 | snare 16ths on beat 4 (15.5–16.0) |
| 9 | 16.0 | RED | Gm7/Bb | hit-buzz 16.0; motif A5 (filtered) |
| 10 | 18.0 | RED | Gm7/Bb | blip-card 19.0; key-press + spark-micro 19.5 |
| 11 | 20.0 | RISE | A7sus4 → A7 | gap 21.875–22.0 |
| 12 | 22.0 | DROP | Dm9 | **SUB HIT** (the main drop) |
| 13 | 24.0 | DROP | Bbmaj9 | |
| 14 | 26.0 | DROP | Fmaj9 | chime-landed; motif C6 |
| 15 | 28.0 | BREATH | Csus2 | `spark-sting-short` 28.0 |
| 16 | 30.0 | BREATH | Bbmaj9 | motif D5 30.0, F5 30.5, A5 31.0, C6 31.5 (dry); 0.5 s riser 31.5–32.0 |
| 17–24 | 32.0–48.0 | FEATURES | Dm9 Bbmaj9 Fmaj9 Csus2 ×2 | card tick at 32, 34, … 46; bar 24 fill + riser, gap 47.875–48.0 |
| 25 | 48.0 | LOCKUP | Dm9 | **spark-sting full** 48.0 (pre-suck 47.5–48.0 sits inside the gap: let the pre-suck bypass the master gap) |
| 26 | 50.0 | LOCKUP | Bbmaj9 | |
| 27 | 52.0 | INSTALL | Fmaj9 | `key-tick-soft` on typed chars 52.0–53.4 |
| 28 | 54.0 | INSTALL | Csus2 | |
| 29 | 56.0 | END | Dadd9 | final chord; spark-micro |
| 30 | 58.0 | END (held) | — | fade 58.5 → 59.95; zeros 59.95–60.0 |

### 5.2 Cutdown 30 s (15 bars) — its own arrangement, rendered from the same instruments

| Bar | Time | Section | Chord | Hit points / cues |
|---|---|---|---|---|
| 1 | 0.0 | OPEN | Dm9 | blip-eye 0.07; key-tick ×48 0.40–1.85; key-enter 1.95; riser 1.0–2.0 |
| 2 | 2.0 | PLANS | Dm9 | SUB HIT; motif D5 |
| 3 | 4.0 | PLANS | Bbmaj9 | whoosh-in 3.6–4.0 |
| 4 | 6.0 | ASKS | Fmaj9 | motif F5; blip-card 6.0; key-press + spark-micro 7.5 |
| 5 | 8.0 | RISE (ASKS hats/clap kept on beats 1–2) | A7sus4 → A7 | blip-card 8.0; key-press + spark-micro 9.25; riser 9.0–9.875; gap 9.875–10.0 |
| 6 | 10.0 | DROP | Dm9 | **SUB HIT**; motif A5 |
| 7 | 12.0 | DROP | Bbmaj9 | chime-landed 12.0; motif C6 |
| 8 | 14.0 | BREATH | Csus2 | `spark-sting-short` 14.0; riser 15.5–16.0 |
| 9 | 16.0 | FEATURES | Dm9 | card tick |
| 10 | 18.0 | FEATURES | Bbmaj9 | card tick |
| 11 | 20.0 | FEATURES (last bar: fill) | Csus2 | card tick; fill; gap 21.875–22.0 |
| 12 | 22.0 | LOCKUP | Dm9 | **spark-sting full** 22.0 |
| 13 | 24.0 | LOCKUP | Bbmaj9 | |
| 14 | 26.0 | END | Dadd9 | final chord; spark-micro; `key-tick-soft` 26.0–27.2 |
| 15 | 28.0 | END (held) | — | fade 28.5 → 29.95; zeros 29.95–30.0 |

### 5.3 Teaser 15 s (2-beat pickup + 7 bars, bar N at 1.0 + (N−1)·2.0 s)

| Bar | Time | Section | Chord | Hit points / cues |
|---|---|---|---|---|
| pickup | 0.0–1.0 | REVERSE SWELL (Dm9) | — | blip-eye 0.5 |
| 1 | 1.0 | PLANS | Dm9 | SUB HIT; motif D5 |
| 2 | 3.0 | ASKS (hats + clap from the start) | Bbmaj9 | motif F5; blip-card 3.0; key-press + spark-micro 4.5 |
| 3 | 5.0 | RISE | A7sus4 → A7 | motif A5 at 5.0; glitch tick at 6.0 (exit 0); snare roll 6.0–6.875; gap 6.875–7.0 |
| 4 | 7.0 | DROP | Dm9 | **SUB HIT**; chime-landed; motif C6; spark-sting pre-suck 8.5–9.0 |
| 5 | 9.0 | BREATH (no motif) | Bbmaj9 | **spark-sting full** 9.0 |
| 6 | 11.0 | LOCKUP without its sting | Fmaj9 (beats 1–2) → Csus2 (3–4) | `key-tick-soft` 12.0–12.9 |
| 7 | 13.0 | END | Dadd9 | final chord; spark-micro; fade 13.5 → 14.95; zeros 14.95–15.0 |

## 6. SFX (stem `sfx`): event cues

Every cue below is triggered by `v2/<film>/events.json`; nothing here is on the music grid. Each
one-shot is normalised to its peak (the "Peak" column, dBFS on the sfx stem before the bus; an
event's `gain_db` offsets it). Reverb sends per cue are in the last column (same IR as the music).

| Cue | Recipe | Peak | Send |
|---|---|---|---|
| `key-tick` | 6 ms noise burst, bandpass at a seeded 3.0–4.5 kHz, Q 1.5, τ 2 ms; plus a 2 ms click (noise HPF 4 kHz + LPF 9 kHz, −10 dB). Seeded level 0…−3 dB, pan ±0.15. One per typed character, at the character's on-screen frame. Ticks closer than 24 ms to the previous kept tick are skipped (fast type-on would otherwise buzz). | −24 | 0 |
| `key-tick-soft` | `key-tick` for the install line and banner type-on. | −31 | 0 |
| `key-enter` | 14 ms noise (τ 5 ms), bandpass 1.8 kHz, + sine thump 120 Hz (with a 10 ms pitch drop) τ 30 ms. | −18 | 0.05 |
| `key-press` (keycap) | As key-enter, bandpass 2.4 kHz. | −16 | 0.08 |
| `blip-eye` | Two sine pings A6 (1760 Hz) then D7 (2349.3 Hz) 55 ms later, each A 1 ms, τ 60 ms. | −20 | 0.2 |
| `blip-card` | Square E5 (659.26 Hz) 50 ms then A5 (880 Hz) τ 80 ms, LPF 3 kHz. | −18 | 0.15 |
| `spark-micro` | FM ping at D7: carrier 2349.3 Hz, ratio 1.5, index 2 → 0 (τ 30 ms), amp τ 0.25 s; plus the 4 diamond grains (below) at −12 dB. | −16 | 0.25 |
| `spark-sting` (full) | Pre-suck: the sting's own reverb tail reversed, 0.5 s, ending at t0, rising (power 2) to −12 dB re the sting; it bypasses the air gaps (§7). At t0: FM bells D6 (1174.66, pan −0.15) and A6 (1760, pan +0.15), ratio 2, index 5 (τ 0.06 s) → 0.6, amp τ 1.6 s; **four diamond grains** ×1.2: sine 2349.3 Hz, 40 ms each (τ 15 ms) at t0 + 0, 25, 50, 75 ms, panned −0.6, +0.6, −0.3, +0.3 (the four points of the diamond); noise shimmer HPF 8 kHz τ 0.4 s, RMS −18 dB re the bell peak. Plus a SUB HIT 2 dB under the bell peak. The Peak value applies to the bells (the sub layer is not counted). | −7 | 0.3 |
| `spark-sting-short` | No pre-suck, no sub hit; bells index 2.4 → 0.6, τ 0.9 s; grains ×0.4; shimmer −30 dB. Kept darker than the full sting so the logo sting stays the brightest moment. | −14 | 0.3 |
| `hit-buzz` (test fail) | Squares at 55.00 and 58.27 Hz together (A1 + Bb1), 180 ms, LPF 900 Hz, crushed to 5 bits, τ 0.12 s, LPF 5 kHz, + KICK at −6 dB. | −14 | 0.1 |
| `chime-landed` | FM bells D6, A6, D7, E7 (1174.66, 1760, 2349.3, 2637.0 Hz) at t0 + 0, 40, 80, 120 ms, panned −0.3, +0.3, −0.15, +0.15; ratio 3.5, index 1.5 (τ 0.1 s); amp τ 1.4 s. Neutral (no third), so it sits on any chord in §2. | −14 | 0.3 |
| `whoosh-in` | Noise → bandpass (Q 1.4) swept 400 → 3500 Hz over `dur` (default 0.4 s) from `t`, gain rising (power 2), stops at t + dur (the landing frame) with a 20 ms ramp; pan −0.5 → +0.5. | −20 | 0.1 |
| `whoosh-out` | `whoosh-in` reversed in time and sweep, from `t` (the start of the pull-back) over `dur`. | −22 | 0.1 |
| `glitch-tick` | GLITCH TICK (§3). | −20 | 0.2 |
| `card-tick` | Card tick (§3), on each feature card's downbeat. | −15 | 0.15 |

### 6.1 `events.json`

`v2/<film>/events.json` is either a bare list or an object `{"_placeholder": true, "events": [...]}`.
Each event: `{"t": <seconds from film start>, "cue": "<cue>"}`, optional `"dur"` (whooshes) and
`"gain_db"`. Cue names are case-insensitive; `_` and `-` are the same; aliases: `landed-chime` →
`chime-landed`, `card-blip` → `blip-card`, `eye-blip` → `blip-eye`, `spark-sting-full`/`sting` →
`spark-sting`, `enter` → `key-enter`, `confirm-y` and `always-a` → `key-press` + `spark-micro`.
Unknown cues are an error; events outside the film are skipped with a warning. The renderer prints
`PLACEHOLDER events.json` while the flag is set. Current files are placeholders built from the film
docs' cue tables (§5 and the shot lists); once `v2/recording/cues.json` exists, regenerate them from
the resolved footage times and drop the flag. Only SFX move; the music does not change.

## 7. Stems, mix bus, loudness, ending

Outputs (all exactly the film length, 48 kHz, stereo):

- `out/v2/audio/<film>.wav`: the mix, 24-bit PCM.
- `out/v2/audio/<film>-music.wav`: everything on the grid (bass, drums, pluck/lead, pad, fx), 32-bit float.
- `out/v2/audio/<film>-sfx.wav`: every event cue (keys, blips, sparks, stings incl. their sub hit and
  pre-suck, chime, whooshes, hit-buzz, card/glitch ticks), 32-bit float.
- With `--stems`: `out/v2/audio/<film>-stems/{bass,drums,pluck,pad,fx,sfx}.wav`, 32-bit float:
  `drums` = kick, clap, hats, rolls and grid sub hits; `pluck` = pluck, strum, lead motif; `fx` =
  risers, reverse swell, RED glitch ticks.

All bus stages are linear per stem (filters) or one shared gain curve (compressor, gaps, loudness,
limiter, fade), so the processed stems sum to the mix. All files are quantised to the 24-bit grid
and the mix is written as exactly `music + sfx` (bit-exact). Each stem carries its own reverb and
delay returns.

Track peaks before the bus (each track normalised over the whole film, then shaped by §4.1): kick
−8, sub hits −7, clap/rolls −13, hats −20, bass −8, pad −11, pluck −14, strum −15, lead −17.5
(RED −18.5, BREATH dry −15.5), risers −13, RED glitches −20, reverse swell −9 dBFS; SFX as in §6.
The keys and blips must be audible but under the music: they are texture, not UI noise.

Master bus, in order (applied to every stem):
1. HPF 25 Hz (2nd order); side channel high-passed at 120 Hz (mono low end); +2 dB high shelf at
   5 kHz (air).
2. Air gaps: gain 0 over the gap windows in §5 (5 ms raised-cosine ramps, ending on the downbeat).
   The spark-sting pre-suck is added after this step, so it plays through the gap.
3. Pre-gain to −16 LUFS, then glue compressor on the sum: ratio 2:1, threshold −18 dBFS, attack
   10 ms, release 150 ms, 30 ms RMS detector; gain reduction capped at 4 dB.
4. Loudness: integrated loudness per ITU-R BS.1770-4 (K-weighting, 400 ms blocks, 75% overlap,
   −70 LUFS absolute and −10 LU relative gates), implemented in `synth.py` (no pyloudnorm needed;
   pyloudnorm and ffmpeg agree within 0.07 LU). Gain to **−14.0 LUFS**.
5. True-peak limiter: required gain from the 4x-oversampled peak, min-filtered over a 5 ms
   look-ahead, attack = look-ahead, 80 ms release; ceiling **−1.5 dBTP** so the AAC-LC 320 kb/s
   encode stays under −1.0 dBTP (the codec adds 0.1–0.3 dB). Re-measure; repeat 4–5 until
   I = −14.0 ± 0.05 LUFS and TP ≤ −1.55 dBTP.
6. End: raised-cosine fade to −∞ over the film's fade window (§5), then exact zeros to the last
   sample (the last 50 ms are digital zero); a 3 ms fade-in at sample 0. The file length equals
   the film length to the sample. No tail past the last frame.

Check: `ffmpeg -i out/v2/audio/trailer60.wav -af ebur128=peak=true -f null -` → `I: -14.0 LUFS`,
`Peak: -1.6 dBFS` (true peak), and `ffprobe` duration 60.000000. Same for 30 s and 15 s.
`python3 v2/music/analyze.py <wav> [--offset 1] [--png out.png]` prints the per-bar envelope,
spectrum, stereo and click report.

Mux (per `direction.md` §7): AAC-LC 320 kb/s; after muxing, check the MP4's audio duration is within
one AAC frame (21 ms) of the video's.

## 8. Listening checks

- Every downbeat in the film tables lands on a picture cut: render a test video with a white flash
  on each bar and listen.
- The drop (trailer 22.0, cutdown 10.0, teaser 7.0) must be the loudest moment before the logo; the
  spark-sting full must be the brightest.
- On laptop speakers the bass still reads (the square sub-octave and saturation give harmonics above
  100 Hz); on headphones nothing below 30 Hz.
- Silence after the last fade: last 50 ms are digital zero.
