#!/bin/sh
# Encode captured frames: the MP4 for a LinkedIn video post and a GIF under 5 MB.
#   ./encode.sh <frames-dir> <name> [fps=25] [gif-fps=15] [gif-width=720]
# For a full-size GIF use gif-fps 16 and gif-width 1080; check the size, cut colours if over 5 MB.
set -e
DIR=$1; NAME=$2; FPS=${3:-25}; GFPS=${4:-15}; GW=${5:-720}
[ -n "$DIR" ] && [ -n "$NAME" ] || { echo "usage: ./encode.sh <frames-dir> <name> [fps] [gif-fps] [gif-width]"; exit 1; }
OUT="$(cd "$(dirname "$0")" && pwd)/output"; mkdir -p "$OUT"
ffmpeg -y -loglevel error -framerate "$FPS" -i "$DIR/f%04d.png" -vf "scale=1080:1350:flags=lanczos" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -movflags +faststart "$OUT/$NAME.mp4"
ffmpeg -y -loglevel error -framerate "$FPS" -i "$DIR/f%04d.png" \
  -vf "fps=$GFPS,scale=$GW:-1:flags=lanczos,split[a][b];[a]palettegen=stats_mode=full:max_colors=200[p];[b][p]paletteuse=dither=sierra2_4a:diff_mode=rectangle" \
  "$OUT/$NAME.gif"
ls -lh "$OUT/$NAME.mp4" "$OUT/$NAME.gif"
