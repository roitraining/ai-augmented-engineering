# Instructor Notes — Lab2 Copilot


**Coverage gaps and how they are handled:**

- **No Plan mode:** the planning prompt template in Step 2.1 is specific enough to produce a plan before code in most cases. If Copilot ignores the "do not write code" instruction and begins implementing immediately, have participants open a fresh conversation and prepend the constraint more prominently.
- **No Debug mode:** the six-step constrained workflow in Part 5 is the documented substitute. The steps are numbered identically to Cursor's Debug mode steps so participants can cross-reference. The key risk is participants collapsing steps 2-4 into one prompt. Enforce the step separation by walking the room after Step 5.2.
- **#changes vs @Branch:** `#changes` attaches uncommitted working tree changes. If participants have committed all changes, have them run `git diff main` and paste the output manually.

**Copilot-specific advantages to highlight:**

- The commit cleanup prompt in Part 6 is a precision prompting exercise that the Cursor version skips (Cursor participants just type `/rework-commits`). The Copilot version teaches the skill of writing the instruction yourself before seeing the reference answer -- this is more transferable to new situations.

**Starter file dependencies:**

`copilot-starters/lab2/` must contain:
- `.github/copilot-instructions.md` (populated with the six DE standards from Lab 1)
- `.github/instructions/perl-conversion.instructions.md` (populated with conversion rules from Lab 1, with `applyTo: "**/*.pl,**/*.py"` frontmatter)
- `.github/skills/pipeline-review/SKILL.md` (populated from Lab 1)
- `src/` (empty directory)

**The engineered regression:**

Identical to the Cursor version. The regression is a sort stability difference between Perl's `reverse sort` and Python's `sorted(..., reverse=True)`. `data/perl_output_reference.csv` ships with the repository and must not be regenerated from Python output. Verify at least five records with equal count values exist in `sample_input.csv` before delivery.

**Verification gaps:**

- `#changes` behavior: confirm `#changes` in the installed Copilot Chat version attaches the working tree diff. If the label or behavior differs, update Step 6.1.
- Planning prompt compliance: test the exact planning prompt in Step 2.1 on the delivery VS Code build. Copilot may not always respect the "do not write code" instruction. If it does not in testing, add a stronger constraint: "If you write any Python code before I say 'proceed', stop and restart the plan."
- Instrumentation cleanup: confirm the `grep "# DEBUG"` command returns no results after the manual cleanup step. If Copilot removes instrumentation automatically in your version, simplify Step 5.7.
