#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# build-assets.sh — generate Carnet PWA icons + OG image from SVG/HTML masters
# Uses headless Chrome as rasterizer (no rsvg-convert / ImageMagick needed).
#
# Outputs:
#   icons/icon-{32,72,96,128,144,152,180,192,384,512}.png  (square, ink bg)
#   og.png                                                  (1200×630)
#
# Run from frontend/ root:  ./tools/build-assets.sh
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TOOLS="$ROOT/tools"
ICONS="$ROOT/icons"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
if [ ! -x "$CHROME" ]; then
  echo "✗ Chrome not found at $CHROME" >&2
  exit 1
fi

mkdir -p "$ICONS"

# ─────────── PWA icons ───────────
SVG_ICON="$TOOLS/icon-master.svg"
[ -f "$SVG_ICON" ] || { echo "✗ missing $SVG_ICON" >&2; exit 1; }

SVG_DATA=$(base64 -i "$SVG_ICON" | tr -d '\n')

for SIZE in 32 72 96 128 144 152 180 192 384 512; do
  HTML="$TMP/icon-$SIZE.html"
  OUT="$ICONS/icon-$SIZE.png"
  cat > "$HTML" <<EOF
<!DOCTYPE html><html><head><style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:${SIZE}px;height:${SIZE}px;overflow:hidden;background:#0A0A0A}
img{display:block;width:${SIZE}px;height:${SIZE}px}
</style></head><body><img src="data:image/svg+xml;base64,${SVG_DATA}"/></body></html>
EOF
  "$CHROME" --headless --disable-gpu --hide-scrollbars \
    --window-size=${SIZE},${SIZE} \
    --screenshot="$OUT" \
    --default-background-color=00000000 \
    "file://$HTML" 2>/dev/null
  printf "  ✓ icon-%s.png  (%s bytes)\n" "$SIZE" "$(stat -f%z "$OUT")"
done

# ─────────── OG image ───────────
HTML_OG="$TOOLS/og-master.html"
[ -f "$HTML_OG" ] || { echo "✗ missing $HTML_OG" >&2; exit 1; }

OG_OUT="$ROOT/og.png"
"$CHROME" --headless --disable-gpu --hide-scrollbars \
  --window-size=1200,630 \
  --screenshot="$OG_OUT" \
  --virtual-time-budget=4000 \
  "file://$HTML_OG" 2>/dev/null

printf "  ✓ og.png       (%s bytes, 1200×630)\n" "$(stat -f%z "$OG_OUT")"

echo ""
echo "Done. Generated $(ls -1 "$ICONS"/icon-*.png | wc -l | tr -d ' ') icons + og.png."
