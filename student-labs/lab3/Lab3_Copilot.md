# Lab 3: Build a DE Pipeline Code Review Agent
**Course:** AI-Augmented Engineering for Data Engineers
**Tool:** GitHub Copilot Enterprise (VS Code)
**Duration:** 75 minutes
**Day:** Day 2, following Module 4

---

## Prerequisites

- [ ] Modules 3 and 4 lectures completed
- [ ] Chapter 3 scoping exercise completed (or scope specification template at end of this document reviewed)
- [ ] Lab 2 completed, or Lab 3 Copilot starter files loaded (see Step 0)
- [ ] VS Code open with GitHub Copilot Chat active
- [ ] Sample pipeline repository open in VS Code
- [ ] Git configured and at least one commit on the repository

---

## A Note on Coverage

This lab follows the same five-part structure and learning objectives as the Cursor version. Where GitHub Copilot Enterprise has a direct equivalent, this lab uses it. Where no equivalent exists, this lab uses the closest available approach and states the difference explicitly.

| Cursor feature | Copilot approach used in this lab |
|---|---|
| `@Branch (Diff with Main)` | `git diff main` output pasted into Copilot Chat |
| `.cursor/BUGBOT.md` | `.github/copilot-instructions.md` + `.github/skills/` for review rules |
| Agent Review (local, reads BUGBOT.md) | `Copilot: Review and Comment` in VS Code |
| Checkpoint restore for iteration rollback | Git history—revert instruction set changes via editing the file |

The most significant difference is the diff context source. Cursor's `@Branch` attaches the full branch diff automatically. In this lab, you run `git diff main` and paste the output into Copilot Chat. The content is identical -- the workflow is slightly more manual.

---

## Lab Overview

Your team reviews dozens of Python pipeline PRs each week. Build a Copilot agent instruction set that reviews pipeline code against DE-specific criteria, flags issues with severity ratings, and produces a structured review summary. Then configure Copilot's review capabilities and compare the output with your custom instruction set.

**What you will produce:**
- A working Copilot review agent instruction set with all five scope components
- A quality rubric score across two iteration cycles
- Updated `.github/copilot-instructions.md` with DE review rules
- A written comparison of your custom instruction set versus Copilot's native review

---

## Step 0: Load Starter Files

Run this before anything else regardless of whether you completed Lab 2. This overwrites any existing files at these paths.

Open a terminal inside VS Code (`` Ctrl+` ``) and run from the `sample_pipeline/` project root:

```powershell
cp -r copilot-starters\lab3\.github .
cp -r copilot-starters\lab3\src .
cp -r copilot-starters\lab3\tests .
cp -r copilot-starters\lab3\docs .
cp -r copilot-starters\lab3\audit .
```

**macOS/Linux:**
```bash
cp -r copilot-starters/lab3/.github .
cp -r copilot-starters/lab3/src .
cp -r copilot-starters/lab3/tests .
cp -r copilot-starters/lab3/docs .
cp -r copilot-starters/lab3/audit .
```

Verify:

```powershell
pytest tests\ -v
```

**macOS/Linux:**
```bash
pytest tests/ -v
```

<details>
<summary>Expected output</summary>

All tests in `tests/test_ingest.py` should pass:

```
tests/test_ingest.py::test_process_records_happy_path PASSED
tests/test_ingest.py::test_process_records_empty_input PASSED
tests/test_ingest.py::test_process_records_null_field PASSED
```

`src/ingest.py` should also exist and contain a complete idiomatic Python conversion of `perl/ingest.pl`.
</details>

<details>
<summary>What the Lab 3 Copilot starter files contain</summary>

```
.github/
  copilot-instructions.md           ← populated with DE team standards from Lab 1
  instructions/
    perl-conversion.instructions.md  ← populated from Lab 1
  skills/
    pipeline-review/
      SKILL.md                       ← populated from Lab 1
  agents/
    (empty directory, ready for optional agent definitions)
```

The `.github/agents/` directory is pre-created. If you want to define a formal Copilot custom agent for the review task, you can create a file here. This lab does not require it -- the instruction set is built directly in Copilot Chat.
</details>

---

## Part 1: Review Your Scope Specification and Build the Agent

### Step 1.1: Review your scope specification

Open your Chapter 3 scope specification document. This is the same document Cursor participants use—the scoping exercise is tool-agnostic.

Confirm it covers all five components. If any are missing, add them now:

| Component | Definition |
|---|---|
| **Tools** | Diff context from `git diff main`. Read-only -- the agent must not edit any files. |
| **Instructions** | Review against `.github/copilot-instructions.md` standards plus five DE criteria: schema drift handling, null safety, idempotency, logging completeness, type hint coverage. |
| **Success criteria** | Every finding has a severity (Critical, Warning, Informational), a file and line number, and a recommendation specific enough to act on in one step. |
| **Failure handling** | If the PR diff is too large to review in one pass, the agent reports what it reviewed and flags the remainder as Needs human review. |
| **Escalation path** | Any finding where agent confidence is Low is escalated rather than included in the summary. |

<details>
<summary>Scope specification template (use if you did not complete the Chapter 3 exercise)</summary>

```
Tools: git diff main output as context. Read-only. The agent must not
edit any files.

Instructions: Review changed code against .github/copilot-instructions.md
standards and five DE criteria:
1. Schema drift handling: does the change validate incoming schema?
2. Null safety: are None values handled on all critical fields?
3. Idempotency: can this step run twice without duplicate records?
4. Logging completeness: are pipeline entry, exit, and errors logged?
5. Type hint coverage: do all functions have complete type hints?

Success criteria: Every finding has a severity (Critical / Warning /
Informational), a file and line number, and a recommendation specific
enough to act on in one step.

Failure handling: If the PR diff is too large to review in one pass,
report what was reviewed and flag the remainder as Needs human review.

Escalation path: Any finding where confidence is Low is marked ESCALATE
rather than included in the summary.

Two failure modes:
1. Non-deterministic output -- same diff produces different findings on
   consecutive runs. Mitigation: explicit output format template.
2. Scope creep -- agent comments on code outside the diff. Mitigation:
   explicit instruction to review only changed lines shown in the diff.
```
</details>

---

### Step 1.2: Build the Version 1 instruction set

Open a new Copilot Chat conversation.

Send the following as the first message. This is your Version 1—you will improve it in Parts 2 and 3:

```
Do not edit any files.

You are a DE pipeline code review agent.
You will be provided with a git diff. Review only the changed lines
shown in the diff. Do not comment on code outside the diff.

Review the changes against .github/copilot-instructions.md standards and:
1. Schema drift handling: does the change validate incoming schema?
2. Null safety: are None values handled on all critical fields?
3. Idempotency: can this step run twice without duplicate records?
4. Logging completeness: are pipeline entry, exit, and errors logged?
5. Type hint coverage: do all functions have complete type hints?

For each finding output:
- Criterion violated
- File and line number
- Severity: Critical / Warning / Informational
- Confidence: High / Medium / Low
- Specific recommendation

If confidence is Low, mark the finding ESCALATE.

End with: overall recommendation APPROVE / REQUEST CHANGES / ESCALATE
```

Do not send the diff yet. The instruction set is established in this first message.

---

### Step 1.3: Get the PR 001 diff and run the review

Switch to the `pr/001` branch:

```powershell
git checkout pr/001
```

**macOS/Linux:**
```bash
git checkout pr/001
```

Get the diff against main:

```powershell
git diff main
```

**macOS/Linux:**
```bash
git diff main
```

<details>
<summary>What to do with the diff output</summary>

Copy the full output of `git diff main` from the terminal. In the same Copilot Chat conversation where you sent the instruction set, paste the diff and add this message:

```
Here is the diff for this PR. Review it against the criteria above.

[paste the git diff main output here]
```

If the diff is very long (more than 300 lines), VS Code may truncate it in the terminal. In that case, redirect to a file first:

```powershell
git diff main > data\pr_diff.txt
code data\pr_diff.txt
```

Then copy from the file and paste into Copilot Chat.
</details>

Paste the diff into the conversation and send. Read every finding before moving to Part 2.

---

## Part 2: First Run and Quality Rubric Score

### Step 2.1: Score the output against the rubric

Score each dimension from 1 (poor) to 5 (excellent). Use the known-issues list your instructor provides to check for false negatives.

| Dimension | Score (1--5) | Notes |
|---|---|---|
| **Coverage**—did the agent find all issues in pr_001? | | |
| **Accuracy**—of issues flagged, how many are real? | | |
| **Clarity**—can you read the summary and know exactly what to do next? | | |
| **Consistency**—paste the same diff a second time. How similar are the two outputs? | | |
| **Total** | **/20** | |

<details>
<summary>Scoring guidance for each dimension</summary>

**Coverage (finding false negatives):** Your instructor has a list of known issues in pr_001. Compare the agent's findings against the list. Each missed issue costs one point.

**Accuracy (finding false positives):** Count how many agent findings describe issues that do not actually exist in the code. Each false positive costs one point.

**Clarity (actionability):** Read each recommendation. Could you act on it immediately without asking a follow-up question? "Consider improving null handling" is not actionable. "Add an explicit None check on `customer_id` at line 47 before passing it to `transform_record()`" is.

**Consistency (determinism):** Paste the identical diff into a new Copilot Chat conversation with the same instruction set. Compare the two outputs. Score 5 if findings are identical, 1 if severity ratings or the finding list differs significantly.

**Production threshold:** 16 out of 20 with no dimension below 3.
</details>

**Identify the single lowest-scoring dimension.** That is your improvement target for Part 3.

---

## Part 3: First Iteration Cycle

### Step 3.1: Track your instruction set version

Before changing anything, open a new file to track your instruction set versions:

```powershell
code docs\review-agent-versions.md
```

**macOS/Linux:**
```bash
code docs/review-agent-versions.md
```

Paste your current Version 1 instruction set into the file with a header:

```markdown
## Version 1 (baseline)
Score: [your total] / 20
Lowest dimension: [dimension name]

[paste your Version 1 instruction set here]
```

Save the file. This is your rollback point if the next change makes things worse.

> **Why track versions in a file rather than a checkpoint:** Copilot Chat does not have a checkpoint restore system like Cursor. Tracking instruction set versions in a Markdown file gives you the same ability to revert -- copy the previous version back into a new conversation and continue.

---

### Step 3.2: Make one targeted change

Based on your lowest-scoring dimension, make exactly one specific change to the instruction set. Do not change more than one thing.

<details>
<summary>Targeted change examples by dimension</summary>

**Coverage low:** Add a more specific instruction for the issue type being missed.

```
For null safety: check every .get() call without a default value
and every function that accepts Optional parameters without
explicit None handling on all critical pipeline fields.
```

**Accuracy low:** Add a constraint against hallucinated findings.

```
Only flag an issue if you can identify the exact file and line
number where it occurs. Do not flag general concerns or patterns
you cannot locate in the diff.
```

**Clarity low:** Tighten the output format.

```
Each recommendation must be a single actionable sentence starting
with a verb. Example: Add an explicit None check on customer_id
at line 47 before passing it to transform_record().
```

**Consistency low:** Add an explicit output template.

```
For every finding, output exactly these fields in this order:
CRITERION: [name]
LOCATION: [file]:[line]
SEVERITY: [Critical|Warning|Informational]
CONFIDENCE: [High|Medium|Low]
RECOMMENDATION: [single actionable sentence starting with a verb]
```
</details>

Save the updated instruction set as Version 2 in `docs/review-agent-versions.md`:

```markdown
## Version 2
Change made: [describe the one change]
Score: [to be filled in after re-run]

[paste your Version 2 instruction set here]
```

---

### Step 3.3: Re-run on PR 001 and re-score

Open a new Copilot Chat conversation. Send the updated Version 2 instruction set as the first message.

Get the diff again (you are still on `pr/001`):

```powershell
git diff main
```

Paste the diff and send: `Review this diff against the criteria above.`

Score all four dimensions again. Record the new total in `docs/review-agent-versions.md`.

| Result | Action |
|---|---|
| Target dimension improved | Keep Version 2. Record new total score. |
| Target dimension unchanged or worse | Return to Version 1 from `docs/review-agent-versions.md`. Try a different approach. |
| Another dimension dropped significantly | Return to Version 1 and try a narrower change. |

---

## Part 4: Second Iteration Cycle and Generalization Test

### Step 4.1: Second iteration

Identify the new lowest-scoring dimension from your Part 3 score. Make one more targeted change, save as Version 3 in `docs/review-agent-versions.md`, and re-run.

If you have already reached 16 out of 20 with no dimension below 3, move directly to Step 4.2.

---

### Step 4.2: Generalization test on PR 002

Switch to the `pr/002` branch:

```powershell
git checkout pr/002
```

**macOS/Linux:**
```bash
git checkout pr/002
```

Get the diff:

```powershell
git diff main
```

Open a new Copilot Chat conversation with your best instruction set. Paste the diff and send: `Review this diff against the criteria above.`

Score the pr_002 output on all four dimensions. Compare to your pr_001 score.

> **If pr_002 scores significantly lower than pr_001:** your instruction changes are over-fitted to pr_001's specific issues. Identify which change caused the over-fitting and broaden or remove it.

---

### Step 4.3: Hard PR test on PR 003

Switch to the `pr/003` branch:

```powershell
git checkout pr/003
```

**macOS/Linux:**
```bash
git checkout pr/003
```

Get the diff:

```powershell
git diff main
```

Open a new Copilot Chat conversation with your best instruction set. Paste the diff and send: `Review this diff against the criteria above.`

PR 003 contains a security-sensitive credential handling change. Verify:

- [ ] The security-sensitive finding is marked ESCALATE (Low confidence)
- [ ] The security-sensitive finding is NOT included in the main summary
- [ ] The overall recommendation is ESCALATE or REQUEST CHANGES, not APPROVE

> **If the overall recommendation is APPROVE:** the escalation criteria are not working. Tighten the escalation path in your instruction set and re-run before moving to Part 5.

---

## Part 5: Configuring Copilot Review and Comparison

### Step 5.1: Understand what you are configuring

In Cursor, two systems are distinct: Bugbot (PR automation) and Agent Review (local). In Copilot Enterprise the equivalent distinction is:

| Cursor | Copilot equivalent | What it reads |
|---|---|---|
| `.cursor/BUGBOT.md` + Bugbot | Copilot code review on GitHub.com | `.github/skills/` (auto-applied) |
| `.cursor/BUGBOT.md` + Agent Review | `Copilot: Review and Comment` in VS Code | `.github/copilot-instructions.md` |
| `.cursor/rules/*.mdc` | `.github/copilot-instructions.md` | (already in use) |

For this lab, you will use the local VS Code path: `Copilot: Review and Comment`. This reads your `.github/copilot-instructions.md` and your `.github/skills/pipeline-review/SKILL.md` automatically.

> **Note on GitHub.com review:** If your repository is connected to GitHub and you have Copilot Enterprise assigned as a reviewer, the code review on GitHub.com will automatically invoke `.github/skills/pipeline-review/SKILL.md` without any additional configuration. This is a Copilot advantage over Cursor—skills extend PR review natively. If your team uses GitHub, this workflow is available without the manual diff step used in this lab.

---

### Step 5.2: Add DE review rules to copilot-instructions.md

Open `.github/copilot-instructions.md`. The file already contains the DE coding standards from Lab 1. Add a new section for code review rules:

```markdown
## Code Review Rules

When reviewing code changes, apply these DE-specific checks in addition
to general coding standards:

### Critical
- Any function reading from external data sources must validate
  the schema before processing records
- Null values on customer_id, transaction_date, and amount fields
  must be handled explicitly
- Pipeline steps that write records must be idempotent: running
  twice must not produce duplicate output

### Warning
- All functions must have type hints on all arguments and the return value
- Pipeline entry and exit must be logged using the project logger
- All file operations must use pathlib.Path

### Informational
- Use collections.Counter for counting and frequency analysis patterns
- Use list comprehensions where they improve readability over for-append loops
```

Save the file.

```powershell
git add .github\copilot-instructions.md
git commit -m "Add DE code review rules to copilot-instructions.md"
```

**macOS/Linux:**
```bash
git add .github/copilot-instructions.md
git commit -m "Add DE code review rules to copilot-instructions.md"
```

---

### Step 5.3: Run Copilot Review and Comment on PR 001

Switch back to pr/001:

```powershell
git checkout pr/001
```

**macOS/Linux:**
```bash
git checkout pr/001
```

In VS Code, open any changed file from the `pr/001` branch. Right-click in the editor and select **Copilot: Review and Comment**, or open the Command Palette (`CTRL+SHIFT+P`) and search for `Copilot Review`.

<details>
<summary>If Copilot Review and Comment does not appear</summary>

Confirm the GitHub Copilot Chat extension is installed and up to date (`CTRL+SHIFT+X`, search for GitHub Copilot Chat, check for updates).

Alternatively, use the Source Control tab: open the Source Control view (`CTRL+SHIFT+G`), find the changed files, and look for a Copilot review option in the file context menu.

If neither option is available, use the manual approach: open Copilot Chat, type `#file:src/ingest.py` to attach the file, and ask Copilot to review the changes against the code review rules in `.github/copilot-instructions.md`.
</details>

---

### Step 5.4: Compare Copilot Review to your custom instruction set

Fill in this comparison table using the Copilot Review output and your best custom instruction set output from Part 4:

| | Your custom instruction set | Copilot Review and Comment |
|---|---|---|
| Known pr_001 issues found | /3 | /3 |
| False positives | | |
| Most actionable finding | | |
| Time to produce output | | |

**Write one sentence:**

> When would you use Copilot Review and Comment instead of your custom instruction set in your daily work, and when would you use the custom instruction set instead?

<details>
<summary>Typical answer pattern</summary>

Copilot Review and Comment is faster and requires no diff preparation—use it for a quick check on a specific file before committing. Your custom instruction set produces more structured output with severity ratings, confidence levels, and DE-specific criteria as a unified review -- use it when you need a complete PR-level assessment with an explicit approval or escalation recommendation.

**Copilot-specific advantage:** if your team uses GitHub and has Copilot Enterprise assigned as a reviewer, `.github/skills/pipeline-review/SKILL.md` automatically extends Copilot's PR review on GitHub.com. This means the structured criteria you built in Lab 1 apply to every PR your team raises, without running the custom instruction set manually.
</details>

---

### Step 5.5: Optional -- Native GitHub.com review (fast-finisher)

If your repository is connected to GitHub and time permits, raise a draft PR from `pr/001` against `main` and assign Copilot as a reviewer.

Copilot will automatically invoke `.github/skills/pipeline-review/SKILL.md` as part of the review. Compare the GitHub.com review output to both your custom instruction set and the VS Code `Copilot: Review and Comment` output.

This demonstrates the full Copilot Enterprise code review integration and does not require any additional configuration beyond what you have already built.

---

## Lab Debrief

Write answers before the room debrief begins. You will share one with the group.

---

**Question 1**

What was your baseline score and your final score after two iteration cycles? What single change made the biggest difference?

---

**Question 2**

In Step 4.2, did your instruction set score similarly on pr_002 as on pr_001? If the score dropped, what caused the over-fitting?

---

**Question 3**

After Part 5, when would you use your custom instruction set versus `Copilot: Review and Comment` for day-to-day code review on your team?

---

**Question 4**

Write one new rule for `.github/copilot-instructions.md` (in the Code Review Rules section) based on an issue your instruction set found in pr_003 that the current rules do not cover.
