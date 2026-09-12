# Instructor Notes — Lab3 Cursor


**PR design requirements:**

- `pr/001` (easy): three known issues—one Critical (missing schema validation), one Warning (missing type hints on two functions), one Informational (for-append loop). All findable by a well-tuned agent. Provide the known-issues list to instructors before delivery.
- `pr/002` (medium): four known issues across two files. At least one requiring understanding of code outside the diff—tests over-fitting from the iteration cycle.
- `pr/003` (hard): five known issues including one security-sensitive credential handling change that must trigger escalation. Overall recommendation must be ESCALATE or REQUEST CHANGES.

**Verification gaps:**

- `@Branch` label: confirm the exact label in the installed Cursor version. Update Step 1.3 if it differs.
- Agent Review settings path: Cursor 3.11 moves Agent Review to Git and PRs. Confirm the correct path for the delivery version.
- Agent Review reading `.cursor/BUGBOT.md`: confirmed from official documentation. Verify in the delivery version that the review output changes when BUGBOT.md rules are present.

**Critical teaching point:**

`.cursor/rules/*.mdc` files do NOT apply to Bugbot or Agent Review. Reinforce this at the start of Part 5 and again at the debrief. Participants who assume their `de-standards.mdc` flows into Bugbot will be confused when it has no effect.

**Starter files:**

`lab-starters/lab3/` contains everything from `lab-starters/lab2/` plus: `src/ingest.py` (complete conversion), `tests/test_ingest.py` (passing test suite), `docs/pipeline-map.md`, and `audit/.gitkeep`. Verify `pytest tests/ -v` passes cleanly after loading before delivery.
