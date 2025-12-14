from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


SELECTED_COLUMNS = [
    "Enter your Section",
    "Username",
    "Enter your Name (FN, MI, LN)",
    "What is your wish #1? (Priority Wish)",
    "Describe your wish #1! (Priority Wish)",
    "What is your wish #2? ",
    "Describe your wish #2! ",
    "What is your wish #3? ",
    "Describe your wish #3! ",
]

ATTEND_COL = "Will you attend the event and participate in our exchange of gifts?"
ATTEND_VALUE = "Will attend and Will participate for the Exchange Gifts"
SECTION_VALUE = "BSCS 2-1N"


def normalize_fieldnames(fieldnames: list[str]) -> dict[str, str]:
    return {name.strip(): name for name in fieldnames}


def filter_and_write(input_path: Path, output_path: Path) -> int:
    with input_path.open("r", encoding="utf-8-sig", newline="") as infile:
        reader = csv.DictReader(infile)
        if reader.fieldnames is None:
            raise SystemExit("No header found in input CSV")

        norm_map = normalize_fieldnames(reader.fieldnames)

        # Check required columns exist
        for required in (ATTEND_COL, "Enter your Section"):
            if required not in norm_map:
                # maybe with slightly different spacing, check normalized variants
                if required.strip() not in norm_map:
                    print(f"Warning: required column '{required}' not found in input CSV", file=sys.stderr)

        matched = 0
        total = 0

        with output_path.open("w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=SELECTED_COLUMNS)
            writer.writeheader()

            for row in reader:
                total += 1

                # safely get normalized values
                def val(col_name: str) -> str:
                    orig = norm_map.get(col_name.strip())
                    if orig is None:
                        return ""
                    return (row.get(orig) or "").strip()

                section = val("Enter your Section")
                attend = val(ATTEND_COL)

                if section == SECTION_VALUE and attend == ATTEND_VALUE:
                    out_row = {col: val(col) for col in SELECTED_COLUMNS}
                    writer.writerow(out_row)
                    matched += 1

    print(f"Processed {total} rows, matched {matched} rows. Output: {output_path}")
    return matched


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Clean attendance CSV for BSCS 2-1N participants")
    p.add_argument("input", help="Input CSV file path")
    p.add_argument("-o", "--output", default="2-2_cleaned.csv", help="Output CSV path")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    filter_and_write(input_path, output_path)


if __name__ == "__main__":
    main()