# Instructor Notes — Lab3 Copilot


**Key differences from the Cursor version to reinforce during delivery:**

- **Version tracking:** Copilot participants track instruction set versions in `docs/review-agent-versions.md` instead of using Cursor's checkpoint restore. Walk the room after Step 3.1 and confirm every participant has saved Version 1 before making any changes.
- **Diff preparation:** participants paste `git diff main` output manually into Copilot Chat. This adds 30-60 seconds per PR but is otherwise equivalent. If participants find the diff too long to paste, have them redirect to a file (`git diff main > data/pr_diff.txt`) and copy from there.
- **Copilot Review location:** `Copilot: Review and Comment` is available via right-click in the editor or the Command Palette. Confirm the exact path in the delivery VS Code build before the session.

**Copilot-specific advantage to highlight:**

`.github/skills/pipeline-review/SKILL.md` automatically extends Copilot code review on GitHub.com PRs. Participants who raise a draft PR (Step 5.5) will see this in action without any additional configuration. This is worth demonstrating if time permits—it shows that the Lab 1 skill work has real production value beyond this lab.

**Starter file dependencies:**

`copilot-starters/lab3/` must contain:
- `.github/copilot-instructions.md` (populated with DE standards from Lab 1)
- `.github/instructions/perl-conversion.instructions.md` (from Lab 1)
- `.github/skills/pipeline-review/SKILL.md` (from Lab 1)
- `.github/agents/.gitkeep` (empty directory pre-created)
- `src/ingest.py` (complete idiomatic Python conversion from Lab 2)
- `tests/test_ingest.py` (passing test suite from Lab 2)
- `docs/pipeline-map.md` (from Lab 2)
- `audit/.gitkeep`

Verify `pytest tests/ -v` passes cleanly after loading before delivery.

**PR design requirements** are identical to the Cursor version:
- `pr/001` (easy): three known issues. Provide the known-issues list to instructors before delivery.
- `pr/002` (medium): four known issues across two files, at least one outside the diff scope.
- `pr/003` (hard): five known issues including one security-sensitive finding that must trigger escalation.
