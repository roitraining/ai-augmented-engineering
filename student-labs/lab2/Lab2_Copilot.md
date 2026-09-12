# Lab 2: Perl to Python Pipeline Conversion
**Course:** AI-Augmented Engineering for Data Engineers
**Tool:** GitHub Copilot Enterprise (VS Code)
**Duration:** 90 minutes
**Day:** Day 1, following Module 2

---

## Prerequisites

- [ ] Module 2 lecture completed
- [ ] Lab 1 completed, or Lab 2 Copilot starter files loaded (see Step 0)
- [ ] VS Code open with GitHub Copilot Chat active
- [ ] Sample pipeline repository open in VS Code
- [ ] pytest accessible from the terminal (`pytest --version` returns a version)
- [ ] Git initialized on the sample_pipeline repository (`git status` returns output without an error)

---

## A Note on Coverage

This lab follows the same six-part structure and learning objectives as the Cursor version. Where GitHub Copilot Enterprise has a direct equivalent, this lab uses it. Where no equivalent exists, this lab uses the closest available approach and states the difference explicitly.

| Cursor feature | Copilot approach used in this lab |
|---|---|
| Plan mode (structural plan before code) | Explicit planning prompt in Agent mode—template provided |
| Debug mode (evidence-first, six-step) | Constrained Agent mode prompts enforcing hypothesis-first discipline |
| @Branch (Diff with Main) | `#changes` in Copilot Chat |
| /rework-commits skill | Natural language prompt to the agent—template provided, written by you first |

The most significant gap is Debug mode. Copilot has no named evidence-first mode. This lab teaches the constrained prompt approach as an explicit substitute, step by step, so you achieve the same discipline through prompt structure rather than mode structure.

---

## Lab Overview

Your team has inherited three Perl pipeline modules with no in-house Perl expertise. Using the four-step conversion framework from Module 2, you will analyze the pipeline using constrained exploration prompts, generate a planning brief before writing any Python, convert the highest-priority module to idiomatic Python, validate with TDD, catch a deliberate regression using a constrained debugging workflow, and prepare the branch for peer review.

**What you will produce:**
- `docs/pipeline-map.md` —a plain-language architectural map of the Perl pipeline
- `docs/conversion-plan.md` —a structured conversion plan reviewed before any code is written
- `tests/test_ingest.py` —a committed TDD test suite
- `src/ingest.py` —an idiomatic Python conversion with all tests passing
- A parity-confirmed diff against the Perl reference output
- A self-reviewed branch with clean commit history

---

## Step 0: Load Starter Files

Run this before anything else regardless of whether you completed Lab 1. This overwrites any existing files at these paths.

Open a terminal inside VS Code (`` CTRL+` ``) and run from the `sample_pipeline/` project root:

```powershell
cp -r copilot-starters\lab2\.github .
cp -r copilot-starters\lab2\src .
```

**macOS/Linux:**
```bash
cp -r copilot-starters/lab2/.github .
cp -r copilot-starters/lab2/src .
```

Verify:

```powershell
ls .github\
```

**macOS/Linux:**
```bash
ls .github/
```

<details>
<summary>Expected output</summary>

```
.github/
  copilot-instructions.md           ← populated with DE team standards from Lab 1
  instructions/
    perl-conversion.instructions.md  ← populated with conversion rules from Lab 1
  skills/
    pipeline-review/
      SKILL.md
```

The Lab 2 Copilot starter files include the completed `.github/` configuration from Lab 1. If you did not complete Lab 1, these files give you a fully working Copilot configuration to start from.
</details>

---

## Part 1: Codebase Analysis with a Constrained Exploration Prompt

### Step 1.1: Open Copilot Chat

Press `CTRL+SHIFT+I` (Windows) or `CMD+SHIFT+I` (Mac) to open Copilot Chat.

Confirm the mode shows **Agent**. This is the only mode available in Copilot—read-only exploration is achieved through prompt constraints rather than a mode switch.

---

### Step 1.2: Map the pipeline using a read-only constraint

Send the following prompt exactly. The constraint on the first line is essential—it prevents Copilot from making changes while it explores:

```
Do not edit any files. Answer only.

Read the three Perl scripts in perl/.
For each script tell me:
- what it does in plain English
- what its inputs and outputs are
- what external libraries or system calls it makes
- which other scripts depend on it
```

Read the full response before continuing.

<details>
<summary>What to expect</summary>

Copilot should describe all three modules without modifying any files:

- `ingest.pl` —reads raw input records, handles rate limiting, maps identifiers via the OpenFIGI API
- `transform.pl` —applies data transformations to the ingested records
- `validate.pl` —checks output data against the registered schema

`ingest.pl` is your conversion target for this lab. It is the most self-contained module with the clearest input/output signature.

If Copilot begins suggesting edits or opens a diff view, it has ignored the constraint. Click **Discard** on any proposed changes and retry with the constraint on the first line of a fresh conversation.
</details>

---

### Step 1.3: Generate the pipeline map

In the same Copilot Chat conversation, send:

```
Do not edit any files. Answer only.

Generate a plain-language Markdown document describing the data
flow through all three Perl modules from raw input to final output.
Include the data transformations at each stage.
```

Copy the Markdown output into a new file:

```powershell
mkdir docs -ErrorAction SilentlyContinue
code docs\pipeline-map.md
```

**macOS/Linux:**
```bash
mkdir -p docs
code docs/pipeline-map.md
```

Paste the Copilot output into `pipeline-map.md` and save.

---

## Part 2: Structured Planning Before Writing Any Python

### Step 2.1: Write and send the planning prompt

Copilot has no named Plan mode. The equivalent is an explicit planning prompt in Agent mode that instructs Copilot to produce a plan and wait for your approval before writing any code.

Open a new Copilot Chat conversation. Attach `perl/ingest.pl` by typing `#file:perl/ingest.pl` at the start of your message.

Send the following planning prompt:

```
#file:perl/ingest.pl

Before writing any Python code, produce a structured conversion plan only.
Do not write any implementation code until I explicitly tell you to proceed.

Research ingest.pl and docs/pipeline-map.md, then produce a numbered
implementation plan covering:
1. The Python function signatures with type hints
2. How each Perl-specific pattern maps to its idiomatic Python equivalent
3. Which external libraries are required
4. The file structure of the output module
5. How the module will be testable with pytest

Requirements the plan must address:
- pathlib.Path for all file handling
- collections.Counter for any counting patterns
- re module with pre-compiled patterns for all regex
- Type hints on all function arguments and return values
- No line-by-line translation

Ask me any clarifying questions before producing the plan.
After I confirm, produce the plan. Do not write any code yet.
```

Answer any clarifying questions Copilot asks before it produces the plan.

<details>
<summary>What a good conversion plan looks like</summary>

A well-structured plan should include steps covering:

1. Analyzing the Perl module's data flow and dependencies
2. Defining the Python function signatures with type hints
3. Replacing each Perl-specific pattern with its idiomatic Python equivalent
4. Adding logging on entry and exit for each function
5. Writing the module to `src/ingest.py`
6. Verifying the output compiles and passes a basic import test

If any step says "translate X directly" or "port X as-is", tell Copilot to replace that step with the idiomatic Python equivalent before you confirm. A plan that contains the word "translate" in a conversion step will produce Perl expressed in Python syntax.
</details>

---

### Step 2.2: Review, edit, and confirm the plan

Read every step before responding. Edit any step you disagree with by telling Copilot what to change:

```
Replace step [N] with: [your preferred approach]
```

When satisfied with the full plan, send:

```
The plan looks good. Save it to docs/conversion-plan.md and then proceed
with the implementation.
```

<details>
<summary>Why confirming the plan matters</summary>

The planning prompt instructs Copilot not to write code until you explicitly confirm. This creates the same approval gate that Cursor's Plan mode Build button provides -- you review the approach before any implementation begins.

The practical difference from Cursor: in Cursor, the Plan mode UI prevents the agent from coding structurally. In Copilot, the protection comes from the prompt instruction. If Copilot begins writing code before you confirm, it has ignored the instruction. Open a fresh conversation and retry with the planning prompt.
</details>

---

## Part 3: Write TDD Tests Before Converting

### Step 3.1: Write tests based on the pipeline map

Copilot will now be in the same conversation where you confirmed the plan. Open a new conversation specifically for test writing to keep concerns separate.

Open a new Copilot Chat conversation. Create the test file:

```powershell
code tests\test_ingest.py
```

**macOS/Linux:**
```bash
code tests/test_ingest.py
```

Send:

```
Do not write any implementation code. Write only pytest tests.

Write pytest tests for the Python equivalent of perl/ingest.pl.
Base the tests on the pipeline map in docs/pipeline-map.md.
Use the sample input files in data/ as test fixtures.
Cover: the happy path with valid input, at least one edge case,
and the null/empty input case.
All tests must fail when run against an empty implementation.
```

Read the generated tests carefully. Verify they test the correct inputs and outputs from `pipeline-map.md`.

> **Do not write any Python implementation code in this step.** If Copilot generates `src/ingest.py` content alongside the tests, discard the implementation and keep only the test file.

---

### Step 3.2: Confirm the tests fail

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

If any test passes on an empty implementation, that test is not testing the right behavior. Ask Copilot to fix it before committing.
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

This commit locks the contract. From this point forward, every Copilot instruction includes: **do not modify the test file**.

---

## Part 4: Apply the Four-Step Conversion Framework

### Step 4.1: Step 1—Document (already done)

Your `docs/pipeline-map.md` from Part 1 is the Step 1 output. Move directly to Step 2.

---

### Step 4.2: Step 2—Generate stubs with a precision prompt

Open a new Copilot Chat conversation. Attach the Perl file and the conversion plan:

```
#file:perl/ingest.pl
#file:docs/conversion-plan.md

Refactor ingest.pl into idiomatic Python following conversion-plan.md.
Do NOT do a line-by-line translation.
Requirements:
- pathlib.Path for all file operations
- collections.Counter for all counting patterns
- re module with pre-compiled patterns for regex used in loops
- Type hints on all functions: arguments and return values
- Follow all instructions in .github/copilot-instructions.md
- Write the output to src/ingest.py
- Do not modify tests/test_ingest.py
```

When Copilot completes, open `src/ingest.py`. It should read like Python, not Perl expressed in Python syntax.

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

If your output looks like the second example, tell Copilot to refactor for idiomatic Python before continuing.
</details>

---

### Step 4.3: Step 3—Refactor idioms

In the same Copilot Chat conversation, send:

```
Review the Python you just wrote in src/ingest.py.
For each of the following, confirm it is correct or fix it:
1. Any for loop that could be a list comprehension
2. Any dict counting pattern that should be collections.Counter
3. Any string path that should be pathlib.Path
4. Any missing or incomplete type hint
5. Any function without entry and exit logging
```

Review the diff before accepting every change. Each change should correspond to one of the five criteria above.

---

### Step 4.4: Run the tests and achieve parity

```powershell
pytest tests\test_ingest.py -v
```

**macOS/Linux:**
```bash
pytest tests/test_ingest.py -v
```

For each failing test, read the error before asking Copilot to fix anything. Send the test output and ask it to fix only the failing tests. Re-run after each fix.

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

`data/perl_output_reference.csv` is a pre-computed file generated from the original Perl script. You do not need Perl installed -- the reference output ships with the repository.

**Empty diff:** parity confirmed. Move to Part 5.

**Non-empty diff:** at least one difference exists. One difference is expected -- it is the engineered regression for Part 5. Note exactly what differs and move on without fixing it.
</details>

> **If the diff shows a difference in record ordering on records with equal count values:** that is the engineered regression. Document it and proceed to Part 5. Do not fix it now.

---

## Part 5: Evidence-First Debugging for the Engineered Regression

### Step 5.1: Understand the approach

Copilot has no named Debug mode. The equivalent is an explicit constrained workflow in Agent mode that enforces evidence-first discipline through prompt structure.

The workflow you will follow has the same six steps as Cursor's Debug mode -- you enforce them through your prompts rather than through a mode switch:

1. **Hypothesize** —ask Copilot for multiple root cause candidates before any code changes
2. **Instrument** —ask Copilot to add targeted logging to collect runtime evidence
3. **Reproduce** —run the reproduction steps to collect logs
4. **Analyze** —give Copilot the log output and ask for root cause analysis
5. **Fix** —accept the targeted fix only after you understand why it works
6. **Verify and clean up** —confirm the fix holds and remove all instrumentation

Do not skip or merge steps. The value of this workflow is the evidence gathered in steps 2 and 3—without it, the fix is a guess.

---

### Step 5.2: Step 1—Generate hypotheses only

Open a new Copilot Chat conversation. Send:

```
Do not modify any files yet. Do not propose a fix yet.

The Python output of src/ingest.py differs from the Perl reference
output in data/perl_output_reference.csv.

Specifically: records with equal counts appear in a different order
in the Python output compared to the Perl reference.

To reproduce:
  python -m src.ingest data/sample_input.csv > data/python_output.csv
  diff data/python_output.csv data/perl_output_reference.csv

Generate exactly three hypotheses for what could cause this ordering
difference. For each hypothesis, describe where in the code you would
add logging to confirm or rule it out.
Do not add any logging yet. Do not propose a fix yet.
```

Read all three hypotheses before continuing. Write down which one you think is most likely.

<details>
<summary>Expected hypotheses</summary>

Well-formed hypotheses should include:

1. **Sort stability difference** -- Perl's `reverse sort` and Python's `sorted(..., reverse=True)` handle tied elements differently
2. **Counter iteration order** -- `Counter.most_common()` may return tied elements in a different order than Perl's hash iteration
3. **Input data ordering** -- the Python file reading order differs from Perl's, affecting which tied records appear first

The correct root cause is hypothesis 1. Debug mode in Cursor would typically list this as one of its candidates. Your instrumentation in Step 5.3 will confirm it.
</details>

---

### Step 5.3: Step 2—Add instrumentation

In the same conversation, send:

```
Based on hypothesis [N] -- [restate the hypothesis you want to test first] --
add targeted logging to src/ingest.py to collect runtime evidence.

The logging should capture:
- The input records and their count values before sorting
- The sort order of tied records after sorting

Mark every log statement you add with the comment # DEBUG
so they are easy to find and remove later.
Do not change any logic. Add logging only.
```

<details>
<summary>What good instrumentation looks like</summary>

```python
# DEBUG
logger.debug(f'Pre-sort records with counts: {[(r["id"], r["count"]) for r in records]}')

records_sorted = sorted(records, key=lambda r: r['count'], reverse=True)

# DEBUG
logger.debug(f'Post-sort order: {[(r["id"], r["count"]) for r in records_sorted]}')
```

The instrumentation should capture the state of records immediately before and after the sort operation, with enough detail to see how tied records are being ordered.
</details>

---

### Step 5.4: Step 3—Reproduce and capture logs

Run the reproduction steps with logging enabled:

```powershell
python -m src.ingest data\sample_input.csv 2>&1 | tee data\debug_output.txt
```

**macOS/Linux:**
```bash
python -m src.ingest data/sample_input.csv 2>&1 | tee data/debug_output.txt
```

Open `data/debug_output.txt` and find the `# DEBUG` log lines. Copy the pre-sort and post-sort entries for any records with tied count values.

---

### Step 5.5: Step 4—Analyze the evidence

In the same Copilot Chat conversation, paste the relevant log output and send:

```
Here is the runtime log output from the instrumented sort:

[paste the pre-sort and post-sort DEBUG log lines here]

Based on this evidence, which of the three hypotheses is confirmed?
What is the exact root cause of the ordering difference between the
Python output and the Perl reference?

Do not propose a fix yet. Explain the root cause only.
```

Read the root cause analysis. Before moving to the fix step, write down:

> In one sentence, what is the root cause? What specifically causes the Python sort output to differ from Perl's on tied records?

<details>
<summary>The root cause explained</summary>

Perl's idiomatic `reverse sort { $a->{count} <=> $b->{count} }` sorts ascending then reverses the entire array. This means tied elements are reversed from their original insertion order.

Python's `sorted(records, reverse=True)` sorts descending and preserves the original order of ties (stable sort). These two behaviors produce different orderings when records have equal count values.

The fix requires sorting with an explicit secondary key that matches Perl's reversal behavior on ties—not just making Python produce the same bytes, but understanding what the Perl sort was actually doing.
</details>

---

### Step 5.6: Step 5—Accept the fix

Send:

```
Now propose the targeted fix that addresses the confirmed root cause.
Explain why the fix works before applying it.
```

Read the explanation. If you cannot explain why the fix works in your own words, ask Copilot to clarify before accepting.

Accept the fix only after you can explain it.

---

### Step 5.7: Step 6—Verify and remove instrumentation

Run the full verification:

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

All tests must pass and the diff must be empty.

Remove all instrumentation log statements:

```
Remove all lines in src/ingest.py that are marked with # DEBUG.
Do not change any other code.
```

Confirm no `# DEBUG` lines remain:

```powershell
Select-String -Path src\ingest.py -Pattern "# DEBUG"
```

**macOS/Linux:**
```bash
grep "# DEBUG" src/ingest.py
```

<details>
<summary>Expected output</summary>

The command should return no results. If any `# DEBUG` lines remain, remove them manually before committing.
</details>

---

## Part 6: Self-Review and Branch Cleanup

### Step 6.1: Self-review using #changes

Open a new Copilot Chat conversation. Type `#changes` to attach the current diff as context.

<details>
<summary>What #changes attaches</summary>

`#changes` in Copilot Chat attaches the working tree diff—all changes that have been made since the last commit. This is equivalent to Cursor's `@Branch (Diff with Main)` for reviewing uncommitted changes.

If you want to review all changes on the branch against main (including committed changes), run `git diff main` in the terminal and paste the output into the chat.
</details>

Send:

```
#changes

Review all changes shown in the diff.
Look for:
1. Bugs or logic errors that were not in the original Perl
2. Anything that does not match our .github/copilot-instructions.md standards
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

---

### Step 6.2: Clean up commit history

Before running the commit cleanup, write your own version of the natural language prompt. This is the precision prompting exercise—write the prompt first, then compare it to the reference.

**Write your prompt here before looking at the reference:**

> How would you ask an agent to reorganize your commit history into clean, logical, semantic commits without losing any changes?

<details>
<summary>Reference prompt for commit history cleanup</summary>

Once you have written your own version, compare it to this reference. Your version may be equally effective—the goal is to write a specific, constrained prompt that leaves the agent no room to invent what it was not told.

```
Reorganize the commit history on this branch into clean, semantic commits.

Steps:
1. Soft reset to main so all changes are staged but uncommitted
2. Read all modified files and understand the full scope of changes
3. Plan a logical sequence of small commits where each commit contains
   one coherent change with a clear why in the commit message
4. Create the commits in this order:
   - First: the test file (tests/test_ingest.py)
   - Then: the initial Python conversion
   - Then: the idiom refactoring
   - Then: the Debug mode fix with a message explaining the root cause
5. Verify the final diff against main matches the original branch exactly.
   No changes should be lost or added.

Do not modify any code. Restructure commits only.
```

Send this prompt (or your own version) in a new Copilot Chat conversation.
</details>

Review the proposed commit sequence before the agent creates them. Confirm the sequence includes at minimum:

- [ ] The test file commit (earliest -- predates the implementation)
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

All tests must pass and the diff must be empty on the final commit.

---

## Lab Debrief

Write answers before the room debrief begins. You will share one with the group.

---

**Question 1**

In Part 2, your planning prompt instructed Copilot not to write code until you confirmed. Did Copilot follow this instruction? If it did not, what did you have to do to enforce the planning gate? How does this compare to what Cursor's Plan mode provides structurally?

---

**Question 2**

In Part 4, what was the most significant difference between a precision prompt output and what a vague prompt would have produced? Name one specific code construct.

---

**Question 3**

In Part 5, you enforced the evidence-first workflow through prompt constraints rather than a mode switch. What was the root cause of the regression? Describe it in one sentence without using the phrase "the fix was." Did the constrained workflow feel different from how you would normally debug with Copilot?

---

**Question 4**

In Part 6, you wrote your own commit cleanup prompt before seeing the reference. How did your prompt compare to the reference? What did the reference include that yours did not, or what did yours include that the reference missed?
