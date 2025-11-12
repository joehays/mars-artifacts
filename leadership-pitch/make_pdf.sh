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

# Configure puppeteer to use system Chrome
export PUPPETEER_EXECUTABLE_PATH=/usr/bin/google-chrome-stable

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
