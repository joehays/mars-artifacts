#!/bin/bash
#
# Build Leadership Brief PDF with Mermaid diagrams
#
# Requirements:
#   - pandoc (markdown → LaTeX/PDF converter)
#   - lualatex (LaTeX engine with emoji support)
#   - mermaid-filter (Mermaid diagram support via NPM)
#   - mermaid-cli (mmdc command for diagram rendering)
#   - google-chrome-stable (for mermaid-cli to render diagrams)
#
# Install:
#   npm install -g mermaid-filter
#   npm install -g @mermaid-js/mermaid-cli
#   apt-get install google-chrome-stable

# Configure puppeteer to use system Chrome/Chromium
# Try multiple common browser locations (works on both container and host)
if [ -x /usr/bin/google-chrome-stable ]; then
    export PUPPETEER_EXECUTABLE_PATH=/usr/bin/google-chrome-stable
elif [ -x /usr/bin/google-chrome ]; then
    export PUPPETEER_EXECUTABLE_PATH=/usr/bin/google-chrome
elif [ -x /usr/bin/chromium-browser ]; then
    export PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser
elif [ -x /usr/bin/chromium ]; then
    export PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium
elif command -v google-chrome-stable &> /dev/null; then
    export PUPPETEER_EXECUTABLE_PATH=$(command -v google-chrome-stable)
elif command -v google-chrome &> /dev/null; then
    export PUPPETEER_EXECUTABLE_PATH=$(command -v google-chrome)
elif command -v chromium-browser &> /dev/null; then
    export PUPPETEER_EXECUTABLE_PATH=$(command -v chromium-browser)
elif command -v chromium &> /dev/null; then
    export PUPPETEER_EXECUTABLE_PATH=$(command -v chromium)
else
    echo "❌ Error: No Chrome/Chromium browser found!"
    echo "Please install one of: google-chrome, chromium-browser, chromium"
    exit 1
fi

echo "Using browser: $PUPPETEER_EXECUTABLE_PATH"

pandoc -f markdown+emoji \
  --pdf-engine=lualatex \
  --filter mermaid-filter \
  -L emoji-direct.lua \
  -H header.tex \
  -V monofont="DejaVu Sans Mono" \
  -V mainfont="DejaVu Serif" \
  -V geometry:top=0.75in \
  -V geometry:bottom=0.75in \
  -V geometry:left=0.75in \
  -V geometry:right=0.75in \
  LEADERSHIP_BRIEF_ORCHESTRATED_AI.md \
  -o orchestrated_ai_draft.pdf

echo "✅ PDF generated: orchestrated_ai_draft.pdf"

#  -L emoji-wrap.lua \
#pandoc -f markdown+emoji \
#  --pdf-engine=lualatex \
#  -L emoji-wrap.lua \
#  -V geometry:top=0.75in \
#  -V geometry:bottom=0.75in \
#  -V geometry:left=0.75in \
#  -V geometry:right=0.75in \
#  LEADERSHIP_BRIEF_ORCHESTRATED_AI.md \
#  -o orchestrated_ai_draft.pdf
