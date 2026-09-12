# Instructor Notes — Lab4 Cursor


**Audit log protection:**

The audit log task is the most likely to be cut under time pressure. Allocate 8 minutes specifically for Part 5 and enforce it. Walk the room at the start of Part 5 and confirm every participant has at least the briefing and Debug records before the gate evaluation records are appended automatically.

**Sample file requirements:**

- `logs/`: four failure log files, one per failure type. Each must contain enough context for the briefing agent to classify the failure type and affected stage from log content alone.
- `metrics/quality_metrics.json`: three named run objects. `clean_run` all within threshold. `soft_breach` one warn_on_breach metric exceeding threshold. `critical_failure` one critical_on_breach metric with at least one additional violation.
- `schemas/expected_schema.json`: at least eight fields. `data/sample_input.csv` must have at least one non-breaking schema difference to produce a non-empty drift output.

**Starter files:**

`lab-starters/lab4/` contains everything from `lab-starters/lab3/` plus `src/transform.py`, `src/validate.py`, their passing test suites, and `audit/agent_decisions.jsonl` with one sample record showing the correct JSONL format. Verify `pytest tests/ -v` passes cleanly after loading.

**Verification gaps:**

- `@Terminals` context attachment: confirm this attaches the terminal buffer in the delivery Cursor version. If not, the fallback is the explicit directory instruction in the prompt.
- Gate agent auto-append to JSONL: confirm the agent appends correctly without reformatting the existing file. If it rewrites the file, add the instruction: `Use append mode. Do not reformat or rewrite any existing lines in the file.`
- `/in-cloud` requires GitHub remote: confirmed from live testing. The error message gives clear guidance. No additional instructor intervention needed unless the client's SCM is not supported.
