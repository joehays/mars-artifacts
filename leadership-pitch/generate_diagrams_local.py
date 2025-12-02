#!/usr/bin/env python3
"""
Generate PNG diagrams from Mermaid source files using LOCAL Mermaid CLI.

This script uses @mermaid-js/mermaid-cli (mmdc) which is self-hosted and air-gap compatible.
NO external API calls to kroki.io or any third-party services.

MARS Principle: Self-hosted and air-gap capable infrastructure.
"""

import subprocess
from pathlib import Path
import sys

# Configuration
MERMAID_CLI = "./node_modules/.bin/mmdc"
SCALE = 3  # 3x scaling for high-quality output
BACKGROUND = "transparent"

# Diagrams to generate
DIAGRAMS = [
    # Part 6: Technical Implementation Details
    "git-worktrees-workflow",
    "litellm-architecture",
    "sysbox-architecture",
    "git-submodules-research",
    "git-submodules-mars",
]

def generate_png(diagram_name: str, base_dir: Path) -> bool:
    """Generate PNG from Mermaid file using local Mermaid CLI."""

    mermaid_file = base_dir / "diagrams" / "mermaid" / f"{diagram_name}.mmd"
    output_file = base_dir / "diagrams" / "png" / f"{diagram_name}.png"

    if not mermaid_file.exists():
        print(f"  ✗ Mermaid file not found: {mermaid_file}")
        return False

    try:
        print(f"  Generating...", end=" ", flush=True)

        # Run local Mermaid CLI (NO external API calls)
        result = subprocess.run(
            [
                MERMAID_CLI,
                "-i", str(mermaid_file),
                "-o", str(output_file),
                "-b", BACKGROUND,
                "-s", str(SCALE),
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0 and output_file.exists():
            size = output_file.stat().st_size
            print(f"✓ Success ({size:,} bytes)")
            return True
        else:
            print(f"✗ Failed: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print(f"✗ Timeout after 60s")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    """Generate PNG diagrams from Mermaid source files."""

    base_dir = Path(__file__).parent

    # Verify Mermaid CLI is installed
    mmdc_path = base_dir / MERMAID_CLI
    if not mmdc_path.exists():
        print("ERROR: Mermaid CLI not found!")
        print(f"Expected: {mmdc_path}")
        print("")
        print("Install with: npm install @mermaid-js/mermaid-cli")
        sys.exit(1)

    print(f"Generating {len(DIAGRAMS)} diagrams using LOCAL Mermaid CLI")
    print(f"Mermaid CLI: {mmdc_path}")
    print(f"Output directory: {base_dir / 'diagrams' / 'png'}")
    print("")

    success_count = 0

    for i, diagram_name in enumerate(DIAGRAMS, 1):
        print(f"[{i}/{len(DIAGRAMS)}] {diagram_name}")

        if generate_png(diagram_name, base_dir):
            success_count += 1

        print()

    print(f"Complete: {success_count}/{len(DIAGRAMS)} diagrams generated")

    if success_count < len(DIAGRAMS):
        sys.exit(1)

if __name__ == "__main__":
    main()
