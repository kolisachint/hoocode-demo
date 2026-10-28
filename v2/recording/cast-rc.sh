# Shell rc for the v2 asciinema take (v2/recording/record_cast.py). Sourced by
# `bash --rcfile` inside asciinema, so the setup is never part of the cast: the first
# frame is the clean `$ ` prompt. Not for interactive use.
DEMO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export TERM=xterm-256color COLORTERM=truecolor
export SCENARIO="$DEMO/v2/recording/scenario.json" TOOLBOX=1
export HOOCODE_BIN="${HOOCODE_BIN:-/home/user/hoocode/target/release/hoocode}"
export HOOCODE_SRC="${HOOCODE_SRC:-/home/user/hoocode}"
export HISTFILE=/dev/null
cd "$DEMO/recording/sample-repo" || exit 1
PS1='$ '
hoocode() { "$DEMO/recording/run-mock.sh" "$@"; }
