#!/usr/bin/env bash
# Restore demo/sample-repo to the committed state, so a re-recording starts from the
# same file. Only tracked files are restored; build output (target/) is git-ignored.
set -euo pipefail
ROOT="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)"
cd "$ROOT"
git checkout -- demo/sample-repo
