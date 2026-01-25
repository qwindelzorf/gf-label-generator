#!/usr/bin/env python3

"""
Shorten URLs in a spreadsheet:
- Reads spreadsheets (CSV, Excel ".xlsx", Apple Numbers ".numbers", OpenDocument ".ods")
- For each row, takes the `reorder_url` column
- Shortens the URL using the v.gd API
- Outputs result to a `short_url` column (creates if it doesn't exist)
- Preserves all other data unchanged
"""

import argparse
import sys
from pathlib import Path


# Import functions from generator.py
from generator import is_url, shorten_url, parse_spreadsheet, write_spreadsheet, debug, info, error, LogLevel


def shorten_urls_in_spreadsheet(input_file: Path, output_file: Path) -> None:
    """Read a spreadsheet, shorten URLs in the `reorder_url` column, write the results into a `short_url` column."""
    # Parse the input spreadsheet
    rows = parse_spreadsheet(input_file)
    debug(f"Parsed {len(rows)} rows from {input_file}")

    # Process each row
    urls_shortened = 0
    urls_skipped = 0

    for row in rows:
        reorder_url = str(row.get("reorder_url", "")).strip()

        if reorder_url and is_url(reorder_url):
            try:
                short_url = shorten_url(reorder_url)
                row["short_url"] = short_url
                debug(f"Shortened: {reorder_url} -> {short_url}")
                urls_shortened += 1
            except ValueError as e:
                error(f"Failed to shorten URL '{reorder_url}': {e}")
                row["short_url"] = ""
                urls_skipped += 1
        else:
            row["short_url"] = ""
            urls_skipped += 1

    # Write the updated spreadsheet
    write_spreadsheet(rows, output_file)
    info(f"Shortened {urls_shortened} URLs, skipped {urls_skipped} empty or invalid URLs")
    print(f"Updated spreadsheet written to: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Shorten URLs in a spreadsheet using the v.gd API")
    parser.add_argument(
        "input_file",
        type=Path,
        help="Path to the input spreadsheet file (CSV, Excel, ODS, or Numbers)",
    )
    parser.add_argument(
        "output_file",
        type=Path,
        nargs="?",
        help="Path to the output spreadsheet file (default: update input file)",
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

    # Determine output file (default to input file if not specified)
    output_file = args.output_file if args.output_file else args.input_file

    # Check input file exists
    if not args.input_file.exists():
        error(f"Input file '{args.input_file}' does not exist.")
        sys.exit(1)

    try:
        shorten_urls_in_spreadsheet(args.input_file, output_file)
    except Exception as e:
        error(f"Failed to process spreadsheet: {e}")
        sys.exit(1)
