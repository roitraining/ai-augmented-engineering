# Instructor Notes — Lab2 Cursor


**The engineered regression:**

The regression is a sort stability difference. `ingest.pl` uses `reverse sort { $a->{count} <=> $b->{count} }` which reverses tied elements. Python's `sorted(..., reverse=True)` is stable and preserves the original order of ties. The difference is only visible on `sample_input.csv` records with equal count values -- verify that at least five such records exist before delivery.

`data/perl_output_reference.csv` must be generated from the original Perl script before delivery. It ships with the repository. Do not regenerate it from the Python output.

**Verification gaps:**

- Plan mode question flow: run the exact prompt in Step 2.2 on the delivery build. If Plan mode produces a plan immediately without asking questions, the prompt is specific enough -- update Step 2.2 to remove the reference to clarifying questions.
- `@Branch` label: confirm the exact label in the installed version. Update Step 6.1 if it differs.
- `/rework-commits` skill: confirm it is present at `.cursor/skills/rework-commits/SKILL.md` in the lab2 starter files and invokes correctly.
- Debug mode instrumentation removal: confirm Debug mode removes its log statements automatically after verification in the installed version. If it does not, add a manual cleanup step.

**Common failure points:**

- Participants skipping the test commit in Step 3.3: enforce this. Walk the room after Step 3.3 and confirm `git log --oneline` shows the test commit before any `src/ingest.py` file.
- Debug mode producing only one hypothesis: bug description is too vague. Have participants paste the actual diff output into the description.
- `/rework-commits` failing: most commonly caused by the branch not being rebased on main. Have participants run `git rebase main` before retrying.
