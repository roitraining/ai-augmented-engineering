# Instructor Notes — Lab4 Copilot


**Key differences from Cursor version:**

- `@terminal` replaces Cursor's `@Terminals`. Confirmed available in VS Code Copilot Chat. Instruct participants to run `ls logs/ && cat logs/failure_001.log` in the terminal before typing `@terminal` so the buffer contains the relevant output.
- The debugging workflow is abbreviated with a reference to Lab 2. If a participant has not completed Lab 2, walk them through the constrained prompt steps using the Lab 2 Copilot instructions as a guide.
- Part 6 uses GitHub Issues to trigger the Copilot coding agent rather than Cursor's `/in-cloud`. No dashboard setup is required if the repository is already on GitHub with Copilot Enterprise assigned.

**Audit log protection:**

Same as Cursor version—protect 8 minutes for Part 5. The gate agent in Part 3 appends automatically, but the briefing and debugging records require manual entry. Walk the room after Part 2 and confirm both manual records are in the file before Part 3 begins.

**Sample file requirements:**

Identical to Cursor version -- same log files, same metrics JSON, same schema JSON.

**Starter files:**

`copilot-starters/lab4/` must contain:
- `.github/copilot-instructions.md` (with DE standards and code review rules from Labs 1 and 3)
- `.github/instructions/perl-conversion.instructions.md` (from Lab 1)
- `.github/skills/pipeline-review/SKILL.md` (from Lab 1)
- `src/ingest.py`, `src/transform.py`, `src/validate.py` (all complete, all passing tests)
- `tests/test_ingest.py`, `tests/test_transform.py`, `tests/test_validate.py`
- `docs/pipeline-map.md`
- `audit/agent_decisions.jsonl` with one sample record showing the correct six-field JSONL format and `"model_used": "GitHub Copilot Enterprise"`

Verify `pytest tests/ -v` passes cleanly after loading.

**@terminal verification:**

Confirm `@terminal` attaches terminal buffer content in the delivery VS Code build. Test by running `ls logs/` in the terminal, then typing `@terminal` in Copilot Chat and asking what files are in the logs directory. If `@terminal` does not return the expected content, have participants use the `#file:` fallback instead: `#file:logs/failure_001.log #file:logs/failure_002.log` etc.
