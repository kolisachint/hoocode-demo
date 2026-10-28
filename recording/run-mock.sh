#!/usr/bin/env bash
# Run the real hoocode binary against the scripted mock LLM (recording/scenario.json),
# in recording/sample-repo. Same setup as scripts/demo/record.py: a throwaway HOME with a
# models.json for provider "demo" (api openai-completions, pointing at mockllm.py),
# the same env, and the same argv. Only the model is scripted; tools run for real.
#
# Usage:  recording/run-mock.sh [hoocode args...]
#         recording/run-mock.sh "Add a --json flag to the stats command"
#
# Env:    HOOCODE_BIN  binary to run (default: hoocode on PATH)
#         HOOCODE_SRC  hoocode source clone, for scripts/tui/mockllm.py
#                      (default /home/user/kolisachint/hoocode; never modified)
#         SCENARIO     scenario file (default recording/scenario.json; v2 uses
#                      v2/recording/scenario.json)
#         TOOLBOX=1    run in a copy of the sample at $HOME/toolbox (the TUI then shows
#                      ~/toolbox instead of the repo path). Default: run in recording/sample-repo.
set -euo pipefail

DEMO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SAMPLE_DIR="$DEMO_DIR/sample-repo"
SCENARIO="${SCENARIO:-$DEMO_DIR/scenario.json}"
TOOLBOX="${TOOLBOX:-0}"
HOOCODE_SRC="${HOOCODE_SRC:-/home/user/kolisachint/hoocode}"
MOCKLLM="$HOOCODE_SRC/scripts/tui/mockllm.py"
HOOCODE_BIN="${HOOCODE_BIN:-hoocode}"
REAL_HOME="${HOME:-/root}"

for tool in python3 cargo; do
  command -v "$tool" >/dev/null || { echo "run-mock.sh needs $tool on PATH" >&2; exit 1; }
done
[[ -f "$MOCKLLM" ]] || { echo "mockllm.py not found at $MOCKLLM (set HOOCODE_SRC)" >&2; exit 1; }
[[ -f "$SCENARIO" ]] || { echo "scenario not found: $SCENARIO" >&2; exit 1; }

WORK="$(mktemp -d "${TMPDIR:-/tmp}/hoocode-demo-XXXXXX")"
MOCK_PID=""
cleanup() {
  if [[ -n "$MOCK_PID" ]]; then
    kill "$MOCK_PID" 2>/dev/null || true
    wait "$MOCK_PID" 2>/dev/null || true
  fi
  rm -rf "$WORK"
}
trap cleanup EXIT

# With TOOLBOX=1 the sample is copied to $WORK/home/toolbox (HOME is $WORK/home in the
# run below), so the working folder shows as ~/toolbox. The copy is made before `prepare`,
# so the build happens in the same folder the run uses.
RUN_DIR="$SAMPLE_DIR"
if [[ "$TOOLBOX" == "1" ]]; then
  mkdir -p "$WORK/home"
  cp -R "$SAMPLE_DIR" "$WORK/home/toolbox"
  RUN_DIR="$WORK/home/toolbox"
fi

# Phase 1: scenario -> mock script, settings, and the `prepare` commands (build once,
# outside the recording). Mirrors record.py's prepare step, with cargo's home kept real.
python3 - "$SCENARIO" "$WORK" "$RUN_DIR" prepare "$REAL_HOME" <<'PY'
import json, os, subprocess, sys
from pathlib import Path

scenario, work, sample, _, real_home = sys.argv[1:6]
sc = json.loads(Path(scenario).read_text())
work, sample = Path(work), Path(sample)
Path(work / "llm-script.json").write_text(json.dumps(sc["llm"]))

home = work / "home"
cfg = home / ".hoocode"
cfg.mkdir(parents=True)
# Same as record.py: no tips or update notices, no semantic index.
(cfg / "settings.json").write_text(json.dumps({"tips": {"enabled": False}, "enableSemanticIndex": False}, indent=2))

env = {
    "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
    "RUSTUP_HOME": os.environ.get("RUSTUP_HOME", str(Path(real_home) / ".rustup")),
    "CARGO_HOME": os.environ.get("CARGO_HOME", str(Path(real_home) / ".cargo")),
    "CARGO_TARGET_DIR": str(work / "cargo-target"),
}
for cmd in sc.get("prepare") or []:
    subprocess.run(cmd, cwd=sample, env={**os.environ, **env, "HOME": real_home}, check=True, capture_output=True)
PY

# Phase 2: the mock LLM on a free port (--port 0), then its port into models.json.
python3 "$MOCKLLM" --script "$WORK/llm-script.json" --port 0 --port-file "$WORK/llm-port" \
  --chunk-size 3 --log "$WORK/requests.jsonl" >/dev/null 2>&1 &
MOCK_PID=$!
for _ in $(seq 1 100); do
  [[ -s "$WORK/llm-port" ]] && break
  sleep 0.05
done
[[ -s "$WORK/llm-port" ]] || { echo "mock LLM did not start" >&2; exit 1; }
PORT="$(cat "$WORK/llm-port")"

python3 - "$SCENARIO" "$WORK" "$PORT" <<'PY'
import json, sys
from pathlib import Path

scenario, work, port = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
model = json.loads(Path(scenario).read_text())["model"]
doc = {
    "providers": {
        model["provider"]: {
            "baseUrl": f"http://127.0.0.1:{port}/v1",
            "api": "openai-completions",
            "apiKey": "demo-key",
            "models": [{"id": model["id"], "name": model["name"], "contextWindow": 200000, "maxTokens": 8192}],
        }
    }
}
(work / "home" / ".hoocode" / "models.json").write_text(json.dumps(doc, indent=2))
PY

# Phase 3: the real binary, with record.py's env (nothing else inherited) and argv.
# Not `exec`: the cleanup trap must run to stop the mock when hoocode exits.
cd "$RUN_DIR"
set +e
env -i \
  HOME="$WORK/home" \
  PATH="${PATH}" \
  TERM=xterm-256color \
  COLORTERM=truecolor \
  LANG=C.UTF-8 \
  LC_ALL=C.UTF-8 \
  TZ=UTC \
  HOOCODE_OFFLINE=1 \
  HOOCODE_CODING_AGENT_DIR="$WORK/home/.hoocode" \
  RUSTUP_HOME="${RUSTUP_HOME:-$REAL_HOME/.rustup}" \
  CARGO_HOME="${CARGO_HOME:-$REAL_HOME/.cargo}" \
  CARGO_TARGET_DIR="$WORK/cargo-target" \
  "$HOOCODE_BIN" --offline --provider demo --model scripted-demo "$@"
status=$?
set -e
exit "$status"
