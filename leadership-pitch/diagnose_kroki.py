#!/usr/bin/env python3
"""
Diagnose Kroki API connectivity issues.
"""

import socket
import urllib.request
import urllib.error
import json

print("=" * 60)
print("Kroki API Diagnostics")
print("=" * 60)

# 1. DNS Resolution
print("\n1. DNS Resolution:")
try:
    ip = socket.gethostbyname("kroki.io")
    print(f"   ✓ kroki.io resolves to: {ip}")
except socket.gaierror as e:
    print(f"   ✗ DNS resolution failed: {e}")
    exit(1)

# 2. TCP Connection
print("\n2. TCP Connection (port 443):")
try:
    sock = socket.create_connection(("kroki.io", 443), timeout=10)
    sock.close()
    print(f"   ✓ TCP connection successful")
except Exception as e:
    print(f"   ✗ TCP connection failed: {e}")
    exit(1)

# 3. HTTPS Connection
print("\n3. HTTPS Connection:")
try:
    req = urllib.request.Request("https://kroki.io/")
    with urllib.request.urlopen(req, timeout=10) as response:
        status = response.getcode()
        print(f"   ✓ HTTPS GET / returned: {status}")
except urllib.error.HTTPError as e:
    print(f"   ⚠ HTTP Error: {e.code} {e.reason}")
except urllib.error.URLError as e:
    print(f"   ✗ URL Error: {e.reason}")
    exit(1)

# 4. Simple Mermaid Test
print("\n4. Simple Mermaid Diagram Test:")
simple_diagram = """graph TD
    A[Start] --> B[End]
"""

payload = json.dumps({
    "diagram_source": simple_diagram,
    "diagram_type": "mermaid",
    "output_format": "png"
}).encode('utf-8')

try:
    req = urllib.request.Request(
        "https://kroki.io",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=30) as response:
        png_data = response.read()
        print(f"   ✓ Simple diagram generated: {len(png_data):,} bytes")
except urllib.error.HTTPError as e:
    print(f"   ✗ HTTP Error: {e.code} {e.reason}")
    try:
        error_body = e.read().decode('utf-8')
        print(f"   Error details: {error_body[:200]}")
    except:
        pass
except urllib.error.URLError as e:
    print(f"   ✗ URL Error: {e.reason}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# 5. Complex Diagram Test
print("\n5. Complex Diagram Test (with scale):")
payload_with_scale = json.dumps({
    "diagram_source": simple_diagram,
    "diagram_type": "mermaid",
    "output_format": "png",
    "diagram_options": {"scale": 3}
}).encode('utf-8')

try:
    req = urllib.request.Request(
        "https://kroki.io",
        data=payload_with_scale,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=30) as response:
        png_data = response.read()
        print(f"   ✓ Diagram with scale=3 generated: {len(png_data):,} bytes")
except urllib.error.HTTPError as e:
    print(f"   ✗ HTTP Error: {e.code} {e.reason}")
    try:
        error_body = e.read().decode('utf-8')
        print(f"   Error details: {error_body[:200]}")
    except:
        pass
except urllib.error.URLError as e:
    print(f"   ✗ URL Error: {e.reason}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 60)
print("Diagnostics Complete")
print("=" * 60)
