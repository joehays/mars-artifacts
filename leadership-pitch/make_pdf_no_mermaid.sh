#!/bin/bash
#
# Build Leadership Brief PDF WITHOUT mermaid-filter (uses pre-generated diagram PDFs)
#
# This is a workaround for environments where:
# - Chrome/Chromium has file access restrictions (snap packages)
# - Running headless without proper browser configuration
# - mermaid-filter fails for any reason
#
# Requirements:
#   - pandoc (markdown → LaTeX/PDF converter)
#   - lualatex (LaTeX engine with emoji support)
#   - Pre-generated diagram PDFs in diagrams/ directory
#
# Pre-generate diagrams with:
#   cd diagrams && bash build_diagrams.sh

echo "📄 Building Leadership Brief PDF (using pre-generated diagrams)..."
echo ""

# Check if diagrams exist
MISSING=0
for diagram in \
    a2a-protocol \
    adr-authoring-workflow \
    gitlab-ci-pipeline \
    langgraph-state-machine \
    mcp-protocol \
    merge-request-workflow \
    opentelemetry-trace \
    precommit-hook-flow
do
    if [ ! -f "diagrams/${diagram}.pdf" ]; then
        echo "❌ Missing: diagrams/${diagram}.pdf"
        MISSING=1
    fi
done

if [ $MISSING -eq 1 ]; then
    echo ""
    echo "❌ Some diagram PDFs are missing!"
    echo "Please generate them first:"
    echo "  cd diagrams && bash build_diagrams.sh"
    exit 1
fi

echo "✅ All diagram PDFs found"
echo ""

# Step 1: Convert mermaid code blocks to image references
echo "📝 Converting mermaid code blocks to image references..."
python3 convert_mermaid_to_images.py LEADERSHIP_BRIEF_ORCHESTRATED_AI.md > LEADERSHIP_BRIEF_WITH_IMAGES.md

if [ $? -ne 0 ]; then
    echo "❌ Failed to convert mermaid blocks"
    exit 1
fi

echo "✅ Conversion complete"
echo ""

# Step 2: Build PDF from converted markdown
echo "🔨 Building PDF..."
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
  LEADERSHIP_BRIEF_WITH_IMAGES.md \
  -o orchestrated_ai_draft.pdf

# Clean up temporary file
rm -f LEADERSHIP_BRIEF_WITH_IMAGES.md

if [ $? -eq 0 ]; then
    echo "✅ PDF generated: orchestrated_ai_draft.pdf"
    ls -lh orchestrated_ai_draft.pdf
else
    echo "❌ PDF generation failed"
    exit 1
fi
