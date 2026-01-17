#!/usr/bin/env python3

"""
Label generator:
- Reads spreadsheets (CSV, Excel ".xlsx", Apple Numbers ".numbers", OpenDocument ".ods") with columns:
  - name
  - description
  - top_symbol
  - side_symbol
  - reorder_url
- Generates an SVG label per row by filling a template SVG (template.svg)
- Creates QR code SVG using segno and embeds it into the template
- Converts final SVG into output format (one file per label) using cairosvg
"""

import argparse
import io
from pathlib import Path
import sys
from typing import Callable
from urllib.parse import quote
import segno
from jinja2 import Template
import cairosvg
import colorama
import requests

import shapes as shape_gen

# Configuration
LABEL_WIDTH_MM = 36
LABEL_HEIGHT_MM = 8.9  # should be 9mm, but leave some margin
LABEL_PRINTER_DPI = 150  # for Brother P710BT label printer


# Icon generator functions - split into side and top view registries
# Each function receives a dict with row data from CSV
SIDE_ICON_GENERATORS: dict[str, Callable] = {
    "washer": shape_gen.washer_std_side,
    "washer_flat": shape_gen.washer_std_side,
    "washer_fender": shape_gen.washer_fender_side,
    "washer_split": shape_gen.washer_split_side,
    "split": shape_gen.washer_split_side,
    "star_i": shape_gen.washer_star_inner_side,
    "star_inner": shape_gen.washer_star_inner_side,
    "washer_star_inner": shape_gen.washer_star_inner_side,
    "star": shape_gen.washer_star_outer_side,
    "star_o": shape_gen.washer_star_outer_side,
    "star_outer": shape_gen.washer_star_outer_side,
    "washer_star": shape_gen.washer_star_outer_side,
    "washer_star_outer": shape_gen.washer_star_outer_side,
    "nut": shape_gen.nut_standard_side,
    "nut_standard": shape_gen.nut_standard_side,
    "nut_thin": shape_gen.nut_thin_side,
    "nut_lock": shape_gen.nut_lock_side,
    "nyloc": shape_gen.nut_lock_side,
    "nut_nyloc": shape_gen.nut_lock_side,
    "nut_flange": shape_gen.nut_flange_side,
    "nut_cap": shape_gen.nut_cap_side,
    "nut_acorn": shape_gen.nut_cap_side,
    "nut_wing": shape_gen.nut_wing_side,
    "wing": shape_gen.nut_wing_side,
    "insert_heat": shape_gen.insert_heat_side,
    "insert_wood": shape_gen.insert_wood_side,
    "insert_press": shape_gen.insert_press_side,
    "button": shape_gen.button_head_side,
    "bhcs": shape_gen.button_head_side,
    "socket": shape_gen.cap_head_side,
    "shcs": shape_gen.cap_head_side,
    "hex": shape_gen.hex_head_side,
    "countersink": shape_gen.flush_head_side,
    "cs": shape_gen.flush_head_side,
    "flush": shape_gen.flush_head_side,
    "wood_screw": shape_gen.wood_screw_side,
    "bearing": shape_gen.bearing_side,
    "bearing_flange": shape_gen.bearing_flange_side,
    "spring": shape_gen.spring_side,
    "coil_spring": shape_gen.spring_side,
}

TOP_ICON_GENERATORS: dict[str, Callable] = {
    "washer": shape_gen.washer_std_top,
    "washer_flat": shape_gen.washer_std_top,
    "washer_fender": shape_gen.washer_fender_top,
    "washer_split": shape_gen.washer_split_top,
    "split": shape_gen.washer_split_top,
    "star": shape_gen.washer_star_outer_top,
    "star_o": shape_gen.washer_star_outer_top,
    "star_outer": shape_gen.washer_star_outer_top,
    "washer_star": shape_gen.washer_star_outer_top,
    "washer_star_outer": shape_gen.washer_star_outer_top,
    "star_i": shape_gen.washer_star_inner_top,
    "star_inner": shape_gen.washer_star_inner_top,
    "washer_star_inner": shape_gen.washer_star_inner_top,
    "nut": shape_gen.nut_standard_top,
    "nut_standard": shape_gen.nut_standard_top,
    "nut_thin": shape_gen.nut_thin_top,
    "nut_lock": shape_gen.nut_lock_top,
    "nyloc": shape_gen.nut_lock_top,
    "nut_nyloc": shape_gen.nut_lock_top,
    "nut_flange": shape_gen.nut_flange_top,
    "nut_cap": shape_gen.nut_cap_top,
    "nut_acorn": shape_gen.nut_cap_top,
    "nut_wing": shape_gen.nut_wing_top,
    "wing": shape_gen.nut_wing_top,
    "insert_heat": shape_gen.insert_heat_top,
    "insert_wood": shape_gen.insert_wood_top,
    "insert_press": shape_gen.insert_wood_top,  # same as wood insert top
    "hex": shape_gen.head_hex_top,
    "socket": shape_gen.head_socket_top,
    "cap": shape_gen.head_socket_top,
    "torx": shape_gen.head_torx_top,
    "slotted": shape_gen.head_slotted_top,
    "flat": shape_gen.head_slotted_top,
    "phillips": shape_gen.head_phillips_top,
    "square": shape_gen.head_square_top,
    "pozidriv": shape_gen.head_pozidriv_top,
    "pozi": shape_gen.head_pozidriv_top,
    "bearing": shape_gen.bearing_top,
    "spring": shape_gen.spring_top,
    "coil_spring": shape_gen.spring_top,
}


# simple logging functions
# enum representing log levels
class LogLevel:
    """Enum representing log levels for the label generator."""

    DEBUG = -2
    INFO = -1
    NORMAL = 0
    WARNING = 1
    ERROR = 2


LOG_LEVEL = LogLevel.NORMAL
xprint = print  # backup the normal print function


def debug(msg: str, *args, **kwargs) -> None:
    """Log a debug message if the current log level is DEBUG or lower."""
    if LOG_LEVEL <= LogLevel.DEBUG:
        xprint(
            f"{colorama.Fore.BLUE}[DEBUG] {msg}{colorama.Style.RESET_ALL}",
            *args,
            **kwargs,
        )


def info(msg: str, *args, **kwargs) -> None:
    """Log an info message if the current log level is INFO or lower."""
    if LOG_LEVEL <= LogLevel.INFO:
        xprint(
            f"{colorama.Fore.GREEN}[INFO ] {msg}{colorama.Style.RESET_ALL}",
            *args,
            **kwargs,
        )


def print(msg: str, *args, **kwargs) -> None:
    """Log a normal message if the current log level is NORMAL or lower."""
    if LOG_LEVEL <= LogLevel.NORMAL:
        xprint(msg, *args, **kwargs)


def warn(msg: str, *args, **kwargs) -> None:
    """Log a warning message if the current log level is WARNING or lower."""
    if LOG_LEVEL <= LogLevel.WARNING:
        xprint(
            f"{colorama.Fore.YELLOW}[WARN ] {msg}{colorama.Style.RESET_ALL}",
            *args,
            **kwargs,
        )


def error(msg: str, *args, **kwargs) -> None:
    """Log an error message if the current log level is ERROR or lower."""
    if LOG_LEVEL <= LogLevel.ERROR:
        if "file" not in kwargs:
            kwargs["file"] = sys.stderr
        xprint(
            f"{colorama.Fore.RED}[ERROR] {msg}{colorama.Style.RESET_ALL}",
            *args,
            **kwargs,
        )


#######################
# Program code
#######################


def read_template(template_file: Path) -> Template:
    """Read an SVG template file and return a Template object."""
    with template_file.open("r", encoding="utf-8") as f:
        return Template(f.read())


def shorten_url(url: str) -> str:
    """Shorten a URL using the v.gd API."""
    if not url.startswith("http://") and not url.startswith("https://"):
        return url
    api_base = "https://v.gd/create.php?format=simple&url="
    try:
        response = requests.get(api_base + quote(url, safe=""), timeout=5)
        response.raise_for_status()
        payload = response.text.strip()

        # strip scheme for more compact encoding
        if payload.startswith("http://"):
            payload = payload[len("http://") :]
        elif payload.startswith("https://"):
            payload = payload[len("https://") :]

        return payload
    except requests.RequestException as e:
        warn(f"URL shortening failed for {url}: {e}")
        return url


def make_qr_svg(content: str, scale_mm: float, qr_type: str = "micro") -> tuple[str, float]:
    """Generate a QR code as an SVG string and return it along with its size in modules."""
    # Create QR as SVG string. segno uses px units; we'll embed SVG and scale via width/height attrs
    # Try running the URL through a shortener, then remove the leading 'http(s)://', so that micro QR can fit more data

    if not content:
        return "", 0

    api_base = "https://v.gd/create.php?format=simple&url="
    create_url = api_base + quote(content, safe="")

    if qr_type not in ("micro", "standard"):
        raise ValueError(f"Invalid qr_type: {qr_type}")

    payload = content
    debug(f"Generating {qr_type} QR for content: {content}")
    qr = None
    if qr_type == "standard":
        qr = segno.make(content)
    elif qr_type == "micro":
        payload = shorten_url(content)
        try:
            # Try to make a micro QR code
            qr = segno.make(payload, micro=(qr_type == "micro"))
        except ValueError:
            # Fallback to standard QR if micro QR is not possible
            info(f"URL too long for micro QR, using standard QR: {content}")
            qr = segno.make(payload, micro=False)
    if qr is None:
        raise RuntimeError("Failed to generate QR code")

    buf = io.BytesIO()
    qr.save(buf, kind="svg", border=0)  # raw svg bytes
    svg_bytes = buf.getvalue().decode("utf-8")
    # strip xml declaration to avoid duplicates when embedding
    svg_body = "\n".join(line for line in svg_bytes.splitlines() if not line.startswith("<?xml"))
    return (svg_body, qr.symbol_size()[0])


def mm_to_px(mm: float) -> int:
    """Convert millimeters to pixels based on the label printer DPI."""
    inches = mm / 25.4
    return int(inches * LABEL_PRINTER_DPI)


EXPECTED_COLUMNS = [
    "name",
    "description",
    "top_symbol",
    "side_symbol",
    "reorder_url",
]


def parse_csv(csv_file: Path, delimiter: str = ",") -> list[dict[str, str]]:
    """Parse a CSV file and return a list of dictionaries representing each row."""
    from csv import DictReader

    rows = []
    with open(csv_file, newline="", encoding="utf-8") as f:
        reader = DictReader(f, delimiter=delimiter)
        for row in reader:
            rows.append(
                {
                    "name": row.get("name", "").strip(),
                    "description": row.get("description", "").strip(),
                    "top_symbol": row.get("top_symbol", "").strip(),
                    "side_symbol": row.get("side_symbol", "").strip(),
                    "reorder_url": row.get("reorder_url", "").strip(),
                }
            )
    return rows


def parse_excel(excel_file: Path) -> list[dict[str, str]]:
    """Parse an Excel file and return a list of dictionaries representing each row."""
    from openpyxl import load_workbook

    rows = []
    wb = load_workbook(excel_file, data_only=True)
    ws = wb.active
    headers = [cell.value for cell in ws[1]]
    for row in ws.iter_rows(min_row=2, values_only=True):
        row_dict = {header: (value if value is not None else "") for header, value in zip(headers, row)}
        rows.append(
            {
                "name": row_dict.get("name", "").strip(),
                "description": row_dict.get("description", "").strip(),
                "top_symbol": row_dict.get("top_symbol", "").strip(),
                "side_symbol": row_dict.get("side_symbol", "").strip(),
                "reorder_url": row_dict.get("reorder_url", "").strip(),
            }
        )
    return rows


def parse_numbers(numbers_file: Path) -> list[dict[str, str]]:
    """Parse a Numbers file and return a list of dictionaries representing each row."""
    from numbers_parser import Document

    doc = Document(numbers_file)
    sheet = doc.sheets[0]
    table = sheet.tables[0]
    headers = [cell.value for cell in table.rows()[0]]
    rows = []
    for row in table.rows()[1:]:
        row_dict = {
            header: (cell.value if cell is not None and cell.value is not None else "")
            for header, cell in zip(headers, row)
        }
        rows.append(
            {
                "name": row_dict.get("name", "").strip(),
                "description": row_dict.get("description", "").strip(),
                "top_symbol": row_dict.get("top_symbol", "").strip(),
                "side_symbol": row_dict.get("side_symbol", "").strip(),
                "reorder_url": row_dict.get("reorder_url", "").strip(),
            }
        )
    return rows


def parse_ods(ods_file: Path) -> list[dict[str, str]]:
    """Parse an ODS file and return a list of dictionaries representing each row."""
    from ezodf import opendoc

    doc = opendoc(ods_file)
    sheet = doc.sheets[0]
    headers = [cell.value for cell in sheet.rows()[0]]
    rows = []
    for row in sheet.rows()[1:]:
        row_dict = {header: (cell.value if cell.value is not None else "") for header, cell in zip(headers, row)}
        rows.append(
            {
                "name": row_dict.get("name", "").strip(),
                "description": row_dict.get("description", "").strip(),
                "top_symbol": row_dict.get("top_symbol", "").strip(),
                "side_symbol": row_dict.get("side_symbol", "").strip(),
                "reorder_url": row_dict.get("reorder_url", "").strip(),
            }
        )
    return rows


def parse_spreadsheet(spreadsheet_file: Path) -> list[dict[str, str]]:
    """Parse a spreadsheet file (CSV, TSV, Excel, ODS, Numbers) and return a list of dictionaries representing each row."""
    extension = spreadsheet_file.suffix.lower()
    match extension:
        case ".csv":
            return parse_csv(spreadsheet_file, delimiter=",")
        case ".tsv":
            return parse_csv(spreadsheet_file, delimiter="\t")
        case ".xls" | ".xlsx":
            return parse_excel(spreadsheet_file)
        case ".ods":
            return parse_ods(spreadsheet_file)
        case ".numbers":
            return parse_numbers(spreadsheet_file)
        case _:
            raise ValueError(f"Unsupported spreadsheet format: {spreadsheet_file.suffix}")


def generate_labels(
    parts_file_path: Path,
    template_file: Path,
    output_dir: Path,
    qr_type: str = "micro",
    output_format: str = "png",
) -> None:
    """Generate labels for the parts listed in the spreadsheet using the provided template."""

    template = read_template(template_file)
    rows = parse_spreadsheet(parts_file_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    for row in rows:
        name = row["name"]
        description = row["description"]
        top_symbol = row["top_symbol"]
        side_symbol = row["side_symbol"]
        reorder_url = row["reorder_url"]
        # Load icons by stem name (print red error if generator missing)
        top_icon = ""
        if top_symbol:
            top_gen = TOP_ICON_GENERATORS.get(top_symbol)
            if top_gen is None:
                error(f"top icon generator not found for '{top_symbol}'")
            else:
                top_icon = top_gen()

        side_icon = ""
        if side_symbol:
            side_gen = SIDE_ICON_GENERATORS.get(side_symbol)
            if side_gen is None:
                error(f"side icon generator not found for '{side_symbol}'")
            else:
                side_icon = side_gen()
        qr_svg, qr_width = make_qr_svg(reorder_url, LABEL_HEIGHT_MM, qr_type=qr_type)

        svg_filled = template.render(
            {
                "LABEL_WIDTH_MM": LABEL_WIDTH_MM,
                "LABEL_HEIGHT_MM": LABEL_HEIGHT_MM,
                "name": name,
                "description": description,
                "top_icon_svg": top_icon,
                "side_icon_svg": side_icon,
                "qr_svg": qr_svg,
                "qr_size": qr_width,  # size of the generated QR code in mm
            }
        )

        # Use name for filename (sanitize for filesystem)
        filename = name.replace("/", "-").replace(" ", "_") + "+" + description.replace(" ", "_").replace("/", "-")
        out_file_path = output_dir / f"{filename}.{output_format}"

        match output_format:
            case "svg":
                # write SVG output
                with out_file_path.open("w", encoding="utf-8") as f:
                    f.write(svg_filled)
            case "pdf":
                # Write PDF output
                cairosvg.svg2pdf(
                    bytestring=svg_filled.encode("utf-8"),
                    write_to=str(out_file_path),
                    output_width=mm_to_px(LABEL_WIDTH_MM),
                    output_height=mm_to_px(LABEL_HEIGHT_MM),
                )
            case "png":
                # Write PNG output
                cairosvg.svg2png(
                    bytestring=svg_filled.encode("utf-8"),
                    write_to=str(out_file_path),
                    output_width=mm_to_px(LABEL_WIDTH_MM),
                    output_height=mm_to_px(LABEL_HEIGHT_MM),
                )
        print(f"Generated: {out_file_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate labels for Gridfinity bins from a spreadsheet")
    parser.add_argument(
        "parts_file",
        type=Path,
        nargs="?",
        default=Path("parts.csv"),
        help="Path to the parts CSV file (default: parts.csv)",
    )
    parser.add_argument(
        "template_file",
        type=Path,
        nargs="?",
        default=Path("template.svg"),
        help="Path to the template SVG file (default: template.svg)",
    )
    parser.add_argument(
        "output_dir",
        type=Path,
        nargs="?",
        default=Path("output"),
        help="Path to the output directory (default: output)",
    )
    parser.add_argument(
        "--format",
        choices=["pdf", "png", "svg"],
        default="png",
        help="Output file format (default: png)",
    )
    parser.add_argument(
        "--qr-type",
        choices=["micro", "standard"],
        default="micro",
        help="Type of QR code to generate (default: micro)",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress non-error log messages",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase logging verbosity (use multiple times for more verbose: -v, -vv, -vvv)",
    )

    args = parser.parse_args()

    # Set log level based on verbosity/quiet flags
    if args.quiet:
        LOG_LEVEL = LogLevel.ERROR  # only errors
    else:
        LOG_LEVEL = max(LogLevel.DEBUG, LogLevel.NORMAL - args.verbose)  # decrease log level with more -v

    # Check input files
    if not args.parts_file.exists():
        error(f"Parts file '{args.parts_file}' does not exist.")
        exit(1)
    if not args.template_file.exists():
        error(f"Template file '{args.template_file}' does not exist.")
        exit(1)

    generate_labels(
        args.parts_file,
        args.template_file,
        args.output_dir,
        qr_type=args.qr_type,
        output_format=args.format,
    )
