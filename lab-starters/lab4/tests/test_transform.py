"""tests/test_transform.py -- Test suite for src/transform.py"""
import pytest
from src.transform import classify_size, validate_timestamp, transform_records

class TestClassifySize:
    def test_block(self): assert classify_size(2_000_000) == "BLOCK"
    def test_large(self): assert classify_size(500_000) == "LARGE"
    def test_mid(self):   assert classify_size(50_000) == "MID"
    def test_small(self): assert classify_size(1_000) == "SMALL"
    def test_exact_block_boundary(self): assert classify_size(1_000_000) == "BLOCK"

class TestValidateTimestamp:
    def test_valid(self):   assert validate_timestamp("2026-08-28 09:30:01") is True
    def test_invalid(self): assert validate_timestamp("28/08/2026 09:30") is False
    def test_none(self):    assert validate_timestamp(None) is False
    def test_empty(self):   assert validate_timestamp("") is False

class TestTransformRecords:
    BASE = {"record_id":"R1","instrument_id":"AAPL US","id_type":"TICKER",
            "exchange_code":"US","figi":"BBG000B9XRY4","price":"189.4200",
            "volume":"15000","timestamp":"2026-08-28 09:30:01",
            "lookup_count":"4","exchange_rank":"1"}

    def test_happy_path(self):
        out = transform_records([self.BASE])
        assert len(out) == 1
        assert out[0]["size_bucket"] in {"SMALL","MID","LARGE","BLOCK"}
        assert out[0]["figi_resolved"] == 1
        assert out[0]["ts_valid"] == 1

    def test_notional_calculated(self):
        out = transform_records([self.BASE])
        assert abs(out[0]["notional"] - 189.42 * 15000) < 0.01

    def test_unknown_figi_gives_resolved_zero(self):
        r = {**self.BASE, "figi": "UNKNOWN"}
        out = transform_records([r])
        assert out[0]["figi_resolved"] == 0

    def test_missing_price_skipped(self):
        r = {**self.BASE, "price": None}
        out = transform_records([r])
        assert len(out) == 0

    def test_price_normalised_to_4dp(self):
        out = transform_records([self.BASE])
        assert out[0]["price"] == "189.4200"
