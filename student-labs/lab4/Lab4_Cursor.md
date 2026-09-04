# Lab 4: Pipeline Monitoring and CI/CD Gate Agent
**Course:** AI-Augmented Engineering for Data Engineers
**Tool:** Cursor (Pro plan)
**Duration:** 75 minutes
**Day:** Day 2, following Modules 5 and 6

---

## Prerequisites

- [ ] Modules 5 and 6 lectures completed
- [ ] Lab 3 completed, or Lab 4 starter files loaded (see Step 0)
- [ ] Sample pipeline repository open in Cursor
- [ ] pytest accessible from the terminal
- [ ] Git configured with a linked remote on the Cursor dashboard (`cursor.com/dashboard`) for the optional Task 6

---

## Lab Overview

Your pipeline runs overnight. Your on-call engineer arrives each morning to a directory of Airflow failure logs with no clear starting point. Build an observability agent that generates a prioritized incident briefing, apply Debug mode to the top failure, implement a CI/CD gate agent with deterministic PASS/FAIL/ESCALATE output, add schema drift detection, and implement an audit log that records every agent decision.

This is the capstone lab. It applies content from Chapters 3 through 6 in one integrated build.

**What you will produce:**
- A morning incident briefing agent with severity-sorted output
- A Debug mode investigation of the top failure with a two-sentence root cause summary
- A CI/CD gate agent with deterministic PASS/FAIL/ESCALATE decisions
- Schema drift detection integrated into the gate decision
- `audit/agent_decisions.jsonl` with a record for every agent decision in this lab

---

## Step 0: Load Starter Files

Run this before anything else regardless of whether you completed Lab 3. This overwrites any existing files at these paths.

Open a terminal inside Cursor (`` Ctrl+` ``) and run from the `sample_pipeline/` project root:

```powershell
cp -r lab-starters\lab4\.cursor .
cp -r lab-starters\lab4\src .
cp -r lab-starters\lab4\tests .
cp -r lab-starters\lab4\docs .
cp -r lab-starters\lab4\audit .
```

**macOS/Linux:**
```bash
cp -r lab-starters/lab4/.cursor .
cp -r lab-starters/lab4/src .
cp -r lab-starters/lab4/tests .
cp -r lab-starters/lab4/docs .
cp -r lab-starters/lab4/audit .
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

All tests should pass:

```
tests/test_ingest.py::test_process_records_happy_path PASSED
tests/test_ingest.py::test_process_records_empty_input PASSED
tests/test_ingest.py::test_process_records_null_field PASSED
tests/test_transform.py::... PASSED
tests/test_validate.py::... PASSED
```

`src/` should contain:

```
ingest.py
transform.py
validate.py
```

`audit/agent_decisions.jsonl` should exist and contain one sample record showing the correct format.
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

Note the four failure types represented across the log files: `schema_drift`, `null_rate_spike`, `timeout`, `dependency_failure`.

---

### Step 1.2: Build the briefing agent

Open a new Agent mode conversation. Send:

```
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
ready to paste directly into Debug mode]
```

Attach the log directory using `@Terminals` if the logs directory is visible in an open terminal. If not, add to your prompt: `The log files are in the logs/ directory. Read each file directly.`

Press Enter. Read the full briefing before continuing.

**Time yourself:** from pressing Enter to knowing what to fix first should be under five minutes.

<details>
<summary>What to do if the briefing takes more than five minutes to read</summary>

The recommended action for each finding is too long or too vague. Add this constraint to your instruction set and re-run:

```
Each recommended action must be a single sentence starting with a verb.
Maximum 20 words. If you cannot describe the action in 20 words,
the action is not specific enough.
```
</details>

---

### Step 1.3: Add the briefing decision to the audit log

Open `audit/agent_decisions.jsonl`. Append a record for the briefing agent. Fill in the values from your actual session:

```json
{"agent": "morning_briefing", "timestamp": "[ISO 8601]", "inputs_reviewed": ["logs/failure_001.log", "logs/failure_002.log", "logs/failure_003.log", "logs/failure_004.log"], "decision": "Briefing generated: [X] Critical, [Y] Warning, [Z] Informational", "confidence": "High", "human_review_triggered": false, "model_used": "[model name from mode selector]"}
```

Save the file.

---

## Part 2: Debug Mode Investigation

### Step 2.1: Enter Debug mode

Copy the **Debug mode entry point** paragraph from the end of your Part 1 briefing output.

Switch to **Debug mode** using the mode selector.

Paste the paragraph as your bug description. Add:

```
To reproduce: run the failed pipeline stage against data/sample_input.csv
Expected: [describe what a successful run produces]
Actual: [describe what the failure log shows]
```

---

### Step 2.2: Follow the Debug mode workflow

Follow the six-step Debug mode workflow:

1. Read all hypotheses before any instrumentation is added
2. Do not modify or remove instrumentation statements Debug mode adds
3. Follow the reproduction steps exactly as given
4. Read the root cause analysis before accepting any fix
5. Accept the fix only after you can explain why it works
6. Confirm instrumentation is removed automatically after verification

> **If you cannot explain why the proposed fix works:** ask Debug mode to explain the root cause and the fix in plain language before accepting.

---

### Step 2.3: Write and save the root cause summary

Before moving to Part 3, write a two-sentence summary:

```
Root cause: [what went wrong and why]
Fix applied: [what was changed and how it prevents recurrence]
```

Save this summary. It goes into the audit log in Part 5.

---

### Step 2.4: Add the Debug investigation to the audit log

Append a record to `audit/agent_decisions.jsonl`:

```json
{"agent": "debug_mode_investigation", "timestamp": "[ISO 8601]", "inputs_reviewed": ["logs/[top failure log]", "src/[affected file]"], "decision": "[your two-sentence root cause summary]", "confidence": "High", "human_review_triggered": false, "model_used": "[model name]"}
```

---

## Part 3: CI/CD Gate Agent

### Step 3.1: Read the metrics file

Open `metrics/quality_metrics.json`. Note the three named run objects: `clean_run`, `soft_breach`, `critical_failure`. Note the metric names, values, and threshold fields across all three runs.

---

### Step 3.2: Build the gate agent

Open a new Agent mode conversation. Send:

```
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

The gate agent is exercising model judgment rather than applying deterministic rules. Add this to your instruction set:

```
The decision logic is deterministic. Apply the rules in the exact order
listed above. Do not exercise judgment about whether to upgrade or
downgrade a decision based on any additional context.
```

Re-run the critical_failure evaluation twice. Both must produce FAIL with identical violations.
</details>

Check that `audit/agent_decisions.jsonl` has a new record for each evaluation run. Open the file and confirm three new records were appended -- one for each scenario.

---

## Part 4: Schema Drift Detection

### Step 4.1: Read the registered schema

Open `schemas/expected_schema.json`. Note the field names, data types, and which fields are required.

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
- [ ] The Debug mode investigation (added manually in Part 2)
- [ ] Each CI/CD gate evaluation (appended automatically by the gate agent in Part 3)

<details>
<summary>Expected audit log structure</summary>

Each line is a complete JSON object. The file should look like this:

```jsonl
{"agent": "morning_briefing", "timestamp": "2026-08-28T07:00:00Z", "inputs_reviewed": ["logs/failure_001.log", "logs/failure_002.log", "logs/failure_003.log", "logs/failure_004.log"], "decision": "Briefing generated: 1 Critical, 2 Warning, 1 Informational", "confidence": "High", "human_review_triggered": false, "model_used": "Cursor Grok 4.6 High Fast"}
{"agent": "debug_mode_investigation", "timestamp": "2026-08-28T07:15:00Z", "inputs_reviewed": ["logs/failure_001.log", "src/validate.py"], "decision": "Root cause: null rate on customer_id exceeded threshold due to upstream schema change at 02:14 UTC. Fix applied: added explicit None check before the transform step.", "confidence": "High", "human_review_triggered": false, "model_used": "Cursor Grok 4.6 High Fast"}
{"agent": "cicd_gate", "timestamp": "2026-08-28T07:30:00Z", "inputs_reviewed": ["metrics/quality_metrics.json"], "decision": "FAIL", "confidence": "High", "human_review_triggered": false, "model_used": "Cursor Grok 4.6 High Fast"}
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

> **The audit log commit is the final mandatory step.** Do not skip it under time pressure. An agent system without a committed audit trail is not production-ready.

---

## Part 6: Cloud Agents Window (Optional)

Complete this part only if all of Parts 1 through 5 are finished and your repository has a linked Git remote configured in the Cursor dashboard at `cursor.com/dashboard`.

> **Do not attempt Cloud Agent tasks if `src/` requires Oracle database connectivity to run its tests.** Cloud Agent VMs cannot reach on-premises services. The Lab 4 starter files are designed to run without external connectivity.

---

### Step 6.1: Launch a parallel gate check

Open the Agents Window: `Ctrl+Shift+P`, then type `Open Agents Window` and press Enter.

Start a new task using `/multitask` and describe a gate check scoped to the `soft_breach` metrics run.

Return to the editor. The parallel task runs independently.

---

### Step 6.2: Hand off the briefing agent to /in-cloud

In the Agents Window, start a new conversation.

Type `/in-cloud` followed by the morning briefing task description. The Cloud Agent clones the repository, runs on its own VM, and reports back.

Monitor progress from the Agents Window.

<details>
<summary>If /in-cloud returns a linked remote error</summary>

```
Cloud agents need a linked git remote, and this workspace has none,
so I can't start one here.
```

Your repository is not connected to the Cursor dashboard. Navigate to `cursor.com/dashboard`, link the repository, and retry. If the repository is not on GitHub or a supported SCM provider, skip Step 6.2 and return to the debrief.
</details>

---

## Lab Debrief

Write answers before the room debrief begins. You will share one with the group.

---

**Question 1**

In Part 2, what was the root cause of the top failure? Was it the first hypothesis Debug mode listed, or a different one? What does that tell you about using Debug mode versus your own intuition?

---

**Question 2**

In Part 3, did the gate agent produce the same decision on consecutive runs for `critical_failure`? If not, what instruction change made it deterministic?

---

**Question 3**

The audit log was the last mandatory step. In a real deployment, when should the audit log be designed -- before or after the agent is built? Why?

---

**Question 4**

Write one rule you will add to your team's `.cursor/rules/` file this week based on something this lab revealed that your current rules do not cover.

---

**Question 5**

Write one agent use case from your real DE work that you will scope and build in the next 30 days. Write the Layer 3 test answer: why can you not write a deterministic script for this?

---

## Instructor Notes

> This section is for instructors only and is not distributed to participants.

**Audit log protection:**

The audit log task is the most likely to be cut under time pressure. Allocate 8 minutes specifically for Part 5 and enforce it. Walk the room at the start of Part 5 and confirm every participant has at least the briefing and Debug records before the gate evaluation records are appended automatically.

**Sample file requirements:**

- `logs/`: four failure log files, one per failure type. Each must contain enough context for the briefing agent to classify the failure type and affected stage from log content alone.
- `metrics/quality_metrics.json`: three named run objects. `clean_run` all within threshold. `soft_breach` one warn_on_breach metric exceeding threshold. `critical_failure` one critical_on_breach metric with at least one additional violation.
- `schemas/expected_schema.json`: at least eight fields. `data/sample_input.csv` must have at least one non-breaking schema difference to produce a non-empty drift output.

**Starter files:**

`lab-starters/lab4/` contains everything from `lab-starters/lab3/` plus `src/transform.py`, `src/validate.py`, their passing test suites, and `audit/agent_decisions.jsonl` with one sample record showing the correct JSONL format. Verify `pytest tests/ -v` passes cleanly after loading.

**Verification gaps:**

- `@Terminals` context attachment: confirm this attaches the terminal buffer in the delivery Cursor version. If not, the fallback is the explicit directory instruction in the prompt.
- Gate agent auto-append to JSONL: confirm the agent appends correctly without reformatting the existing file. If it rewrites the file, add the instruction: `Use append mode. Do not reformat or rewrite any existing lines in the file.`
- `/in-cloud` requires GitHub remote: confirmed from live testing. The error message gives clear guidance. No additional instructor intervention needed unless the client's SCM is not supported.
