#!/usr/bin/env bash
# Broken-link scan for docs/. Resolves every local href/src and reports
# any that don't exist on disk. External URLs are listed but not fetched
# (avoids flaky network failures and rate limits).
#
# Usage: bash tests/check-links.sh
# Exit: 0 if all local links resolve, 1 otherwise.

set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DOCS="$ROOT/docs"

if [[ ! -d "$DOCS" ]]; then
  echo "✗ docs/ not found at $DOCS"
  exit 1
fi

cd "$DOCS"

broken=0
checked=0
external=0

# Find all HTML files
mapfile -t html_files < <(find . -name '*.html' -not -path './node_modules/*' | sort)

for f in "${html_files[@]}"; do
  dir=$(dirname "$f")
  # Extract href and src attributes
  # Strip <script>...</script> blocks so we don't match URLs inside JS string literals.
  body=$(awk '/<script[^>]*>/{inscript=1; next} /<\/script>/{inscript=0; next} !inscript' "$f")
  while IFS= read -r raw; do
    # raw is the URL value
    url="$raw"
    # Strip fragments and query strings for filesystem check
    path="${url%%#*}"
    path="${path%%\?*}"

    # Skip empty, javascript:, mailto:, tel:
    if [[ -z "$path" ]]; then continue; fi
    case "$path" in
      javascript:*|mailto:*|tel:*|data:*) continue ;;
      http://*|https://*|//*) external=$((external + 1)); continue ;;
    esac

    checked=$((checked + 1))

    # Resolve relative to the file's directory
    if [[ "$path" == /* ]]; then
      resolved="$DOCS$path"
    else
      resolved="$DOCS/${dir#./}/$path"
    fi
    # Normalize
    resolved=$(cd "$(dirname "$resolved")" 2>/dev/null && pwd)/$(basename "$resolved") || resolved="$resolved"

    if [[ ! -e "$resolved" ]]; then
      echo "✗ $f → $url"
      broken=$((broken + 1))
    fi
  done < <(echo "$body" | grep -oE '(href|src)="[^"]+"' | sed -E 's/^(href|src)="([^"]+)"$/\2/')
done

echo ""
echo "─────────────────────────────────────"
echo "Local links checked: $checked"
echo "External (skipped): $external"
echo "Broken: $broken"

if [[ $broken -gt 0 ]]; then
  exit 1
fi
exit 0
