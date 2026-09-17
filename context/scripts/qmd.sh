#!/usr/bin/env bash
# Isolate every client checkout and use qmd's matching Node installation.
set -euo pipefail
TASK_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
TASK_INDEX="$(python3 -c 'import hashlib,sys; print("content-engine-"+hashlib.sha256(sys.argv[1].encode()).hexdigest()[:16])' "$TASK_ROOT")"
if [[ "${1:-}" == "--print-index" ]]; then
  printf '%s\n' "$TASK_INDEX"
  exit 0
fi
QMD_COMMAND="$(command -v qmd)" || { echo "qmd is not installed. Use rg until it is available." >&2; exit 127; }
QMD_ENTRY="$(python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$QMD_COMMAND")"
QMD_PREFIX="${QMD_ENTRY%%/lib/node_modules/*}"
QMD_NODE="$QMD_PREFIX/bin/node"
if [[ -x "$QMD_NODE" ]]; then
  export PATH="$(dirname "$QMD_NODE"):$PATH"
  exec "$QMD_NODE" "$QMD_ENTRY" --index "$TASK_INDEX" "$@"
fi
exec "$QMD_COMMAND" --index "$TASK_INDEX" "$@"
