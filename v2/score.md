# Score and SFX: synthesis spec

Original score, synthesized in code (Python 3 + numpy, scipy allowed for filters/convolution). No
samples, no sample packs, no presets. One script, `v2/score/score.py --film {trailer60,cutdown30,teaser15}`,
writes `v2/score/out/<film>.wav` (final mix) and `v2/score/out/<film>-stems/*.wav`.
The teaser WAV is shared by all three teaser aspects.

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
| Randomness | `numpy.random.default_rng(20261028)` per stem (seed + stem index). Same seed → bit-identical output. |
| Source of event times | `v2/<film>/events.json` (one list of `{t, cue}` per film, the SFX tables of the film docs). The composition reads the same file for its typed-char times, so picture and sound cannot drift. |

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
"Band-limited saw/square" = PolyBLEP (or additive to 20 kHz).

| Instrument | Recipe |
|---|---|
| **PAD "air"** | Per note: 3 band-limited saws at −9, 0, +9 cents, each −10 dB. Mix → 2-pole SVF lowpass, cutoff per section (default 1400 Hz), Q 0.7, cutoff LFO sine 0.125 Hz ±200 Hz. Amp ADSR A 1.2 s, D 1.0 s, S 0.8, R 2.0 s (in groove sections the chord-change attack is 0.3 s, overlapping the release). Air layer: white noise → bandpass 7 kHz, Q 0.8, −32 dB under the pad, same envelope. Notes alternately panned ±0.3. Stereo chorus: two modulated delays 12 ms / 17 ms, depth 2 ms, rates 0.30 / 0.37 Hz, L/R, wet 0.4. Reverb send 0.35. |
| **BASS "pulse"** | 2 band-limited saws ±6 cents + square one octave down at 0.5. Saturate `tanh(1.8x)/tanh(1.8)`. 4-pole ladder lowpass, resonance 0.25, cutoff = base + env·amount; filter env A 2 ms, τ 140 ms, no sustain. Amp: A 3 ms, τ_D 120 ms to S 0.7, R 40 ms. Gate per pattern. HPF 30 Hz. Mono. Sidechain from the kick: gain × (1 − 0.5·e^(−t/0.09)) after each kick. |
| **KICK** | Sine, f(t) = 45 + 105·e^(−t/0.035) Hz; amp e^(−t/0.32); length 0.5 s. Click: 2 ms white noise HPF 2 kHz at −12 dB. Soft clip tanh(1.5x). |
| **SUB HIT** | Sine, f(t) = 38 + 42·e^(−t/0.08) Hz (80 → 38 Hz); A 2 ms, amp e^(−t/0.6); length 2.0 s. Layer one KICK at t0 and 80 ms of noise LPF 800 Hz at −18 dB. |
| **CLAP** | Three noise bursts at 0, 10, 20 ms (each 8 ms, τ 3 ms), then a tail τ 90 ms; bandpass 1.2 kHz Q 1.2; body sine 190 Hz τ 40 ms at −10 dB. Reverb send 0.25. |
| **HAT** | White noise → 2nd-order HPF 7 kHz. Closed τ 18 ms, open τ 120 ms. Pan +0.2. Velocity per step. |
| **PLUCK "signal"** | Band-limited saw + square (0.3, +5 cents). 2-pole LP, cutoff env 5000 → 700 Hz, τ 90 ms, Q 1.0. Amp A 2 ms, τ 220 ms, length 0.6 s. Ping-pong delay 0.375 s (dotted 8th), feedback 0.32, wet 0.22, delay path HPF 300 Hz / LPF 5 kHz. Reverb send 0.20. Notes alternately panned ±0.25. |
| **LEAD "spark" (motif)** | FM bell: carrier sine f, modulator sine 2f, index I(t) = 4·e^(−t/0.08) + 0.6. Amp A 1 ms, τ 0.9 s. Plus a sine at 2f, −14 dB. Reverb send 0.40 (BREATH motif: 0.10, "dry"). Filtered variant (RED): LPF 1.5 kHz. |
| **RISER** | White noise → bandpass, centre swept exponentially 300 → 8000 Hz over its length, Q 2. Plus sine sweep 220 → 1760 Hz at −20 dB. Gain curve −40 → −6 dB with a cubic ease-in. Stops dead at its end time (5 ms ramp). |
| **SNARE ROLL** | CLAP hits: 8ths on beats 1–2, 16ths on beat 3, 32nds on beat 4 until the air gap. Velocity ramps 0.3 → 1.0; its bandpass centre ramps 1.0 → 3.5 kHz. |
| **REVERSE SWELL** | Render the target chord on PAD (A 0, 1.0 s) plus noise burst through the reverb, take 1.0 s of the wet tail, reverse it, place it to end exactly on the target downbeat. |
| **GLITCH TICK** | 4 ms sine burst at a seeded frequency 3–6 kHz, bit-crushed to 6 bits with sample-and-hold ×4; −20 dB; seeded pan ±0.6. "Card tick": the same plus a 2 ms click and a 30 ms 2.4 kHz sine, used on feature-card downbeats. |
| **REVERB** | Convolution with a synthesized stereo IR: 3.5 s of independent L/R white noise, envelope 10^(−3t/2.8) (RT60 2.8 s), pre-delay 20 ms, progressive damping: filter the IR in 8 consecutive segments with one-pole LPF from 9 kHz down to 2 kHz. One shared reverb bus. |

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
| ASKS | Kick HALF (first half of section) → FOUR (second half); BASS PULSE base 260 Hz, env +1000; Hats OFF8; Clap in the second half; Pluck ARP; LEAD motif at start. |
| RED | Kick out, clap out. BASS PEDAL on Bb1, ladder cutoff 150 Hz with an LFO at 4 Hz (8ths) ±120 Hz; PAD cutoff 800 Hz; Hats 16 at vel ×0.3; 6 GLITCH TICKs per bar on seeded 32nd positions; LEAD motif (filtered) at start. |
| RISE | Chord A7sus4 for beats 1–2, A7 for beats 3–4; BASS PULSE on A1; SNARE ROLL; RISER over the bar; **air gap** on the last 16th: master gain to 0 with 5 ms ramps (tails are cut on purpose). |
| DROP | SUB HIT at start; Kick FOUR; BASS PULSE base 400 Hz, env +1600; Clap; Hats 16; Pluck ARP full; PAD 2200 Hz; LEAD motif at start (and per film table). |
| BREATH | All drums out. PAD 1400 Hz; BASS PEDAL; LEAD motif dry on the cues in the film table; a 0.5 s RISER into the next downbeat. |
| FEATURES | Kick GROOVE-B; BASS OFFBEAT base 300 Hz; Clap; Hats OFF8 + 16th ghosts at vel 0.25; Pluck ARP; Card tick on every downbeat. Last bar: SNARE ROLL on beats 3–4 + 1-bar RISER, air gap on the last 16th. |
| LOCKUP | Spark-sting full at start (with its own sub hit); Kick ONE; BASS PEDAL; PAD 2200 Hz; Pluck SPARSE. |
| INSTALL | PAD 1400 Hz; BASS PEDAL; Pluck ARP vel ×0.4 with the pluck's cutoff env start lowered 5000 → 2500 Hz across the section; Hats OFF8 in the first bar only at vel ×0.5. |
| END | Final chord Dadd9 at start: PAD (A 0.05 s, R 3.0 s), PLUCK strum (5 notes, 30 ms apart, upward), SUB HIT at −6 dB, spark-micro. Nothing else. Master fade (§7). |

## 5. Arrangements (bar → timecode maps)

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
| 15 | 28.0 | BREATH | Csus2 | spark-sting short 28.0 |
| 16 | 30.0 | BREATH | Bbmaj9 | motif D5 30.0, F5 30.5, A5 31.0, C6 31.5 (dry); 0.5 s riser 31.5–32.0 |
| 17–24 | 32.0–48.0 | FEATURES | Dm9 Bbmaj9 Fmaj9 Csus2 ×2 | card tick at 32, 34, … 46; bar 24 fill + riser, gap 47.875–48.0 |
| 25 | 48.0 | LOCKUP | Dm9 | **spark-sting full** 48.0 (pre-suck 47.5–48.0 sits inside the gap: let the pre-suck bypass the master gap) |
| 26 | 50.0 | LOCKUP | Bbmaj9 | |
| 27 | 52.0 | INSTALL | Fmaj9 | key-tick (soft, −6 dB) on typed chars 52.0–53.4 |
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
| 8 | 14.0 | BREATH | Csus2 | spark-sting short 14.0; riser 15.5–16.0 |
| 9 | 16.0 | FEATURES | Dm9 | card tick |
| 10 | 18.0 | FEATURES | Bbmaj9 | card tick |
| 11 | 20.0 | FEATURES (last bar: fill) | Csus2 | card tick; fill; gap 21.875–22.0 |
| 12 | 22.0 | LOCKUP | Dm9 | **spark-sting full** 22.0 |
| 13 | 24.0 | LOCKUP | Bbmaj9 | |
| 14 | 26.0 | END | Dadd9 | final chord; spark-micro; key-tick (soft) 26.0–27.2 |
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
| 6 | 11.0 | LOCKUP without its sting | Fmaj9 (beats 1–2) → Csus2 (3–4) | key-tick (soft) 12.0–12.9 |
| 7 | 13.0 | END | Dadd9 | final chord; spark-micro; fade 13.5 → 14.95; zeros 14.95–15.0 |

## 6. SFX (stem `sfx`, except stings → `fx`)

| Cue | Recipe | Peak (dBFS, on its stem) |
|---|---|---|
| `key-tick` | 6 ms noise burst, bandpass at a seeded 3.0–4.5 kHz, Q 1.5, τ 2 ms; plus a 2 ms click. Seeded level ±3 dB, pan ±0.15. One per typed character, at the character's on-screen frame. | −26 |
| `key-enter` | 14 ms noise, bandpass 1.8 kHz, + sine thump 120 Hz τ 30 ms. | −18 |
| `key-press` (keycap) | As key-enter, bandpass 2.4 kHz. | −16 |
| `blip-eye` | Two sine pings A6 (1760 Hz) then D7 (2349.3 Hz), 35 ms each, 20 ms apart, τ 60 ms. | −20 |
| `blip-card` | Square E5 (659.26 Hz) 50 ms then A5 (880 Hz) 70 ms, LPF 3 kHz, τ 80 ms. | −18 |
| `spark-micro` | FM ping at D7: carrier 2349.3 Hz, ratio 1.5, index 2 → 0 (τ 30 ms), amp τ 0.25 s; plus the 4 diamond grains (below) at −12 dB. | −16 |
| `spark-sting` full | Pre-suck: the sting's reverb tail reversed, 0.5 s, ending at t0, rising to −12 dB. At t0: SUB HIT + FM bells D6 (1174.66) and A6 (1760), ratio 2, index 5 (τ 0.06 s) → 0.6, amp τ 1.6 s; **four diamond grains**: sine 2349.3 Hz, 40 ms each (τ 15 ms) at t0 + 0, 25, 50, 75 ms, panned −0.6, +0.6, −0.3, +0.3 (the four points of the diamond); noise shimmer HPF 8 kHz τ 0.4 s at −24 dB. Reverb send 0.5. | −8 |
| `spark-sting` short | No pre-suck, no sub hit; bells τ 0.9 s. | −12 |
| `hit-buzz` (test fail) | Squares at 55.00 and 58.27 Hz together (A1 + Bb1), 180 ms, LPF 900 Hz, crushed to 5 bits, τ 0.12 s, + KICK at −6 dB. | −14 |
| `chime-landed` | FM bells D6, A6, D7, E7 (1174.66, 1760, 2349.3, 2637.0 Hz) at t0 + 0, 40, 80, 120 ms; ratio 3.5, index 1.5 (τ 0.1 s); amp τ 1.4 s; reverb 0.4. Neutral (no third), so it sits on any chord in §2. | −14 |
| `whoosh-in` | Noise → bandpass swept 400 → 3500 Hz over 0.4 s, gain rising (power 2), stops at the landing frame with a 20 ms ramp; pan −0.5 → +0.5. | −20 |
| `whoosh-out` | `whoosh-in` reversed in time and sweep. | −22 |
| `glitch-tick` / card tick | §3. | −20 |

## 7. Stems, mix bus, loudness, ending

Stems (each the full film length, 48 kHz, 32-bit float, stereo): `bass`, `drums` (kick, clap, hats,
rolls, sub hits that are not stings), `pluck` (pluck + lead motif), `pad`, `fx` (risers, swells,
stings, glitch), `sfx` (keys, blips, chime, whooshes, hit-buzz). The mix is the sum of the stems.

Nominal stem peaks before the bus (guide): kick −6, bass −10, pad −16, pluck −14, lead −12 dBFS;
SFX as in §6. The keys and blips must be audible but under the music: they are texture, not UI noise.

Master bus, in order:
1. HPF 25 Hz (2nd order).
2. Glue compressor: ratio 2:1, threshold −18 dBFS, attack 10 ms, release 150 ms, RMS detector;
   at most ~3 dB gain reduction.
3. Air gaps: master gain 0 over the gap windows in §5 (5 ms ramps). The spark-sting pre-suck bypasses
   this (it is summed after this step).
4. Loudness: measure integrated loudness (ITU-R BS.1770-4, e.g. `pyloudnorm`), gain to **−14.0 LUFS**.
5. True-peak limiter: 5 ms look-ahead, ceiling **−1.0 dBTP** measured on a 4x-oversampled signal.
   Re-measure; repeat 4–5 until I = −14.0 ± 0.5 LUFS and TP ≤ −1.0 dBTP.
6. End: raised-cosine fade to −∞ over the film's fade window (§5), then exact zeros to the last sample.
   The file length equals the film length to the sample. No tail past the last frame.

Check: `ffmpeg -i out/trailer60.wav -af ebur128=peak=true -f null -` → `I: -14.0 LUFS`, `Peak ≤ -1.0 dBFS`
(true peak), and `ffprobe` duration 60.000000. Same for 30 s and 15 s.

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
