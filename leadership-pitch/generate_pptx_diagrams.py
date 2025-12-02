#!/usr/bin/env python3
"""
Generate PNG diagrams for PowerPoint presentation.
Uses Kroki service to render high-quality PNG images from Mermaid source.
"""

import json
import sys
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

def render_diagram_png(mmd_source, output_path, scale=3):
    """Render mermaid diagram to PNG using Kroki API at specified scale."""

    # Kroki API endpoint (POST) - get PNG at high resolution
    url = f"https://kroki.io/mermaid/png"

    # Prepare JSON payload with scale factor for higher quality
    payload = json.dumps({
        "diagram_source": mmd_source,
        "diagram_type": "mermaid",
        "output_format": "png"
    }).encode('utf-8')

    print(f"  Kroki PNG (scale={scale})... ", end='', flush=True)

    try:
        # Make POST request for PNG
        req = Request(
            url,
            data=payload,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'MARS-Leadership-Presentation/1.0'
            },
            method='POST'
        )

        with urlopen(req, timeout=60) as response:
            png_data = response.read()

        # Write PNG directly
        output_path.write_bytes(png_data)

        png_size = output_path.stat().st_size
        print(f"✓ ({png_size:,} bytes)")
        return True

    except HTTPError as e:
        try:
            error_body = e.read().decode('utf-8')
            print(f"✗ HTTP {e.code}: {error_body[:200]}")
        except:
            print(f"✗ HTTP Error {e.code}: {e.reason}")
        return False
    except URLError as e:
        print(f"✗ URL Error: {e.reason}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    diagrams_dir = Path("diagrams")
    mermaid_dir = diagrams_dir / "mermaid"
    png_dir = diagrams_dir / "png"

    # Create PNG output directory
    png_dir.mkdir(exist_ok=True)

    if not mermaid_dir.exists():
        print(f"Error: {mermaid_dir} directory not found")
        sys.exit(1)

    # Find all .mmd files
    mmd_files = sorted(mermaid_dir.glob("*.mmd"))

    if not mmd_files:
        print(f"No .mmd files found in {mermaid_dir}")
        sys.exit(1)

    print(f"Found {len(mmd_files)} mermaid diagrams")
    print(f"Output directory: {png_dir}")
    print()

    success_count = 0
    fail_count = 0

    for mmd_file in mmd_files:
        diagram_name = mmd_file.stem
        output_png = png_dir / f"{diagram_name}.png"

        print(f"[{success_count + fail_count + 1}/{len(mmd_files)}] {diagram_name}")

        # Read mermaid source
        try:
            mmd_source = mmd_file.read_text(encoding='utf-8')
        except Exception as e:
            print(f"  ✗ Failed to read {mmd_file}: {e}")
            fail_count += 1
            continue

        # Render to PNG via Kroki (scale=3 for high quality)
        if render_diagram_png(mmd_source, output_png, scale=3):
            success_count += 1
        else:
            fail_count += 1

        print()

    # Summary
    print("=" * 60)
    print(f"✅ Success: {success_count}/{len(mmd_files)}")
    if fail_count > 0:
        print(f"❌ Failed: {fail_count}/{len(mmd_files)}")
    print(f"📁 PNG files in: {png_dir.absolute()}")
    print("=" * 60)

    if fail_count > 0:
        sys.exit(1)

if __name__ == '__main__':
    main()
