# Gridfinity Label Generator

This project procedurally generates labels for Gridfinity bins

## Summary / approach

- Data source: CSV or JSON describing each part (sku, name, description, icon SVG path or category, reorder URL).
- Layout: single SVG template per label (vector, size in mm). Template contains placeholders for: icon (embedded SVG), name/description text, and QR code (SVG).
- Generation: fill SVG with data per row (Jinja2 templating), generate QR as SVG (segno), embed icon SVG or a generated silhouette, then convert each filled SVG to PDF or PNG (CairoSVG).
- Printing: print PNGs to a lable printer (e.g.: via `ptouch-print`)

## Setup

Install the python requirments from `requirements.txt`. I recommend using a virtual environment.

## Usage

Configure your parts in a CSV file, then run the script. It will generate files to be printed into the specified folder
