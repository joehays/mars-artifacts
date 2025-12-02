#!/bin/bash
#
# Build Leadership Brief PDF with pre-generated PNG diagrams
#
# This script uses orchestrated_ai_presentation_final.md which has PNG image
# references instead of mermaid code blocks, avoiding the need for mermaid-filter
# and browser rendering (which has file access issues).
#
# Requirements:
#   - pandoc (markdown → LaTeX/PDF converter)
#   - lualatex (LaTeX engine with emoji support)
#   - Pre-generated PNG diagrams in diagrams/png/ directory
#
# To regenerate PNG diagrams (if needed):
#   python3 generate_pptx_diagrams.py

echo "📄 Building Leadership Brief PDF (using pre-generated PNG diagrams)..."
echo ""

# Check if source file exists
if [ ! -f "orchestrated_ai_presentation_final.md" ]; then
    echo "❌ Error: orchestrated_ai_presentation_final.md not found!"
    exit 1
fi

# Check if PNG diagrams exist
if [ ! -d "diagrams/png" ] || [ -z "$(ls -A diagrams/png/*.png 2>/dev/null)" ]; then
    echo "❌ Error: No PNG diagrams found in diagrams/png/"
    echo "Generate them with: python3 generate_pptx_diagrams.py"
    exit 1
fi

PNG_COUNT=$(ls diagrams/png/*.png 2>/dev/null | wc -l)
echo "✅ Found $PNG_COUNT PNG diagrams in diagrams/png/"
echo ""

echo "🔨 Building PDF with pandoc..."
pandoc -f markdown+emoji \
  --pdf-engine=lualatex \
  -L emoji-direct.lua \
  -H header.tex \
  -V monofont="DejaVu Sans Mono" \
  -V mainfont="DejaVu Serif" \
  -V geometry:top=0.75in \
  -V geometry:bottom=0.75in \
  -V geometry:left=0.75in \
  -V geometry:right=0.75in \
  orchestrated_ai_presentation_final.md \
  -o orchestrated_ai_presentation_final.pdf

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ PDF generated: orchestrated_ai_presentation_final.pdf"
    ls -lh orchestrated_ai_presentation_final.pdf
else
    echo ""
    echo "❌ PDF generation failed"
    exit 1
fi

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
