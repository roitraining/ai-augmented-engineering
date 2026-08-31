---
name: pipeline-review
description: Reviews Python pipeline code against DE team standards. Checks schema drift handling, null safety on critical fields, idempotency, logging completeness, and type hint coverage. Groups findings by severity.
---

Review the provided Python pipeline code against the following five criteria.
For each finding, state the criterion violated, the exact file and line number,
and a specific recommendation. Every recommendation must be a single actionable
sentence starting with a verb.

Group all findings by severity:

## Critical
Issues that will cause data loss, silent failures, or incorrect pipeline output.

- Schema drift: does the code validate the incoming data schema before processing?
  Flag any function that reads external data without checking field names and types
  against a registered schema.

- Null safety: are None values handled explicitly on all critical fields?
  Critical fields for this pipeline: instrument_id, exchange_code, price, volume,
  figi, record_id. Flag any code that accesses these fields without a None check
  or a .get() with a default value.

- Idempotency: can this pipeline step run twice on the same input without producing
  duplicate output records? Flag any write operation that does not check for
  existing records before inserting.

## Warning
Issues that reduce reliability or violate team standards.

- Logging completeness: does every pipeline function log on entry and exit using
  the project logger? Flag any function missing logger.info on entry or exit.

- Type hint coverage: do all function arguments and return types have type hints?
  Flag any function argument or return type that is not annotated.

- File handling: are all file operations using pathlib.Path? Flag any use of
  os.path, open() with a raw string path, or string concatenation for file paths.

## Informational
Style issues and improvement opportunities.

- List comprehensions: flag any for-append loop that could be a list comprehension.
- Counter usage: flag any manual dict counting pattern that should use
  collections.Counter.

After reviewing all findings, end with:

Overall recommendation: APPROVE / REQUEST CHANGES / ESCALATE

ESCALATE if any finding has Low confidence and involves security, credentials,
regulatory reporting logic, or price/position calculation.
