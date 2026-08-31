# DE Pipeline Review Rules

## Critical
- Any function reading from external data sources must validate the schema before processing records
- Null values on customer_id, instrument_id, price, and volume fields must be handled explicitly
- Pipeline steps that write records must be idempotent: running twice must not produce duplicate output

## Warning
- All functions must have type hints on all arguments and the return value
- Pipeline entry and exit must be logged using the project logger
- All file operations must use pathlib.Path

## Informational
- Use collections.Counter for counting and frequency analysis patterns
- Use list comprehensions where they improve readability over for-append loops
