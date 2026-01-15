# Gridfinity Label Generator - AI Agent Instructions

## Project Overview
This is a Python-based label generator for Gridfinity bins. It reads part data from CSV, fills an SVG template using Jinja2, generates QR codes, and outputs PDFs/PNGs/SVGs suitable for label printing.

## Architecture & Data Flow
1. **Input**: CSV file ([parts.csv](../parts.csv)) with columns: `name,description,top_symbol,side_symbol,reorder_url`
2. **Template**: [template.svg](../template.svg) - Jinja2-templated SVG with placeholders for text, icons, and QR codes
3. **Processing**: [generator.py](../generator.py) fills template for each CSV row
4. **Output**: SVG/PDF/PNG files per row in the CSV in `output/` directory

## Key Technical Patterns

### Label Dimensions
- Fixed size: 9mm × 36mm (configured in `LABEL_WIDTH_MM`/`LABEL_HEIGHT_MM`), which fits standard 1x1 Gridfinity label holders
- Conversion to pixels uses 150 DPI in `mm_to_px()` function (configured in `LABEL_PRINTER_DPI` constant)

### SVG Template Structure

### Icon Integration
- Icons are SVGs, generated via functions in `ICON_GENERATORS` dictionary
- Icons scaled to fit within a 100mm square area on the left side of the label
- The template scales icons down to fit the label height while maintaining aspect ratio

### QR Code Generation
- Uses `segno` library with `micro=True` setting
- XML declaration stripped from generated SVG to prevent duplication when embedding
- Always generated from `reorder_url` field
  - Tries to generate a micro QR; falls back to standard QR if URL too long
  - Embedded directly into the label SVG
  - QR code doesn't necessarily have to be valid URL; can be any string
  - If it is a URL, it should start with `http://` or `https://` to ensure proper encoding
  - URLs will be attempted to be shortened, by using external services, if they exceed micro QR capacity

### Output Formats
- One file per label, type as specified: `output/{filename}.png`
- PDF/PNG use `cairosvg` with dimensions calculated via `mm_to_px()`
- PNG is the default output format

## Development Workflow

### Running the Generator
```bash
python generator.py
```
Hardcoded to read `parts.csv` by default, but may be changed with a command line argument.

### Dependencies
Install via: `pip install -r requirements.txt`
- `segno`: QR code generation
- `jinja2`: SVG templating
- `cairosvg`: SVG→PDF/PNG conversion (requires Cairo system library)

### Printing Labels
Use `ptouch-print` command (see [readme.md](../readme.md)) to send PNGs to label printer.

## Important Conventions

### Icon Generation
- Icon generator functions take no parameters and return SVG strings
- Icon names in CSV must match keys in `*_ICON_GENERATORS` dictionaries (case-sensitive)
- Missing icon generators will raise errors during generation
- Icons are designed to fit within a 100mm square area before scaling

### File Naming
- Input CSV must have exact column names: `name,description,top_symbol,side_symbol,reorder_url`
- Output files named using `name` field - ensure no special characters/spaces

### Color Handling
- Colors default to `#000000` if empty/missing in CSV
- SVG elements use inline `fill` attributes for color specification

### Issues to Watch
- No error handling for missing/malformed icon paths or reorder URLs
- No handling for malformed CSV rows
- Assumes all icons specified in CSV have corresponding generator functions (will error if missing)
- QR generation will proceed even with empty URLs (may produce blank/minimal QR)
