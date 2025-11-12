# Leadership Brief PDF Build Guide

This directory contains the Leadership Brief document and multiple build methods for generating the PDF.

## Files

- `LEADERSHIP_BRIEF_ORCHESTRATED_AI.md` - Source markdown document
- `orchestrated_ai_draft.pdf` - Generated PDF output
- `header.tex` - LaTeX configuration (fonts, image scaling)
- `emoji-direct.lua` - Lua filter for emoji rendering
- `diagrams/` - Pre-generated diagram PDFs

## Build Scripts

### 1. `make_pdf.sh` (Primary Method)

**Best for**: Systems with working Chrome/Chromium

**Requires**:
- pandoc
- lualatex (texlive-luatex)
- mermaid-filter (npm package)
- mermaid-cli (npm package)
- Chrome or Chromium browser (non-snap version)

**Usage**:
```bash
bash make_pdf.sh
```

**Features**:
- Generates diagrams on-the-fly from mermaid code blocks
- Auto-detects Chrome/Chromium location
- Configures headless mode automatically

### 2. `make_pdf_no_mermaid.sh` (Fallback Method)

**Best for**:
- Snap-packaged Chromium (file access restrictions)
- Headless systems where mermaid-filter fails
- Systems without Chrome/Chromium

**Requires**:
- pandoc
- lualatex (texlive-luatex)
- Pre-generated diagram PDFs (in `diagrams/` directory)

**Usage**:
```bash
bash make_pdf_no_mermaid.sh
```

**Features**:
- Uses pre-generated diagram PDFs (no browser needed)
- Faster build (skips diagram rendering)
- 100% reliable on headless systems

### 3. `check_browser.sh` (Diagnostic Tool)

**Usage**:
```bash
bash check_browser.sh
```

Shows which browsers are installed and where they are located.

## Common Issues

### Issue: `net::ERR_ACCESS_DENIED` (Snap Chromium)

**Problem**: Snap-packaged Chromium can't access local files due to sandbox restrictions.

**Solutions**:
1. Use `make_pdf_no_mermaid.sh` (recommended for headless)
2. Install non-snap Chrome:
   ```bash
   sudo snap remove chromium
   wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
   sudo dpkg -i google-chrome-stable_current_amd64.deb
   ```

### Issue: Images Don't Fit on Pages

**Fixed**: Images now auto-scale to fit within page margins via `header.tex`:
- Max width: `\linewidth` (full text width)
- Max height: `0.9\textheight` (90% of page height)
- Preserves aspect ratio

### Issue: Missing Fonts

**Problem**: FiraCode Nerd Font not available

**Fixed**: Changed to DejaVu Sans Mono (widely available)

## Dependencies Installation

### Ubuntu/Debian:

```bash
# LaTeX
sudo apt-get install texlive-luatex texlive-fonts-recommended texlive-fonts-extra

# Pandoc
sudo apt-get install pandoc

# Chrome (non-snap)
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb

# NPM packages
npm install -g mermaid-filter @mermaid-js/mermaid-cli
```

## Regenerating Diagrams

If you need to update the pre-generated diagram PDFs:

```bash
cd diagrams
bash build_diagrams.sh
```

## Image Scaling Configuration

Images are automatically scaled via LaTeX configuration in `header.tex`:

```latex
\usepackage{graphicx}
\setkeys{Gin}{width=\linewidth,height=0.9\textheight,keepaspectratio}
```

This ensures all diagrams fit within page margins without manual sizing.

## Recent Fixes

- **2025-11-12**: Added LaTeX image auto-scaling
- **2025-11-12**: Added browser auto-detection
- **2025-11-12**: Added headless/snap Chromium workaround
- **2025-11-12**: Added `make_pdf_no_mermaid.sh` fallback script
