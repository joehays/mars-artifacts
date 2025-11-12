#!/bin/bash
#
# Build all Mermaid diagrams to standalone PDF files
#
# This script renders all .mmd files in diagrams/mermaid/ to PDF format.
# PDFs can be embedded in presentations, documentation, or used standalone.
#
# Requirements:
#   - @mermaid-js/mermaid-cli (mmdc command)
#
# Install:
#   npm install -g @mermaid-js/mermaid-cli
#
# Usage:
#   ./build_diagrams.sh          # Build all diagrams
#   ./build_diagrams.sh --clean  # Clean PDFs then build

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Change to script directory
cd "$(dirname "$0")"

# Check for mmdc command
if ! command -v mmdc &> /dev/null; then
    echo -e "${RED}Error: mmdc command not found${NC}"
    echo -e "${YELLOW}Install with: npm install -g @mermaid-js/mermaid-cli${NC}"
    exit 1
fi

# Clean existing PDFs if --clean flag is provided
if [[ "$1" == "--clean" ]]; then
    echo -e "${YELLOW}Cleaning existing diagram PDFs...${NC}"
    rm -f diagrams/*.pdf
    echo -e "${GREEN}✓ Cleaned${NC}"
fi

# Create output directory if it doesn't exist
mkdir -p diagrams

# Count diagrams
total_diagrams=$(find diagrams/mermaid -name "*.mmd" | wc -l)
current=0

echo -e "${GREEN}Building ${total_diagrams} diagrams...${NC}"
echo ""

# Render each .mmd file to PDF
for mmd_file in diagrams/mermaid/*.mmd; do
    # Skip if no files found
    [ -e "$mmd_file" ] || continue

    current=$((current + 1))

    # Get base filename without extension
    basename=$(basename "$mmd_file" .mmd)

    # Output path
    pdf_file="diagrams/${basename}.pdf"

    echo -e "${YELLOW}[$current/$total_diagrams]${NC} Rendering ${basename}..."

    # Render to PDF with transparent background
    if mmdc -i "$mmd_file" -o "$pdf_file" -b transparent 2>&1 | grep -q "Error"; then
        echo -e "${RED}✗ Failed: ${basename}${NC}"
        exit 1
    else
        echo -e "${GREEN}✓ Success: ${pdf_file}${NC}"
    fi
done

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ All diagrams built successfully!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "Output directory: ${YELLOW}diagrams/${NC}"
echo -e "Total PDFs: ${GREEN}${total_diagrams}${NC}"
echo ""
echo -e "Generated PDFs:"
ls -1 diagrams/*.pdf | while read -r pdf; do
    size=$(du -h "$pdf" | cut -f1)
    echo -e "  • $(basename "$pdf") ${YELLOW}(${size})${NC}"
done
