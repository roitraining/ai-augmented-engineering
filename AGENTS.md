# AGENTS.md
## Cloud Agent Onboarding Guide -- cursor_augmented_engineering

This file is read automatically by Cursor Cloud Agents before starting any task.
It describes how to set up the environment, run tests, and what limitations apply.

---

## Environment Setup

Python 3.11 or higher is required.

```bash
python -m venv venv
source venv/bin/activate          # macOS/Linux
# venv\Scripts\activate           # Windows
pip install -r requirements.txt
```

Required environment variable for network tasks only:
```
OPENFIGI_API_KEY=<your key>       # Not required for test runs -- mock fixtures are used
```

---

## Running Tests

```bash
pytest tests/ -v --no-header
```

All tests use mock fixtures. No external connections are required.

Expected: all tests pass on a clean clone without any environment variables set.

If tests fail on a clean clone, check that requirements.txt dependencies are installed
and that you are running Python 3.11+.

---

## Pipeline Stages

The pipeline has three stages. Run each from the project root:

**Stage 1: Ingest**
```bash
python src/ingest.py data/sample_input.csv > data/python_output.csv
```
Expected: data/python_output.csv with 20 rows plus header.

**Stage 2: Transform**
```bash
python src/transform.py data/python_output.csv > data/transformed.csv
```
Expected: data/transformed.csv with added notional, size_bucket, figi_resolved, ts_valid columns.

**Stage 3: Validate**
```bash
python src/validate.py data/transformed.csv
```
Expected: RESULT: PASS printed to stdout, exit code 0.

---

## Parity Check

After any Perl-to-Python conversion, verify output matches the Perl reference:

```bash
python src/ingest.py data/sample_input.csv > data/python_output.csv
diff data/python_output.csv data/perl_output_reference.csv
```

An empty diff means parity is confirmed. Any diff output indicates a regression.

---

## Skills to Invoke

After modifying any src/ file:
```
/pipeline-review
```

After completing a Perl-to-Python conversion:
```
/rework-commits
```

---

## Known Limitations

**Oracle database:** This repository uses CSV files and mock fixtures for all test data.
Do not attempt to connect to any Oracle database from a Cloud Agent VM.
The production pipeline connects to an on-premises Oracle instance that is not
reachable from Cursor's cloud infrastructure.

**OpenFIGI API:** Do not call the live OpenFIGI API from Cloud Agent tasks.
All tests mock the HTTP layer. The OPENFIGI_API_KEY environment variable is
not set in Cloud Agent environments.

**Perl execution:** Cloud Agent VMs may not have Perl installed. All reference
output files are pre-computed and committed to the repository. Do not attempt
to run any .pl files in a Cloud Agent environment.
