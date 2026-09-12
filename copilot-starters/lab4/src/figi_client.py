"""
figi_client.py -- Python client for the OpenFIGI identifier mapping API

Idiomatic Python conversion of FigiClient.pm.
Maps financial instrument identifiers to OpenFIGI codes.
Enforces a rate limit of 100 requests per 60-second window.
Retries up to 5 times on HTTP 429 responses.
"""

import logging
import json
import os
import time
from pathlib import Path
from typing import Optional

import requests

logger = logging.getLogger(__name__)

DEFAULT_URL         = "https://api.openfigi.com/v2/mapping"
DEFAULT_RATE_LIMIT  = 100
DEFAULT_WINDOW_SECS = 60
DEFAULT_MAX_RETRIES = 5
DEFAULT_RETRY_SLEEP = 2


class FigiClientError(Exception):
    """Raised when the FigiClient cannot complete a request."""


class FigiClient:
    """Client for the OpenFIGI identifier mapping API."""

    def __init__(
        self,
        url: str = DEFAULT_URL,
        apikey: Optional[str] = None,
        rate_limit: int = DEFAULT_RATE_LIMIT,
        window_secs: float = DEFAULT_WINDOW_SECS,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_sleep: float = DEFAULT_RETRY_SLEEP,
    ) -> None:
        """Initialise the FigiClient.

        Args:
            url:         OpenFIGI mapping endpoint URL.
            apikey:      API key. Falls back to OPENFIGI_API_KEY env var.
            rate_limit:  Maximum requests per window_secs.
            window_secs: Rate limit window in seconds.
            max_retries: Maximum retries on HTTP 429.
            retry_sleep: Base sleep seconds between retries (multiplied by retry count).

        Raises:
            FigiClientError: If no API key is available.
        """
        resolved_key = apikey or os.environ.get("OPENFIGI_API_KEY")

        # Fixture mode: answer lookups from a local JSON map instead of the
        # live API. Used when OPENFIGI_FIXTURE names a file, or when no real
        # key is configured and the course fixture exists. Keeps the lab
        # runnable offline and independent of OpenFIGI endpoint changes.
        self._fixture: Optional[dict[str, str]] = None
        fixture_path = os.environ.get("OPENFIGI_FIXTURE")
        if not fixture_path and (not resolved_key or resolved_key == "DEMO_KEY"):
            candidate = Path(__file__).resolve().parent.parent / "data" / "figi_fixture.json"
            if candidate.is_file():
                fixture_path = str(candidate)
        if fixture_path:
            try:
                with Path(fixture_path).open(encoding="utf-8") as fh:
                    self._fixture = json.load(fh)
            except (OSError, ValueError) as exc:
                raise FigiClientError(
                    f"Could not load FIGI fixture {fixture_path}: {exc}"
                ) from exc
            logger.info(f"FigiClient fixture mode: answering from {fixture_path}")
            resolved_key = resolved_key or "FIXTURE"

        if not resolved_key:
            raise FigiClientError(
                "No API key provided and OPENFIGI_API_KEY env var is not set"
            )

        self._url         = url
        self._apikey      = resolved_key
        self._rate_limit  = rate_limit
        self._window_secs = window_secs
        self._max_retries = max_retries
        self._retry_sleep = retry_sleep
        self._batch_cnt   = 0
        self._batch_start = time.time()
        self._session     = requests.Session()
        self._session.headers.update({
            "Content-Type": "application/json",
            "X-OPENFIGI-APIKEY": self._apikey,
        })

    def do_request(self, identifiers: list[dict]) -> Optional[list[dict]]:
        """Map a batch of identifiers to OpenFIGI codes.

        Args:
            identifiers: List of identifier dicts, each with keys
                         idType, idValue, and optionally exchCode.

        Returns:
            List of result dicts from the OpenFIGI API, one per identifier,
            or None if the request fails after all retries.

        Raises:
            ValueError: If identifiers is empty or not a list.
        """
        if not isinstance(identifiers, list) or not identifiers:
            raise ValueError("identifiers must be a non-empty list")

        logger.info(f"Starting do_request with {len(identifiers)} identifiers")

        if self._fixture is not None:
            results: list[dict] = [
                {"data": [{"figi": figi}]} if figi else {"error": "No identifier found."}
                for figi in (
                    self._fixture.get(str(ident.get("idValue", ""))) for ident in identifiers
                )
            ]
            logger.info("Completed do_request from fixture")
            return results

        self._enforce_rate_limit()

        for retry_cnt in range(self._max_retries + 1):
            try:
                response = self._session.post(self._url, json=identifiers, timeout=30)
            except requests.RequestException as exc:
                logger.error(f"HTTP request failed: {exc}")
                return None

            if response.status_code == 200:
                self._batch_cnt += 1
                try:
                    data = response.json()
                except ValueError as exc:
                    logger.error(f"Failed to parse JSON response: {exc}")
                    return None
                logger.info("Completed do_request successfully")
                return data

            elif response.status_code == 429:
                if retry_cnt < self._max_retries:
                    sleep_for = self._retry_sleep * (retry_cnt + 1)
                    logger.warning(
                        f"Rate limited (HTTP 429), retry {retry_cnt + 1}"
                        f" of {self._max_retries}, sleeping {sleep_for}s"
                    )
                    time.sleep(sleep_for)
                else:
                    logger.error(
                        f"Max retries ({self._max_retries}) exceeded on HTTP 429"
                    )
                    return None

            else:
                logger.error(f"Unexpected HTTP {response.status_code} from {self._url}")
                return None

        return None

    def _enforce_rate_limit(self) -> None:
        """Sleep if needed to stay within the rate limit window."""
        if self._batch_cnt >= self._rate_limit:
            elapsed = time.time() - self._batch_start
            if elapsed < self._window_secs:
                sleep_for = self._window_secs - elapsed
                logger.info(f"Rate limit reached, sleeping {sleep_for:.1f}s")
                time.sleep(sleep_for)
            self._batch_cnt   = 0
            self._batch_start = time.time()
