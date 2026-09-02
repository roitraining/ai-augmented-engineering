# PR Branch Specification and Creation Instructions

Run these commands after the initial git commit on main.
Each branch introduces known issues. Students find them with the review agent in Lab 3.

---

## Setup: verify main is clean

```bash
git log --oneline -1
git status
```

Confirm: one commit on main, working tree clean, all tests passing.

---

## pr/001 -- Easy (3 known issues)

Create the branch:
```bash
git checkout -b pr/001
```

**Change 1 (Critical): Add a new function without schema validation**

Append to `src/ingest.py`, before the `main()` function:

```python
def load_supplementary_records(supplementary_path: Path, existing_records: list[dict]):
    with supplementary_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            existing_records.append(dict(row))
    return existing_records
```

Known issue: reads external data without validating schema against expected fields.
Criterion violated: Schema drift handling (Critical).

**Change 2 (Warning): Add a utility function without type hints**

Append to `src/transform.py`, before the `main()` function:

```python
def compute_weighted_price(prices, volumes):
    total_volume = sum(volumes)
    if total_volume == 0:
        return 0.0
    return sum(p * v for p, v in zip(prices, volumes)) / total_volume
```

Known issue: two function arguments (`prices`, `volumes`) and the return type have no type hints.
Criterion violated: Type hint coverage (Warning).

**Change 3 (Informational): Add a for-append loop**

In `src/validate.py`, inside `validate_records()`, after the `seen_ids` initialisation,
add this at the top of the function:

```python
    exchange_list = []
    for r in records:
        exchange_list.append(r.get("exchange_code") or "UNKNOWN")
```

Known issue: list comprehension would be more idiomatic. `exchange_list = [r.get("exchange_code") or "UNKNOWN" for r in records]`
Criterion violated: Informational (for-append pattern).

Commit and push:
```bash
git add src/ingest.py src/transform.py src/validate.py
git commit -m "feat(ingest): add supplementary record loader and weighted price utility"
git push origin pr/001
```

---

## pr/002 -- Medium (4 known issues, one requiring cross-file context)

```bash
git checkout main
git checkout -b pr/002
```

**Change 1 (Critical): Remove null check on price before calculation**

In `src/transform.py` in `transform_records()`, find:

```python
        try:
            price  = float(price_raw)
            volume = int(volume_raw)
        except (ValueError, TypeError):
```

Replace with:

```python
        try:
            price  = float(price_raw)
            volume = int(volume_raw)
        except ValueError:
```

Known issue: removes `TypeError` from the exception handler, so a None value for price_raw raises TypeError
rather than being caught. This silently crashes the pipeline on null price records.
Criterion violated: Null safety (Critical).

**Change 2 (Critical): Write records without idempotency check**

Append to `src/transform.py`, before `main()`:

```python
def append_to_daily_summary(record: dict, output_path: Path) -> None:
    with output_path.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(record.keys()))
        writer.writerow(record)
```

Known issue: opens in append mode without checking whether the record already exists.
Running twice produces duplicate rows in the daily summary file.
Criterion violated: Idempotency (Critical).
Note: this issue requires understanding the write pattern, which is not evident from the diff alone
-- the reviewer must know that append mode without deduplication is non-idempotent.

**Change 3 (Warning): Remove pipeline exit log**

In `src/transform.py` in `main()`, remove:

```python
    logger.info("Transform pipeline complete")
```

Known issue: exit log is missing.
Criterion violated: Logging completeness (Warning).

**Change 4 (Warning): Add os.path usage**

In `src/validate.py` in `main()`, change:

```python
    input_path = Path(input_file)
    if not input_path.exists():
```

to:

```python
    import os
    input_path = Path(input_file)
    if not os.path.exists(input_file):
```

Known issue: uses os.path instead of pathlib.Path.
Criterion violated: File handling (Warning).

Commit and push:
```bash
git add src/transform.py src/validate.py
git commit -m "feat(transform): add daily summary writer and fix error handling"
git push origin pr/002
```

---

## pr/003 -- Hard (5 known issues + security-sensitive escalation trigger)

```bash
git checkout main
git checkout -b pr/003
```

**Change 1 (Security/Escalation trigger): Hardcoded credential**

In `src/figi_client.py` in `__init__()`, change:

```python
        resolved_key = apikey or os.environ.get("OPENFIGI_API_KEY")
        if not resolved_key:
            raise FigiClientError(
                "No API key provided and OPENFIGI_API_KEY env var is not set"
            )
```

to:

```python
        resolved_key = apikey or os.environ.get("OPENFIGI_API_KEY") or "demo-fallback-key-2026"
        if not resolved_key:
            raise FigiClientError(
                "No API key provided and OPENFIGI_API_KEY env var is not set"
            )
```

Known issue: hardcoded credential fallback. The string `demo-fallback-key-2026` is a literal
credential value in source code. Severity: ESCALATE regardless of agent confidence.
Criterion violated: Security (ESCALATE).

**Change 2 (Critical): Swallow FigiClientError silently**

In `src/ingest.py` in `resolve_figis()`, change:

```python
    try:
        results = client.do_request(identifiers)
    except FigiClientError as exc:
        logger.error(f"FigiClient request failed: {exc}")
        results = None
```

to:

```python
    try:
        results = client.do_request(identifiers)
    except Exception:
        results = None
```

Known issue: swallows all exceptions silently, including unexpected errors.
No log entry is produced when the FIGI client fails.
Criterion violated: Null safety + Logging completeness (Critical).

**Change 3 (Critical): Overwrite output file without idempotency check**



Append this function to `src/ingest.py` before `main()`:

```python
def archive_run(records: list[dict], archive_dir: Path) -> None:
    archive_file = archive_dir / "run_archive.csv"
    with archive_file.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(records[0].keys()))
        writer.writerows(records)
```

Known issue: append-only archive with no deduplication. Running twice doubles all records.
Criterion violated: Idempotency (Critical).

**Change 4 (Warning): Missing type hints on new function**

In `src/validate.py`, append before `main()`:

```python
def summarise_violations(violations):
    return {
        "total": len(violations),
        "by_field": {},
    }
```

Known issue: no type hints on argument or return value.
Criterion violated: Type hint coverage (Warning).

**Change 5 (Warning): Logging removed from validate entry**

In `src/validate.py` in `main()`, remove:

```python
    logger.info(f"Starting validate pipeline for {input_file}")
```

Known issue: pipeline entry not logged.
Criterion violated: Logging completeness (Warning).

Commit and push:
```bash
git add src/figi_client.py src/ingest.py src/validate.py
git commit -m "feat: add run archiving, improve error handling, add violation summary"
git push origin pr/003
```

---

## Post-creation verification

```bash
git checkout pr/001 && echo "pr/001 OK"
git checkout pr/002 && echo "pr/002 OK"
git checkout pr/003 && echo "pr/003 OK"
git checkout main
```

Known issues per PR for instructor reference:

| PR | Critical | Warning | Info | Security/Escalate |
|----|----------|---------|------|-------------------|
| pr/001 | 1 | 1 | 1 | 0 |
| pr/002 | 2 | 2 | 0 | 0 |
| pr/003 | 2 | 2 | 0 | 1 |
