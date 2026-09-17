#!/usr/bin/env bash
set -euo pipefail
TASK_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
QMD_RUN="$TASK_ROOT/scripts/qmd.sh"
if TASK_STATE="$("$QMD_RUN" collection show context 2>/dev/null)"; then
  TASK_STORED_PATH="$(printf '%s\n' "$TASK_STATE" | sed -n 's/^  Path: *//p')"
  [[ "$TASK_STORED_PATH" == "$TASK_ROOT" ]] || { echo "This index points at another folder: $TASK_STORED_PATH" >&2; exit 1; }
else
  "$QMD_RUN" collection add "$TASK_ROOT" --name context --mask '**/*.md'
fi
"$QMD_RUN" context add qmd://context 'Author context, writing sources and content strategy. Stub pages contain prompts, not facts.'
echo 'Search with: ./context/scripts/qmd.sh search backstory -c context'
