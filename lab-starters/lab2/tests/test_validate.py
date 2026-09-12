"""tests/test_validate.py -- Test suite for src/validate.py"""
import pytest
from src.validate import validate_records

BASE = {"record_id":"R1","instrument_id":"AAPL US","id_type":"TICKER",
        "exchange_code":"US","figi":"BBG000B9XRY4","price":"189.4200",
        "volume":"15000","timestamp":"2026-08-28 09:30:01","lookup_count":"4",
        "exchange_rank":"1","notional":"2841300.0","size_bucket":"BLOCK",
        "figi_resolved":"1","ts_valid":"1"}

class TestValidateRecords:
    def test_passing_record(self):
        result = validate_records([BASE])
        assert result["passed_count"] == 1
        assert result["critical"] == []

    def test_missing_record_id(self):
        r = {**BASE, "record_id": ""}
        result = validate_records([r])
        assert any("missing record_id" in v for v in result["critical"])

    def test_duplicate_record_id(self):
        result = validate_records([BASE, BASE])
        assert any("duplicate" in v for v in result["critical"])

    def test_bad_price_format(self):
        r = {**BASE, "price": "189.42"}
        result = validate_records([r])
        assert any("price" in v for v in result["critical"])

    def test_non_positive_volume(self):
        r = {**BASE, "volume": "0"}
        result = validate_records([r])
        assert any("volume" in v for v in result["critical"])

    def test_unresolved_figi(self):
        r = {**BASE, "figi_resolved": "0"}
        result = validate_records([r])
        assert any("figi_resolved" in v for v in result["critical"])

    def test_invalid_timestamp_is_warning_not_critical(self):
        r = {**BASE, "ts_valid": "0"}
        result = validate_records([r])
        assert result["passed_count"] == 1
        assert any("ts_valid" in w for w in result["warnings"])
        assert result["critical"] == []
