# HooCode teaser (15 s, Huashu Motion)

A 15-second vertical (1080 x 1920) social teaser for HooCode, built as a [Huashu Motion](https://github.com/alchaincyf/huashu-motion) film: one `index.html` (HTML + GSAP), no build step, no network at render time.

- Brief and beat sheet: `brief.md`
- Conventions used, and what the tool needs: `NOTES.md`
- Output: `../out/teaser-9x16.mp4` (1080 x 1920, 30 fps, 15.0 s, no soundtrack)

## Edit it

Huashu Motion is an agent skill plus the `om` CLI. To install the skill for Claude Code:

```sh
npx skills add alchaincyf/huashu-motion -a claude-code
```

Then open the studio on this folder and point at the frame to comment:

```sh
om studio teaser            # live preview, direct edits, frame comments
```

Editable without touching code: the copy (`name`, `version`, `verb1-3`, `binaryA/B`, `tagline`, `installA/B`, `promise`) and the colours are declared as composition variables on `<html>` in `index.html`. `om set key=value teaser` changes a default. Timing is in the timeline near the bottom of `index.html`.

## Render

```sh
export OM_CHROME=/path/to/chrome    # only if Chrome is not in a standard place
om check teaser                     # structure, motion rules, sampled frames
om still teaser --at 1,5,9,13,14.5  # PNG stills to look at
om render teaser --silent           # -> teaser/out/teaser-v1.mp4
```

Needs Node 22+, FFmpeg and a Chrome/Chromium. `om doctor` reports what is missing. The 1:1 variant is `om fork teaser teaser-square --size 1080x1080`. Fork re-lays the film out, so review it after forking.

## Credit line

Huashu Motion adds a small "Made with huashu-motion" to the last 1.2 s of films of 4 s or more. It is switched off here with `data-om-signature="off"` on the root `<div id="film">`, as requested. Keep that attribute if you edit or re-export the film. The skill's own guidance keeps the credit on fan-made films, so turn it off only when the film is your own brand's work.

## Fonts and licences

Inter (variable) and JetBrains Mono are bundled in `assets/fonts/`, both SIL Open Font License 1.1. See `assets/fonts/LICENSES.md`. GSAP is bundled in `vendor/gsap.min.js` (GreenSock standard licence; see `vendor/GSAP-LICENSE.txt`). `vendor/om.js` comes from the huashu-motion runtime (MIT).
