# Huashu Motion conventions (as used in this teaser)

Source read from the cloned skill (`alchaincyf/huashu-motion`, MIT, v0.3.1): `skills/huashu-motion/SKILL.md`, `references/contract.md`, `templates/blank/`, `cli/om.js`, `cli/lib/browser.js`, `runtime/om-engine.js`, `README.en.md`.

## Project shape

- One film = one folder. The folder holds exactly one composition `*.html` at its root (`index.html`). Drafts go in a subfolder.
- `vendor/gsap.min.js` (GSAP 3.14.2, bundled by the blank template) and `vendor/om.js` (runtime helpers: `OM.vars()`, `OM.sfx`, `OM.region`, ...). Both are copied in by `om new`. No CDN is used, so the film is self-contained.
- `assets/fonts/` holds the typefaces, declared with `@font-face` in `index.html`.
- `out/` (renders, `<name>-vN.mp4`, never overwritten) and `.om/` (history, inbox, render log) are written by the tools.

## Root element and size

```html
<div id="film" data-composition-id="film" data-width="1080" data-height="1920" data-fps="30" data-om-signature="off">
```

- `data-width` / `data-height` are the frame in px. Vertical 1080x1920 is the documented format. The render viewport comes from them. The 1:1 variant is `om fork <dir> <newdir> --size 1080x1080`. Fork re-layout lands in the inbox, so it needs its own pass. It was not rendered here.
- `data-fps` defaults to 30 if absent (`cli/lib/render.js`).
- No `data-duration` on the root. The film is as long as the paused timeline, which ends at 15.0 s via `tl.to({}, { duration: 0 }, 15)`.

## Timeline registration

```js
const tl = gsap.timeline({ paused: true });
...
window.__timelines['film'] = tl;   // key = data-composition-id
```

Everything is a function of time. No `Date.now()`, no `Math.random()` (use `OM.random(seed)` or a fixed hash), no network. The teaser uses a sin-hash for pixel jitter.

## Editable values

`data-composition-variables` on `<html>` is a JSON array. Types: `string`, `number` (min/max/step), `color`, `boolean`, `enum`. `group` sorts them in the studio.

- `data-var-text="id"` replaces an element's text.
- `var(--id)` in CSS; every scalar variable is a CSS custom property on the root (the colours here are used that way).
- `OM.vars()` in script, for data and logic.
- `data-om-var="id"` on a container whose text a script builds (the verbs, binary lines). This lets the studio edit it in place.

## Pointing, scenes, signature

- `data-om-id="name"` on anything a person might click. Keep ids stable.
- `tl.addLabel('scene:<id>', t)` labels are the studio's scene strip: `scene:mark`, `scene:verbs`, `scene:binary`, `scene:install`.
- The signature: a film of 4 s or more gets "Made with huashu-motion" for its last 1.2 s, unless the root or `<html>` has `data-om-signature="off"`. `data-om-signature="top-left"` (or another corner) pins it instead.

## Checks the tool runs

`om check` rules that shaped the file:
- Animate transforms and opacity (`x`, `y`, `scale`, `scaleX`, `yPercent`, `opacity`), never layout (`left`, `top`, `width`) during a tween. Static `left`/`top` placement is fine.
- Elements that are hidden by `opacity` still count as layout for coverage. Hidden layers (the binary-line beat) use `visibility: hidden`, and it is set to visible at 7.0 s.
- A reveal mask (`overflow: hidden` + `yPercent`) reports "text-clipped" mid-tween. The lines use opacity and rise instead.
- Decorative full-frame layers go before content in the DOM.

## Rendering

- `om doctor` checks Node, FFmpeg and Chrome.
- `om check <dir>` validates and samples frames. `om still <dir> --at 0,1,...` saves PNGs of the composition.
- `om render <dir> --silent` writes `<dir>/out/<name>-v1.mp4`. `--silent` suppresses the no-soundtrack warning (the brief has no music).
- The browser comes from `OM_CHROME` or an installed Chrome/Chromium. Here it is `OM_CHROME=/opt/pw-browsers/chromium`.
- Requirements: Node 22+ (`package.json` has no runtime deps, so no `npm install` is needed), FFmpeg, and a browser.

## Fonts

`om fonts` lists the bundled faces. It has no monospace face, so JetBrains Mono (OFL) was added from `@fontsource/jetbrains-mono@5.3.0` and declared by hand, the way the blank template declares its fonts. Inter comes from the bundle (`Inter-var.woff`).
