# Lab 4: Pipeline Monitoring and CI/CD Gate Agent
**Course:** AI-Augmented Engineering for Data Engineers
**Tool:** GitHub Copilot Enterprise (VS Code)
**Duration:** 75 minutes
**Day:** Day 2, following Modules 5 and 6

---

## Prerequisites

- [ ] Modules 5 and 6 lectures completed
- [ ] Lab 3 completed, or Lab 4 Copilot starter files loaded (see Step 0)
- [ ] VS Code open with GitHub Copilot Chat active
- [ ] Sample pipeline repository open in VS Code
- [ ] pytest accessible from the terminal
- [ ] Repository connected to GitHub (required for Part 6)

---

## A Note on Coverage

This lab follows the same five-part structure and learning objectives as the Cursor version. Where GitHub Copilot Enterprise has a direct equivalent, this lab uses it.

| Cursor feature | Copilot approach used in this lab |
|---|---|
| `@Terminals` for log context | `@terminal` in Copilot Chat (confirmed available in VS Code) |
| Debug mode (six-step, structured) | Abbreviated constrained prompt workflow—refer to Lab 2 for full detail |
| `/in-cloud` (Cloud Agent handoff) | Copilot coding agent via GitHub issue assignment |
| `/multitask` (parallel subagents) | Copilot Agents Window—multiple parallel sessions |
| Cursor dashboard for remote linking | GitHub repository—no dashboard setup required |

The optional Part 6 uses GitHub as the SCM, which removes the dashboard linking step required in the Cursor version. If your repository is already on GitHub with Copilot Enterprise assigned, Part 6 works without any additional setup.

---

## Lab Overview

Your pipeline runs overnight. Build an observability agent that generates a prioritized incident briefing, investigate the top failure using an evidence-first debugging workflow, implement a CI/CD gate agent with deterministic decisions, add schema drift detection, and implement an audit log that records every agent decision.

**What you will produce:**
- A morning incident briefing agent with severity-sorted output
- An evidence-first investigation of the top failure with a two-sentence root cause summary
- A CI/CD gate agent with deterministic PASS/FAIL/ESCALATE decisions
- Schema drift detection integrated into the gate decision
- `audit/agent_decisions.jsonl` with a record for every agent decision in this lab

---

## Step 0: Load Starter Files

Run this before anything else regardless of whether you completed Lab 3. This overwrites any existing files at these paths.

Open a terminal inside VS Code (`` CTRL+` ``) and run from the `sample_pipeline/` project root:

```powershell
cp -r copilot-starters\lab4\.github .
cp -r copilot-starters\lab4\src .
cp -r copilot-starters\lab4\tests .
cp -r copilot-starters\lab4\docs .
cp -r copilot-starters\lab4\audit .
```

**macOS/Linux:**
```bash
cp -r copilot-starters/lab4/.github .
cp -r copilot-starters/lab4/src .
cp -r copilot-starters/lab4/tests .
cp -r copilot-starters/lab4/docs .
cp -r copilot-starters/lab4/audit .
```

Verify:

```powershell
pytest tests\ -v
ls src\
```

**macOS/Linux:**
```bash
pytest tests/ -v
ls src/
```

<details>
<summary>Expected output</summary>

All tests should pass across all three pipeline modules.

`src/` should contain `ingest.py`, `transform.py`, and `validate.py`.

`audit/agent_decisions.jsonl` should exist and contain one sample record showing the correct JSONL format.

<details>
<summary>Sample record format in the starter file</summary>

```json
{"agent": "example_agent", "timestamp": "2026-08-28T06:00:00Z", "inputs_reviewed": ["example_input.csv"], "decision": "Example decision text", "confidence": "High", "human_review_triggered": false, "model_used": "GitHub Copilot Enterprise"}
```

Every record you append in this lab must match this structure exactly. The six fields are required: `agent`, `timestamp`, `inputs_reviewed`, `decision`, `confidence`, `human_review_triggered`, `model_used`.
</details>
</details>

---

## Part 1: Morning Incident Briefing Agent

### Step 1.1: Examine the log files

Open a terminal. List and preview the overnight failure logs:

```powershell
ls logs\
Get-Content logs\failure_001.log -Head 20
```

**macOS/Linux:**
```bash
ls logs/
head -20 logs/failure_001.log
```

Note the four failure types across the log files: `schema_drift`, `null_rate_spike`, `timeout`, `dependency_failure`.

---

### Step 1.2: Build the briefing agent

Open a new Copilot Chat conversation.

Type `@terminal` in the chat input. This attaches context from your integrated terminal, including any log output currently visible in the terminal buffer.

<details>
<summary>What @terminal attaches and when to use it</summary>

`@terminal` is a VS Code Copilot Chat participant that knows about the integrated terminal shell, its contents, and its buffer. It attaches recent terminal output as context without requiring you to copy and paste.

For the briefing agent, run the following in the terminal first so the log directory listing is in the buffer:

```powershell
ls logs\; Get-Content logs\failure_001.log
```

**macOS/Linux:**
```bash
ls logs/ && cat logs/failure_001.log
```

Then type `@terminal` in Copilot Chat. Copilot will have the terminal output as context alongside your prompt.

If `@terminal` does not produce the expected context, use the `#file:` fallback: attach each log file individually with `#file:logs/failure_001.log` etc.
</details>

Send the following prompt after typing `@terminal`:

```
@terminal

Do not edit any files.

You are a pipeline observability agent.
Read all failure log files in the logs/ directory.
For each failure determine:
- failure_type: schema_drift / null_rate_spike / timeout /
  dependency_failure / unknown
- severity: Critical / Warning / Informational
- affected_stage: which pipeline stage failed
- recommended_action: one specific actionable next step
- confidence: High / Medium / Low

Sort all failures by severity (Critical first), not by log timestamp.

Output format:
## Morning Incident Briefing -- [date]

### CRITICAL
[failure_type] | [affected_stage] | Confidence: [level]
Recommended action: [specific action]

### WARNING
[same format]

### INFORMATIONAL
[same format]

### Debug mode entry point
[one paragraph bug description for the highest-severity failure,
ready to use as evidence-first debugging input]
```

Read the full briefing before continuing.

**Time yourself:** from pressing Enter to knowing what to fix first should be under five minutes.

<details>
<summary>What to do if the briefing takes more than five minutes to read</summary>

The recommended action for each finding is too long or too vague. Add this constraint and re-run in a new conversation:

```
Each recommended action must be a single sentence starting with a verb.
Maximum 20 words.
```
</details>

---

### Step 1.3: Add the briefing decision to the audit log

Open `audit/agent_decisions.jsonl`. Append a record for the briefing agent:

```json
{"agent": "morning_briefing", "timestamp": "[ISO 8601]", "inputs_reviewed": ["logs/failure_001.log", "logs/failure_002.log", "logs/failure_003.log", "logs/failure_004.log"], "decision": "Briefing generated: [X] Critical, [Y] Warning, [Z] Informational", "confidence": "High", "human_review_triggered": false, "model_used": "GitHub Copilot Enterprise"}
```

Save the file.

---

## Part 2: Evidence-First Debugging Investigation

### Step 2.1: Run the constrained debugging workflow

This part uses the six-step evidence-first workflow from Lab 2 Part 5. The steps are abbreviated here—refer to Lab 2 for full detail on each step.

Copy the **Debug mode entry point** paragraph from the end of your Part 1 briefing output.

Open a new Copilot Chat conversation. Work through the six steps using constrained prompts:

**Step 1—Hypotheses only:**

```
Do not modify any files. Do not propose a fix yet.

[paste the Debug mode entry point paragraph here]

Generate exactly three hypotheses for the root cause.
For each, describe where you would add logging to confirm or rule it out.
Do not add any logging yet.
```

**Step 2—Instrumentation:**

```
Based on hypothesis [N], add targeted logging marked # DEBUG
to collect runtime evidence. Add logging only. Do not change any logic.
```

**Step 3—Reproduce:**

Run the reproduction steps from the terminal. Capture the `# DEBUG` log output.

**Step 4—Analyze:**

```
Here is the runtime log output:
[paste the # DEBUG log lines]

Which hypothesis is confirmed? Explain the root cause only.
Do not propose a fix yet.
```

**Step 5—Fix:**

```
Now propose the targeted fix. Explain why it works before applying it.
```

**Step 6—Verify and clean up:**

Run verification. Then:

```
Remove all lines marked # DEBUG. Do not change any other code.
```

Confirm no `# DEBUG` lines remain:

```powershell
Select-String -Path src\*.py -Pattern "# DEBUG"
```

**macOS/Linux:**
```bash
grep -r "# DEBUG" src/
```

---

### Step 2.2: Write and save the root cause summary

Write a two-sentence summary before moving to Part 3:

```
Root cause: [what went wrong and why]
Fix applied: [what was changed and how it prevents recurrence]
```

---

### Step 2.3: Add the investigation to the audit log

Append a record to `audit/agent_decisions.jsonl`:

```json
{"agent": "debugging_investigation", "timestamp": "[ISO 8601]", "inputs_reviewed": ["logs/[top failure log]", "src/[affected file]"], "decision": "[your two-sentence root cause summary]", "confidence": "High", "human_review_triggered": false, "model_used": "GitHub Copilot Enterprise"}
```

---

## Part 3: CI/CD Gate Agent

### Step 3.1: Read the metrics file

Open `metrics/quality_metrics.json`. Note the three named run objects: `clean_run`, `soft_breach`, `critical_failure`. Note the metric names, values, and threshold fields.

---

### Step 3.2: Build the gate agent

Open a new Copilot Chat conversation. Send:

```
Do not edit any files except audit/agent_decisions.jsonl.

You are a CI/CD quality gate agent.
Read metrics/quality_metrics.json.
Evaluate each metric against its defined threshold.

Decision rules (apply in this exact order):
- If any metric marked critical_on_breach exceeds threshold: decision = FAIL
- If any metric marked warn_on_breach exceeds threshold: decision = ESCALATE
- If all metrics are within threshold: decision = PASS

Output exactly this structure:
{
  "decision": "PASS" | "FAIL" | "ESCALATE",
  "metrics_evaluated": [list of metric names checked],
  "violations": [{metric, value, threshold, severity}],
  "rationale": "one sentence plain-language explanation",
  "timestamp": "ISO 8601 timestamp"
}

After the JSON, output a plain-language two-sentence version
for the on-call engineer.

After producing the decision, append one record to
audit/agent_decisions.jsonl with these fields:
agent, timestamp, inputs_reviewed, decision, confidence,
human_review_triggered (true if ESCALATE), model_used.
Append only. Do not rewrite the existing file.
```

---

### Step 3.3: Test all three scenarios

Send each evaluation in the same conversation:

```
Evaluate the clean_run metrics.
```

Verify decision is **PASS**.

```
Evaluate the soft_breach metrics.
```

Verify decision is **ESCALATE**.

```
Evaluate the critical_failure metrics.
```

Verify decision is **FAIL**.

---

### Step 3.4: Test decision consistency

Run the `critical_failure` evaluation a second time without changing anything.

The decision and violations list must be identical between runs.

<details>
<summary>What to do if the decision differs between runs</summary>

Add this to your instruction set and re-run:

```
The decision logic is deterministic. Apply the rules in the exact order
listed above. Do not exercise judgment about whether to upgrade or
downgrade a decision based on any additional context.
```
</details>

Open `audit/agent_decisions.jsonl` and confirm a new record was appended for each evaluation.

---

## Part 4: Schema Drift Detection

### Step 4.1: Read the registered schema

Open `schemas/expected_schema.json`. Note the field names, data types, and required fields.

---

### Step 4.2: Extend the gate agent

In the gate agent conversation, send:

```
Also check for schema drift.
Compare the incoming data schema (read from the first row of
data/sample_input.csv) against the registered schema in
schemas/expected_schema.json.

Classify each difference:
- Breaking (column removed, type incompatibly changed, required
  field made nullable): add schema_drift_breaking to violations,
  severity=Critical. If any breaking drift: decision = FAIL
  regardless of other metrics.
- Non-breaking (new column, widened type, optional field added):
  add schema_drift_non_breaking to violations, severity=Warning.
- Informational (metadata only): note in rationale only.
```

Run the full gate check including schema drift against `critical_failure` metrics.

Verify the output includes both quality metric violations and schema drift findings.

---

## Part 5: Audit Log Completion

### Step 5.1: Confirm the audit log is complete

Open `audit/agent_decisions.jsonl`. Confirm it contains records for:

- [ ] The morning briefing agent (added manually in Part 1)
- [ ] The debugging investigation (added manually in Part 2)
- [ ] Each CI/CD gate evaluation (appended automatically by the gate agent in Part 3)

<details>
<summary>Expected audit log structure</summary>

Each line is a complete JSON object:

```jsonl
{"agent": "morning_briefing", "timestamp": "2026-08-28T07:00:00Z", "inputs_reviewed": ["logs/failure_001.log", "logs/failure_002.log", "logs/failure_003.log", "logs/failure_004.log"], "decision": "Briefing generated: 1 Critical, 2 Warning, 1 Informational", "confidence": "High", "human_review_triggered": false, "model_used": "GitHub Copilot Enterprise"}
{"agent": "debugging_investigation", "timestamp": "2026-08-28T07:15:00Z", "inputs_reviewed": ["logs/failure_001.log", "src/validate.py"], "decision": "Root cause: null rate on customer_id exceeded threshold due to upstream schema change at 02:14 UTC. Fix applied: added explicit None check before the transform step.", "confidence": "High", "human_review_triggered": false, "model_used": "GitHub Copilot Enterprise"}
{"agent": "cicd_gate", "timestamp": "2026-08-28T07:30:00Z", "inputs_reviewed": ["metrics/quality_metrics.json"], "decision": "FAIL", "confidence": "High", "human_review_triggered": false, "model_used": "GitHub Copilot Enterprise"}
```
</details>

---

### Step 5.2: Commit the audit log

```powershell
git add audit\agent_decisions.jsonl
git commit -m "Add agent audit log for Lab 4 session"
```

**macOS/Linux:**
```bash
git add audit/agent_decisions.jsonl
git commit -m "Add agent audit log for Lab 4 session"
```

> **The audit log commit is the final mandatory step.** Do not skip it under time pressure.

---

## Part 6: Copilot Coding Agent via GitHub (Optional)

Complete this part only if all of Parts 1 through 5 are finished and your repository is connected to GitHub with Copilot Enterprise enabled.

---

### Step 6.1: Raise a GitHub issue for a parallel gate check

Navigate to your repository on GitHub.com. Open the **Issues** tab and create a new issue:

**Title:** `Run CI/CD gate check against soft_breach metrics and report findings`

**Body:**
```
Run the quality gate agent against the soft_breach metrics in
metrics/quality_metrics.json. Report the decision, violations list,
and plain-language rationale. Append the result to
audit/agent_decisions.jsonl.
```

Assign **Copilot** as the assignee. Click **Assign to Copilot** or select Copilot from the assignee dropdown.

<details>
<summary>What happens when you assign Copilot to an issue</summary>

Copilot reads the issue description, creates an implementation plan, clones the repository, executes the task, and opens a pull request with the results.

For this task, Copilot should run the gate evaluation and append an audit record. Review the PR diff before merging to confirm the audit record was appended correctly and no other files were changed.

This is the Copilot equivalent of Cursor's `/in-cloud` command. The difference: Cursor's `/in-cloud` is triggered from inside the editor. Copilot's coding agent is triggered from GitHub Issues. Both hand off a task to a cloud agent running on a remote VM.
</details>

---

### Step 6.2: Run parallel sessions in the Agents Window

Open the VS Code Agents Window (`CTRL+SHIFT+P`, search `Open Agents Window` or `Copilot: Open Agents Window`).

Start two agent sessions simultaneously:

**Session 1:** Ask Copilot to analyze the log files and identify which failure type has occurred most frequently based on log timestamps.

**Session 2:** Ask Copilot to review the schema drift findings from Part 4 and suggest three additional fields that should be added to `schemas/expected_schema.json` based on the incoming data patterns.

Monitor both sessions from the Agents Window. Each runs independently without blocking the other.

<details>
<summary>This is the Copilot equivalent of Cursor's /multitask</summary>

Cursor's `/multitask` runs async subagents in parallel from the Agents Window. The VS Code Copilot Agents Window (available as of July 2026) provides the same capability: multiple agent sessions running simultaneously, trackable from one interface.

The July 2026 VS Code release added worktree support to the Agents Window -- each session can work in an isolated Git worktree without affecting the others. If your VS Code version supports worktrees in the Agents Window, you can enable this from the session settings.
</details>

---

## Lab Debrief

Write answers before the room debrief begins. You will share one with the group.

---

**Question 1**

In Part 2, what was the root cause of the top failure? Was it the first hypothesis you generated, or a different one? Did the constrained prompt workflow feel different from how you would normally debug with Copilot?

---

**Question 2**

In Part 3, did the gate agent produce the same decision on consecutive runs for `critical_failure`? If not, what instruction change made it deterministic?

---

**Question 3**

The audit log was the last mandatory step. In a real deployment, when should the audit log be designed -- before or after the agent is built? Why?

---

**Question 4**

Write one instruction you will add to your team's `.github/copilot-instructions.md` this week based on something this lab revealed that your current instructions do not cover.

---

**Question 5**

Write one agent use case from your real DE work that you will scope and build in the next 30 days. Write the Layer 3 test answer: why can you not write a deterministic script for this?

---

## Instructor Notes

> This section is for instructors only and is not distributed to participants.

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
