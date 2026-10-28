# Teaser, 15.0 s, three aspects from one timeline

Read `direction.md` first. One shared timeline module (all times below) and one score WAV
(`score.md` §5.3); three compositions differ only in layout. **Built** (2026-10-28) in
`v2/teaser15/` (rebuild steps: `v2/teaser15/README.md`); the times below are as built.

- 9:16 1080x1920 → `out/v2/hoocode-teaser-9x16.mp4`
- 1:1 1080x1080 → `out/v2/hoocode-teaser-1x1.mp4`
- 16:9 1920x1080 → `out/v2/hoocode-teaser-16x9.mp4`
- posters (frame 0) → `out/v2/hoocode-teaser-<aspect>-poster.png`

Footage: `out/v2/hoocode-v2-4k.mp4` (3840x2160, 30 fps, 30.1 s). Footage times are clip seconds from
`v2/recording/cues.json`; `v2/teaser15/build.py` turns them into in-points so each cue's first frame
lands on its beat, and writes `v2/teaser15/events.json` from the same numbers.

Grid: 120 BPM, a 2-beat pickup (0.0–1.0), then 7 bars; bar N starts at 1.0 + (N-1) x 2.0 s.
Must read with sound off (social autoplay): every beat has its word on screen.

## 1. Timeline (shared, as built)

| Time | Bar.beat | Beat | Content | Footage (clip in-point, speed) | Audio (SFX from events.json) |
|---|---|---|---|---|---|
| 0.0–1.0 | pickup | OWL | Owl (owl.txt drawn as quadrant rects on the TUI cell) + banner `hoo│code` / `coding agent · v0.2.20`, fully drawn on frame 0 (poster), eyes `#27272A`. Linear drift 1.0 → 1.035. **0.5**: eyes `#00F0FF` with glow 18 → 8 px. | none | music: reverse swell; `blip-eye` 0.5 |
| 1.0–3.0 | 1.1 | **plans.** | 1.0 hard cut: verb slams (on screen from the downbeat frame, scale 1.12 → 1.0, 0.25 s expo.out), label `01 / 04`, window. Camera cuts in at 0.94 and pushes to 1.0 over 1.0–1.5 (power3.out). `TodoWrite 4 items · 0 done` appears at 1.2; the task panel (the 4-item plan) appears **1.5** and the brackets snap on it (1.5). The transcript scrolls on (Read, Edit) under the fixed panel. | 5.937 (`PANEL` lands on 1.5), 1.0x, to 7.937 | music: sub hit, motif D5 |
| 3.0–5.0 | 2.1 | **asks.** | 3.0 cut: `asks.`, `02 / 04`; card 1 is already up (`◎ CLEARANCE NEEDED`, `BUILD asks for Edit`, REACH, `y go, once · a always Edit in BUILD …`). Push 3.0–3.5; brackets on `◎ CLEARANCE NEEDED` / `Edit src/main.rs` at 3.5. **4.5**: keycap `y` `go, once` slams in over the window's bottom-right corner, key depresses, cyan spark-micro diamond. **4.6**: the card leaves in the footage (`Y1`), brackets off. 4.8–5.0 hold (frame 450; card 2 would appear at 4.83). | 13.204 (`Y1` lands on 4.6), 1.0x, to 15.004; still frame 450 4.8–5.0 | `blip-card` 3.0; `key-press` + `spark-micro` 4.5; music: motif F5, kick/hats/clap |
| 5.0–7.0 | 3.1 | **tests.** | Red → green. 5.0 cut: `tests.`, `03 / 04`; the window holds the failed run (`04 ⊗ Shell cargo test --quiet`, `Command exited with code 101`, the red/green fix diff) with brackets on `Command exited with code 101`, and the status chip (keycap slot) reads `● exit 101` (dim). **5.467** (frame 164, the closest frame to beat 2): the re-run lands live, `06 ● Shell cargo test --quiet`, `running 2 tests`, `test result: ok. 2 passed; 0 failed`; red brackets off; the chip flips to `◆ exit 0 · 2 passed` (signal, diamond pop). 5.6–6.0 push in 1.15x (left edge fixed) onto the result; brackets on `test result: ok. 2 passed` at **6.0**. 6.875–7.0 freeze (air gap). | still frame 683 (first frame after `Y3`) 5.0–5.467; 23.237 (`EXIT0`), 1.0x, 5.467–6.875; still frame 739 6.875–7.0 | `hit-buzz` (−3 dB) 5.0; `glitch-tick` 5.467; music: motif A5, A7sus4 → A7, snare roll 6.0–6.875, gap 6.875–7.0 |
| 7.0–9.0 | 4.1 | **lands.** | 7.0 cut (the drop): `lands.`, `04 / 04`; `● LANDED · 7 steps · 1 hit · 22s · 960 tokens · $0.000` is on screen on the first frame, with `4 items · 4 done`, the ticked plan and the comms frame `● LANDED · 22s · 7 steps`. Push 7.0–7.5; brackets on `● LANDED` at 7.5. | 26.604 (`LANDED` on 7.0), 1.0x, to 28.604 | `chime-landed` 7.0; music: DROP sub hit, motif C6; sting pre-suck 8.5–9.0 |
| 9.0–11.0 | 5.1 | SPARK | 9.0 cut to the field: Symbol C, circles drawn and kissing; **spark at 9.0**: diamond 0 → 1.0 (back.out(2.2), peak about 1.18) over 0.30 s, glow on the diamond 0 → 24 → 8 px; arcs draw 9.05–9.40. Drift 1.0 → 1.03. **9.5**: tagline rises in (28 px, 0.45 s expo.out). | none | `spark-sting` 9.0 |
| 11.0–13.0 | 6.1 | LOCKUP | 11.0 cut: HooCode lockup with the mark drawn; diamond pops 0.4 → 1.0 (11.0–11.3), signal arc draws 11.0–11.25, divider and `code` fade up 11.05–11.45. Cursor: on 11.5–12.0, rests while the install line types, on 13.5–14.0, solid from 14.0. 11.5: sub-line rises in. 11.9: install box fades in (0.1 s); 12.0–12.867: the command types, 64 chars on 27 frames (char k on frame 360 + ⌊27k/64⌋), cyan block cursor after it. | none | `key-tick-soft` one per char at its frame (score.py keeps 27, one per frame); music: Fmaj9 → Csus2 |
| 13.0–15.0 | 7.1 | END | 13.0: `npm install -g hoocode  ·  pip install hoocode` and `v0.2.20` fade in (0.3 s); the lockup's diamond pulses 1.0 → 1.35 → 1.0; install cursor off. Frame 14.967 = complete end card. | none | `spark-micro` 13.0; music: Dadd9, fade 13.5 → 14.95, zeros to 15.0 |

Copy (exact):

- Verbs: `plans.` `asks.` `tests.` `lands.` (full stop `#00F0FF`)
- Step labels: `01 / 04` … `04 / 04` (JetBrains Mono, `#71717A`)
- Keycap: `y` + `go, once`
- Tagline (9.5): "Nothing applied without your say-so."
- Sub-line (11.5): "A terminal coding agent, written in Rust."
- Install (12.0): `$ curl -fsSL https://kolisachint.github.io/hoocode/install.sh | sh`
- 13.0: `npm install -g hoocode  ·  pip install hoocode` and `v0.2.20`

## 2. Per-aspect layout (as built)

All positions are px at the delivery size, `(x, y, w, h)`. Footage window: `#18181B`, 2 px `#27272A`
border, radius 20, 16 px inset, footage area `#09090B` with radius 6, `overflow: hidden`, shadow
`0 40px 120px rgba(0,0,0,.55)`. Verb: Inter 800, tracking -0.04em, full stop `#00F0FF`. Step label:
JetBrains Mono 500, `#71717A`, +0.12em. Keycap: `#18181B`, 2 px `#27272A`, radius 12; key in a
`#09090B` cap, JetBrains Mono 700 `#00F0FF`; label JetBrains Mono 500 `#A1A1AA`. Brackets: 28 px arms,
3 px `#00F0FF`, glow `rgba(0,240,255,.40)`, 14 px / 5 px padding around the cue's cells.

### 9:16 (1080x1920)

Key copy stays within y 250–1520 (platform UI above and below); sides 64–72.

| Element | Box | Notes |
|---|---|---|
| Owl group (0–1 s) | owl 560 px wide from y 470; banner centred below | `hoo│code` mono 700 96 px; tag mono 500 34 px. Group spans y 470–1180. |
| Verb | x 68, top 250 | 200 px. |
| Step label | right-aligned at x 1008, top 318 | 28 px (beside the verb, not under it). |
| Footage window | (40, 490, 1000, 1030) | inner 964 x 994, bottom at 1520. Shows 1570 px of the 4K width on plans (text about 30 px) and 1320 px on asks, tests, lands (key strings about 36 px). |
| Keycap / status chip | right edge 1056, top 1380, h 132 | key 64 px, label 32 px; chip mono 700 40 px; over the window's bottom-right corner; bottom 1512. |
| Symbol C | 860 wide at (110, 470) | |
| Tagline | (64, 1010, 952) centred | Inter 700 84 px, 2 lines. |
| Lockup | 980 wide at (50, 420) | End-card group spans y about 500–1250, optically centred in the safe zone. |
| Sub-line | centred, top 744 | Inter 500 46 px `#A1A1AA`. |
| Install box | (64, 860, 952) | Mono 500 40 px, 3 lines: `$ curl -fsSL` / `https://kolisachint.github.io/` / `hoocode/install.sh \| sh`. |
| npm · pip / version | centred, top 1146 / 1204 | mono 32 px `#A1A1AA` / 40 px `#00F0FF`. |

### 1:1 (1080x1080)

5% margins (54 px).

| Element | Box | Notes |
|---|---|---|
| Owl group | owl 380 wide from y 262; banner below | name 72 px, tag 28 px. |
| Verb | x 56, top 50 | 150 px. |
| Step label | right-aligned at x 1026, top 110 | 24 px. |
| Footage window | (54, 236, 972, 790) | inner 936 x 754; 1570 px of source width. |
| Keycap / status chip | right edge 1004, top 900, h 116 | key 54 px, label 28 px; chip 34 px. |
| Symbol C | 620 wide at (230, 250) | |
| Tagline | (60, 640, 960) centred | Inter 700 64 px, 2 lines. |
| Lockup | 760 wide at (160, 206) | |
| Sub-line | centred, top 476 | 36 px. |
| Install box | (64, 576, 952) | mono 27 px, 2 lines. |
| npm · pip / version | centred, top 802 / 856 | 27 px / 30 px. |

### 16:9 (1920x1080)

Title-safe 96 px sides, 54 px top/bottom.

| Element | Box | Notes |
|---|---|---|
| Owl group | owl 440 wide, banner to its right, centred row at y 330 | name 136 px, tag 42 px (the TUI's banner layout). |
| Verb | x 92, top 384 | 176 px. |
| Step label | (98, 600) | 24 px. |
| Footage window | (760, 72, 1064, 936) | inner 1028 x 900; 1680 px of source width (text about 30 px). |
| Keycap / status chip | right edge 1856, top 892, h 128 | key 60 px, label 30 px; chip 38 px. |
| Symbol C | 760 wide at (580, 200) | |
| Tagline | (96, 700, 1728) centred | Inter 700 80 px, 1 line. |
| Lockup | 1000 wide at (460, 170) | |
| Sub-line | centred, top 540 | 44 px. |
| Install box | (236, 650, 1448) | mono 34 px, 1 line. |
| npm · pip / version | centred, top 830 / 884 | 30 px / 34 px. |

## 3. Footage crops (as built)

Geometry of the 4K take: 117 x 32 cells of 29 x 65 px, grid origin (224, 40); cell (c, r) spans
x 224 + 29c, y 40 + 65r. Crops are in 4K px (`teaser.js`, `SHOTS`): `x` = left edge, `w` = width per
aspect (9:16 / 1:1 / 16:9), height = `w` / window aspect, placed by its bottom edge or centre. The
camera cuts in at 0.94 and pushes to 1.0 over the first beat of each act, centred on the cue;
brackets ride inside the push.

| Crop | w (9:16 / 1:1 / 16:9) | Placement | Brackets on (cells) | Shows |
|---|---|---|---|---|
| C-PLAN | 1570 / 1570 / 1680 | x 232, bottom 2160 | cols 2–51, rows 25–28: the task panel | `M1 Add a --json flag…`, plan text, `01 ● TodoWrite 4 items · 0 done`, the 4 plan rows, `◐ IN FLIGHT` frame |
| C-CARD | 1320 / 1570 / 1680 | x 180, bottom 2330 / 2210 / 2210 | cols 0–20, rows 27–28: `◎ CLEARANCE NEEDED` / `Edit src/main.rs` | `03 ● Edit` diff, plan rows, the whole 5-row card incl. `y go, once · a always Edit in BUILD`; room below the card for the keycap |
| C-TEST | 1320 / 1400 / 1500 | x 200, centre y 950; push 1.15x 5.6–6.0 (left edge fixed, about the result row) | red: cols 8–35, row 10 `Command exited with code 101` (5.0–5.467); green: cols 8–32, row 16 `test result: ok. 2 passed` (6.0) | red: step 04 ⊗, exit 101 line, fix diff; green: `Running them again.`, `06 ● Shell cargo test --quiet`, `running 2 tests`, the result, `Took 0.2s`, `Tests pass.` |
| C-LAND | 1320 / 1570 / 1680 | x 232, bottom 2190 | cols 2–9, row 23: `● LANDED` | `07 ● TodoWrite 4 items · 4 done`, summary, `● LANDED · 7 steps · 1 hit · 22s …`, ticked plan, comms `● LANDED` |

## 4. Notes

- The teaser has no red step and no typed-task beat: 15 s fits one idea per bar.
- Frame 0 is the poster on most platforms: the owl must be fully drawn at frame 0 (eyes dark is fine).
- The verb, label and window positions are the same for all four acts within an aspect: only content
  changes, so the cuts read as one rhythm.
- C-CARD checked against the take: the whole 5-row card fits, `◎ CLEARANCE NEEDED` through `or type a reply`.
- The tests act is red → green inside one crop: the take scrolls the failing step away exactly as the
  passing run lands (`HIT_END` = `EXIT0`). The red beat is a still (frame 683) because the take scrolls
  one row in the next frames, which would slide the text out of its brackets.
- `exit 0` sits 2900 px right of `test result: ok` in the take; no legible crop holds both, so `exit 0`
  is a brand-styled status chip (keycap slot, JetBrains Mono) and the crop stays on the result block.
- No window frame is more than about half empty.
