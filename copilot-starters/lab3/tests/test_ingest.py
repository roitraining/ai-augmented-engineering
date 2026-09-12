"""
tests/test_ingest.py

TDD test suite for src/ingest.py -- written before implementation
and committed to lock the conversion contract.

All tests use mock fixtures. No network calls, no filesystem writes.
"""

import csv
import io
import textwrap
from collections import Counter
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.ingest import load_records, resolve_figis, rank_exchanges, write_output


# ─── Fixtures ─────────────────────────────────────────────────────────────────

SAMPLE_CSV = textwrap.dedent("""\
    record_id,instrument_id,id_type,exchange_code,price,volume,timestamp
    REC001,AAPL US,TICKER,US,189.4200,15000,2026-08-28 09:30:01
    REC002,MSFT US,TICKER,US,415.7800,8200,2026-08-28 09:30:05
    REC003,BARC LN,TICKER,GB,215.6000,42000,2026-08-28 09:30:08
    REC004,VOD LN,TICKER,GB,74.8200,91000,2026-08-28 09:30:11
""")

FIGI_RESPONSE = [
    {"data": [{"figi": "BBG000B9XRY4"}]},
    {"data": [{"figi": "BBG000BPH459"}]},
    {"data": [{"figi": "BBG000C04830"}]},
    {"data": [{"figi": "BBG000C4R6H8"}]},
]


@pytest.fixture
def sample_csv_path(tmp_path: Path) -> Path:
    p = tmp_path / "sample_input.csv"
    p.write_text(SAMPLE_CSV, encoding="utf-8")
    return p


@pytest.fixture
def sample_records() -> list[dict]:
    reader = csv.DictReader(io.StringIO(SAMPLE_CSV))
    return [dict(r) for r in reader]


@pytest.fixture
def mock_client() -> MagicMock:
    client = MagicMock()
    client.do_request.return_value = FIGI_RESPONSE
    return client


# ─── load_records ─────────────────────────────────────────────────────────────

class TestLoadRecords:
    def test_happy_path_returns_records(self, sample_csv_path: Path) -> None:
        records = load_records(sample_csv_path)
        assert len(records) == 4

    def test_returns_list_of_dicts(self, sample_csv_path: Path) -> None:
        records = load_records(sample_csv_path)
        assert all(isinstance(r, dict) for r in records)

    def test_preserves_all_columns(self, sample_csv_path: Path) -> None:
        records = load_records(sample_csv_path)
        expected = {"record_id", "instrument_id", "id_type", "exchange_code",
                    "price", "volume", "timestamp"}
        assert expected.issubset(set(records[0].keys()))

    def test_first_record_values(self, sample_csv_path: Path) -> None:
        records = load_records(sample_csv_path)
        assert records[0]["record_id"] == "REC001"
        assert records[0]["instrument_id"] == "AAPL US"
        assert records[0]["exchange_code"] == "US"

    def test_file_not_found_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_records(tmp_path / "nonexistent.csv")

    def test_empty_file_raises(self, tmp_path: Path) -> None:
        p = tmp_path / "empty.csv"
        p.write_text("record_id,instrument_id,id_type,exchange_code,price,volume,timestamp\n")
        with pytest.raises(ValueError, match="No records found"):
            load_records(p)


# ─── resolve_figis ────────────────────────────────────────────────────────────

class TestResolveFigis:
    def test_happy_path_maps_all_ids(
        self, sample_records: list[dict], mock_client: MagicMock
    ) -> None:
        result = resolve_figis(sample_records, mock_client)
        assert result["AAPL US"] == "BBG000B9XRY4"
        assert result["BARC LN"] == "BBG000C04830"

    def test_unknown_on_empty_data(self, sample_records: list[dict]) -> None:
        client = MagicMock()
        client.do_request.return_value = [
            {"data": []},
            {"data": []},
            {"data": []},
            {"data": []},
        ]
        result = resolve_figis(sample_records, client)
        assert all(v == "UNKNOWN" for v in result.values())

    def test_unknown_on_api_failure(self, sample_records: list[dict]) -> None:
        client = MagicMock()
        client.do_request.return_value = None
        result = resolve_figis(sample_records, client)
        assert all(v == "UNKNOWN" for v in result.values())

    def test_skips_records_without_instrument_id(self, mock_client: MagicMock) -> None:
        records = [{"record_id": "REC001", "instrument_id": "", "id_type": "TICKER",
                    "exchange_code": "US"}]
        mock_client.do_request.return_value = []
        result = resolve_figis(records, mock_client)
        assert result == {}


# ─── rank_exchanges ────────────────────────────────────────────────────────────

class TestRankExchanges:
    def test_counts_exchanges_correctly(self, sample_records: list[dict]) -> None:
        counts, _ = rank_exchanges(sample_records)
        assert counts["US"] == 2
        assert counts["GB"] == 2

    def test_returns_counter(self, sample_records: list[dict]) -> None:
        counts, _ = rank_exchanges(sample_records)
        assert isinstance(counts, Counter)

    def test_rank_dict_has_all_exchanges(self, sample_records: list[dict]) -> None:
        counts, ranks = rank_exchanges(sample_records)
        assert set(ranks.keys()) == set(counts.keys())

    def test_ranks_start_at_one(self, sample_records: list[dict]) -> None:
        _, ranks = rank_exchanges(sample_records)
        assert min(ranks.values()) == 1

    def test_null_exchange_code_gets_unknown(self) -> None:
        records = [{"record_id": "R1", "exchange_code": None}]
        counts, _ = rank_exchanges(records)
        assert "UNKNOWN" in counts

    def test_higher_count_gets_lower_rank(self) -> None:
        records = [
            {"record_id": "R1", "exchange_code": "US"},
            {"record_id": "R2", "exchange_code": "US"},
            {"record_id": "R3", "exchange_code": "GB"},
        ]
        _, ranks = rank_exchanges(records)
        assert ranks["US"] < ranks["GB"]

    def test_equal_counts_rank_by_exchange_code(self) -> None:
        """Ties break on exchange_code ascending, regardless of input order."""
        records = [
            {"record_id": "R1", "exchange_code": "US"},
            {"record_id": "R2", "exchange_code": "GB"},
            {"record_id": "R3", "exchange_code": "DE"},
        ]
        _, ranks = rank_exchanges(records)
        assert ranks == {"DE": 1, "GB": 2, "US": 3}


# ─── write_output ──────────────────────────────────────────────────────────────

class TestWriteOutput:
    def _capture_output(
        self,
        records: list[dict],
        figi_map: dict,
        counts: Counter,
        ranks: dict,
    ) -> list[dict]:
        import sys
        from io import StringIO
        buf = StringIO()
        old_stdout = sys.stdout
        sys.stdout = buf
        write_output(records, figi_map, counts, ranks)
        sys.stdout = old_stdout
        buf.seek(0)
        return list(csv.DictReader(buf))

    def test_output_row_count_matches_input(self, sample_records: list[dict]) -> None:
        figi_map = {r["instrument_id"]: "BBG000XXXXX" for r in sample_records}
        counts, ranks = rank_exchanges(sample_records)
        rows = self._capture_output(sample_records, figi_map, counts, ranks)
        assert len(rows) == len(sample_records)

    def test_output_has_required_columns(self, sample_records: list[dict]) -> None:
        figi_map = {r["instrument_id"]: "BBG000XXXXX" for r in sample_records}
        counts, ranks = rank_exchanges(sample_records)
        rows = self._capture_output(sample_records, figi_map, counts, ranks)
        required = {"record_id", "instrument_id", "figi", "lookup_count", "exchange_rank"}
        assert required.issubset(set(rows[0].keys()))

    def test_figi_written_to_output(self, sample_records: list[dict]) -> None:
        figi_map = {"AAPL US": "BBG000B9XRY4"}
        counts, ranks = rank_exchanges(sample_records)
        rows = self._capture_output(sample_records, figi_map, counts, ranks)
        aapl_row = next(r for r in rows if r["instrument_id"] == "AAPL US")
        assert aapl_row["figi"] == "BBG000B9XRY4"

    def test_unknown_figi_for_missing_id(self, sample_records: list[dict]) -> None:
        counts, ranks = rank_exchanges(sample_records)
        rows = self._capture_output(sample_records, {}, counts, ranks)
        assert all(r["figi"] == "UNKNOWN" for r in rows)
