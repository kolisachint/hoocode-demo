# HooCode teaser, 15 s (Huashu Motion)

## Format
- Primary: 1080 x 1920 vertical, 30 fps, exactly 15.0 s, no soundtrack.
- Optional variant: 1080 x 1080 (1:1) via `om fork teaser teaser-square --size 1080x1080`. Not rendered yet; the layout needs its own pass.
- No "Made with huashu-motion" line (`data-om-signature="off"`).

## Brand rules
- Brand only. Do not imitate or mock the HooCode TUI: no terminal windows, panes, prompts or mock output.
- Wordmark, 3 text rows, rendered as a 14 x 6 pixel grid, one cell per quadrant:
  ```
  ▟▀▀▀▀▀▙
  ▌▟▙ ▟▙▐
  ▜▄▄▄▄▄▛
  ```
  Gradient by glyph column, #5cc8bb to #9b8cff.
- Colours: background #09090B, ink #FAFAFA, muted #A1A1AA, accent #00F0FF, rule #27272A.
- Type: a mono face (JetBrains Mono, OFL) for the name, version, tagline and install command; Inter (sans, 800/900) for the headline words.
- Copy: name `hoocode`, version `v0.2.20`, tagline "A terminal coding agent, written in Rust.", promise "nothing applied without your say-so.".

## Beats
| Time | Beat | Content |
|---|---|---|
| 0.0 - 3.0 s | Owl wordmark | Pixels snap in row by row behind a cyan scan line, with two glitch bursts. Frame 0 already shows the ghosted owl (poster). |
| 3.0 - 7.0 s | Kinetic verbs | "plans." (3.0), "asks." (4.33), "lands." (5.66). Each punches in from 1.34x scale and hard-cuts out. Full stop in cyan. |
| 7.0 - 11.0 s | Binary | "one static binary" / "any model provider" rise in; accent rule above. |
| 11.0 - 15.0 s | Closer | Wordmark shrinks to top centre; "hoocode v0.2.20"; tagline; install box with the command typed out; promise line. Hold to 15.0. |

Install command (typed in the box, 12.95 - 13.85 s):
```
$ curl -fsSL
https://kolisachint.github.io/hoocode/install.sh | sh
```

## Out of scope
- No music or sound effects (the brief does not ask for them). Add with `om sound` if wanted.
- No narration.
- No product screenshots: the brand has no logo file in this branch, only the glyph spec (`brand/wordmark.txt`).
