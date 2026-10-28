# Trailer, 60.0 s, 1920x1080, 30 fps

Read `direction.md` first. Grid: 120 BPM, bar = 2.0 s, bar N starts at (N-1) x 2.0 s. 30 bars.
Footage = `out/v2/hoocode-v2.mp4` (2880x1620, scaled so 1.0x fills 1920x1080). Cue names come from
`recording.md` §4; `Z(w, x0, CUE@p)` from `recording.md` §5. "Fit" speed = play the clip span so its
out-cue lands on the shot's end time (speed = clip span / shot length; clamp 0.8x–4x; if it would
exceed 4x, cut out the middle with a hard cut on a beat instead).

## 1. Structure

| Bars | Time | Act | Score section (`score.md`) |
|---|---|---|---|
| 1–2 | 0.0–4.0 | Cold open: owl, typed task | INTRO, TYPE |
| 3–4 | 4.0–8.0 | **plans.** | PLANS |
| 5–8 | 8.0–16.0 | **asks.** | ASKS |
| 9–11 | 16.0–22.0 | **tests.** red, fix, rise | RED, RISE |
| 12–14 | 22.0–28.0 | green, **lands.** | DROP |
| 15–16 | 28.0–32.0 | "Shell, Edit and Write ask first." | BREATH |
| 17–24 | 32.0–48.0 | Eight feature cards | FEATURES |
| 25–26 | 48.0–52.0 | HooCode lockup + tagline | LOCKUP |
| 27–30 | 52.0–60.0 | Install card, end | INSTALL, END |

## 2. Shot list

| # | Time | Visual | On-screen copy | Footage in → out (speed) | Camera / zoom | Out transition | Music / SFX |
|---|---|---|---|---|---|---|---|
| 1 | 0.0–2.0 | `#09090B`. Owl glyph (`tui/owl.txt`) centred, 3 rows at 120 px. Eyes `#27272A` at 0.0; eyes light `#00F0FF` at 1.0 (2-frame snap, glow 16 px). At 1.0 the banner text types to the right of the owl: `hoo│code` (0.0–0.4 s of type), then `coding agent · v0.2.20` below it (1.5). | `hoo│code` · `coding agent · v0.2.20` | none | static; whole group drifts scale 1.00→1.03 linear | hard cut 2.0 | Pad Dm9 from silence (fade 0→ -18 dB over 1.5 s). Eye light blip at 1.0 (SFX `blip-eye`). Ticks on banner chars. |
| 2 | 2.0–4.0 | Typed task, JetBrains Mono 500 52 px, left-aligned at x=160, y=540: `$ ` in `#71717A`, the rest `#FAFAFA`, `--json` in `#00F0FF`. Types 2.05–3.60 (32 ms/char), cursor `_` blinks on beats 3.5, 3.75 off/on. | `$ hoocode "Add a --json flag to the stats command"` | none | slow push 1.00→1.06 linear | **Enter**: hard cut at 4.0 | `key-tick` per char (48). `key-enter` at 3.95. Riser (1 bar, noise) into 4.0. |
| 3 | 4.0–6.0 | Footage wide, full-bleed. Verb plate right third: centre x=1500, y=540, 520x240, text `plans.` 168 px. Plate slams in at 4.0, cut out at 5.9. | **plans.** | `TUI` → `PLAN − 0.4` (fit, ≈1.5–2x) | 1.0x, drift to 1.04x | — (continuous into 4) | Downbeat 4.0: sub hit + kick enters. Motif note D5. |
| 4 | 6.0–8.0 | Punch-in on the task panel's 4 plan items. Focus brackets around the 4 rows at 6.0. | — | `PLAN − 0.4` → `PANEL + 1.6` (1.0x) | push 5.6→6.0 to `Z(0.56, 0.0, PANEL@0.45)`; drift to `Z(0.54, …)` | 7.6–8.0 pull back to 1.0x (lands 8.0) | `whoosh-in` 5.6–6.0. |
| 5 | 8.0–10.0 | Wide: read, the diff streaming. Verb plate `asks.` 8.0–9.9. | **asks.** | `READ − 0.3` → `CARD1` (fit, ≈2–3x) | 1.0x → 1.08x linear | — | Motif F5 at 8.0. Hats enter. |
| 6 | 10.0–12.0 | Clearance card 1, with the Edit diff above it. Focus brackets around `◎ CLEARANCE NEEDED` at 10.0. Keycap at 11.5, bottom-right (x=1560, y=880): `y` + `go, once`. Spark micro (small cyan diamond, 24 px, top-left of keycap) at 11.5. | keycap `y` `go, once` | `CARD1` → `Y1 + 0.1`. Hold on `CARD1` frames (the 2.5 s VHS sleep covers it); align so `Y1` (card gone) lands at 11.6 | push 9.6→10.0 to `Z(0.66, 0.0, CARD1@0.82)` | hard cut 12.0 | `blip-card` at 10.0. `key-press` + `spark-micro` 11.5. |
| 7 | 12.0–14.0 | Clearance card 2 (Shell, `$ cargo test --quiet`). Brackets at 12.0. Keycap at 13.5: `a` + `always cargo in this session`. | keycap `a` `always cargo in this session` | `CARD2 − 0.1` → `A2 + 0.1`, align `A2` at 13.6 | `Z(0.66, 0.0, CARD2@0.82)` held (cut in already zoomed) | at 13.6 pull back 0.4 s to 1.0x | `blip-card` 12.0. `key-press` + `spark-micro` 13.5. |
| 8 | 14.0–16.0 | Wide: cargo compiles and runs. | — | `A2` → `HIT − 0.05` (fit) | 1.0x; 15.6→16.0 push to shot 9's rect | — | Bar 8: fill on beat 4 (snare 16ths). |
| 9 | 16.0–18.0 | **Red.** Land on the right edge: ` HIT ` chip + `exit 101`. 16.5–17.6 pan left (`power3.inOut`) to the left edge to read `test result: FAILED`. Verb plate `tests.` lower-left (centre x=420, y=900) 16.0–17.9. | **tests.** | `HIT` → `FIXTEXT − 0.2` (1.0x, freeze last frame if short) | `Z(0.60, 0.40, HIT@0.30)` at 16.0 → `Z(0.60, 0.0, FAILED@0.45)` by 17.6 | hard cut 18.0 | `hit-buzz` at 16.0. Kick drops out, bass to Bb pedal (RED). Motif A5 at 16.0, filtered. |
| 10 | 18.0–20.0 | The fix: 18.0–19.0 punch on the one-line diff (`-` spaces / `+` compact). 19.0 cut to card 3; keycap `y` `go, once` at 19.5. | keycap `y` `go, once` | 18.0–19.0: `FIXTEXT` → `CARD3 − 0.1` (fit). 19.0–20.0: `CARD3` → `Y3 + 0.4`, `Y3` at 19.6 | 18.0: `Z(0.70, 0.0, FIXTEXT@0.35)`; 19.0: `Z(0.66, 0.0, CARD3@0.82)` | hard cut 20.0 | `blip-card` 19.0. `key-press` + `spark-micro` 19.5. |
| 11 | 20.0–22.0 | Wide: the re-run, no card (the point: `a` covered it). 21.6–22.0 push to shot 12's rect. | — | `Y3` → `EXIT0 − 0.03` (fit) | 1.0x → 1.05x; push 21.6→22.0 | air gap: picture holds 21.875–22.0 | RISE: A7sus4→A7, snare roll, noise riser; silence 21.875–22.0. |
| 12 | 22.0–24.0 | **Green.** Land on `exit 0` (right edge). Brackets around `exit 0` at 22.0. 22.6–23.6 pan left to `test result: ok. 2 passed`. | — | `EXIT0` → `DONE − 0.2` (1.0x; trim) | `Z(0.60, 0.40, EXIT0@0.30)` → `Z(0.60, 0.0, OK@0.45)` | — | **DROP** at 22.0: sub hit, full groove. |
| 13 | 24.0–26.0 | Wide: plan ticks to `4 items · 4 done`, summary streams. | — | `DONE − 0.2` → `LANDED − 0.03` (fit) | 1.0x; push 25.6→26.0 | — | |
| 14 | 26.0–28.0 | Punch on the landing line + ticked plan + comms frame `● LANDED`. Brackets around `● LANDED` at 26.0. Verb plate `lands.` right third 26.0–27.9. | **lands.** | `LANDED` → `END` (1.0x, freeze last frame) | `Z(0.62, 0.0, LANDED@0.30)`, drift to 0.60 | hard cut 28.0 | `chime-landed` 26.0. Motif C6. |
| 15 | 28.0–30.0 | Brand card, no footage. Centre: headline. 29.0: key legend below, JetBrains Mono 36, keys `#00F0FF`, labels `#A1A1AA`, separators `#71717A`. Symbol C (`symbol.svg`, 200 px wide) top-centre at y=260, nodes drawn, spark fires at 28.0 (small: diamond only, arcs stay hidden). | "Shell, Edit and Write ask first." / `y go, once · a always · n abort + say why · e edit first` | none | static | hard cut 30.0 | `spark-sting` (short variant) 28.0. BREATH: drums out. |
| 16 | 30.0–32.0 | Four verbs stacked left-aligned at x=480, Inter 800 120 px, one per beat: 30.0 `plans.`, 30.5 `asks.`, 31.0 `tests.`, 31.5 `lands.`. Each previous verb dims to `#71717A` when the next lands. | plans. asks. tests. lands. | none | static | hard cut 32.0 | Motif D5 F5 A5 C6 on the four beats (pluck, dry). Riser last beat. |
| 17–24 | 32.0–48.0 | Eight feature cards, 2.0 s each, see §3. | §3 | none | §3 | hard cut on each downbeat | FEATURES groove. `glitch-tick` on each card's downbeat. Bar 24: fill + air gap 47.875–48.0. |
| 25 | 48.0–50.0 | HooCode lockup (`hoocode.svg`) centred, 1100 px wide. Build: 47.5–47.9 `h` stem + arch draw; 47.6–48.0 node circles draw; **48.0 spark**; 48.05–48.35 signal arc draws; 48.3 divider fades in; 48.4–48.8 `code` fades up per glyph (4 x 0.1 s); cursor `_` solid at 48.8, then blinks on beats. | — | none | static, 1.00→1.02 drift | — | `spark-sting` (full) 48.0 + sub hit. LOCKUP. |
| 26 | 50.0–52.0 | Tagline fades/rises in under the lockup at 50.0, Inter 700 64 px `#FAFAFA`, centred, y=760. | "Nothing applied without your say-so." | none | static | 51.6–52.0 lockup moves up to y=260 and scales to 640 px wide (`power3.inOut`); tagline fades out 51.6 | |
| 27–28 | 52.0–56.0 | Install card: panel 1280x300 at y=420 centred (`#18181B`, border `#27272A`), JetBrains Mono 500 34 px, types 52.0–53.4 (`$ ` `#71717A`, command `#FAFAFA`). 54.0: line under the panel, mono 30 `#A1A1AA`. 55.0: platform line, mono 24 `#71717A`. | `$ curl -fsSL https://kolisachint.github.io/hoocode/install.sh \| sh` / `npm install -g hoocode  ·  pip install hoocode` / `macOS · Linux · x64 · arm64 · MIT · v0.2.20` | none | static | — | `key-tick` per char at 50% level. INSTALL. |
| 29–30 | 56.0–60.0 | Hold. 56.0: URL line at y=900, Inter 500 36 px `#A1A1AA`, `hoocode` in it `#FAFAFA`. Lockup cursor blinks on beats until 59.0, then solid. Last frame (59.967) = full end card, nothing moving. | `kolisachint.github.io/hoocode` | none | static | none (film ends on the card) | END: final chord D(add9) at 56.0, `spark-micro` on the cursor at 56.0; fade to digital silence by 59.95. |

## 3. Feature cards (bars 17–24)

Layout (all eight): `#09090B` field. Panel 1440x560, centred, `#18181B`, 1 px `#27272A`, radius 20 px,
glow `radial-gradient(circle at 30% 20%, rgba(0,240,255,0.15) 0%, transparent 50%)`. Inside, padding
96 px: label (JetBrains Mono 500 22 px caps, `#71717A`, tracking 0.12em) at top; headline Inter 700
80 px `#FAFAFA` below; detail JetBrains Mono 500 36 px `#A1A1AA`, tokens in `#00F0FF` where marked
`[...]`. Symbol C (`symbol.svg`, 140 px) top-right inside the panel; its diamond flashes (opacity
0.3 → 1 → 0.3, 0.3 s) on the downbeat.

Motion per card: downbeat hard cut to the new panel content; label on (no animation); headline rises
24 px → 0 with opacity 0 → 1, 0.45 s `expo.out`; detail types from beat 2 (+0.5 s) at 16 ms/char.
Cards 3 and 8 alternate: panel enters with a 0.3 s horizontal wipe (clip-path from left), to break the
rhythm once per half.

| Card | Time | Label | Headline | Detail |
|---|---|---|---|---|
| 1 | 32.0 | `01 / BINARY` | One static binary. | no Node · no Python · no runtime to install |
| 2 | 34.0 | `02 / PLATFORMS` | macOS and Linux. | [x64] · [arm64] · static musl builds on Linux |
| 3 | 36.0 | `03 / PROVIDERS` | Any model provider. | Anthropic · OpenAI · Google · OpenRouter<br>Groq · DeepSeek · xAI · Fireworks · [/login] |
| 4 | 38.0 | `04 / MODES` | Four modes. | [ask] · [plan] · [build] · [debug] |
| 5 | 40.0 | `05 / SUBAGENTS` | Subagents in the background. | same approval gate as the main agent |
| 6 | 42.0 | `06 / SESSIONS` | Sessions you can come back to. | [--continue] · [/resume] · [/fork] · [/tree] |
| 7 | 44.0 | `07 / OPEN FORMATS` | Extensible with open formats. | AGENTS.md · skills · MCP servers · plugins |
| 8 | 46.0 | `08 / SCRIPTABLE` | Scriptable. | [hoocode -p] · [--mode json] · [--mode rpc] |

(Cyan rule from direction §2: a card with several `[...]` tokens is the one exception; keep each token
short.)

## 4. Audio cue list (absolute times)

| Time | Cue (`score.md` §6) |
|---|---|
| 0.0 | Pad in |
| 1.0 | `blip-eye` |
| 2.05–3.55 | `key-tick` x48 (on the typed chars) |
| 3.95 | `key-enter` |
| 4.0 | sub hit, groove in, motif D5 |
| 5.6 | `whoosh-in` |
| 7.6, 13.6 | `whoosh-out` (pull-backs) |
| 8.0 | motif F5 |
| 10.0, 12.0, 19.0 | `blip-card` |
| 11.5, 13.5, 19.5 | `key-press` + `spark-micro` |
| 16.0 | `hit-buzz`, motif A5 (filtered) |
| 20.0–21.875 | riser + snare roll; 21.875–22.0 silence |
| 22.0 | DROP: sub hit |
| 26.0 | `chime-landed`, motif C6 |
| 28.0 | `spark-sting` short |
| 30.0–31.5 | motif D5 F5 A5 C6 (one per beat) |
| 32.0 … 46.0 (every 2.0) | `glitch-tick` |
| 47.875–48.0 | silence |
| 48.0 | `spark-sting` full |
| 52.0–53.4 | `key-tick` (soft) |
| 56.0 | final chord, `spark-micro` |
| 59.95 | silence; file ends 60.000 |

## 5. Notes

- Footage speeds are "fit" because exact clip times exist only after recording. After `cues.json`
  exists, write the resolved in/out/speed per shot into the composition and check that no shot needs
  more than 4x. If the clip is longer than expected, cut, don't speed: preferred cut points are
  `READ` → (diff on screen), and inside the cargo compile wait.
- Without the red step (scenario turns 5–6 dropped): shots 9–10 become `tests.` on the wide cargo run
  and a punch on `test result: ok`; shot 11 is the riser on wide footage; shot 12 is unchanged (`EXIT0`).
  The score keeps RED/RISE (the tension then reads as "waiting on the tests").
- Overlays never cover the cue text: verb plates sit right third (shots 3, 5, 14) or lower-left
  (shot 9), where the TUI has no text at that moment. Check each against the real frames.
- Last frame must be the complete end card (thumbnail fallback).
