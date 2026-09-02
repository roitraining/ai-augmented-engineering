"""
validate.py -- Market data pipeline output validator

Reads transformed CSV from transform.py and validates each record
against the registered schema. Prints a validation report to stdout
and exits non-zero if critical violations are found.

Usage:
    python src/validate.py data/transformed.csv
"""

import csv
import logging
import sys
from pathlib import Path
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

PRICE_PATTERN_4DP = r"^\d+\.\d{4}$"
VALID_SIZE_BUCKETS = {"SMALL", "MID", "LARGE", "BLOCK"}

import re
_price_re = re.compile(r"^\d+\.\d{4}$")


def validate_records(records: list[dict]) -> dict:
    """Validate transformed pipeline records against the registered schema.

    Args:
        records: List of transformed record dicts from transform.py output.

    Returns:
        Dict with keys: record_count, passed_count, critical, warnings, info.
    """
    logger.info(f"Starting validate_records with {len(records)} records")

    seen_ids: set[str] = set()
    critical: list[str] = []
    warnings: list[str] = []
    info: list[str]     = []
    passed = 0

    for r in records:
        record_id = r.get("record_id") or ""
        row = f"record_id={record_id}"
        record_ok = True

        # CRITICAL: record_id present and unique
        if not record_id:
            critical.append(f"{row}: missing record_id")
            record_ok = False
        elif record_id in seen_ids:
            critical.append(f"{row}: duplicate record_id")
            record_ok = False
        seen_ids.add(record_id)

        # CRITICAL: instrument_id present
        if not r.get("instrument_id"):
            critical.append(f"{row}: missing instrument_id")
            record_ok = False

        # CRITICAL: price format (positive, 4 decimal places)
        price_str = r.get("price") or ""
        if not _price_re.match(price_str) or float(price_str) <= 0:
            critical.append(
                f"{row}: price '{price_str}' is not a positive number "
                f"with 4 decimal places"
            )
            record_ok = False

        # CRITICAL: volume positive integer
        vol_str = r.get("volume") or ""
        try:
            vol = int(vol_str)
            if vol <= 0:
                raise ValueError
        except (ValueError, TypeError):
            critical.append(f"{row}: volume '{vol_str}' is not a positive integer")
            record_ok = False

        # CRITICAL: figi resolved
        figi_res = r.get("figi_resolved")
        if str(figi_res) != "1":
            critical.append(f"{row}: figi_resolved=0, FIGI lookup failed")
            record_ok = False

        # WARNING: timestamp valid
        if str(r.get("ts_valid")) != "1":
            warnings.append(f"{row}: ts_valid=0, timestamp format invalid")

        # WARNING: notional positive
        try:
            notional = float(r.get("notional") or 0)
            if notional <= 0:
                warnings.append(f"{row}: notional={notional} is not positive")
        except (ValueError, TypeError):
            warnings.append(f"{row}: notional is not numeric")

        # INFO: size bucket recognised
        bucket = r.get("size_bucket") or ""
        if bucket not in VALID_SIZE_BUCKETS:
            info.append(f"{row}: unknown size_bucket '{bucket}'")

        if record_ok:
            passed += 1

    logger.info(
        f"Completed validate_records: {passed}/{len(records)} passed, "
        f"{len(critical)} critical, {len(warnings)} warnings"
    )

    return {
        "record_count": len(records),
        "passed_count": passed,
        "critical":     critical,
        "warnings":     warnings,
        "info":         info,
    }


def print_report(result: dict) -> int:
    """Print the validation report and return the exit code.

    Args:
        result: Dict returned by validate_records().

    Returns:
        0 if no critical violations, 1 otherwise.
    """
    print("=== Pipeline Validation Report ===")
    print(f"Records processed : {result['record_count']}")
    print(f"Records passed    : {result['passed_count']}")
    print(f"Critical violations: {len(result['critical'])}")
    print(f"Warnings          : {len(result['warnings'])}")
    print(f"Info              : {len(result['info'])}")
    print()

    if result["critical"]:
        print("CRITICAL VIOLATIONS:")
        for v in result["critical"]:
            print(f"  {v}")
        print()

    if result["warnings"]:
        print("WARNINGS:")
        for w in result["warnings"]:
            print(f"  {w}")
        print()

    if result["info"]:
        print("INFO:")
        for i in result["info"]:
            print(f"  {i}")
        print()

    if result["critical"]:
        print("RESULT: FAIL")
        return 1

    print("RESULT: PASS")
    return 0


def main(input_file: str) -> None:
    """Run the validation pipeline stage.

    Args:
        input_file: Path string to the transformed input CSV.
    """
    logger.info(f"Starting validate pipeline for {input_file}")

    import os
        input_path = Path(input_file)
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with input_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        records = list(reader)

    result   = validate_records(records)
    exit_code = print_report(result)

    logger.info("Validate pipeline complete")
    sys.exit(exit_code)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <input_csv>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])
