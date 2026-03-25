#!/bin/bash
#
# Publish packaged late-brake skill to ClawHub
#
# Usage:
#   ./scripts/publish_skill.sh [changelog message]
#
# Example:
#   ./scripts/publish_skill.sh "Initial release with core features"

set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST="$ROOT/dist/late-brake"
DEFAULT_CHANGELOG="Initial release of late-brake racing lap analysis skill"

CHANGELOG="${1:-$DEFAULT_CHANGELOG}"

# Check package exists
if [ ! -d "$DIST" ]; then
    echo "❌ Package directory not found: $DIST"
    echo "Run ./scripts/package_skill.sh first to build the package"
    exit 1
fi

# Check clawhub CLI
if ! command -v clawhub &> /dev/null; then
    echo "❌ clawhub CLI not found. Install with: npm i -g clawhub"
    exit 1
fi

echo "✅ Found clawhub: $(clawhub --cli-version)"
echo
echo "🚀 Publishing to ClawHub..."
echo "   Package: $DIST"
echo "   Changelog: $CHANGELOG"
echo

# Version is read from frontmatter in SKILL.md
clawhub publish "$DIST" --no-input --changelog "$CHANGELOG"

echo
echo "🎉 Published successfully!"
echo
echo "Install with: clawhub install late-brake"
