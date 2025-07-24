#!/usr/bin/env bash
# File: fetch-icons.sh
# Usage: bash fetch-icons.sh
# Looks for “shield” (or “security”), “search”, “lock”, and “info”
# icons under /usr/share/icons and /usr/share/pixmaps (SVG or PNG),
# then copies them into frontend/icons/<name>.png
# Finally, adjusts permissions so nothing remains “locked.”

set -e

TARGET_DIR="/home/ncterry/Desktop/ai-cookbook/UserInterfaceXXX/frontend/icons"
mkdir -p "$TARGET_DIR"

declare -A ICON_NAMES=(
  [shield]="shield"
  [search]="search"
  [lock]="lock"
  [info]="info"
)

# Where to look for icons
SEARCH_PATHS=(
  /usr/share/icons
  /usr/share/pixmaps
)

for key in "${!ICON_NAMES[@]}"; do
  name="${ICON_NAMES[$key]}"
  echo -n "🔍 Finding icon for '$key'… "

  # Build patterns (shield also checks for “security”)
  if [[ "$key" == "shield" ]]; then
    PATTERNS=( -iname "*shield*.svg" -o -iname "*security*.svg" -o -iname "*shield*.png" -o -iname "*security*.png" )
  else
    PATTERNS=( -iname "*${key}*.svg" -o -iname "*${key}*.png" )
  fi

  # Find first match
  file=$(find "${SEARCH_PATHS[@]}" -type f \( "${PATTERNS[@]}" \) | head -n1)

  if [[ -z "$file" ]]; then
    echo "⚠️  none found"
    continue
  fi

  ext="${file##*.}"
  out="$TARGET_DIR/${name}.png"

  if [[ "$ext" == "svg" ]]; then
    if command -v convert >/dev/null 2>&1; then
      convert -background none "$file" -resize 32x32 "$out"
      echo "✅ converted SVG → $out"
    else
      cp "$file" "$out"
      echo "✅ copied SVG → $out (as .png)"
    fi
  else
    cp "$file" "$out"
    echo "✅ copied PNG → $out"
  fi

  # Ensure the copied file is user-writable and world-readable
  chmod 644 "$out"
done

# Ensure the icons directory is user-writable and listable by others
chmod 755 "$TARGET_DIR"

echo "🎉 Done. Your icons are in $TARGET_DIR with open permissions."
