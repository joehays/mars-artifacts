#!/usr/bin/env python3
"""
Generate PNG diagrams for the 5 new technical deep-dive Mermaid files.
Uses Kroki API with retry logic and delays to avoid overwhelming the service.
"""

import json
import time
import urllib.request
import urllib.error
from pathlib import Path

# Configuration
KROKI_URL = "https://kroki.io"
SCALE = 3
RETRY_ATTEMPTS = 3
RETRY_DELAY = 5  # seconds between retries

# The 5 new diagrams we need
NEW_DIAGRAMS = [
    "git-worktrees-workflow",
    "litellm-architecture",
    "sysbox-architecture",
    "git-submodules-research",
    "git-submodules-mars",
]

def generate_png(mermaid_file: Path, output_file: Path) -> bool:
    """Generate PNG from Mermaid file using Kroki API with retries."""

    # Read Mermaid content
    mermaid_content = mermaid_file.read_text()

    # Prepare Kroki request
    payload = json.dumps({
        "diagram_source": mermaid_content,
        "diagram_type": "mermaid",
        "output_format": "png",
        "diagram_options": {"scale": SCALE}
    }).encode('utf-8')

    # Try with retries
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            print(f"  Attempt {attempt}/{RETRY_ATTEMPTS}...", end=" ", flush=True)

            req = urllib.request.Request(
                f"{KROKI_URL}",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=30) as response:
                png_data = response.read()
                output_file.write_bytes(png_data)
                print(f"✓ Success ({len(png_data):,} bytes)")
                return True

        except urllib.error.HTTPError as e:
            print(f"✗ HTTP {e.code}: {e.reason}")
            if attempt < RETRY_ATTEMPTS:
                print(f"    Waiting {RETRY_DELAY}s before retry...")
                time.sleep(RETRY_DELAY)

        except urllib.error.URLError as e:
            print(f"✗ Error: {e.reason}")
            if attempt < RETRY_ATTEMPTS:
                print(f"    Waiting {RETRY_DELAY}s before retry...")
                time.sleep(RETRY_DELAY)

        except Exception as e:
            print(f"✗ Error: {e}")
            if attempt < RETRY_ATTEMPTS:
                print(f"    Waiting {RETRY_DELAY}s before retry...")
                time.sleep(RETRY_DELAY)

    return False

def main():
    """Generate PNG diagrams for new Mermaid files."""

    base_dir = Path("/workspace/mars-v2/external/mars-artifacts/leadership-pitch")
    mermaid_dir = base_dir / "diagrams" / "mermaid"
    png_dir = base_dir / "diagrams" / "png"

    print(f"Generating {len(NEW_DIAGRAMS)} new diagrams")
    print(f"Output directory: {png_dir}")
    print()

    success_count = 0

    for i, diagram_name in enumerate(NEW_DIAGRAMS, 1):
        print(f"[{i}/{len(NEW_DIAGRAMS)}] {diagram_name}")

        mermaid_file = mermaid_dir / f"{diagram_name}.mmd"
        output_file = png_dir / f"{diagram_name}.png"

        if not mermaid_file.exists():
            print(f"  ✗ Mermaid file not found: {mermaid_file}")
            continue

        if generate_png(mermaid_file, output_file):
            success_count += 1

        # Delay between diagrams to avoid overwhelming Kroki
        if i < len(NEW_DIAGRAMS):
            print(f"  Waiting 2s before next diagram...")
            time.sleep(2)
        print()

    print(f"Complete: {success_count}/{len(NEW_DIAGRAMS)} diagrams generated")

if __name__ == "__main__":
    main()
