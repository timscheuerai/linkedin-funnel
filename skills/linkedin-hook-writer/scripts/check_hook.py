#!/usr/bin/env python3
"""Count a LinkedIn opening; character slices are NOT rendered feed previews."""

import argparse
import json
import sys
from pathlib import Path


def analyze(source: str) -> dict:
    text = source.replace("\r\n", "\n").replace("\r", "\n")
    first_line = ""
    opening_end = 0
    content_lines = 0
    offset = 0
    for line in text.splitlines(keepends=True):
        # A trailing line separator is excluded from the line length, but
        # intervening separators remain part of the opening block.
        body = line.removesuffix("\n")
        if body.strip():
            content_lines += 1
            if content_lines == 1:
                first_line = body
            opening_end = offset + len(body)
            if content_lines == 2:
                break
        offset += len(line)

    opening = text[:opening_end]
    warnings = []
    if not text.strip():
        warnings.append("No post text supplied.")
    if text and text[0].isspace():
        warnings.append("Leading whitespace spends opening space; check it is intentional.")
    if len(first_line) > 60:
        warnings.append("First line exceeds the soft 60-character target; judge clarity, do not auto-reject.")
    if len(opening) > 140:
        warnings.append("Opening block exceeds 140 characters; check that the essential point arrives earlier.")
    if "\n\n" in opening:
        warnings.append("Opening includes a blank line; rendered visibility may be shorter than the character slice.")
    total_utf16 = len(text.encode("utf-16-le")) // 2
    if len(text) > 3000:
        warnings.append("Full text exceeds the documented 3,000-character post limit.")
    elif total_utf16 > 3000:
        warnings.append("UTF-16 length exceeds 3,000; confirm the composer's Unicode count or shorten.")

    return {
        "measurement": "Unicode code points; whitespace preserved; CRLF/CR normalized to LF",
        "preview_status": "Character slices only. No rendered-line or exact see-more simulation.",
        "total_characters": len(text),
        "total_utf16_units": total_utf16,
        "first_content_line": first_line,
        "first_content_line_characters": len(first_line),
        "opening_block": opening,
        "opening_block_definition": "Start through the end of the second nonempty source line, or the only nonempty line",
        "opening_block_characters": len(opening),
        "opening_hard_line_breaks": opening.count("\n"),
        "slice_140": text[:140],
        "slice_210": text[:210],
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", nargs="?", help="UTF-8 plain-text draft; stdin when omitted")
    parser.add_argument("--json", action="store_true", help="Return machine-readable counts")
    args = parser.parse_args()
    try:
        source = Path(args.file).read_text(encoding="utf-8") if args.file else sys.stdin.read()
    except (OSError, UnicodeError) as exc:
        parser.error(str(exc))
    result = analyze(source)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result["measurement"])
        print(f"First content line: {result['first_content_line_characters']} characters (soft target: about 40-60)")
        print(f"Opening block: {result['opening_block_characters']} characters (working budget: 140)")
        print(f"Full post: {result['total_characters']} characters; {result['total_utf16_units']} UTF-16 units")
        print(result["preview_status"])
        for budget in (140, 210):
            print(f"\nFirst {budget} characters, stress check only:\n{result[f'slice_{budget}']}")
        for warning in result["warnings"]:
            print(f"\nNOTE: {warning}")
    return 0 if source.strip() else 1


if __name__ == "__main__":
    raise SystemExit(main())
