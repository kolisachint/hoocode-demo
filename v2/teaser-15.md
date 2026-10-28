# Teaser, 15.0 s, three aspects from one timeline

Read `direction.md` first. One shared timeline module (all times below) and one score WAV
(`score.md` §5.3); three compositions differ only in layout:

- 9:16 1080x1920 → `out/v2/teaser-9x16.mp4`
- 1:1 1080x1080 → `out/v2/teaser-1x1.mp4`
- 16:9 1920x1080 → `out/v2/teaser-16x9.mp4`

Grid: 120 BPM, a 2-beat pickup (0.0–1.0), then 7 bars; bar N starts at 1.0 + (N-1) x 2.0 s.
Must read with sound off (social autoplay): every beat has its word on screen.

## 1. Timeline (shared)

| Time | Bar.beat | Beat | Content | Footage (cue in → out, speed) | Crop (see §3) | Audio |
|---|---|---|---|---|---|---|
| 0.0–1.0 | pickup | OWL | Owl glyph centred in the hero zone, eyes `#27272A` on frame 0 (poster: the owl is fully drawn on frame 0). Eyes light `#00F0FF` at 0.5. | none | — | Reverse swell into 1.0; `blip-eye` 0.5. |
| 1.0–3.0 | 1.1 | **plans.** | 1.0 hard cut: verb `plans.` slams in the verb zone; footage window appears (cut) with the plan. 1.0→1.4 push to the plan crop; brackets 1.4. Step label `01 / 04`. | `PLAN − 0.6` → `PANEL + 1.4` (1.0x) | C-PLAN | Sub hit + groove in; motif D5. |
| 3.0–5.0 | 2.1 | **asks.** | 3.0 cut: verb `asks.`; window shows card 1 (crop C-CARD). 4.5: keycap `y` `go, once` overlaps the window's bottom-right corner; spark micro; card disappears in the footage at 4.6. Label `02 / 04`. | `CARD1` → `Y1 + 0.4`, `Y1` at 4.6 (hold `CARD1` frames as needed) | C-CARD | `blip-card` 3.0; motif F5; `key-press` + `spark-micro` 4.5. |
| 5.0–7.0 | 3.1 | **tests.** | 5.0 cut: verb `tests.`; window shows the passing re-run from the left (`cargo test --quiet`, `running 2 tests`). 5.6–6.0 pan right; lands on `exit 0` at 6.0, brackets. Label `03 / 04`. 6.875–7.0 freeze (air gap). | `EXIT0 − 1.0` → `EXIT0 + 0.875` (1.0x, freeze last 0.125 s) | C-EXIT (pan) | Tension: A7sus4 → A7, snare roll 6.0–6.875; silence 6.875–7.0. Motif A5 at 5.0. |
| 7.0–9.0 | 4.1 | **lands.** | 7.0 cut: verb `lands.`; window shows the landing line and ticked plan; brackets on `● LANDED`. Label `04 / 04`. | `LANDED − 0.03` → `END` (1.0x, freeze) | C-LAND | DROP: sub hit; `chime-landed`; motif C6. |
| 9.0–11.0 | 5.1 | SPARK | 9.0 cut to brand field, no footage. Symbol C (`symbol.svg`) in the hero zone, cut in with both circles fully drawn and kissing, diamond and arcs hidden. **Spark at 9.0** (diamond 0 → 1.18 → 1.0, 0.30 s); arcs radiate 9.05–9.4 (stroke-dashoffset). 9.5: tagline rises in below. | none | — | `spark-sting` full at 9.0 (its pre-suck runs 8.5–9.0, under the end of bar 4). |
| 11.0–13.0 | 6.1 | LOCKUP | 11.0 cut: HooCode lockup (`hoocode.svg`), cursor blinking on beats. 11.5: sub-line. 12.0–12.9: install line types in its box. | none | — | Pad Fmaj7 → Csus2; `key-tick` (soft) on the typed chars. |
| 13.0–15.0 | 7.1 | END | 13.0: `npm install -g hoocode · pip install hoocode` and `v0.2.20` appear (opacity 0→1, 0.3 s). Cursor blinks on beats to 14.0, then solid. Frame 14.967 = complete end card. | none | — | Final chord D(add9) at 13.0, `spark-micro`; decay; digital silence by 14.95; file ends 15.000. |

Copy (exact):

- Verbs: `plans.` `asks.` `tests.` `lands.` (full stop `#00F0FF`)
- Step labels: `01 / 04` … `04 / 04` (JetBrains Mono, `#71717A`)
- Keycap: `y` + `go, once`
- Tagline (9.5): "Nothing applied without your say-so."
- Sub-line (11.5): "A terminal coding agent, written in Rust."
- Install (12.0): `$ curl -fsSL https://kolisachint.github.io/hoocode/install.sh | sh`
- 13.0: `npm install -g hoocode  ·  pip install hoocode` and `v0.2.20`

## 2. Per-aspect layout

All positions are px at the delivery size, `(x, y, w, h)` of the box; text boxes left-aligned unless
"centred". The footage window: `#18181B` 2 px border `#27272A`, radius 20 px, footage inside with
16 px inset, `overflow: hidden`. Verb sizes per `direction.md` §3.

### 9:16 (1080x1920)

| Element | Box | Notes |
|---|---|---|
| Owl / hero zone (0–1 s, 9–11 s) | centred, centre y=760 | Owl rows 150 px. Symbol C 760 px wide. |
| Verb | (72, 250, 936, 230) | Inter 800 200 px, baseline ~ y=440. |
| Step label | (72, 500, 400, 40) | 26 px. |
| Footage window | (40, 580, 1000, 820) | Crop aspect 968:788 ≈ 1.23. |
| Keycap | (680, 1330, 340, 150) | Overlaps window's bottom-right edge by 70 px. |
| Tagline | centred, (72, 1080, 936, 200) | Inter 700 72 px, 2 lines: "Nothing applied" / "without your say-so." |
| Lockup | centred, 860 px wide, centre y=700 | |
| Sub-line | centred, (72, 860, 936, 60) | Inter 500 40 px `#A1A1AA`. |
| Install box | (72, 1000, 936, 190) | Mono 34 px, 2 lines: `$ curl -fsSL` / `https://kolisachint.github.io/hoocode/install.sh \| sh` (break after `-fsSL`). |
| npm · pip / version | centred, y=1230 / y=1290 | Mono 30 px `#A1A1AA` / mono 30 px `#00F0FF`. |
| Keep clear | y < 220, y > 1500 | Platform UI. Nothing important there. |

### 1:1 (1080x1080)

| Element | Box | Notes |
|---|---|---|
| Hero zone | centred, centre y=540 | Owl rows 120 px. Symbol C 620 px wide, centre y=440 (tagline below). |
| Verb | (60, 50, 700, 170) | Inter 800 150 px. |
| Step label | (820, 140, 200, 40) | right-aligned at x=1020, 22 px. |
| Footage window | (40, 240, 1000, 780) | Crop aspect 968:748 ≈ 1.29. |
| Keycap | (700, 900, 320, 140) | |
| Tagline | centred, (60, 700, 960, 150) | Inter 700 60 px, 2 lines. |
| Lockup | centred, 760 px wide, centre y=330 | |
| Sub-line | centred, y=500 | Inter 500 34 px. |
| Install box | (60, 600, 960, 170) | Mono 30 px, 2 lines (same break as 9:16). |
| npm · pip / version | centred, y=820 / y=880 | Mono 26 px. |

### 16:9 (1920x1080)

| Element | Box | Notes |
|---|---|---|
| Hero zone | centred, centre y=500 | Owl rows 130 px. Symbol C 760 px wide, centre y=420. |
| Verb | (96, 380, 640, 200) | Inter 800 168 px, vertically centred left column. |
| Step label | (96, 600, 400, 40) | 22 px. |
| Footage window | (760, 90, 1064, 900) | Crop aspect 1032:868 ≈ 1.19. |
| Keycap | (1480, 860, 360, 150) | |
| Tagline | centred, (96, 760, 1728, 100) | Inter 700 72 px, 1 line. |
| Lockup | centred, 1000 px wide, centre y=380 | |
| Sub-line | centred, y=560 | Inter 500 40 px. |
| Install box | centred, (300, 650, 1320, 110) | Mono 34 px, 1 line. |
| npm · pip / version | centred, y=820 / y=880 | Mono 30 px. |

## 3. Footage crops (per aspect)

Notation as `recording.md` §5, but the crop height follows the window aspect: `w` = crop width as a
fraction of the 2880 px source; height = `w` x 2880 / window aspect. Anchor row at `p` of the crop
height; clamp inside the frame. At these widths the terminal text renders 31–36 px tall.

| Crop | 9:16 (aspect 1.23) | 1:1 (aspect 1.29) | 16:9 (aspect 1.19) | Shows |
|---|---|---|---|---|
| C-PLAN | `w 0.46, x0 0.0, PANEL@0.40` | `w 0.46, x0 0.0, PANEL@0.40` | `w 0.42, x0 0.0, PANEL@0.40` | `01 ● TodoWrite 4 items` above, the 4 plan rows, comms frame top edge |
| C-CARD | `w 0.48, x0 0.0, CARD1@0.70` | `w 0.48, x0 0.0, CARD1@0.70` | `w 0.44, x0 0.0, CARD1@0.70` | `◎ CLEARANCE NEEDED`, `Edit src/main.rs`, REACH, `y go, once · a always…` (the keys row is cut after `a always` at these widths; that is fine, the keycap repeats `y go, once`) |
| C-EXIT | start `w 0.46, x0 0.0, EXIT0@0.25` → pan to `x0 0.54` | same | `w 0.42`, `x0 0.0` → `x0 0.58` | left: `06 ● Shell cargo test --quiet`, `running 2 tests`, `test result: ok. 2 passed`; right: `exit 0 · 3 lines` |
| C-LAND | `w 0.50, x0 0.0, LANDED@0.25` | same | `w 0.46, x0 0.0, LANDED@0.25` | `● LANDED · 7 steps · …`, ticked plan, comms frame `● LANDED` |

Camera inside the window: cut in at 0.94 of the crop scale and push to 1.0 over the first 0.4 s of
each beat (`power3.out`); C-EXIT pans with `power3.inOut` 5.6–6.0.

## 4. Notes

- The teaser has no red step and no typed-task beat: 15 s fits one idea per bar.
- Frame 0 is the poster on most platforms: the owl must be fully drawn at frame 0 (eyes dark is fine).
- The verb, label and window positions are the same for all four acts within an aspect: only content
  changes, so the cuts read as one rhythm.
- Check C-CARD against the real recording: if `◎ CLEARANCE NEEDED` and `y go, once` do not both fit,
  move `p` (the card is 5 rows; it must be whole).
