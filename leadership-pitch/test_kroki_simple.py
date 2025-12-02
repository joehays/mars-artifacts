#!/usr/bin/env python3
"""
Test Kroki with the simplest possible diagram and extended timeout.
"""

import json
import urllib.request
import time

# Ultra-simple 2-node diagram
simple_diagram = "graph TD\n    A-->B"

print("Testing Kroki with ultra-simple diagram:")
print(f"Diagram: {simple_diagram!r}")
print()

payload = json.dumps({
    "diagram_source": simple_diagram,
    "diagram_type": "mermaid",
    "output_format": "png"
}).encode('utf-8')

print("Attempting POST to https://kroki.io/mermaid/png")
print(f"Payload size: {len(payload)} bytes")
print()

for attempt in range(1, 4):
    print(f"Attempt {attempt}/3 (120s timeout)...")

    try:
        req = urllib.request.Request(
            "https://kroki.io/mermaid/png",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        start = time.time()
        with urllib.request.urlopen(req, timeout=120) as response:
            png_data = response.read()
            elapsed = time.time() - start

        print(f"✅ SUCCESS in {elapsed:.1f}s")
        print(f"   PNG size: {len(png_data):,} bytes")

        # Save it
        with open("/tmp/test-kroki.png", "wb") as f:
            f.write(png_data)
        print(f"   Saved to /tmp/test-kroki.png")
        break

    except urllib.error.HTTPError as e:
        print(f"❌ HTTP {e.code}: {e.reason}")
        break
    except urllib.error.URLError as e:
        elapsed = time.time() - start
        print(f"❌ Timeout after {elapsed:.1f}s: {e.reason}")
        if attempt < 3:
            print(f"   Waiting 5s before retry...")
            time.sleep(5)
    except Exception as e:
        print(f"❌ Error: {e}")
        break

print("\nDone.")
