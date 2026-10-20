#!/bin/sh
# Bundle scene.js (three.js modules) into 1 classic script, because module scripts
# do not load from file://, then render the still (1x, 2x and a phone preview).
#   ./build.sh [page.html]   default scene.html; pass scene-x.html for an X variant
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
PAGE=${1:-scene.html}
npx --yes esbuild@0.24.0 "$HERE/scene.js" --bundle --format=iife --minify \
  --alias:three="$HERE/vendor/three.module.min.js" --outfile="$HERE/scene.bundle.js"
node "$HERE/render.mjs" "$PAGE"
