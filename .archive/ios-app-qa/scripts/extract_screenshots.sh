#!/bin/bash
# Extract PNG screenshots from the latest Xcode test result bundle
# Usage: extract_screenshots.sh <output_dir> [project_name]
#
# Example:
#   ./extract_screenshots.sh ./qa-screenshots MyApp

set -euo pipefail

OUTPUT_DIR="${1:?Usage: extract_screenshots.sh <output_dir> [project_name]}"
PROJECT="${2:-}"

mkdir -p "$OUTPUT_DIR"

# Find the latest xcresult
if [ -n "$PROJECT" ]; then
    RESULT=$(find ~/Library/Developer/Xcode/DerivedData/${PROJECT}-*/Logs/Test -name "*.xcresult" -type d 2>/dev/null | sort | tail -1)
else
    RESULT=$(find ~/Library/Developer/Xcode/DerivedData/*/Logs/Test -name "*.xcresult" -type d 2>/dev/null | sort | tail -1)
fi

if [ -z "$RESULT" ]; then
    echo "ERROR: No .xcresult found"
    exit 1
fi

echo "Result bundle: $RESULT"

# Extract all PNG files from Data directory
count=0
for f in "$RESULT"/Data/data.*; do
    if file -b "$f" 2>/dev/null | grep -qi "png"; then
        size=$(wc -c < "$f" | tr -d ' ')
        cp "$f" "$OUTPUT_DIR/img-${size}.png"
        count=$((count + 1))
    fi
done

echo "Extracted $count screenshots to $OUTPUT_DIR/"
ls -lhS "$OUTPUT_DIR/"*.png 2>/dev/null
