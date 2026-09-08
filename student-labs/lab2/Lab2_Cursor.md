# Lab 2: Perl to Python Pipeline Conversion
**Course:** AI-Augmented Engineering for Data Engineers
**Tool:** Cursor (Pro plan)
**Duration:** 90 minutes
**Day:** Day 1, following Module 2

---

## Prerequisites

- [ ] Module 2 lecture completed
- [ ] Lab 1 completed, or Lab 2 starter files loaded (see Step 0)
- [ ] Sample pipeline repository open in Cursor
- [ ] pytest accessible from the terminal (`pytest --version` returns a version)
- [ ] Git initialized on the sample_pipeline repository (`git status` returns output without an error)

---

## Lab Overview

Your team has inherited three Perl pipeline modules with no in-house Perl expertise. Using the four-step conversion framework from Module 2, you will analyze the pipeline in Ask mode, generate a Plan mode conversion brief, convert the highest-priority module to idiomatic Python, validate with TDD, catch a deliberate regression using Debug mode, and prepare the branch for peer review.

**What you will produce:**
- `docs/pipeline-map.md` —a plain-language architectural map of the Perl pipeline
- `docs/conversion-plan.md` —a Plan mode conversion brief
- `tests/test_ingest.py` —a committed TDD test suite
- `src/ingest.py` —an idiomatic Python conversion with all tests passing
- A parity-confirmed diff against the Perl reference output
- A self-reviewed branch with clean commit history

---

## Step 0: Load Starter Files

Run this before anything else regardless of whether you completed Lab 1. This overwrites any existing files at these paths.

Open a terminal inside Cursor (`` Ctrl+` ``) and run from the `sample_pipeline/` project root:

```powershell
cp -r lab-starters\lab2\.cursor .
cp -r lab-starters\lab2\src .
```

**macOS/Linux:**
```bash
cp -r lab-starters/lab2/.cursor .
cp -r lab-starters/lab2/src .
```

Verify:

```powershell
ls .cursor\rules\
ls .cursor\skills\
```

**macOS/Linux:**
```bash
ls .cursor/rules/
ls .cursor/skills/
```

<details>
<summary>Expected output</summary>

```
.cursor/rules/
  de-standards.mdc
  perl-to-python.mdc

.cursor/skills/
  pipeline-review/
    SKILL.md
  rework-commits/
    SKILL.md
```

If either directory is empty or missing, re-run the copy commands from the correct project root.
</details>

---

## Part 1: Codebase Analysis with Ask Mode

### Step 1.1: Switch to Ask mode

Click the mode selector in the chat input and select **Ask**. Confirm the mode indicator shows Ask before sending any message.

Ask mode is read-only. Nothing you do in this part modifies any file. If you notice files changing, you are in Agent mode—switch back before continuing.

---

### Step 1.2: Map the pipeline

Send the following prompt:

```
Read the three Perl scripts in perl/.
For each script tell me:
- what it does in plain English
- what its inputs and outputs are
- what external libraries or system calls it makes
- which other scripts depend on it
```

Read the full response before continuing.

<details>
<summary>What to expect from Ask mode</summary>

Ask mode will search the codebase and return a description of each script without modifying anything. You should see a description of three modules:

- `ingest.pl` —reads raw input records, handles rate limiting, maps identifiers via the OpenFIGI API
- `transform.pl` —applies data transformations to the ingested records
- `validate.pl` —checks output data against the registered schema

`ingest.pl` is your conversion target for this lab. It is the most self-contained module with the clearest input/output signature and the richest set of Perl idioms to convert.
</details>

---

### Step 1.3: Generate the pipeline map

In the same Ask mode conversation, send:

```
Generate a plain-language Markdown document describing the data
flow through all three Perl modules from raw input to final output.
Include the data transformations at each stage.
```

Copy the Markdown output into a new file:

```powershell
# Create the docs directory if it does not exist
mkdir docs -ErrorAction SilentlyContinue
# Open the file for editing
code docs\pipeline-map.md
```

**macOS/Linux:**
```bash
mkdir -p docs
code docs/pipeline-map.md
```

Paste the Ask mode output into `pipeline-map.md` and save. This document is the specification for Parts 2 and 3.

---

## Part 2: Plan Mode Conversion Brief

### Step 2.1: Switch to Plan mode

Click the mode selector and choose **Plan**.

<details>
<summary>What Plan mode does before writing any code</summary>

When you send a task to Plan mode, the agent:
1. Researches the codebase and the attached files
2. Asks you clarifying questions about requirements it cannot determine from the code
3. Produces a structured, editable implementation plan
4. Waits for you to approve the plan before writing any code

The plan is a reviewable document. You can edit any step before clicking **Build**. This is the structural safeguard—no code is written until you explicitly approve the approach.
</details>

---

### Step 2.2: Generate the conversion plan

Attach `perl/ingest.pl` using @Files. Type `@` in the chat input, select **Files**, and choose `perl/ingest.pl`.

Send the following prompt:

```
Convert ingest.pl to idiomatic Python. Requirements:
- Use pathlib.Path for all file handling
- Use collections.Counter for any counting patterns
- Use the re module with pre-compiled patterns for all regex
- Add type hints on all function arguments and return values
- Do not produce a line-by-line translation
- Follow all rules in .cursor/rules/
- The Python output must be testable with pytest
Ask me any clarifying questions before producing the plan.
```

Answer any clarifying questions Plan mode asks. Refer it to `.cursor/rules/` for library preferences.

When Plan mode produces the plan, **read every step before doing anything else**.

<details>
<summary>What a good conversion plan looks like</summary>

A well-structured plan should include steps covering:

1. Analyzing the Perl module's data flow and dependencies
2. Defining the Python function signatures with type hints
3. Replacing each Perl-specific pattern with its idiomatic Python equivalent
4. Adding logging on entry and exit for each function
5. Writing the module to `src/ingest.py`
6. Verifying the output compiles and passes a basic import test

If any step says "translate X directly" or "port X as-is", edit that step to describe the idiomatic Python equivalent instead. A plan that contains the word "translate" in a conversion step is a plan that will produce Perl expressed in Python syntax.
</details>

Edit any step you disagree with. When satisfied, click **Build**. Plan mode passes the plan to the Agent as its instruction set.

---

### Step 2.3: Save the plan to workspace

After the plan is generated and before clicking Build, save it:

```powershell
code docs\conversion-plan.md
```

**macOS/Linux:**
```bash
code docs/conversion-plan.md
```

Paste the plan content and save. This becomes team documentation—the next engineer converting a similar Perl module has a starting point.

> **If Agent mode starts writing code immediately without producing a plan:** you are in Agent mode, not Plan mode. Check the mode indicator and switch to Plan mode before retrying.

---

## Part 3: Write TDD Tests Before Converting

### Step 3.1: Write tests based on the pipeline map

Switch to **Agent mode**.

Create the test file:

```powershell
code tests\test_ingest.py
```

**macOS/Linux:**
```bash
code tests/test_ingest.py
```

Send the following prompt:

```
Write pytest tests for the Python equivalent of perl/ingest.pl.
Base the tests on the pipeline map in docs/pipeline-map.md.
Use the sample input files in data/ as test fixtures.
Cover: the happy path with valid input, at least one edge case,
and the null/empty input case.
Do NOT write the implementation. Write only tests.
All tests must fail when run against an empty implementation.
```

Read the generated tests carefully. Verify they test the correct inputs and outputs from the pipeline map. Edit any test that does not match the expected behavior documented in `pipeline-map.md`.

> **Do not write any Python implementation code in this step.** Tests only. If you find yourself writing `src/ingest.py`, stop and return to the test file.

---

### Step 3.2: Confirm the tests fail

Run from the terminal:

```powershell
pytest tests\test_ingest.py -v
```

**macOS/Linux:**
```bash
pytest tests/test_ingest.py -v
```

<details>
<summary>Expected output</summary>

Every test should fail with an `ImportError` or `ModuleNotFoundError`:

```
FAILED tests/test_ingest.py::test_process_records_happy_path - ImportError: cannot import name 'process_records' from 'src.ingest'
FAILED tests/test_ingest.py::test_process_records_empty_input - ImportError: ...
FAILED tests/test_ingest.py::test_process_records_null_field - ImportError: ...
```

If any test **passes** on an empty implementation, that test is not testing the right behavior. Ask the agent to fix it so it fails correctly before committing.
</details>

---

### Step 3.3: Commit the tests

```powershell
git add tests\test_ingest.py
git commit -m "Add TDD tests for ingest module conversion"
```

**macOS/Linux:**
```bash
git add tests/test_ingest.py
git commit -m "Add TDD tests for ingest module conversion"
```

This commit locks the contract. From this point forward, every agent instruction includes: **do not modify the test file**.

> **The commit is not optional.** Without it, the agent can take the easy path of modifying the tests to make them pass rather than writing correct implementation code. The commit timestamp is your proof that the tests existed before the implementation.

---

## Part 4: Apply the Four-Step Conversion Framework

### Step 4.1: Step 1—Document (already done)

Your `docs/pipeline-map.md` from Part 1 is the Step 1 output. Move directly to Step 2.

---

### Step 4.2: Step 2—Generate stubs with a precision prompt

Open a new Agent mode conversation.

Attach both `@perl/ingest.pl` and `@docs/conversion-plan.md` using the @ menu.

Send:

```
Refactor ingest.pl into idiomatic Python following conversion-plan.md.
Do NOT do a line-by-line translation.
Requirements:
- pathlib.Path for all file operations
- collections.Counter for all counting patterns
- re module with pre-compiled patterns for regex used in loops
- Type hints on all functions: arguments and return values
- Follow all rules in .cursor/rules/de-standards.mdc
- Write the output to src/ingest.py
- Do not modify tests/test_ingest.py
```

When the agent completes, open `src/ingest.py`. It should read like Python, not Perl expressed in Python syntax.

<details>
<summary>Signs your conversion is idiomatic vs literal</summary>

**Idiomatic Python (good):**
```python
from collections import Counter
from pathlib import Path
import re

PATTERN = re.compile(r'\b\d{1,3}(?:\.\d{1,3}){3}\b')

def count_ip_addresses(log_files: list[Path]) -> Counter:
    logger.info(f'Starting count_ip_addresses with {len(log_files)} files')
    counts: Counter = Counter()
    for path in log_files:
        counts.update(PATTERN.findall(path.read_text()))
    logger.info(f'Completed count_ip_addresses: {len(counts)} unique IPs')
    return counts
```

**Literal Perl translation (bad):**
```python
def count_ip_addresses(log_files):
    ip_count = {}
    for f in log_files:
        fh = open(f, 'r')
        for line in fh:
            match = re.search(r'\b\d{1,3}(?:\.\d{1,3}){3}\b', line)
            if match:
                ip = match.group(0)
                if ip not in ip_count:
                    ip_count[ip] = 0
                ip_count[ip] += 1
        fh.close()
    return ip_count
```

If your output looks like the second example, stop and ask the agent to refactor for idiomatic Python before continuing.
</details>

---

### Step 4.3: Step 3—Refactor idioms

In the same Agent mode conversation, send:

```
Review the Python you just wrote in src/ingest.py.
For each of the following, confirm it is correct or fix it:
1. Any for loop that could be a list comprehension
2. Any dict counting pattern that should be collections.Counter
3. Any string path that should be pathlib.Path
4. Any missing or incomplete type hint
5. Any function without entry and exit logging
```

Read the diff before accepting. Every change should correspond to one of the five criteria above. If the agent made additional changes, ask it to explain each one before accepting.

---

### Step 4.4: Run the tests and achieve parity

```powershell
pytest tests\test_ingest.py -v
```

**macOS/Linux:**
```bash
pytest tests/test_ingest.py -v
```

For each failing test, read the error message before asking the agent to fix anything. Send the test output to the agent and ask it to fix only the failing tests. Re-run after each fix.

When all tests pass, run the parity check:

```powershell
python -m src.ingest data\sample_input.csv > data\python_output.csv
diff data\python_output.csv data\perl_output_reference.csv
```

> **Windows note:** PowerShell's `>` operator writes UTF-16 by default, which breaks the diff comparison. If the diff produces no output or a binary comparison error, use this instead:
> ```powershell
> python -m src.ingest data\sample_input.csv | Out-File -FilePath data\python_output.csv -Encoding utf8
> ```

**macOS/Linux:**
```bash
python -m src.ingest data/sample_input.csv > data/python_output.csv
diff data/python_output.csv data/perl_output_reference.csv
```

<details>
<summary>What the parity check tells you</summary>

`data/perl_output_reference.csv` is a pre-computed file generated by running the original Perl script against `sample_input.csv`. You do not need Perl installed -- the reference output ships with the repository.

**Empty diff:** parity confirmed. The Python output matches the Perl reference exactly.

**Non-empty diff:** there is at least one difference. One difference is expected -- it is the engineered regression for Part 5. Note what it is and move on. Do not fix it here.
</details>

> **If the diff shows a difference in record ordering on records with equal count values:** that is the engineered regression. Document it and proceed to Part 5. Do not fix it now.

---

## Part 5: Debug Mode for the Engineered Regression

### Step 5.1: Switch to Debug mode

Click the mode selector and choose **Debug**.

<details>
<summary>What Debug mode does differently from Agent mode</summary>

Debug mode follows a six-step evidence-first workflow before proposing any fix:

1. **Hypothesize** —generates multiple root cause candidates from reading the code
2. **Instrument** —adds targeted log statements connected to a local debug server
3. **Reproduce** —gives you specific steps to trigger the failure and capture logs
4. **Analyze** —reads the collected runtime logs to identify the actual root cause
5. **Fix** —proposes a targeted fix based on confirmed evidence, not assumption
6. **Verify and clean up** —confirms the fix holds, removes all instrumentation

Do not modify or remove the instrumentation Debug mode adds. Do not accept a fix until you can explain why it addresses the root cause.
</details>

---

### Step 5.2: Describe the bug to Debug mode

Send the following bug description, filling in the exact diff output from your Part 4 parity check:

```
Bug: the Python output of src/ingest.py differs from the Perl
reference output in data/perl_output_reference.csv.

Expected: records with equal counts appear in the order
produced by Perl's sort algorithm.

Actual: records with equal counts appear in a different order
in the Python output.

To reproduce:
  python -m src.ingest data/sample_input.csv > data/python_output.csv
  diff data/python_output.csv data/perl_output_reference.csv
```

<details>
<summary>Why a precise bug description matters</summary>

Debug mode generates its hypotheses from your description. A vague description ("the output is wrong") produces generic hypotheses that take longer to narrow down. A precise description ("records with equal counts appear in a different order") tells the agent exactly which code path to instrument.

If Debug mode produces only one hypothesis, your description is too vague. Add the actual diff output from Part 4 to the description and retry.
</details>

---

### Step 5.3: Follow the Debug mode workflow

Read the hypotheses Debug mode generates before any instrumentation is added to your code.

When Debug mode adds instrumentation log statements, do not remove or modify them.

Follow the reproduction steps exactly as given. Use the terminal commands provided.

When Debug mode identifies the root cause from the collected logs, read the analysis in full before accepting any fix.

**Before accepting the fix, write down:**

> In one sentence, what is the root cause? What specifically causes the Python sort output to differ from Perl's on tied records?

<details>
<summary>The root cause explained</summary>

Perl's idiomatic `reverse sort { $a->{count} <=> $b->{count} }` sorts ascending then reverses the entire array. This means tied elements are reversed from their original insertion order.

Python's `sorted(records, reverse=True)` sorts descending and preserves the original order of ties (stable sort). These two behaviors produce different orderings when records have equal count values.

The fix requires sorting with an explicit secondary key that matches Perl's reversal behavior on ties -- not just making Python produce the same bytes, but understanding what the Perl sort was actually doing.

Debug mode should find this by instrumenting the sort function, capturing the ordering of tied records at runtime, and comparing it to what the Perl reference shows.
</details>

Accept the targeted fix only after you can explain it. Verify:

```powershell
pytest tests\test_ingest.py -v
python -m src.ingest data\sample_input.csv > data\python_output.csv
diff data\python_output.csv data\perl_output_reference.csv
```

> **Windows note:** PowerShell's `>` operator writes UTF-16 by default, which breaks the diff comparison. If the diff produces no output or a binary comparison error, use this instead:
> ```powershell
> python -m src.ingest data\sample_input.csv | Out-File -FilePath data\python_output.csv -Encoding utf8
> ```

**macOS/Linux:**
```bash
pytest tests/test_ingest.py -v
python -m src.ingest data/sample_input.csv > data/python_output.csv
diff data/python_output.csv data/perl_output_reference.csv
```

All tests must pass and the diff must be empty before moving to Part 6.

Confirm Debug mode removed all its instrumentation automatically. If any `# DEBUG` log statements remain, ask Debug mode to clean them up.

---

## Part 6: Self-Review and Branch Cleanup

### Step 6.1: @Branch self-review

Open a new Agent mode conversation.

Type `@` in the chat input and select **Branch (Diff with Main)** from the menu. This attaches the full diff of your current branch as context.

<details>
<summary>What to do if @Branch does not appear in the menu</summary>

The label may appear as **@Diff** or **@Git Diff** depending on your Cursor version. All three refer to the same capability -- the full diff of your current branch against main. Select whichever label appears.

If no diff-related option appears, confirm you have at least one commit on a branch other than main. The diff is empty if you have not committed anything.
</details>

Send:

```
Review all changes on this branch.
Look for:
1. Bugs or logic errors that were not in the original Perl
2. Anything that does not match our .cursor/rules/de-standards.mdc standards
3. Missing error handling
4. Functions without complete type hints
5. Any logging that is missing on entry or exit
Report findings grouped by severity: Critical, Warning, Informational.
```

Address any Critical or Warning findings before continuing.

Then send a follow-up:

```
What questions will reviewers have about these changes?
What context should I include in the PR description?
```

Use the response to draft your PR description.

---

### Step 6.2: Run /rework-commits

Open a new Agent mode conversation.

Type `/rework-commits` and press Enter.

<details>
<summary>What /rework-commits does</summary>

`/rework-commits` is a skill that ships with the sample repository at `.cursor/skills/rework-commits/SKILL.md`. It is not a built-in Cursor command.

When invoked, the skill instructs the agent to:
1. Reset to main (soft reset, changes preserved)
2. Read all changes across modified files
3. Plan a logical sequence of small, semantic commits
4. Create each commit with a descriptive message explaining the why
5. Verify the final diff matches your original branch exactly—no changes lost

The skill only restructures commits. It does not modify code.
</details>

Review the proposed commit sequence before the agent creates them. Confirm the sequence covers at minimum:

- [ ] The test file commit (earliest—predates the implementation)
- [ ] The initial Python conversion
- [ ] The idiom refactoring
- [ ] The Debug mode fix

Run final verification:

```powershell
git log --oneline
pytest tests\test_ingest.py -v
python -m src.ingest data\sample_input.csv > data\python_output.csv
diff data\python_output.csv data\perl_output_reference.csv
```

> **Windows note:** PowerShell's `>` operator writes UTF-16 by default, which breaks the diff comparison. If the diff produces no output or a binary comparison error, use this instead:
> ```powershell
> python -m src.ingest data\sample_input.csv | Out-File -FilePath data\python_output.csv -Encoding utf8
> ```

**macOS/Linux:**
```bash
git log --oneline
pytest tests/test_ingest.py -v
python -m src.ingest data/sample_input.csv > data/python_output.csv
diff data/python_output.csv data/perl_output_reference.csv
```

All tests must pass and the diff must be empty on the final commit. Your branch is ready for peer review.

---

## Lab Debrief

Write answers before the room debrief begins. You will share one with the group.

---

**Question 1**

In Part 2, Plan mode asked clarifying questions before producing the plan. What did those questions reveal about the conversion that you had not anticipated?

---

**Question 2**

In Part 4, what was the most significant difference between a precision prompt output and what a vague prompt would have produced? Name one specific code construct.

---

**Question 3**

In Part 5, what was the root cause of the engineered regression? Describe it in one sentence without using the phrase "the fix was."

---

**Question 4**

After `/rework-commits`, how many commits does your branch have? What does the earliest commit message say and why does that order matter?

---

## Instructor Notes

> This section is for instructors only and is not distributed to participants.

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
