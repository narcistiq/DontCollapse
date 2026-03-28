#!/usr/bin/env bash
set -euo pipefail

CONFIG_PATH="${1:-stitch/stitch.config.sh}"

if [[ ! -f "$CONFIG_PATH" ]]; then
  echo "Config file not found: $CONFIG_PATH" >&2
  exit 1
fi

# shellcheck source=/dev/null
source "$CONFIG_PATH"

if [[ -z "${SCREEN_IMAGE_URL:-}" || -z "${SCREEN_CODE_URL:-}" ]]; then
  echo "Missing Stitch hosted URLs in $CONFIG_PATH" >&2
  echo "Set SCREEN_IMAGE_URL and SCREEN_CODE_URL, then run again." >&2
  exit 1
fi

SCREEN_DIR="$OUTPUT_ROOT/$SCREEN_ID"
mkdir -p "$SCREEN_DIR"

echo "Downloading screen image..."
curl -L "$SCREEN_IMAGE_URL" -o "$SCREEN_DIR/$SCREEN_IMAGE_FILE"

echo "Downloading screen code package..."
curl -L "$SCREEN_CODE_URL" -o "$SCREEN_DIR/$SCREEN_CODE_FILE"

cat >"$SCREEN_DIR/metadata.txt" <<EOF
PROJECT_TITLE=$PROJECT_TITLE
PROJECT_ID=$PROJECT_ID
SCREEN_NAME=$SCREEN_NAME
SCREEN_ID=$SCREEN_ID
EOF

echo "Done. Files saved to: $SCREEN_DIR"
