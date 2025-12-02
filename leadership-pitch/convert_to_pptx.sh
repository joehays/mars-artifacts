#!/bin/bash
# Convert markdown presentation to PowerPoint format
# Usage: ./convert_to_pptx.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INPUT_MD="$SCRIPT_DIR/orchestrated_ai_presentation.md"
OUTPUT_PPTX="$SCRIPT_DIR/orchestrated_ai_presentation.pptx"
REFERENCE_PPTX="$SCRIPT_DIR/reference.pptx"

echo "🎯 Converting Markdown to PowerPoint..."
echo "   Input: $INPUT_MD"
echo "   Output: $OUTPUT_PPTX"

# Check if input exists
if [ ! -f "$INPUT_MD" ]; then
    echo "❌ Error: Input file not found: $INPUT_MD"
    exit 1
fi

# Check if pandoc is available
if ! command -v pandoc &> /dev/null; then
    echo "❌ Error: pandoc is not installed"
    echo "   Install with: sudo apt install pandoc"
    exit 1
fi

# Convert with pandoc
# Options:
#   -f markdown: Input format is markdown
#   -t pptx: Output format is PowerPoint
#   -o: Output file
#   --slide-level=2: Level 2 headers (##) create new slides
#   --reference-doc: Use custom template (if exists)

if [ -f "$REFERENCE_PPTX" ]; then
    echo "📋 Using reference template: $REFERENCE_PPTX"
    pandoc -f markdown -t pptx \
        --slide-level=2 \
        --reference-doc="$REFERENCE_PPTX" \
        -o "$OUTPUT_PPTX" \
        "$INPUT_MD"
else
    echo "📋 Using default PowerPoint template"
    pandoc -f markdown -t pptx \
        --slide-level=2 \
        -o "$OUTPUT_PPTX" \
        "$INPUT_MD"
fi

if [ -f "$OUTPUT_PPTX" ]; then
    echo "✅ Successfully created: $OUTPUT_PPTX"
    echo "   File size: $(du -h "$OUTPUT_PPTX" | cut -f1)"
    echo ""
    echo "🎨 To customize styling:"
    echo "   1. Open $OUTPUT_PPTX in PowerPoint"
    echo "   2. Modify master slides (View → Slide Master)"
    echo "   3. Save as reference.pptx in same directory"
    echo "   4. Re-run this script to apply custom styling"
else
    echo "❌ Error: Failed to create PowerPoint file"
    exit 1
fi
