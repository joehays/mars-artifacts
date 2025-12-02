#!/usr/bin/env python3
"""
Rebuild diagram PDFs from SVG files using cairosvg.
This avoids the mmdc/Chrome dependency.
"""

import subprocess
import sys
from pathlib import Path

def main():
    diagrams_dir = Path("diagrams")

    # Find all SVG files
    svg_files = list(diagrams_dir.glob("*.svg"))

    if not svg_files:
        print("No SVG files found in diagrams/")
        sys.exit(1)

    print(f"Found {len(svg_files)} SVG files")
    print()

    for svg_file in svg_files:
        pdf_file = svg_file.with_suffix('.pdf')
        print(f"Converting {svg_file.name} → {pdf_file.name}")

        # Use cairosvg to convert SVG to PDF
        try:
            result = subprocess.run(
                ['cairosvg', str(svg_file), '-o', str(pdf_file)],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"  ✓ Success")
        except subprocess.CalledProcessError as e:
            print(f"  ✗ Failed: {e.stderr}")
        except FileNotFoundError:
            print("  ✗ cairosvg not found. Install with: pip install cairosvg")
            sys.exit(1)

    print()
    print(f"✅ Converted {len(svg_files)} diagrams")

if __name__ == '__main__':
    main()
