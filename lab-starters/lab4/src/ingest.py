"""
ingest.py -- Market data identifier ingestion pipeline

Reads a CSV file of market data records, resolves each instrument
identifier to its OpenFIGI code using FigiClient, counts lookup
frequency by exchange code, and writes enriched records to stdout as CSV.

Usage:
    python src/ingest.py data/sample_input.csv > data/python_output.csv
"""

import csv
import logging
import sys
from collections import Counter
from pathlib import Path
from typing import Optional

from src.figi_client import FigiClient, FigiClientError

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

CRITICAL_FIELDS = {"instrument_id", "exchange_code", "price", "volume", "record_id"}


def load_records(input_path: Path) -> list[dict]:
    """Load market data records from a CSV file.

    Args:
        input_path: Path to the input CSV file.

    Returns:
        List of record dicts with string values for all columns.

    Raises:
        FileNotFoundError: If input_path does not exist.
        ValueError: If the CSV file contains no records.
    """
    logger.info(f"Starting load_records from {input_path}")

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    records: list[dict] = []
    with input_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            for field in CRITICAL_FIELDS:
                if row.get(field) is None:
                    logger.warning(
                        f"Record {row.get('record_id', '?')}: missing critical field {field}"
                    )
            records.append(dict(row))

    if not records:
        raise ValueError(f"No records found in {input_path}")

    logger.info(f"Completed load_records: {len(records)} records loaded")
    return records


def resolve_figis(
    records: list[dict],
    client: FigiClient,
) -> dict[str, str]:
    """Resolve instrument identifiers to OpenFIGI codes.

    Args:
        records: List of market data record dicts.
        client:  Configured FigiClient instance.

    Returns:
        Mapping of instrument_id to FIGI string (or 'UNKNOWN' on failure).
    """
    logger.info(f"Starting resolve_figis with {len(records)} records")

    identifiers = [
        {
            "idType": r.get("id_type") or "TICKER",
            "idValue": r["instrument_id"],
            "exchCode": r.get("exchange_code") or None,
        }
        for r in records
        if r.get("instrument_id")
    ]

    try:
        results = client.do_request(identifiers)
    except FigiClientError as exc:
        logger.error(f"FigiClient request failed: {exc}")
        results = None

    figi_map: dict[str, str] = {}
    if results:
        for i, item in enumerate(results):
            instrument_id = identifiers[i]["idValue"]
            data = item.get("data") if item else None
            figi_map[instrument_id] = data[0]["figi"] if data else "UNKNOWN"
    else:
        for ident in identifiers:
            figi_map[ident["idValue"]] = "UNKNOWN"

    logger.info(f"Completed resolve_figis: {len(figi_map)} identifiers resolved")
    return figi_map


def rank_exchanges(records: list[dict]) -> tuple[Counter, dict[str, int]]:
    """Count and rank exchanges by lookup frequency.

    Exchanges with equal counts are ranked by exchange_code ascending,
    so the ranking is deterministic regardless of input order.

    Args:
        records: List of market data record dicts.

    Returns:
        Tuple of (exchange_counts Counter, exchange_rank dict).
    """
    logger.info(f"Starting rank_exchanges with {len(records)} records")

    exchange_counts: Counter = Counter(
        r.get("exchange_code") or "UNKNOWN" for r in records
    )

    # Sort descending by count, then by exchange_code so ties are deterministic.
    sorted_exchanges = sorted(exchange_counts, key=lambda e: (-exchange_counts[e], e))

    exchange_rank = {exch: rank + 1 for rank, exch in enumerate(sorted_exchanges)}

    logger.info(f"Completed rank_exchanges: {len(exchange_counts)} exchanges ranked")
    return exchange_counts, exchange_rank


def write_output(
    records: list[dict],
    figi_map: dict[str, str],
    exchange_counts: Counter,
    exchange_rank: dict[str, int],
) -> None:
    """Write enriched records to stdout as CSV.

    Args:
        records:         Original market data records.
        figi_map:        instrument_id -> FIGI mapping.
        exchange_counts: Count of records per exchange.
        exchange_rank:   Rank of each exchange by frequency.
    """
    logger.info(f"Starting write_output for {len(records)} records")

    out_cols = [
        "record_id", "instrument_id", "id_type", "exchange_code",
        "figi", "price", "volume", "timestamp", "lookup_count", "exchange_rank",
    ]

    writer = csv.DictWriter(sys.stdout, fieldnames=out_cols, lineterminator="\n")
    writer.writeheader()

    for r in records:
        instrument_id = r.get("instrument_id") or ""
        exchange_code = r.get("exchange_code") or "UNKNOWN"
        writer.writerow({
            "record_id":     r.get("record_id") or "",
            "instrument_id": instrument_id,
            "id_type":       r.get("id_type") or "",
            "exchange_code": exchange_code,
            "figi":          figi_map.get(instrument_id, "UNKNOWN"),
            "price":         r.get("price") or "",
            "volume":        r.get("volume") or "",
            "timestamp":     r.get("timestamp") or "",
            "lookup_count":  exchange_counts.get(exchange_code, 0),
            "exchange_rank": exchange_rank.get(exchange_code, 0),
        })

    logger.info("Completed write_output")


def main(input_file: str) -> None:
    """Run the ingest pipeline.

    Args:
        input_file: Path string to the input CSV file.
    """
    logger.info(f"Starting ingest pipeline for {input_file}")

    input_path = Path(input_file)
    records = load_records(input_path)

    client = FigiClient()
    figi_map = resolve_figis(records, client)
    exchange_counts, exchange_rank = rank_exchanges(records)
    write_output(records, figi_map, exchange_counts, exchange_rank)

    logger.info("Ingest pipeline complete")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <input_csv>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])
