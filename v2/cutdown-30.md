# Cutdown, 30.0 s, 1920x1080, 30 fps

Same grid, look and footage as `trailer-60.md` (read it first; shot styles, plates, keycaps, brackets
and card layouts are defined there). 120 BPM, 15 bars, bar N starts at (N-1) x 2.0 s. The cutdown
skips the red test (it uses only the passing re-run) and shows three feature cards. Its score is its
own arrangement (`score.md` §5.2), not a cut of the 60 s mix.

## 1. Structure

| Bars | Time | Act | Score section |
|---|---|---|---|
| 1 | 0.0–2.0 | Owl + typed task | OPEN |
| 2–3 | 2.0–6.0 | **plans.** | PLANS |
| 4–5 | 6.0–10.0 | **asks.** (Edit `y`, Shell `a`) | ASKS (bar 5 ends with an air gap) |
| 6 | 10.0–12.0 | **tests.** `exit 0` | DROP |
| 7 | 12.0–14.0 | **lands.** | DROP |
| 8 | 14.0–16.0 | "Shell, Edit and Write ask first." | BREATH |
| 9–11 | 16.0–22.0 | Three feature cards | FEATURES |
| 12–13 | 22.0–26.0 | Lockup + tagline | LOCKUP |
| 14–15 | 26.0–30.0 | Install card, end | END |

## 2. Shot list

| # | Time | Visual | On-screen copy | Footage in → out (speed) | Camera / zoom | Out | Music / SFX |
|---|---|---|---|---|---|---|---|
| 1 | 0.0–2.0 | Owl (120 px rows) at top-centre y=330, eyes light at 0.0+2 frames (frame 0 shows eyes dark for the poster, eyes lit by 0.07). Under it the task types 0.40–1.85 (30 ms/char), JetBrains Mono 48 px centred, `--json` cyan. | `$ hoocode "Add a --json flag to the stats command"` | none | 1.00→1.04 | hard cut 2.0 (Enter) | Pad in from -inf over 0.5 s. `blip-eye` 0.07. `key-tick` per char. `key-enter` 1.95. |
| 2 | 2.0–4.0 | Footage wide; `plans.` plate right third 2.0–3.9. | **plans.** | `TUI` → `PLAN − 0.4` (fit) | 1.0x→1.04x | — | Sub hit + groove 2.0; motif D5. |
| 3 | 4.0–6.0 | Punch on the 4 plan items, brackets 4.0. | — | `PLAN − 0.4` → `PANEL + 1.6` | push 3.6→4.0 to `Z(0.56, 0.0, PANEL@0.45)` | hard cut 6.0 | `whoosh-in` 3.6. |
| 4 | 6.0–8.0 | Card 1 with diff above (cut in already zoomed). `asks.` plate lower-left 6.0–7.4. Keycap `y` `go, once` 7.5. | **asks.** · keycap | `CARD1` → `Y1 + 0.1`, `Y1` at 7.6 | `Z(0.66, 0.0, CARD1@0.82)` | hard cut 8.0 | Motif F5, `blip-card` 6.0; `key-press` + `spark-micro` 7.5. |
| 5 | 8.0–10.0 | Card 2 (Shell). Keycap `a` `always cargo in this session` at 9.25. 9.5–9.875: hard cut to wide footage of cargo compiling (`Y3` → …), push toward the `EXIT0` rect. | keycap | 8.0–9.5: `CARD2` → `A2 + 0.1`, `A2` at 9.35. 9.5–9.875: `Y3 + 0.2` → `EXIT0 − 0.03` (fit, up to 4x; jump cut is fine) | 8.0 `Z(0.66, 0.0, CARD2@0.82)`; 9.5 1.0x → push to shot 6 rect by 10.0 | air gap: freeze 9.875–10.0 | `blip-card` 8.0; `key-press` + `spark-micro` 9.25; short riser 9.0–9.875; silence 9.875–10.0. |
| 6 | 10.0–12.0 | **Green.** Land on `exit 0`, brackets. 10.6–11.6 pan left to `test result: ok. 2 passed`. `tests.` plate lower-left 10.0–11.9. | **tests.** | `EXIT0` → `DONE − 0.2` (1.0x) | `Z(0.60, 0.40, EXIT0@0.30)` → `Z(0.60, 0.0, OK@0.45)` | hard cut 12.0 | DROP 10.0: sub hit, full groove; motif A5. |
| 7 | 12.0–14.0 | `● LANDED` punch, brackets 12.0; `lands.` plate right third. | **lands.** | `LANDED − 0.03` → `END` (1.0x, freeze) | `Z(0.62, 0.0, LANDED@0.30)` | hard cut 14.0 | `chime-landed` 12.0; motif C6. |
| 8 | 14.0–16.0 | Brand card: symbol C top (spark at 14.0), headline, key legend at 15.0 (as trailer shot 15). | "Shell, Edit and Write ask first." / `y go, once · a always · n abort + say why · e edit first` | none | static | hard cut 16.0 | `spark-sting` short 14.0; drums out. |
| 9 | 16.0–18.0 | Feature card (trailer §3 layout), label `01 / BINARY`. | One static binary. / no Node · no Python · no runtime to install | none | per trailer §3 | cut | `glitch-tick` 16.0. |
| 10 | 18.0–20.0 | Feature card `02 / PROVIDERS`. | Any model provider. / Anthropic · OpenAI · Google · OpenRouter / Groq · DeepSeek · xAI · Fireworks · [/login] | none | | cut | `glitch-tick` 18.0. |
| 11 | 20.0–22.0 | Feature card `03 / MODES`. | Four modes. Subagents. Sessions. / [ask] · [plan] · [build] · [debug] | none | | cut; air gap 21.875–22.0 (picture holds) | `glitch-tick` 20.0; fill; silence 21.875–22.0. |
| 12 | 22.0–24.0 | Lockup build (as trailer shot 25, shifted to 22.0: spark exactly at 22.0). | — | none | | — | `spark-sting` full 22.0. |
| 13 | 24.0–26.0 | Tagline under lockup at 24.0; 25.6–26.0 lockup moves up to y=260, 640 px wide. | "Nothing applied without your say-so." | none | | — | |
| 14–15 | 26.0–30.0 | Install card (as trailer shots 27–30, compressed): curl line types 26.0–27.2; 27.5 npm · pip line; 28.0 platform line + URL. Cursor blinks on beats to 29.0, then solid. Last frame = complete end card. | `$ curl -fsSL https://kolisachint.github.io/hoocode/install.sh \| sh` / `npm install -g hoocode  ·  pip install hoocode` / `macOS · Linux · x64 · arm64 · MIT · v0.2.20` / `kolisachint.github.io/hoocode` | none | static | none | Final chord D(add9) at 26.0, `spark-micro` 26.0, decay; digital silence by 29.95; file ends 30.000. |

## 3. Notes

- The jump from card 2 (`A2`) to the passing run skips the red test and card 3. The edit is a hard
  cut inside shot 5, so it reads as "time passes", not as a continuous take.
- Card 11 headline differs from the trailer (it merges cards 4–6) because it is the only modes card.
  All three items are verified (`direction.md` §6).
- Audio cues are those in the table; times are absolute.
