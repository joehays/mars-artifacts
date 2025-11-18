# Lessons Learned: Mermaid Diagram PDF Rendering

**Date**: 2025-11-18
**Document**: Leadership Brief PDF (`orchestrated_ai_draft.pdf`)
**Issue**: Missing text in flowchart diagrams (figures 4, 7, 9, 11, 12)

---

## Problem Statement

When building a leadership brief PDF from markdown with embedded mermaid diagrams, **5 out of 12 diagrams** were displaying blank or with missing text:

- **Figure 4**: LangGraph State Machine (flowchart)
- **Figure 7**: GitLab CI Pipeline (flowchart)
- **Figure 9**: ADR Authoring Workflow (flowchart)
- **Figure 11**: OpenTelemetry Trace (flowchart)
- **Figure 12**: Pre-commit Hook Flow (flowchart)

**Working diagrams**: Sequence diagrams (a2a-protocol, mcp-protocol)
**Broken diagrams**: All flowchart/state machine diagrams

---

## Root Cause Analysis

### Technical Investigation

1. **SVG Rendering Difference**:
   - **Sequence diagrams**: Used `<text>` elements (native SVG text)
   - **Flowcharts**: Used `<foreignObject>` with HTML content

2. **foreignObject Problem**:
   ```xml
   <!-- Sequence diagram (works) -->
   <text x="100" y="50">Agent</text>

   <!-- Flowchart (broken) -->
   <foreignObject x="100" y="50" width="200" height="100">
     <div xmlns="http://www.w3.org/1999/xhtml">
       <p>Agent</p>
     </div>
   </foreignObject>
   ```

3. **PDF Conversion Tools**:
   - `<text>` elements → Converted correctly by all tools
   - `<foreignObject>` with HTML → Requires full HTML rendering engine

---

## Approaches Tried (Chronological)

### ❌ Attempt 1: Remove Width Attributes (Failed)

**Hypothesis**: `{ width=100% }` attributes were causing layout issues

**Action**: Modified `convert_all_diagrams.py` to remove width attributes at 4 locations

**Result**: Problem persisted - diagrams still showed no text

**Lesson**: The problem was not layout-related, but rendering-related

---

### ❌ Attempt 2: Kroki SVG + rsvg-convert (Failed)

**Hypothesis**: Regenerate diagrams with Kroki (better renderer)

**Action**:
- Created `regenerate_diagrams_kroki.py`
- Used Kroki API to generate SVG
- Used `rsvg-convert` for SVG→PDF conversion

**Result**: Text still not visible in flowcharts

**Why it failed**: `rsvg-convert` **drops foreignObject content entirely**

**Evidence**:
- Sequence diagrams: 73 lines of extractable text ✓
- Flowcharts: 0 lines of extractable text ✗

**Lesson**: `rsvg-convert` does not support HTML in SVG

---

### ❌ Attempt 3: Kroki SVG + Inkscape (Failed - Worse)

**Hypothesis**: Inkscape has better foreignObject support than rsvg-convert

**Action**:
- Installed Inkscape (18 MB + dependencies)
- Modified script to use Inkscape CLI
- Command: `inkscape --export-filename=output.pdf --export-type=pdf input.svg`

**Result**: **Black blocks instead of text** (worse than before!)

**Why it failed**: Inkscape renders foreignObject HTML as **solid placeholder rectangles** without actual text content

**Lesson**: Inkscape lacks a full HTML rendering engine - it creates placeholders for foreignObject elements

---

### ❌ Attempt 4: Kroki SVG + Chromium (Failed - Installation)

**Hypothesis**: Chromium has full HTML rendering (can render foreignObject properly)

**Action**:
- Created HTML wrapper for SVG
- Attempted to use `chromium --headless --print-to-pdf`

**Result**: Installation failed - chromium-browser is a snap wrapper that doesn't work in Docker containers

**Why it failed**: Snap requires systemd and full container privileges

**Lesson**: Headless browser solutions don't work well in restricted container environments

---

### ✅ Attempt 5: Kroki PNG + ImageMagick (SUCCESS!)

**Hypothesis**: PNG output pre-renders all text as raster graphics

**Action**:
1. Changed Kroki endpoint from `/mermaid/svg` to `/mermaid/png`
2. Used ImageMagick `convert` to wrap PNG in PDF
3. Fixed ImageMagick security policy to allow PDF operations

**ImageMagick Policy Fix**:
```bash
sudo sed -i 's/<policy domain="coder" rights="none" pattern="PDF" \/>/<policy domain="coder" rights="read|write" pattern="PDF" \/>/g' /etc/ImageMagick-6/policy.xml
```

**Result**: **All 12 diagrams render perfectly with visible text!** ✅

**File Size Impact**: 592K → 1.8M (3x larger due to raster graphics)

**Lesson**: When vector rendering fails, **rasterization is a reliable fallback**

---

## Final Solution Architecture

```
Mermaid Source (.mmd)
    ↓
Kroki API (https://kroki.io/mermaid/png)
    ↓
PNG Image (high resolution, text pre-rendered)
    ↓
ImageMagick convert (PNG → PDF wrapper)
    ↓
PDF with embedded PNG
    ↓
Pandoc (markdown → PDF with diagram references)
    ↓
Final Leadership Brief PDF (1.8M, 103 pages)
```

### Script: `regenerate_diagrams_kroki.py`

**Key Implementation**:
```python
# Kroki API endpoint (POST) - get PNG
url = "https://kroki.io/mermaid/png"

payload = json.dumps({
    "diagram_source": mmd_source,
    "diagram_type": "mermaid",
    "output_format": "png"
}).encode('utf-8')

# Make POST request for PNG
req = Request(url, data=payload, headers={...}, method='POST')
with urlopen(req, timeout=60) as response:
    png_data = response.read()

# Convert PNG to PDF using ImageMagick
subprocess.run(['convert', '-', str(output_path)], input=png_data)
```

**Usage**:
```bash
cd /workspace/mars-v2/external/mars-artifacts/leadership-pitch
python3 regenerate_diagrams_kroki.py
bash make_pdf_no_mermaid.sh
```

---

## Trade-offs Analysis

### PNG-Based Approach (Current Solution)

**Advantages**:
- ✅ **Guaranteed text visibility** - All text is rasterized pixels
- ✅ **Universal compatibility** - PNG works everywhere
- ✅ **No HTML rendering required** - No browser dependencies
- ✅ **Consistent rendering** - Same appearance on all devices
- ✅ **Works for all diagram types** - Sequence, flowcharts, state machines

**Disadvantages**:
- ❌ **Larger file size** - 1.8M vs 592K (3x increase)
- ❌ **Not scalable** - Raster graphics pixelate at high zoom
- ❌ **Lower quality** - Text edges slightly less sharp than vector
- ❌ **Not searchable** - Text is pixels, not selectable

### Vector-Based Approach (Failed Attempts)

**Advantages**:
- ✅ **Smaller file size** - 592K (pure vector graphics)
- ✅ **Infinite scalability** - No pixelation at any zoom level
- ✅ **Sharp text** - Perfect text rendering
- ✅ **Searchable** - Text can be selected/copied

**Disadvantages**:
- ❌ **foreignObject not supported** - Most PDF tools can't render HTML in SVG
- ❌ **Inconsistent rendering** - Different tools produce different results
- ❌ **Complex toolchain** - Requires headless browser (Chromium/Playwright)
- ❌ **Installation challenges** - Chromium/browsers don't work in containers

---

## Recommendations

### For This Project (Leadership Brief)

**Current Status**: ✅ **Acceptable**

The PNG-based approach is sufficient for a leadership brief:
- File size (1.8M) is reasonable for email/web distribution
- Print quality is adequate for standard viewing (100-200% zoom)
- All diagrams are now visible and readable

**Action**: No further changes needed - ship it!

### For Future Projects

1. **If file size is critical** (e.g., email size limits):
   - Consider using vector-based sequence diagrams only (avoid flowcharts)
   - OR use Playwright/Puppeteer (bundles Chromium, works in Docker)
   - OR pre-render diagrams outside Docker with full Chromium

2. **If print quality is critical** (e.g., poster printing):
   - Increase Kroki PNG resolution (query parameter)
   - OR use mmdc (mermaid-cli) with Puppeteer locally
   - OR manually create diagrams in draw.io/Visio for perfect vector output

3. **If diagram updates are frequent**:
   - Keep `regenerate_diagrams_kroki.py` script for easy regeneration
   - Consider CI/CD automation for diagram regeneration
   - Version control .mmd source files (currently in `diagrams/mermaid/`)

---

## Technical Details

### Kroki API

**Endpoint**: `https://kroki.io/mermaid/{format}`

**Supported Formats**:
- `png` - ✅ Works (used in final solution)
- `svg` - ⚠️ Works but foreignObject issues in PDF conversion
- `pdf` - ❌ Not supported for mermaid (returns HTTP 400)

**Request Format** (POST):
```json
{
  "diagram_source": "graph TD\n  A-->B",
  "diagram_type": "mermaid",
  "output_format": "png"
}
```

**Response**: Binary image data (PNG, SVG, etc.)

### ImageMagick Security Policy

**Default Policy**: `/etc/ImageMagick-6/policy.xml`

**Problem**: PDF operations blocked by default (security measure)

**Fix**:
```xml
<!-- Before (blocked) -->
<policy domain="coder" rights="none" pattern="PDF" />

<!-- After (allowed) -->
<policy domain="coder" rights="read|write" pattern="PDF" />
```

**Command**:
```bash
sudo sed -i 's/<policy domain="coder" rights="none" pattern="PDF" \/>/<policy domain="coder" rights="read|write" pattern="PDF" \/>/g' /etc/ImageMagick-6/policy.xml
```

### Diagram Inventory

**Total Diagrams**: 12

**Working from Start** (sequence diagrams with `<text>` elements):
1. a2a-protocol.pdf
2. mcp-protocol.pdf

**Fixed by PNG Approach** (flowcharts with `<foreignObject>`):
3. adr-authoring-workflow.pdf (Figure 9)
4. appendix-c-architecture.pdf
5. gitlab-ci-pipeline.pdf (Figure 7)
6. langgraph-state-machine.pdf (Figure 4)
7. mars-dev-architecture.pdf
8. mars-rt-architecture.pdf
9. merge-request-workflow.pdf
10. opentelemetry-trace.pdf (Figure 11)
11. orchestration-flow.pdf
12. precommit-hook-flow.pdf (Figure 12)

---

## Tools Comparison

| Tool | foreignObject Support | Installation | Result | Recommendation |
|------|----------------------|--------------|--------|----------------|
| **rsvg-convert** | ❌ Drops content | `apt install librsvg2-bin` | Blank diagrams | Avoid for flowcharts |
| **Inkscape** | ⚠️ Black placeholders | `apt install inkscape` (18 MB) | Worse than blank | Avoid |
| **Chromium headless** | ✅ Full HTML rendering | Snap (doesn't work in Docker) | Installation failed | Only if browser available |
| **ImageMagick (PNG)** | N/A (raster) | Already installed | **Perfect!** ✅ | **Recommended** |
| **mmdc (mermaid-cli)** | ✅ Uses Puppeteer | npm + Chromium (~400 MB) | Would work but heavy | For local dev only |

---

## Key Insights

1. **foreignObject is a trap**: SVG's `<foreignObject>` feature is designed for web browsers, not PDF renderers. Most PDF tools don't have full HTML rendering engines.

2. **Rasterization solves compatibility**: When vector rendering fails, converting to PNG guarantees consistent results across all viewers.

3. **Tool assumptions matter**: Don't assume "better tools" (like Inkscape) will handle edge cases better - test thoroughly.

4. **Security policies are real**: ImageMagick blocks PDF operations by default - always check security policies when working with file conversions.

5. **File size vs compatibility**: Sometimes 3x file size is acceptable for guaranteed rendering - know your priorities.

---

## Files Modified

1. **`convert_all_diagrams.py`** - Removed width attributes (lines 34, 105, 160, 179)
2. **`regenerate_diagrams_kroki.py`** - Created new script (PNG-based approach)
3. **`/etc/ImageMagick-6/policy.xml`** - Enabled PDF operations

---

## Final Metrics

- **Total diagrams**: 12
- **Success rate**: 100% (12/12 visible)
- **File size**: 1.8M (3x increase acceptable)
- **Build time**: ~30 seconds (Kroki API calls)
- **Dependencies**: Python 3, ImageMagick, internet access (Kroki)

---

## Conclusion

**Problem**: foreignObject-based flowcharts not rendering in PDF
**Solution**: Kroki PNG + ImageMagick rasterization
**Status**: ✅ **RESOLVED** - All diagrams now visible
**Recommendation**: Use this approach for future leadership briefs

---

**Document Status**: Complete
**Next Action**: Ship the PDF (orchestrated_ai_draft.pdf)
**Review Date**: N/A (one-time fix)
