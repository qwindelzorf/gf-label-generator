# Gridfinity Label Generator — Copilot Instructions (for AI coding agents)

Purpose: help an AI agent become productive quickly in this repo by summarizing architecture, workflows, conventions, and important code patterns discovered in `generator.py`, `template.svg`, and `shapes.py`.

Core files
- `generator.py`: main program — CSV -> templated SVG -> exported PNG/PDF/SVG. Key functions: `generate_labels()`, `make_qr_svg()`, `compose_icons()`, `mm_to_px()`.
- `template.svg`: Jinja2 SVG template. Expects variables: `LABEL_WIDTH_MM`, `LABEL_HEIGHT_MM`, `name`, `description`, `icon_svg`, `qr_svg`, `qr_size`.
- `shapes.py`: icon generator functions that return SVG snippets (strings) used by mappings in `generator.py`.
- `parts.csv`: canonical input CSV; exact column names required: `name,description,top_symbol,side_symbol,reorder_url`.

Big picture
- Data flow: read `parts.csv` -> for each row, map `top_symbol`/`side_symbol` to generator functions in `TOP_ICON_GENERATORS`/`SIDE_ICON_GENERATORS` -> compose icon SVG via `compose_icons()` -> create QR SVG via `make_qr_svg()` -> render `template.svg` with Jinja2 -> convert to PNG/PDF (CairoSVG) or write raw SVG.
- Why structure is this way: SVG templating keeps layout vector-first; icon generators produce small SVG fragments so labels stay compact and fully vector; QR generation is embedded as SVG to preserve sharpness.

Important, project-specific patterns & gotchas
- Icon registries: `TOP_ICON_GENERATORS` and `SIDE_ICON_GENERATORS` map CSV token -> function in `shapes.py`. Keys are case-sensitive and must match the CSV values.
- `compose_icons(top_icon, side_icon)`: if both present, returns positioned `<g>` groups scaled to a 100x100-like view. If only one icon present the raw icon SVG is used.
- QR generation (`make_qr_svg`): attempts to shorten HTTP(S) URLs via `https://v.gd` to fit micro QR codes; strips URL scheme before micro-QR encoding; falls back to standard QR when too long; returns (svg_body, symbol_size). It also strips the XML declaration to avoid duplication when embedding.
- Template variables: `qr_size` passed into the template is the QR symbol size used by the template to scale placement. The template computes `qr_scale` and positions the QR on the right.
- Measurement units: label sizes are in millimeters. `mm_to_px()` uses `LABEL_PRINTER_DPI` (default 150) — changing DPI affects output raster sizes.
- Filename policy: output filename is built from `name` and `description` with specific sanitization (`/` replaced with `-`, spaces to `_`) — keep this when modifying filename logic.
- Logging: `generator.py` defines custom logging helpers (`debug`, `info`, `print`, `warn`, `error`) and a `LOG_LEVEL` enum. CLI flags `-q/--quiet` and `-v/--verbose` adjust `LOG_LEVEL`.

How to run (developer workflows)
- Create/activate virtualenv and install deps:
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
- Run generator (defaults to `parts.csv`, `template.svg`, `output/`):
```
python3 generator.py
```
- Useful flags:
  - `--format` choose output: `png` (default), `pdf`, or `svg`.
  - `--qr-type` choose `micro` (default) or `standard`.
  - `-q/--quiet` suppresses non-error logs.
  - `-v/--verbose` increase logging verbosity (repeatable).

Where to look for change points
- If adding new icon types: add a generator in `shapes.py` and register it in both `TOP_ICON_GENERATORS`/`SIDE_ICON_GENERATORS` as needed.
- If changing label layout: edit `template.svg` — template expects the SVG snippet for `icon_svg` and `qr_svg` already scaled; the template uses mm-based font sizes and positions.
- If changing QR behavior: update `make_qr_svg()` (URL shortening, micro vs standard logic, border, or SVG cleanup).

Testing & iteration tips for agents
- Quick local run: create a small `parts.csv` row and run `python3 generator.py --format=svg` to inspect the produced SVG (fast, no Cairo dependency required for viewing vectors).
- When modifying icon functions, returning valid SVG fragments (no XML declaration, valid viewBox or paths) keeps embedding simple.
- To debug layout, open the generated SVG in a vector viewer (Inkscape or browser) rather than raster output.

Files/locations to reference often
- `generator.py` — orchestrator and source of most behavioral details
- `template.svg` — layout rules (font sizes computed from `LABEL_HEIGHT_MM`)
- `shapes.py` — icon primitives
- `parts.csv` — example data and required CSV columns
- `requirements.txt` — external deps: `segno`, `jinja2`, `cairosvg`, `requests`

Next steps for the agent
- Preserve existing README content when updating docs; edit `template.svg` only when confident about mm-to-px impacts; prefer generating `svg` outputs to iterate quickly.

If any part of the repo or a workflow is unclear, tell me which file or behavior you want clarified and I will expand this doc or add inline comments in the code.
