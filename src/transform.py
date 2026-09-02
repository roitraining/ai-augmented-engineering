"""
transform.py -- Market data transformation pipeline stage

Reads enriched CSV from ingest.py, applies normalisation and derived
field calculations, and writes transformed records to stdout as CSV.

Usage:
    python src/transform.py data/python_output.csv > data/transformed.csv
"""

import csv
import logging
import re
import sys
from pathlib import Path
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

BLOCK_THRESHOLD = 1_000_000
LARGE_THRESHOLD =   100_000
MID_THRESHOLD   =    10_000

TS_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")

CRITICAL_FIELDS = {"record_id", "price", "volume"}


def classify_size(notional: float) -> str:
    """Classify a trade notional value into a size bucket.

    Args:
        notional: Trade notional value (price * volume).

    Returns:
        One of: BLOCK, LARGE, MID, SMALL.
    """
    if notional >= BLOCK_THRESHOLD:
        return "BLOCK"
    if notional >= LARGE_THRESHOLD:
        return "LARGE"
    if notional >= MID_THRESHOLD:
        return "MID"
    return "SMALL"


def validate_timestamp(ts: Optional[str]) -> bool:
    """Validate a timestamp string matches YYYY-MM-DD HH:MM:SS.

    Args:
        ts: Timestamp string to validate.

    Returns:
        True if the format is valid, False otherwise.
    """
    if not ts:
        return False
    return bool(TS_PATTERN.match(ts))


def transform_records(records: list[dict]) -> list[dict]:
    """Apply transformations to a list of enriched market data records.

    Transformations:
        - Normalises price to 4 decimal places.
        - Calculates notional (price * volume).
        - Classifies notional into size bucket.
        - Flags whether FIGI was resolved.
        - Validates timestamp format.

    Args:
        records: List of enriched record dicts from ingest.py output.

    Returns:
        List of transformed record dicts with additional fields.
    """
    logger.info(f"Starting transform_records with {len(records)} records")

    output: list[dict] = []
    skipped = 0

    for r in records:
        record_id = r.get("record_id") or "?"

        price_raw  = r.get("price")
        volume_raw = r.get("volume")

        if price_raw is None or volume_raw is None:
            logger.warning(f"Skipping record {record_id}: missing price or volume")
            skipped += 1
            continue

        try:
            price  = float(price_raw)
            volume = int(volume_raw)
        except ValueError:
            logger.warning(
                f"Skipping record {record_id}: non-numeric price={price_raw!r}"
                f" or volume={volume_raw!r}"
            )
            skipped += 1
            continue

        if price <= 0 or volume <= 0:
            logger.warning(
                f"Skipping record {record_id}: non-positive price={price} or volume={volume}"
            )
            skipped += 1
            continue

        notional     = price * volume
        size_bucket  = classify_size(notional)
        figi_resolved = int(
            bool(r.get("figi")) and r.get("figi") != "UNKNOWN"
        )
        ts_valid = int(validate_timestamp(r.get("timestamp")))

        output.append({
            **r,
            "price":         f"{price:.4f}",
            "notional":      notional,
            "size_bucket":   size_bucket,
            "figi_resolved": figi_resolved,
            "ts_valid":      ts_valid,
        })

    logger.info(
        f"Completed transform_records: {len(output)} transformed, {skipped} skipped"
    )
    return output

def append_to_daily_summary(record: dict, output_path: Path) -> None:
    with output_path.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(record.keys()))
        writer.writerow(record)

def main(input_file: str) -> None:
    """Run the transform pipeline stage.

    Args:
        input_file: Path string to the enriched input CSV.
    """
    logger.info(f"Starting transform pipeline for {input_file}")

    input_path = Path(input_file)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with input_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        records = list(reader)

    transformed = transform_records(records)

    if not transformed:
        logger.error("No records survived transformation")
        sys.exit(1)

    out_fields = list(records[0].keys()) + [
        "notional", "size_bucket", "figi_resolved", "ts_valid"
    ]

    writer = csv.DictWriter(sys.stdout, fieldnames=out_fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(transformed)



if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <input_csv>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])
