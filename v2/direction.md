# HooCode launch films v2: creative direction

Status: direction for implementers (2026-10-28). Docs only; nothing here is rendered.
Product: `hoocode` v0.2.20, a terminal coding agent written in Rust.
Companion docs: `trailer-60.md`, `cutdown-30.md`, `teaser-15.md`, `score.md`, `recording.md`.

## 1. The idea

**Plans. Asks. Tests. Lands.**

Four verbs, four beats of a bar, four acts. Each verb is a real state on the HooCode screen:

| Verb | What the viewer sees on screen (real UI string) | Source |
|---|---|---|
| plans. | `TodoWrite  4 items · 0 done` and the plan in the task panel | `crates/hoocode-code-tui-widgets/src/tools/todo.rs` |
| asks. | `◎ CLEARANCE NEEDED` · `BUILD asks for Edit` · `y go, once` | `crates/hoocode-code-tui-app/src/clearance_card.rs` |
| tests. | `HIT` `exit 101`, then `exit 0` | `crates/hoocode-code-tui-widgets/src/tool_execution.rs` |
| lands. | `● LANDED` | `crates/hoocode-code-tui-app/src/comms_frame.rs`, `trajectory.rs` |

The brand's own mark carries the idea. Symbol C is two kissing nodes with a diamond spark between
them: one node is the agent, one is you, and **the spark is your say-so**. Every time the user presses
`y` or `a` in the footage, the cyan diamond fires (picture + sound). The spark fires in full only at the
logo moment, so the logo pays off what the film showed.

Closing line (the product's own tagline, `brand/brand.json`, README of `hoocode`):

> **Nothing applied without your say-so.**

Supporting line: "A terminal coding agent, written in Rust." (hoocode `README.md`, line 1 of the
description).

Mid-film line (trailer and cutdown): "Shell, Edit and Write ask first." (`docs/user/quickstart.md`,
"In a session").

## 2. Visual language

- **The terminal is the hero, full-bleed.** The footage is recorded at 2880x1620 on `#09090B`
  (the brand base), so it sits edge to edge in 16:9 with no window chrome, no traffic lights, no
  frame. Text in the wide shot is about 27 px tall on a 1080p frame (v1: about 13 px).
- **Punch-ins on the four moments.** Every act has one push-in to a cue (plan, clearance card,
  exit code, LANDED). The camera moves; the footage pixels are never recoloured.
- **Focus brackets.** At each punch-in landing, four cyan corner brackets (arms 28 px, stroke 3 px,
  `#00F0FF`, glow `0 0 12px rgba(0,240,255,0.40)`) snap around the cue text. They are the only
  graphic drawn over the footage apart from the verb plate and keycaps.
- **Verb plate.** Big verb (`plans.` etc.), Inter 800, `#FAFAFA`, the full stop in `#00F0FF`.
  Over footage it sits on a plate: `#09090B` at 88% opacity, 1 px `#27272A` border, radius 20 px.
- **Keycaps.** When the user answers a card: a keycap, `#18181B` fill, 2 px `#27272A` border,
  radius 12 px, key letter in JetBrains Mono 700 `#00F0FF`, label in JetBrains Mono 500 `#A1A1AA`
  (exact card text: `go, once`, `always cargo in this session`).
- **Brand cards** (no footage): `#09090B` field; panel `#18181B`, 1 px `#27272A`, radius 20 px,
  with the design-review glow `radial-gradient(circle at 30% 20%, rgba(0,240,255,0.15) 0%, transparent 50%)`.
- **Colour.** Brand tokens only: `#00F0FF` (signal), `rgba(0,240,255,0.15)` (dim), `rgba(0,240,255,0.40)`
  (glow), `#09090B`, `#18181B`, `#27272A`, `#FAFAFA`, `#E4E4E7`, `#A1A1AA`, `#71717A`. No gradients
  between hues. Cyan is rare: one cyan element per frame at most (the spark, the full stop, a
  bracket set, or one token in a line). The v1 gradient `#5cc8bb → #9b8cff` is gone.
- **Footage colours are the product's.** The TUI's own theme (default `dark`: teal accent, amber
  clearance card, olive LANDED, magenta session chip) stays as recorded. That is what users get.
  Never reuse those colours in the motion graphics.

## 3. Typography

Inter (variable, `teaser/assets/fonts/Inter-var.woff`) for display; JetBrains Mono
(`teaser/assets/fonts/jetbrains-mono-latin-{400,500,700}-normal.woff`) for anything a terminal would
print: commands, flags, keys, labels, versions. Tracking: display -0.04em, labels +0.12em uppercase.

Sizes in px at the delivery resolution:

| Role | Face / weight | 16:9 1920x1080 | 1:1 1080x1080 | 9:16 1080x1920 |
|---|---|---|---|---|
| Verb (`plans.`) | Inter 800 | 168 | 150 | 200 |
| Headline (brand cards, tagline) | Inter 700 | 80 | 60 | 72 |
| Sub-headline | Inter 500 | 44 | 36 | 44 |
| Mono body (install, flags) | JetBrains Mono 500 | 36 | 30 | 34 |
| Keycap letter / label | JetBrains Mono 700 / 500 | 64 / 30 | 56 / 26 | 64 / 30 |
| Label (`01 / BINARY`) | JetBrains Mono 500, caps, `#71717A` | 22 | 22 | 26 |
| Minimum text anywhere | | 22 | 22 | 26 |

Safe areas: 16:9 title-safe 96 px each side. 1:1 margin 60 px. 9:16: no text above y=220 or
below y=1500 (platform UI), side margins 72 px.

## 4. Motion principles

- **Everything lands on the grid.** 120 BPM, 30 fps: 1 beat = 0.5 s = 15 frames, 1 bar = 2.0 s.
  Cuts on downbeats; secondary events on beats; type-on and ticks on 16ths (0.125 s).
- **Easing.**
  - Enter: `expo.out` (cubic-bezier(0.16, 1, 0.3, 1)), 0.45 s.
  - Exit: `power2.in`, 0.25 s, or a hard cut (preferred on downbeats).
  - Camera (punch-in, pan): `power3.inOut`, 0.40 s, **starting 0.40 s before the beat** so it lands
    on the beat. Slow drift between moves: linear, at most +4% scale per 2 s.
  - Spark: the diamond scales 0 → 1.18 → 1.0 over 0.30 s (`back.out(2.2)` is the only overshoot
    allowed in the films), glow `drop-shadow 0 → 24px → 8px rgba(0,240,255,0.40)`.
- **Verb slam.** Opacity 0 → 1 in 2 frames, scale 1.12 → 1.00 over 0.25 s `expo.out`; hard cut out.
- **Type-on.** One character per 32 ms for commands, a block cursor `_` in `#00F0FF` at the end.
  Cursor blink: on for 0.5 s, off for 0.5 s, phase-locked to the beat (the product blinks at 530 ms,
  `CURSOR_BLINK_PERIOD` in `crates/hoocode-code-tui-app/src/wordmark.rs`; the films round to the beat).
- **No** bounces, wiggles, 3D flips, blur-ins, light leaks, particle fields, starfields or countdowns.
- **Determinism.** Everything is a function of timeline time. The lockup SVG's CSS `@keyframes
  hoo-blink` must be removed when inlined; the timeline drives `.cursor` opacity.
- Max punch-in: 2.0x of frame (the source is 1.5x the 1080p delivery, so 2.0x = 1.33x pixel upscale).

## 5. Brand asset usage

Copy from `/home/user/hoo-brand/assets/` into `v2/assets/brand/` (same file names). Dark variants
only; the `-light` files and `explore/` studies are not used.

| File | Used in | How |
|---|---|---|
| `hoocode.svg` (HooCode lockup, 274x80) | End card of all films (trailer 48.0, cutdown 22.0, teaser 11.0) | Inline the SVG. Build order: `h` stem + arch draw (stroke-dashoffset), two node circles draw, diamond `polygon` sparks, signal arc draws, divider fades, `code` paths fade up, `.cursor` blinks on beats. Drop its `<rect>` background (the field is already `#09090B`) or keep it; it is the same colour. |
| `symbol.svg` (Symbol C, 168x80) | Teaser spark moment 9.0; trailer/cutdown "breath" card corner; feature-card corner motif | Inline. Circles draw, kiss, `polygon` = the spark, the two cyan arcs radiate out. |
| `icon.svg` (Symbol C tile, 200x200) | Thumbnails / poster stills for upload (one per film) | Static, centred, 360 px on 16:9 poster. |
| `tui/owl.txt` (owl glyph) | Cold open of trailer, cutdown, teaser | Render in JetBrains Mono 500: body `#FAFAFA`, the two eye glyph pairs `▟▙` `#00F0FF` (colours from `tui/owl.ans`: 97 bright white, 38;2;0;240;255 cyan). Line-height 1.0, letter-spacing 0 so the quadrant blocks meet. |
| `wordmark.svg`, `favicon.svg`, `icon-mono.svg` | Not used | Monogram A and the bare `hoo` wordmark would compete with the HooCode lockup. |
| HooCowork / HooTeams lockups | Not used | Off-message for a HooCode launch. |

The owl banner next to the glyph uses the product's real banner text: `hoo│code` (`hoo` `#FAFAFA`,
`│` `#71717A`, `code` `#00F0FF`) and `coding agent · v0.2.20` (`#71717A`), as drawn by
`crates/hoocode-code-tui-app/src/wordmark.rs` (default tagline "coding agent").

## 6. Product facts the films use (all verified)

| Claim on screen | Source |
|---|---|
| A terminal coding agent, written in Rust. | hoocode `README.md` |
| One static binary. No Node, no Python, no runtime to install. | `README.md` ("single native binary: no Node, no Python, no runtime to install"); Linux builds static (musl) |
| macOS and Linux, x64 and arm64 | `README.md` Install; `docs/user/install.md` |
| Anthropic · OpenAI · Google · OpenRouter · Groq · DeepSeek · xAI · Fireworks | `README.md` "Any provider" |
| Shell, Edit and Write ask first | `docs/user/quickstart.md` |
| ask · plan · build · debug | `docs/user/quickstart.md` Modes |
| Subagents, through the same approval gate | `README.md` "Subagents" |
| `--continue` · `/resume` · `/fork` · `/tree` | `README.md`, `docs/user/quickstart.md` Sessions |
| AGENTS.md · skills · MCP servers · plugins | `README.md` "Extensible with open formats" |
| `hoocode -p` · `--mode json` · `--mode rpc` | `README.md` Quick start |
| `curl -fsSL https://kolisachint.github.io/hoocode/install.sh \| sh` · `npm install -g hoocode` · `pip install hoocode` | `README.md` Install |
| MIT · v0.2.20 | `README.md` badge; workspace `Cargo.toml` `version = "0.2.20"` |
| Docs at kolisachint.github.io/hoocode | `README.md` Documentation |

Do not claim: PR creation, Windows, Homebrew, crates.io, speed numbers, benchmarks.

## 7. Deliverables and pipeline

| Film | Size | Duration | Output |
|---|---|---|---|
| Trailer | 1920x1080 | 60.0 s (1800 frames) | `out/v2/trailer-60.mp4` |
| Cutdown | 1920x1080 | 30.0 s (900 frames) | `out/v2/cutdown-30.mp4` |
| Teaser | 1080x1920 / 1080x1080 / 1920x1080 | 15.0 s (450 frames) each | `out/v2/teaser-9x16.mp4`, `teaser-1x1.mp4`, `teaser-16x9.mp4` |

All 30 fps, H.264 High, yuv420p, CRF 16, AAC-LC 320 kb/s 48 kHz stereo. Render picture silent,
render score WAV (`score.md`), mux with `ffmpeg -i video.mp4 -i score.wav -map 0:v -map 1:a -c:v copy
-c:a aac -b:a 320k` (no `-shortest`; both are exactly the film length). The teaser's three aspects
share one timeline module and one WAV; only layout CSS differs.

Footage: one VHS recording (`recording.md`) feeds every film. Each film's footage times are written as
**cues** (named screen strings), resolved to clip seconds in `v2/recording/cues.json` after recording.

## 8. v1 → v2 changes

| v1 | v2 |
|---|---|
| Invented teal→violet gradient `#5cc8bb → #9b8cff` on the owl and wordmark | Brand tokens only; real SVG marks (`hoocode.svg`, `symbol.svg`); owl in white with cyan eyes per `owl.ans`. Drop the `gradient` key from `brand/brand.json`. |
| Footage 1600x900 shrunk into a window ~1280 px wide; text ~13 px | Recorded 2880x1620 @ FontSize 40, full-bleed; punch-ins up to 2.0x on four cues |
| macOS traffic-light window bar, starfield, "MISSION CONTROL" T-3 countdown | Removed. The film opens on the owl and the typed task. |
| Captions below the frame ("01 plans the mission") | Verb plate over footage, timed to the cue: `plans.` `asks.` `tests.` `lands.` |
| Teaser: brand only, no product footage, content in the top 40% of 9:16 | Teaser uses real footage crops in a 1000 px window filling the middle of the frame; layouts per aspect |
| Only 9:16 teaser | 9:16, 1:1, 16:9 from one timeline |
| 45 s trailer, flat pacing (21 s of 1x footage, 5 s still hold) | 60 s + 30 s; footage speed-ramped to the bar grid; one tension-release (red test → green) |
| No audio | Original synthesized score at 120 BPM, D minor → D major, plus SFX; -14 LUFS, -1 dBTP |
| Scenario: plan, read, edit, test, land | Adds a real red→green loop (first test run fails, model fixes, re-run passes) and shows the `a` always key |
| Feature claims: "one static binary / any model provider" only | Eight verified feature cards (section 6) |
