# Gridfinity Label Generator

Small tool to generate Gridfinity bin labels (SVG -> PNG/PDF) from a CSV.

## Overview

- Core idea: read `parts.csv`, compose an icon and QR (as embedded SVG), render a Jinja2 `template.svg` per row, and export PNG/PDF/SVG via CairoSVG when requested.

## Core files

- `generator.py`: main program and CLI (CSV -> templated SVG -> exported PNG/PDF/SVG).
- `template.svg`: the Jinja2 SVG label template used for layout.
- `shapes.py`: icon generator functions and icon registries used by the generator.
- `parts.csv`: canonical input CSV. Required columns: `name,description,top_symbol,side_symbol,reorder_url`.
- `requirements.txt`: Python dependencies (see Quickstart).
- `output/`: default output folder for generated files.

## Quickstart

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

1. Install dependencies:

```bash
pip install -r requirements.txt
```

1. Run the generator (defaults: `parts.csv` -> `output/`):

```bash
python3 generator.py
```

### Useful flags

- `--format` : `png` (default), `pdf`, or `svg`.
- `--qr-type` : `micro` (default) or `standard`.
- `-q/--quiet` : suppress non-error logs.
- `-v/--verbose` : increase logging verbosity (repeatable).

## Notes & tips

- Icon registration: add or modify icon generators in `shapes.py` and register them in `TOP_ICON_GENERATORS` / `SIDE_ICON_GENERATORS`. Tokens are case-sensitive and must match CSV values.
- QR generation: URLs are shortened (v.gd) when possible for micro-QRs; the generator embeds QR as raw SVG to keep vector quality.
- Template units: label sizes are mm. `mm_to_px()` converts to pixels using `LABEL_PRINTER_DPI` (default 150). Changing DPI affects raster output sizes.
- Fast iteration: use `--format=svg` to inspect vector output quickly without CairoSVG rasterization.
- Filenames: output filenames are derived from `name` and `description` with simple sanitization (spaces -> `_`, `/` -> `-`).
- Debugging: open generated SVGs in a browser or Inkscape to check layout before producing PNG/PDF.

## Troubleshooting

- If CairoSVG fails, verify system packages for Cairo and Pango are installed, or export SVG only with `--format=svg`.

License / Contributions

Feel free to open issues or PRs to add icons, tweak the template, or improve QR handling.
