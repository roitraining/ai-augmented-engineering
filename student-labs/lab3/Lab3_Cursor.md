# Lab 3: Build a DE Pipeline Code Review Agent
**Course:** AI-Augmented Engineering for Data Engineers
**Tool:** Cursor (Pro plan)
**Duration:** 75 minutes
**Day:** Day 2, following Module 4

---

## Prerequisites

- [ ] Modules 3 and 4 lectures completed
- [ ] Chapter 3 scoping exercise completed (or scope specification template at end of this document reviewed)
- [ ] Lab 2 completed, or Lab 3 starter files loaded (see Step 0)
- [ ] Sample pipeline repository open in Cursor
- [ ] Git configured and at least one commit on the repository

---

## Lab Overview

Your team reviews dozens of Python pipeline PRs each week. Manual review is inconsistent and depends on who is available. Build a Cursor agent that reviews pipeline code against DE-specific criteria, flags issues with severity ratings, and produces a structured review summary ready for human sign-off. Then configure `.cursor/BUGBOT.md` and compare Agent Review output with your custom agent.

**What you will produce:**
- A working code review agent instruction set with all five scope components
- A quality rubric score across two iteration cycles
- `.cursor/BUGBOT.md` configured with DE review rules
- A written comparison of your custom agent versus Agent Review on the same PR

---

## Step 0: Load Starter Files

Run this before anything else regardless of whether you completed Lab 2. This overwrites any existing files at these paths.

Open a terminal inside Cursor (`` CTRL+` ``) and run from the `sample_pipeline/` project root:

```powershell
cp -r lab-starters\lab3\.cursor .
cp -r lab-starters\lab3\src .
cp -r lab-starters\lab3\tests .
cp -r lab-starters\lab3\docs .
cp -r lab-starters\lab3\audit .
```

**macOS/Linux:**
```bash
cp -r lab-starters/lab3/.cursor .
cp -r lab-starters/lab3/src .
cp -r lab-starters/lab3/tests .
cp -r lab-starters/lab3/docs .
cp -r lab-starters/lab3/audit .
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

If any test fails, the starter files did not copy correctly. Re-run the copy commands from the correct project root.

`src/ingest.py` should also exist and contain a complete idiomatic Python conversion of `perl/ingest.pl`. This is the baseline the three sample PRs are built on top of.
</details>

---

## Part 1: Review Your Scope Specification and Build the Agent

### Step 1.1: Review your scope specification

Open your Chapter 3 scope specification document.

Confirm it covers all five components. If any are missing, add them now using these definitions:

| Component | Definition |
|---|---|
| **Tools** | `@Branch (Diff with Main)` for context. Read-only access only—the agent must not edit any files. |
| **Instructions** | Review against `.cursor/rules/de-standards.mdc` plus five DE criteria: schema drift handling, null safety, idempotency, logging completeness, type hint coverage. |
| **Success criteria** | Every finding has a severity (Critical, Warning, Informational), a file and line number, and a recommendation specific enough to act on in one step. |
| **Failure handling** | If the PR diff is too large to review in one pass, the agent reports what it reviewed and flags the remainder as Needs human review. |
| **Escalation path** | Any finding where agent confidence is Low is escalated rather than included in the summary. |

<details>
<summary>Scope specification template (use if you did not complete the Chapter 3 exercise)</summary>

```
Tools: @Branch (Diff with Main) for context. Read-only file access.
The agent must not edit any files.

Instructions: Review changed code against .cursor/rules/de-standards.mdc
and five DE criteria:
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
1. Non-deterministic output -- same PR produces different findings on
   consecutive runs. Mitigation: explicit output format template.
2. Scope creep -- agent comments on code outside the diff. Mitigation:
   explicit instruction to review only changed lines.
```
</details>

---

### Step 1.2: Build the Version 1 instruction set

Open a new Agent mode conversation.

Send the following as the first message. This is your Version 1—you will improve it in Parts 2 and 3:

```
You are a DE pipeline code review agent.
Context: @Branch (Diff with Main). Review only changed lines.
Do NOT modify any files.

Review the changes against .cursor/rules/de-standards.mdc and:
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

---

### Step 1.3: Run against PR 001

Switch to the `pr/001` branch:

```powershell
git checkout pr/001
```

**macOS/Linux:**
```bash
git checkout pr/001
```

In the Agent mode conversation from Step 1.2, type `@` and select **Branch (Diff with Main)** from the menu.

<details>
<summary>If @Branch does not appear in the menu</summary>

The label may appear as **@Diff** or **@Git Diff** depending on your Cursor version. All three refer to the same capability—the full diff of your current branch against main.

If no diff option appears at all, confirm you switched to the `pr/001` branch and have at least one commit on it that differs from main.
</details>

Type: `Review the changes on this branch.` and press Enter.

Read every finding before moving to Part 2.

---

## Part 2: First Run and Quality Rubric Score

### Step 2.1: Score the output against the rubric

Score each dimension from 1 (poor) to 5 (excellent). Use the known-issues list your instructor provides to check for false negatives.

| Dimension | Score (1--5) | Notes |
|---|---|---|
| **Coverage**—did the agent find all issues in pr_001? | | |
| **Accuracy**—of issues flagged, how many are real? | | |
| **Clarity**—can you read the summary and know exactly what to do next? | | |
| **Consistency**—run the agent on pr_001 a second time. How similar are the two outputs? | | |
| **Total** | **/20** | |

<details>
<summary>Scoring guidance for each dimension</summary>

**Coverage (finding false negatives):** Your instructor has a list of known issues in pr_001. Compare the agent's findings against the list. Each missed issue costs one point. Score 5 only if the agent found every known issue.

**Accuracy (finding false positives):** Count how many agent findings describe issues that do not actually exist in the code. Each false positive costs one point. Score 5 only if every finding is real.

**Clarity (actionability):** Read each recommendation. Could you act on it immediately without asking a follow-up question? A finding that says "consider improving null handling" is not actionable. A finding that says "add an explicit None check on `customer_id` at line 47 before passing it to `transform_record()`" is. Score 5 only if every recommendation is immediately actionable.

**Consistency (determinism):** Run the identical prompt a second time with `@Branch` re-attached. Compare the two outputs. Score 5 if the findings are identical. Score 1 if the severity ratings or the finding list differs significantly between runs.

**Production threshold:** 16 out of 20 with no dimension below 3. First-run scores below 14 are normal.
</details>

**Identify the single lowest-scoring dimension.** That is your improvement target for Part 3.

---

## Part 3: First Iteration Cycle

### Step 3.1: Note the current instruction set state

Before changing anything, find the message containing your instruction set in the chat timeline. Note that the **Restore Checkpoint** button is available on that message—you can revert to this state if your change makes things worse.

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

**Consistency low:** Add an explicit output template with required field names.

```
For every finding, output exactly these fields in this order:
CRITERION: [name]
LOCATION: [file]:[line]
SEVERITY: [Critical|Warning|Informational]
CONFIDENCE: [High|Medium|Low]
RECOMMENDATION: [single actionable sentence starting with a verb]
```
</details>

Send the updated instruction set as a new message in the conversation.

---

### Step 3.3: Re-run on PR 001 and re-score

Re-attach `@Branch` and type: `Review the changes on this branch using the updated instructions.`

Score all four dimensions again. Record the new total.

| Result | Action |
|---|---|
| Target dimension improved | Keep the change. Record new total score. |
| Target dimension unchanged or worse | Restore from the checkpoint noted in Step 3.1. Try a different approach to the same dimension. |
| Another dimension dropped significantly | Restore and try a narrower change. |

---

## Part 4: Second Iteration Cycle and Generalization Test

### Step 4.1: Second iteration

Identify the new lowest-scoring dimension from your Part 3 score. Make one more targeted change using the same approach as Part 3.

If you have already reached 16 out of 20 with no dimension below 3, move directly to Step 4.2. Do not force an additional change.

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

Re-attach `@Branch` and type: `Review the changes on this branch.`

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

Re-attach `@Branch` and type: `Review the changes on this branch.`

PR 003 contains a security-sensitive credential handling change. Verify:

- [ ] The security-sensitive finding is marked ESCALATE (Low confidence)
- [ ] The security-sensitive finding is NOT included in the main summary
- [ ] The overall recommendation is ESCALATE or REQUEST CHANGES, not APPROVE

> **If the overall recommendation is APPROVE:** the escalation criteria are not working. Tighten the escalation path in your instruction set and re-run before moving to Part 5.

---

## Part 5: .cursor/BUGBOT.md and Agent Review

### Step 5.1: Understand what you are configuring

Two distinct systems are used in this part. Keep them separate:

| System | What it is | What it reads |
|---|---|---|
| **Bugbot** | PR automation requiring SCM connection via Cursor dashboard | `.cursor/BUGBOT.md` |
| **Agent Review** | Local in-editor review, no SCM required | `.cursor/BUGBOT.md` |
| **Your .cursor/rules/*.mdc files** | In-editor agent context | NOT read by either Bugbot or Agent Review |

> **Critical:** `.cursor/rules/*.mdc` files are NOT read by Bugbot or Agent Review. Rules for these tools must be written separately in `.cursor/BUGBOT.md`. Your `de-standards.mdc` rules from Lab 1 do not flow into Bugbot or Agent Review automatically.

---

### Step 5.2: Create .cursor/BUGBOT.md

In the Cursor file explorer, navigate to `.cursor/` inside the project.

Create a new file named `BUGBOT.md` inside the `.cursor/` directory.

> **The correct path is `.cursor/BUGBOT.md`**—not `BUGBOT.md` at the project root, and not `.cursor/rules/BUGBOT.md`. A file at the wrong path is silently ignored.

Add the following content:

```markdown
# DE Pipeline Review Rules

## Critical
- Any function reading from external data sources must validate
  the schema before processing records
- Null values on customer_id, transaction_date, and amount fields
  must be handled explicitly
- Pipeline steps that write records must be idempotent: running
  twice must not produce duplicate output

## Warning
- All functions must have type hints on all arguments and the return value
- Pipeline entry and exit must be logged using the project logger
- All file operations must use pathlib.Path

## Informational
- Use collections.Counter for counting and frequency analysis patterns
- Use list comprehensions where they improve readability over for-append loops
```

Save and commit:

```powershell
git add .cursor\BUGBOT.md
git commit -m "Add .cursor/BUGBOT.md with DE pipeline review rules"
```

**macOS/Linux:**
```bash
git add .cursor/BUGBOT.md
git commit -m "Add .cursor/BUGBOT.md with DE pipeline review rules"
```

---

### Step 5.3: Enable and run Agent Review

Open Cursor Settings (`CTRL+,` on Windows, `CMD+,` on Mac). Search for **Agent Review**.

Enable Agent Review at **Quick** depth.

> **If the settings path has moved:** try searching for "review" in settings. In Cursor 3.11 and later, Agent Review may be under **Git and PRs** rather than **Agents**.

Switch back to the `pr/001` branch:

```powershell
git checkout pr/001
```

**macOS/Linux:**
```bash
git checkout pr/001
```

Open the **Source Control** tab in the left sidebar. Look for a **Review** or **Agent Review** button and run it against the pr_001 changes.

---

### Step 5.4: Compare Agent Review to your custom agent

Fill in this comparison table using the Agent Review output and your best custom agent output from Part 4:

| | Your custom agent | Agent Review |
|---|---|---|
| Known pr_001 issues found | /3 | /3 |
| False positives | | |
| Most actionable finding | | |
| Time to produce output | | |

**Write one sentence:**

> When would you use Agent Review instead of your custom agent in your daily work, and when would you use the custom agent instead?

<details>
<summary>Typical answer pattern</summary>

Agent Review is faster and requires no setup -- use it for a quick sanity check before pushing. Your custom agent produces more structured output with severity ratings, confidence levels, and DE-specific criteria -- use it before raising a PR or during an asynchronous review process where the output needs to be actionable by someone who was not present during the review.

Neither replaces the other. The professional workflow is: Agent Review before pushing, custom agent before raising the PR.
</details>

---

## Lab Debrief

Write answers before the room debrief begins. You will share one with the group.

---

**Question 1**

What was your baseline score and your final score after two iteration cycles? What single change made the biggest difference?

---

**Question 2**

In Step 4.2, did your agent score similarly on pr_002 as on pr_001? If the score dropped, what caused the over-fitting?

---

**Question 3**

After Part 5, when would you use your custom agent versus Agent Review for day-to-day code review on your team?

---

**Question 4**

Write one new rule for `.cursor/BUGBOT.md` based on an issue your agent found in pr_003 that your current BUGBOT.md does not cover.

---

## Instructor Notes

> This section is for instructors only and is not distributed to participants.

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
