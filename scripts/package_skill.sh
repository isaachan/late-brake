#!/bin/bash
#
# Package late-brake as OpenClaw skill to dist/ directory
#
# Follows OpenClaw skill structure requirements:
# dist/late-brake/
# ├── SKILL.md              # Skill metadata and docs
# ├── references/           # referenced documentation
# └── scripts/              # late_brake source code (directly here)

set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST="$ROOT/dist/late-brake"

echo "🚀 Packaging late-brake as OpenClaw skill..."

# Clean dist
rm -rf "$DIST"
mkdir -p "$DIST"
echo "Cleaned dist directory: $DIST"

# Copy root SKILL.md
cp "$ROOT/SKILL.md" "$DIST/"
echo "✅ Copied SKILL.md"

# Copy references (docs referenced in SKILL.md)
mkdir -p "$DIST/references"
cp "$ROOT/docs/compare-json-schema.md" "$DIST/references/"
cp "$ROOT/docs/data-format.md" "$DIST/references/"
cp "$ROOT/docs/track-format.md" "$DIST/references/"
cp "$ROOT/docs/vbo-format.md" "$DIST/references/"
echo "✅ Copied references/"

# Copy source code directly to scripts/
mkdir -p "$DIST/scripts"
cp -r "$ROOT/src/"* "$DIST/scripts/"
find "$DIST/scripts/" -name "*.pyc" -delete
rm -rf "$DIST/scripts/late_brake.egg-info"
echo "✅ Copied source to scripts/"

# Verify package
echo
echo "✅ Verification - checking required files:"
MISSING=0

CHECK_FILES=(
    "$DIST/SKILL.md"
    "$DIST/references/compare-json-schema.md"
    "$DIST/scripts/late_brake/cli.py"
)

for f in "${CHECK_FILES[@]}"; do
    if [ -f "$f" ]; then
        echo "   ✓ $f"
    else
        echo "   ✗ $f - MISSING"
        MISSING=$((MISSING+1))
    fi
done

if [ $MISSING -ne 0 ]; then
    echo
    echo "❌ Verification failed - $MISSING files missing"
    exit 1
fi

echo
echo "✅ Package verification passed"
echo "📦 Package location: $DIST"
echo "📋 Structure:"
find "$DIST" -type f | sort | sed -e "s|$DIST/|  |" | awk -F/ 'BEGIN {prev=""} {
    for (i=1; i<=NF-1; i++) {
        if ($i != prev) {
            printf "%s%s/\n", substr("    ", 1, 2*(i-1)), $i
            prev = $i
        }
    }
    printf "%s%s\n", substr("    ", 1, 2*(NF-1)), $NF
}'

echo
echo "🎉 Packaging completed successfully!"
echo
echo "Next steps:"
echo "  ./scripts/publish_skill.sh <version> [changelog]"
