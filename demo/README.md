# HooCode demo assets

Launch-demo assets for HooCode, a ratatui-based terminal coding agent.

Files:

- `hoocode.tape`: VHS script that records the terminal demo to `out/hoocode.mp4` and `out/hoocode.gif`.
- `storyboard.md`: 45s launch film storyboard and a 15s social teaser cut list.
- `film/index.html`: HyperFrames-style composition (GSAP timeline, 1920x1080) that wraps the clip.
- `out/`: generated video and GIF (create with `mkdir -p demo/out`).

## Prerequisites

- VHS >= 0.8 (`Wait+Screen` needs it). Install with `go install github.com/charmbracelet/vhs@latest` or `brew install vhs`. VHS needs `ttyd` and `ffmpeg` on PATH.
- The `hoo` binary on PATH (placeholder name, see TODO).
- A sample repo at `demo/sample-repo` (not created yet, see TODO).

## Run it

1. Record the terminal demo from the repo root:

   ```sh
   mkdir -p demo/out
   vhs demo/hoocode.tape
   ```

2. Preview the film in a browser:

   ```sh
   npx serve demo -l 5055
   # open http://localhost:5055/film/index.html
   # add ?autoplay to play on load; click or Space toggles play
   ```

3. Render the film with HyperFrames: TBD. The exact command and flags still need to be taken from the HyperFrames docs.

4. Re-run step 1 for each release, then re-render the film.

## TODO and assumptions

Everything below is a placeholder or guess. Fix these before recording the final version.

**Product facts**

- [ ] Binary name is `hoo`. Used in `hoocode.tape` (`Require hoo`, `Type "hoo"`) and the README.
- [ ] Install command is `curl -fsSL https://hoocode.dev/install.sh | sh`. Used in `film/index.html` and `storyboard.md`.
- [ ] Version is `v0.1.25`. Shown in the film outro and the teaser end card.
- [ ] Brand spelling and wordmark `HOO` are placeholders. Check the logo and brand name.
- [ ] Product name appears as "HooCode" everywhere. Confirm the capitalization.

**Keybindings and UI text (VHS tape)**

- [ ] Enter submits a prompt.
- [ ] Enter approves the plan. The approve key is a guess.
- [ ] Ctrl+C quits. Replace with the real quit key or slash command.
- [ ] Screen strings the tape waits on: `/Plan/`, `/tests passed/`, `/Pull request/`. Confirm the real UI text.
- [ ] The app starts from a bash prompt with no login or API key setup on screen. If it needs a key or sign-in, add setup steps to the hidden section of the tape.

**Sample repo and tasks**

- [ ] `demo/sample-repo` does not exist. Create a small Rust crate with a `stats` subcommand and passing `cargo test`. Without it, the tape fails at `cd`.
- [ ] Task 1 prompt: "Add a --json output flag to the stats command". Edit it in `hoocode.tape`. Film captions do not repeat it.
- [ ] Task 2 is the agent run: edit files, then `cargo test` passes. Compile time may need a longer `Wait+Screen@90s` timeout.
- [ ] Task 3 prompt: "Open a pull request with these changes". The tape assumes the PR opens inside the TUI and shows a URL. The PR will target a real remote. Use a throwaway repo or a sandbox account. Do not run this against a real project.
- [ ] Clip footage is about 25s. Re-check the film timings if you change the tape.

**Film and HyperFrames**

- [ ] HyperFrames render CLI command and flags are unknown. Check the HyperFrames docs for the render command, viewport (1920x1080 assumed), fps, and how the composition is handed to the renderer. The HTML has a comment on this.
- [ ] `?autoplay` plays the timeline on load. Without it the timeline starts paused. This is my reading of the spec.
- [ ] The `data-composition-id` and `data-duration="45"` attributes follow the spec. Confirm the exact HyperFrames attribute names.
- [ ] The video is driven by a `currentTime` tween, so it never plays on its own. Confirm this works in the HyperFrames renderer.
- [ ] Captions and countdown copy are drafts.

**Teaser (Huashu Motion)**

- [ ] Remove the "Made with huashu-motion" credit, as requested. Before publishing, check the Huashu Motion license for any attribution it requires.
- [ ] Do not imitate the HooCode UI in the teaser. The storyboard says so, but the cut list has not been reviewed against it.

**Tooling**

- [ ] `demo/out/` must exist before recording.
- [ ] `vhs validate demo/hoocode.tape` passes (checked with VHS installed via `go install`). The tape has not been recorded yet: `ttyd`, `ffmpeg`, and a real `hoo` binary are not set up, and the sample repo is missing. Expect timing and `Wait+Screen` timeouts to need tuning on the first real run.
