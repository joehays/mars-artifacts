#!/bin/bash
#
# Check which browsers are available for mermaid-cli
#

echo "🔍 Checking for Chrome/Chromium browsers..."
echo ""

FOUND=0

# Check common paths
for path in \
    /usr/bin/google-chrome-stable \
    /usr/bin/google-chrome \
    /usr/bin/chromium-browser \
    /usr/bin/chromium \
    /snap/bin/chromium \
    /opt/google/chrome/chrome \
    /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome
do
    if [ -x "$path" ]; then
        echo "✅ Found: $path"
        VERSION=$("$path" --version 2>/dev/null || echo "unknown")
        echo "   Version: $VERSION"
        FOUND=1
    fi
done

# Check PATH
for cmd in google-chrome-stable google-chrome chromium-browser chromium; do
    if command -v $cmd &> /dev/null; then
        LOCATION=$(command -v $cmd)
        echo "✅ Found in PATH: $cmd → $LOCATION"
        VERSION=$($cmd --version 2>/dev/null || echo "unknown")
        echo "   Version: $VERSION"
        FOUND=1
    fi
done

echo ""

if [ $FOUND -eq 0 ]; then
    echo "❌ No Chrome/Chromium browser found!"
    echo ""
    echo "To install on Ubuntu/Debian:"
    echo "  sudo apt-get install google-chrome-stable"
    echo "  # OR"
    echo "  sudo apt-get install chromium-browser"
    echo ""
    echo "To install on macOS:"
    echo "  brew install --cask google-chrome"
    echo "  # OR"
    echo "  brew install chromium"
    exit 1
else
    echo "✅ At least one browser is available for mermaid-cli!"
fi
