#!/usr/bin/env python3
"""
Regenerate mermaid diagrams using Kroki service.

Kroki renders diagrams with proper text elements that convert correctly to PDF.
"""

import base64
import sys
import zlib
from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

def encode_diagram(source):
    """Encode diagram source for Kroki URL (compressed + base64 + url-safe)."""
    compressed = zlib.compress(source.encode('utf-8'), 9)
    encoded = base64.urlsafe_b64encode(compressed).decode('utf-8')
    return encoded

def render_diagram_pdf(mmd_source, output_path):
    """Render mermaid diagram to PDF using Kroki API (PNG) + ImageMagick."""

    import json
    import subprocess

    # Kroki API endpoint (POST) - get PNG (high resolution)
    url = "https://kroki.io/mermaid/png"

    # Prepare JSON payload
    payload = json.dumps({
        "diagram_source": mmd_source,
        "diagram_type": "mermaid",
        "output_format": "png"
    }).encode('utf-8')

    print(f"  Kroki PNG... ", end='', flush=True)

    try:
        # Make POST request for PNG
        req = Request(
            url,
            data=payload,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'MARS-Leadership-Brief/1.0'
            },
            method='POST'
        )

        with urlopen(req, timeout=60) as response:
            png_data = response.read()

        print(f"✓ ", end='', flush=True)

        # Convert PNG to PDF using ImageMagick
        print(f"PNG→PDF... ", end='', flush=True)

        result = subprocess.run(
            ['convert', '-', str(output_path)],
            input=png_data,
            capture_output=True,
            timeout=60
        )

        if result.returncode != 0:
            print(f"✗ ImageMagick failed: {result.stderr.decode()[:100]}")
            return False

        # Check output file size
        if not output_path.exists():
            print(f"✗ PDF not created")
            return False

        pdf_size = output_path.stat().st_size
        print(f"✓ ({pdf_size:,} bytes)")
        return True

    except HTTPError as e:
        # Try to read error response
        try:
            error_body = e.read().decode('utf-8')
            print(f"✗ HTTP {e.code}: {error_body[:200]}")
        except:
            print(f"✗ HTTP Error {e.code}: {e.reason}")
        return False
    except URLError as e:
        print(f"✗ URL Error: {e.reason}")
        return False
    except subprocess.TimeoutExpired:
        print(f"✗ Timeout during PNG→PDF conversion")
        return False
    except FileNotFoundError:
        print(f"✗ ImageMagick not found (install imagemagick)")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    diagrams_dir = Path("diagrams")
    mermaid_dir = diagrams_dir / "mermaid"

    if not mermaid_dir.exists():
        print(f"Error: {mermaid_dir} directory not found")
        sys.exit(1)

    # Find all .mmd files
    mmd_files = sorted(mermaid_dir.glob("*.mmd"))

    if not mmd_files:
        print(f"No .mmd files found in {mermaid_dir}")
        sys.exit(1)

    print(f"Found {len(mmd_files)} mermaid diagrams")
    print()

    success_count = 0
    fail_count = 0

    for mmd_file in mmd_files:
        diagram_name = mmd_file.stem
        output_pdf = diagrams_dir / f"{diagram_name}.pdf"

        print(f"[{success_count + fail_count + 1}/{len(mmd_files)}] {diagram_name}")

        # Read mermaid source
        try:
            mmd_source = mmd_file.read_text(encoding='utf-8')
        except Exception as e:
            print(f"  ✗ Failed to read {mmd_file}: {e}")
            fail_count += 1
            continue

        # Render to PDF via Kroki
        if render_diagram_pdf(mmd_source, output_pdf):
            success_count += 1
        else:
            fail_count += 1

        print()

    # Summary
    print("=" * 60)
    print(f"✅ Success: {success_count}/{len(mmd_files)}")
    if fail_count > 0:
        print(f"❌ Failed: {fail_count}/{len(mmd_files)}")
    print("=" * 60)

    if fail_count > 0:
        sys.exit(1)

if __name__ == '__main__':
    main()
