# Lab 4: Pipeline Monitoring and CI/CD Gate Agent
**Course:** AI-Augmented Engineering for Data Engineers
**Tool:** Cursor (Pro or Teams plan)
**Duration:** 75 minutes
**Day:** Day 2, following Modules 5 and 6

---

## Prerequisites

- [ ] Modules 5 and 6 lectures completed
- [ ] Lab 3 completed, or not; Task 0 loads the Lab 4 starting point either way
- [ ] The repository's `lab-workspace` folder open in the Cursor IDE, with the venv active in the terminal
- [ ] pytest accessible from the terminal
- [ ] Optional, for Task 6.2 only: a fork of the repo under your own GitHub account, linked at `cursor.com/dashboard` with the Cursor GitHub app installed

---

## Lab Overview

Your pipeline runs overnight. Your on-call engineer arrives each morning to a directory of Airflow failure logs with no clear starting point. Build an observability agent that generates a prioritized incident briefing, apply Debug mode to the top failure, implement a CI/CD gate agent with deterministic PASS/FAIL/ESCALATE output, add schema drift detection, and keep an audit log that records every agent decision.

This is the capstone lab. It applies content from Chapters 3 through 6 in one integrated build.

**What you will produce:**
- `.cursor/agents/incident-briefing.md`: a read-only briefing subagent with severity-sorted output
- A Debug mode investigation of the top failure with a two-sentence root cause summary
- A CI/CD gate agent with deterministic PASS/FAIL/ESCALATE decisions
- Schema drift detection integrated into the gate decision
- `audit/agent_decisions.jsonl` with a record for every agent decision in this lab

**How this lab is written:** each Task has numbered steps. A numbered step is something you do. Text between steps explains what you are looking at; the boxes marked "What you should see" tell you what a correct result looks like. The agent's behaviour varies from run to run: it may ask questions before acting, act at once, or describe a change and wait for your go-ahead. If it asks, answer; if it waits, reply `Go ahead`. The steps describe the end state, not every turn of the conversation.

---

## Task 0: Load the starter files

Do this whether or not you completed Lab 3. It resets the workspace to the Lab 4 starting point, including the `audit/` folder this lab writes to.

1. Open a terminal inside Cursor: menu **Terminal → New Terminal**. It opens in `lab-workspace/`; every command in this lab runs from there.

2. Make sure the prompt starts with `(venv)`. If it does not, run `source venv/bin/activate` (Windows: `venv\Scripts\activate`).

3. Put away anything unfinished. Run `git status --short`; if it prints anything, commit on the branch you are on:

   ```bash
   git add -A
   git commit -m "Lab 3 checkpoint"
   ```

4. Go back to `main` (Lab 3 left you on a `pr/` branch):

   ```bash
   git checkout main
   ```

5. Load the Lab 4 starter files:

   ```bash
   python lab.py start 4
   ```

   If the loader refuses because of uncommitted changes, repeat step 3.

6. Confirm the load:

   ```bash
   python lab.py status
   ```

<details open>
<summary>What you should see</summary>

```
Workspace: .../ai-augmented-engineering/lab-workspace
  lab1       ...
  lab2       ...
  lab3       ...
  lab4       25/25 files identical, 0 extra lab file(s) present  <- matches
  solution   ...
git: uncommitted changes present
```

Only the **lab4** line matters: `25/25 files identical` and `<- matches`. `git: uncommitted changes present` is normal here; step 7 clears it.
</details>

7. Create the branch this lab works on, then commit the starting state on it:

   ```bash
   git checkout -B lab4
   git branch --show-current
   git add -A
   git commit -m "Lab 4 start state"
   ```

   The second command must print `lab4` before you read on. **`-B`, not `-b`.** If you are starting this lab over and the branch already exists, `-b` fails — and because the next command runs anyway, the start-state commit lands on `main` instead of on your branch. `-B` resets the branch to where you are now, so the step works the first time and every time after.

8. Confirm the tests pass and the working files are there:

   ```bash
   pytest tests/ -q
   ls src/ audit/
   ```

<details open>
<summary>What you should see</summary>

`42 passed`. `src/` contains `__init__.py`, `figi_client.py`, `ingest.py`, `transform.py`, `validate.py`. `audit/` contains `agent_decisions.jsonl`.
</details>

9. In the Explorer, open `audit/agent_decisions.jsonl` and leave the tab open. It holds one sample record showing the format; you add records to it by hand in Tasks 1 and 2.

10. Confirm **File → Auto Save** has a check mark next to it.

---

## Task 1: Morning incident briefing agent

### Task 1.1: Examine the log files

1. Confirm the overnight failure logs are there:

   ```bash
   ls logs/
   ```

   Four files, `failure_001.log` through `failure_004.log`.

2. Open all four in the editor and skim them. Four failure types are represented: `schema_drift`, `null_rate_spike`, `timeout`, `dependency_failure`.

---

### Task 1.2: Build the briefing subagent

In Lab 3 you built a reviewer as a subagent instead of a prompt, so it survived the conversation that made it. Do the same here: the morning briefing is the most repeated job on this list, and it is read-only, which makes it the easiest agent you will ever scope.

1. Click **+** for a new conversation, then **check the mode before you type anything**. Open the
   mode picker (∞) at the bottom of the chat input and confirm it reads **Agent**.

   A new conversation does not always open in Agent mode — it can inherit the mode from the last
   conversation in that window, so a window you last used in Ask mode opens in Ask mode. Ask mode
   cannot write files, so `/create-subagent` will discuss your agent at length and create nothing.
   If the run produces no file, this is why.

2. Type `/`, choose **create-subagent**, and after the tag paste the following, starting with the line `Create a subagent named incident-briefing.`:

   ```
   Create a subagent named incident-briefing.
   You are a pipeline observability agent.
   The log files are in the logs/ directory. Read each file directly.

   For each failure determine:
   failure_type (schema_drift / null_rate_spike / timeout / dependency_failure / unknown);
   severity (Critical / Warning / Informational);
   affected_stage (which pipeline stage failed);
   recommended_action (one specific actionable next step);
   confidence (High / Medium / Low).

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

3. Click **Keep** in the change summary. The new file is `.cursor/agents/incident-briefing.md`.

4. Open it and check the two settings: **Read-only** on, **Background** off. Cursor often gets
   both right from your prompt, and it may carry them over from the last agent you built, so
   this is a confirmation rather than a change. Set whichever is wrong.

   Read-only is right for the same reason it was right in Lab 3: a briefing reads logs and writes nothing, so take the edit tools away rather than asking it not to use them. Background stays off on purpose, and Task 2 is why: a foreground subagent hands its findings back into this conversation, so you can switch this same conversation to Debug mode next. A background subagent would return immediately and leave the briefing in a tab of its own.

5. Click **+** for a new conversation, note the time, type `/`, choose **incident-briefing** and press Enter.

6. Read the full briefing. Expand the **Explored** lines above it to confirm it read all four logs; if it read only some, send `Read all four files in logs/ and redo the briefing.`

<details open>
<summary>What you should see</summary>

A briefing with the four failures sorted into severity sections and a final "Debug mode entry point" paragraph. The severity split is the model's judgment; a typical result is one Critical, two Warning, one Informational, with the schema drift on top.

No change summary: Read-only means there is nothing to keep or undo. If one appears, Read-only is off in the agent file.

From pressing Enter to knowing what to fix first should be under five minutes. If it took longer because the recommended actions were long or vague, send this and read the re-run:

```
Each recommended action must be a single sentence starting with a verb. Maximum 20 words.
If you cannot describe the action in 20 words, the action is not specific enough.
```
</details>

---

### Task 1.3: Add the briefing decision to the audit log

1. Open the `audit/agent_decisions.jsonl` tab and read the record already in it. One JSON object,
   one line, no line breaks inside it. That is the whole format: JSONL is "one JSON object per
   line", which is what makes a log you can append to forever and still parse a line at a time.

2. Put the cursor at the very end of the last line and press **Enter** to open a new line.

3. Copy the block below onto it, and fill in the bracketed values from your session. The copy
   button takes the trailing blank line with it, so the file will end with a newline — which the
   gate agent in Task 3 needs, or its first record is glued onto the end of yours.

   ```json
   {"agent": "morning_briefing", "timestamp": "[ISO 8601]", "inputs_reviewed": ["logs/failure_001.log", "logs/failure_002.log", "logs/failure_003.log", "logs/failure_004.log"], "decision": "Briefing generated: [X] Critical, [Y] Warning, [Z] Informational", "confidence": "High", "human_review_triggered": false, "model_used": "[model name from the model picker, e.g. Cursor Grok 4.6 High Fast]"}


   ```

4. Check the result: your record is on one line, and there is an empty line under it. If your
   editor wrapped the long line across the screen that is fine — wrapping is display, not content.
   What matters is that you never pressed Enter in the middle of the record. Auto Save handles the
   rest.

---

## Task 2: Debug mode investigation

**Read this before you start, because it decides what "success" looks like.**

You are about to hand an agent a failure report and ask it to investigate. The most likely result
is that it reproduces the run, finds nothing wrong, and tells you there is nothing to fix. **That is
the expected answer and the task is not broken.** Do not go hunting for a bug.

Here is why. Those logs came from an overnight Airflow run against the live vendor API. This
repository answers FIGI lookups from a local fixture file whenever no API key is set, so the vendor
call the log blames cannot fail here, and the pipeline runs clean every time.

Which makes this the real subject of the task: **what you do when an agent investigates and finds
nothing.** The right move is to accept it and record it. The tempting move — and the one some
agents will offer you — is to change the code anyway, so that something was done. Watch for that,
and refuse it.

---

### Task 2.1: Switch the same conversation to Debug mode

1. Stay in the briefing conversation. Open the mode picker (∞) at the bottom of the chat input and choose **Debug**. Switching modes in place keeps everything above it: the briefing is still in this conversation, and Debug mode can read it.

2. Send these three lines, with the placeholders filled in from the briefing above:

   ```
   Investigate the failure described in the Debug mode entry point above.

   To reproduce: run the failed pipeline stage against data/sample_input.csv
   Expected: [what a successful run produces]
   Actual: [what the failure log shows]
   ```

   You do not paste the briefing paragraph back in. It is already in this conversation, a few
   messages up, and Debug mode can read it — which is exactly why Task 1.2 had you leave
   **Background** off. A background subagent would have delivered that briefing into a tab of
   its own, and you would be copying it across right now.

---

### Task 2.2: Follow the Debug mode workflow

Debug mode reads the report and tries to reproduce the failure (it may ask you how, or run the stage itself), proposes a fix and applies it on disk, re-runs, and offers **Mark as Fixed**. This failure came from an overnight Airflow run, and the log names things that may not exist in this repository.

1. Read everything it says before you click anything.

2. Answer what it asks. Debug mode is the most interactive mode in Cursor, and this run will
   probably stop for you at least once:

   - It may ask **how to reproduce** the failure. Answer in one line, or say what you do not know.
   - When it proposes a series of steps, or wants to switch modes to carry them out, a
     **Proceed** button appears. Click it. Cursor asks first because *Auto-Approve Mode
     Transitions* is off by default; if you ignore it, it goes ahead on its own after fifteen
     seconds.
   - It may say something like "the debug log file is missing, so I'll confirm the instrumentation
     is still in place". Nothing is wrong. Debug mode instruments the code, runs it, writes what it
     learns to `.cursor/debug-<id>.log`, and reads that file back; early in the run the file does
     not exist yet. Open it afterwards if you are curious — it is a numbered list of the hypotheses
     it tested and what each one showed, which is the most honest view of an agent's reasoning you
     will get all day. It is in `.gitignore`, so it will not follow you into a commit.

3. Identify which of four outcomes you got, and act on it:

   - **It reproduces the run cleanly, finds nothing wrong, and reports that no changes are needed.**
     This is common and it is the *right* answer — the box below says why. Nothing to keep, nothing
     to undo. Go to Task 2.3 and write that down as your root cause.
   - It reproduces the failure and fixes the line that raised it. Read the explanation, click **Mark as Fixed**, then **Keep**.
   - It says the failure cannot be reproduced here and asks what to do. Send: `The DAG is not in this repo. Using the log as evidence, name the function in src/ that would raise this error and propose the smallest fix.` Then read the proposal and decide as in the next line.
   - It proves the failure cannot be reproduced and **proposes a fix anyway**. Do not Keep a change to code that is not failing. Click **Undo** in the change summary, then **Confirm**.

<details open>
<summary>What you should see</summary>

**"No changes needed" is a pass, not a failure of the lab.** These logs came from an overnight
Airflow run against the live vendor API. This repository answers FIGI lookups from
`data/figi_fixture.json` whenever no API key is set, so the vendor call the log blames cannot fail
here — a clean run is the honest result, and an agent that reports one and stops has just done the
hardest thing an agent does, which is decline to act. If you want to see it prove that, open
`.cursor/debug-<id>.log`: the entries record `using_fixture: true` and the run completing without
an exception.

The other common outcome is the fourth: Debug mode runs `validate.py`, reports that the failure does
not reproduce, and still writes a null-handling change (often with tests) into `src/`. The change
summary lists two or three files. Undo it.

If you cannot explain why a proposed fix works, or the agent cannot show you the line that raises the error, do not accept it. A fix for a failure it could not reproduce is a guess. Sending `Explain the root cause and the fix in plain language` first is always allowed.
</details>

---

### Task 2.3: Write the root cause summary

1. Write two sentences somewhere you can copy them from in a moment — a scratch file, the chat
   input, anywhere. You are going to paste them into the audit log in Task 2.4, so write them as
   **one line**, with a space between the sentences rather than a line break:

   ```
   Root cause: [what went wrong and why, or "not reproducible in this repo" and what the log shows]. Fix applied: [what was changed and how it prevents recurrence, or "none" and why you rejected the proposal].
   ```

   If the agent found nothing wrong, that is your root cause and it is a perfectly good record:
   "not reproducible in this repo; the FIGI client runs from the local fixture, so the vendor call
   the log blames cannot fail here. Fix applied: none." An audit log that only records the times
   something was changed is not an audit log.

---

### Task 2.4: Add the Debug investigation to the audit log

1. Open `audit/agent_decisions.jsonl` and look at what is in it: the record that shipped, and the
   briefing record you added in Task 1.3. Same shape every time, one object per line.

2. Put the cursor at the end of the last line, press **Enter**, and copy the block below onto the
   new line. The copy button takes the trailing blank line with it, so the file still ends with a
   newline.

3. Fill in the bracketed values, putting your Task 2.3 sentences into the `decision` field. Keep
   the whole record on one line: a line break anywhere inside it — including between your two
   sentences — splits it into two lines, neither of which parses, and the gate agent in Task 3 is
   what reads this file next.

   ```json
   {"agent": "debug_mode_investigation", "timestamp": "[ISO 8601]", "inputs_reviewed": ["logs/[top failure log]", "src/[affected file]"], "decision": "[your Task 2.3 sentences, on one line]", "confidence": "High", "human_review_triggered": [true if you rejected a proposed fix, otherwise false], "model_used": "[model name]"}


   ```

<details open>
<summary>Or let the agent do it</summary>

You have an agent sitting right there with the whole investigation in its context. In the same
conversation, send:

```
Open audit/agent_decisions.jsonl and look at the format of the existing records.
Append one new record for this investigation, in exactly that format, on its own line.
Use my summary for the decision field: [paste your two sentences].
```

That is worth doing once, because it is what Task 3 does at scale — the gate agent appends its own
records without being walked through the format each time. Read what it wrote before you move on.
An audit log you did not check is a log you are trusting rather than keeping.
</details>

---

## Task 3: CI/CD gate agent

### Task 3.1: Read the metrics file

1. Open `metrics/quality_metrics.json` in the Explorer. Note the three named run objects, `clean_run`, `soft_breach` and `critical_failure`, and for each metric its value, threshold, and whether it is marked `critical_on_breach` or `warn_on_breach`.

---

### Task 3.2: Build the gate agent

1. Click **+** for a new conversation (Agent mode).

2. Send this prompt:

   ```
   You are a CI/CD quality gate agent.

   Read metrics/quality_metrics.json. Evaluate each metric against its defined threshold.
   A metric breaches its threshold when it is above a maximum or below a minimum.

   Decision rules (apply in this exact order):
   - If any metric marked critical_on_breach breaches its threshold: decision = FAIL
   - If any metric marked warn_on_breach breaches its threshold: decision = ESCALATE
   - If all metrics are within threshold: decision = PASS

   Output exactly this structure:
   {
     "decision": "PASS" | "FAIL" | "ESCALATE",
     "metrics_evaluated": [list of metric names checked],
     "violations": [{metric, value, threshold, severity}],
     "rationale": "one sentence plain-language explanation",
     "timestamp": "ISO 8601 timestamp"
   }

   After the JSON, output a plain-language two-sentence version for the on-call engineer.

   After producing each decision, append one record to audit/agent_decisions.jsonl with these fields:
   agent, timestamp, inputs_reviewed, decision, confidence, human_review_triggered (true if ESCALATE), model_used.
   Append only. Do not rewrite or reformat the existing file.
   If the file does not end with a newline, add one before appending.
   ```

3. Read the response.

   Notice what this agent is not. You built the briefing agent as a read-only subagent; this one stays an instruction in a conversation, and it would be wrong to make it read-only, because appending to the audit log is half its job. The toggle is a scoping decision you make per agent from what the agent has to do, not a safety setting you turn on everywhere. Watching it choose and run the append command is also the point of Task 3.4, and that is easier to see here than inside a subagent's own trace.

<details open>
<summary>What you should see</summary>

The agent may evaluate all three runs straight away, wait for you to name one, or ask whether it should write to the audit file. Either is fine; answer `Yes, append` if it asks. It usually appends the audit records with a short terminal command rather than the file editor, so you may not see a Keep button; the `audit/agent_decisions.jsonl` tab updates instead. If a terminal command needs approval, a **Run** button appears under it; click it.
</details>

---

### Task 3.3: Test all three scenarios

**Read this before you type anything.** Given the prompt in Task 3.2, the agent almost always
evaluates all three runs on its own, in one answer — that is the expected result and you should
check its three decisions against the list below and go straight to step 2.

The prompts in step 1 are a **fallback**, for the case where it evaluated only one run or skipped
one. Sending them when the agent has already answered wastes several minutes and tells you nothing
you did not have.

1. **Only if a run is missing from its answer**, send the matching prompt below in the same
   conversation, and check the decision:

   ```
   Evaluate the clean_run metrics.
   ```

   Decision **PASS**.

   ```
   Evaluate the soft_breach metrics.
   ```

   Decision **ESCALATE**.

   ```
   Evaluate the critical_failure metrics.
   ```

   Decision **FAIL**.

2. **Before you continue, note:**

   > Did all three decisions match? If one did not, which rule did the agent apply differently from the way you read it?

---

### Task 3.4: Test decision consistency

1. Run the `critical_failure` evaluation a second time without changing anything:

   ```
   Evaluate the critical_failure metrics.
   ```

2. Compare the two `critical_failure` outputs. The decision and the violations list must be identical (timestamps will differ).

<details open>
<summary>If the decision differs between runs</summary>

The gate agent is exercising judgment rather than applying deterministic rules. Send this, then run the `critical_failure` evaluation twice more; both must produce FAIL with identical violations:

```
The decision logic is deterministic. Apply the rules in the exact order listed above.
Do not exercise judgment about whether to upgrade or downgrade a decision based on any additional context.
```
</details>

3. Check the audit file:

   ```bash
   wc -l audit/agent_decisions.jsonl
   python -c "import json; [json.loads(l) for l in open('audit/agent_decisions.jsonl') if l.strip()]; print('valid JSONL')"
   ```

<details open>
<summary>What you should see</summary>

A line count of at least 7: the sample record, your two hand-written records, and one gate record per evaluation (three scenarios plus the re-run), plus any extra re-runs. Then `valid JSONL`.

If the second command fails with a JSON error, two records share a line: a hand-written record was missing its trailing newline. Put the line break in by hand in the editor and run the check again. Your hand-written records must be untouched otherwise.
</details>

---

## Task 4: Schema drift detection

### Task 4.1: Read the registered schema

1. Open `schemas/expected_schema.json` in the Explorer. Note the field names, data types, and which fields are required.

2. Open `data/sample_input.csv` and compare its header row with the schema. Three schema fields are not in the input: `figi`, `lookup_count`, `exchange_rank`. They are optional output fields.

---

### Task 4.2: Extend the gate agent

1. In the gate agent conversation, send:

   ```
   Also check for schema drift.
   Compare the incoming data schema (read from the first row of data/sample_input.csv)
   against the registered schema in schemas/expected_schema.json.

   Classify each difference:
   - Breaking (required column removed, type incompatibly changed, required field made nullable):
     add schema_drift_breaking to violations, severity=Critical.
     If any breaking drift: decision = FAIL regardless of other metrics.
   - Non-breaking (new column, widened type, optional field added or absent from the input):
     add schema_drift_non_breaking to violations, severity=Warning.
   - Informational (metadata only): note in rationale only.

   Run the full gate check including schema drift against the critical_failure metrics.
   ```

2. Read the output.

<details open>
<summary>What you should see</summary>

Both kinds of finding in one result: the `critical_failure` metric violations and the schema drift findings. The three absent optional columns are reported as non-breaking, and the decision stays FAIL on the metrics. One more gate record lands in the audit file.
</details>

---

## Task 5: Audit log completion

### Task 5.1: Confirm the audit log is complete

1. Open `audit/agent_decisions.jsonl` and confirm it contains records for:

   - [ ] The morning briefing agent (added by hand in Task 1)
   - [ ] The Debug mode investigation (added by hand in Task 2)
   - [ ] Each CI/CD gate evaluation (appended by the gate agent in Tasks 3 and 4)

<details open>
<summary>What you should see</summary>

Each line is a complete JSON object, like this:

```jsonl
{"agent": "morning_briefing", "timestamp": "2026-08-28T07:00:00Z", "inputs_reviewed": ["logs/failure_001.log", "logs/failure_002.log", "logs/failure_003.log", "logs/failure_004.log"], "decision": "Briefing generated: 1 Critical, 2 Warning, 1 Informational", "confidence": "High", "human_review_triggered": false, "model_used": "Cursor Grok 4.6 High Fast"}
{"agent": "debug_mode_investigation", "timestamp": "2026-08-28T07:15:00Z", "inputs_reviewed": ["logs/failure_001.log", "src/validate.py"], "decision": "Root cause: null rate on exchange_code exceeded threshold due to upstream schema change at 02:14 UTC. Fix applied: none; the failure does not reproduce in this repo and the proposed change was rejected.", "confidence": "High", "human_review_triggered": true, "model_used": "Cursor Grok 4.6 High Fast"}
{"agent": "cicd_gate", "timestamp": "2026-08-28T07:30:00Z", "inputs_reviewed": ["metrics/quality_metrics.json"], "decision": "FAIL", "confidence": "High", "human_review_triggered": false, "model_used": "Cursor Grok 4.6 High Fast"}
```
</details>

---

### Task 5.2: Commit the audit log

1. Commit:

   ```bash
   git add audit/agent_decisions.jsonl
   git commit -m "Add agent audit log for Lab 4 session"
   ```

   This commit is the final mandatory step. Do not skip it under time pressure: an agent system without a committed audit trail is not production-ready.

---

### Task 5.3: Turn this morning into an agent

Look back at what you have just done. You investigated a failure, evaluated three CI/CD runs
against a metrics file, extended the rules for schema drift, and recorded every decision in an
audit log in a fixed format. Tomorrow's overnight run will need all of it again.

Everything in this lab argues that a job you will repeat belongs in a file rather than in a
conversation. The gate work is still in a conversation. Fix that.

1. Stay in the gate agent conversation, the one that has the whole Task 3 and Task 4 history in it.
   Confirm the mode picker reads **Agent**.

2. Type `/`, choose **create-subagent**, and after the tag send:

   ```
   Create a subagent named cicd-gate from what we did in this conversation.
   It should read metrics/quality_metrics.json, evaluate every run in the file against the
   thresholds, and return PASS, ESCALATE or FAIL per run with the violations that drove each
   decision.
   It should apply the schema drift rules we added, comparing the columns present against
   schemas/expected_schema.json.
   It should append one record per evaluation to audit/agent_decisions.jsonl in the format
   already used in that file, one JSON object per line.
   Keep the decision rules exactly as we settled them in this conversation.
   ```

3. Click **Keep**. Open `.cursor/agents/cicd-gate.md` and read what it wrote.

4. Check one thing before you trust it: are the thresholds and the decision rules in the file, or
   does the file assume whoever runs it already knows them? An agent built from a conversation
   inherits the conversation's assumptions, and the conversation is about to end.

5. Commit it:

   ```bash
   git add .cursor/agents/cicd-gate.md
   git commit -m "Add CI/CD gate subagent"
   ```

<details open>
<summary>What you should see</summary>

A file with the thresholds, the three decisions, the drift rules and the audit format written out —
or one that leans on context that no longer exists, which is the more interesting result and the
reason for step 4. Either way you now have the thing this whole lab has been arguing for: the
morning's work as a file, versioned with the pipeline it watches, runnable by whoever is on call
tomorrow.

This agent cannot be Read-only, because appending to the audit log is a write. That is worth
noticing after three agents where Read-only was the right answer: the toggle follows the job, not
the habit.
</details>

---

## Task 6: Cloud Agents Window (optional)

Do this Task only if Tasks 1 through 5 are finished. Tasks 6.1 and 6.2 work on any clone. Task 6.3 needs a repository you administer, linked in the Cursor dashboard at `cursor.com/dashboard` with the Cursor GitHub app installed; on the shared course repository, expect it to stop at the message quoted in its box, which is itself the lesson.

Do not attempt Cloud Agent tasks on code whose tests need on-premises services (an Oracle database, say). Cloud Agent VMs cannot reach them. The Lab 4 starter files run without external connectivity.

**Setting this up for the first time is an administration job, and this course does not cover it.**
Most people will read Task 6.3 rather than run it, which is fine — the message it stops on is the
lesson. If you want to set it up properly afterwards, on a repository you administer, these are the
pages to start from:

- [Cloud Agents overview](https://cursor.com/docs/cloud-agent) — what a cloud agent is and what it runs on
- [Cloud environment setup](https://cursor.com/docs/cloud-agent/setup) — the machine, the snapshot and the install commands
- [GitHub integration](https://cursor.com/docs/integrations/github) — linking the repository and installing the Cursor GitHub app, which is the step that needs an organisation administrator

Read those before you ask your platform team for anything; the request lands much better when you
already know which app is being installed and what it can see.

### Task 6.1: Launch a parallel gate check

1. Click **Agents Window ↗** at the top right of the editor. (Multitask also works from the chat panel in the editor; the Agents Window is where you can watch several agents at once.)

2. Click **New Chat**, type `/multitask` (or choose **Multitask** from the mode picker) and send:

   ```
   Run the CI/CD gate check from metrics/quality_metrics.json for the soft_breach run only.
   Report the decision and violations. Do not write to any file.
   ```

3. Watch for **1 subagent running** under the message. Click it: the subagent opens as its own tab with its own prompt, model and result.

4. Return to the editor with **IDE ↗**.

<details open>
<summary>What you should see</summary>

The task runs independently of your other conversations and reports ESCALATE with two warnings. Nothing is written: `git status --short` shows no new change.
</details>

---

### Task 6.2: Run the briefing subagent in the background

Multitask splits one request across subagents Cursor invents for the job. Background does something different: it runs an agent *you* defined without blocking you. The briefing agent is the natural candidate, because a morning briefing is exactly the thing you want running while you do something else.

1. Open `.cursor/agents/incident-briefing.md` and turn **Background** on. Leave Read-only on.

2. Click **+** for a new conversation, type `/`, choose **incident-briefing** and press Enter.

3. Watch what happens differently: the conversation comes back to you straight away instead of waiting for the briefing. Send another message in the same conversation while the agent is still working, for example `What is in schemas/expected_schema.json?`

4. Go back and read the briefing when it lands.

<details open>
<summary>What you should see</summary>

The call returns immediately and the subagent reports separately when it is done, so you keep working in the meantime. That is the whole difference, and it is why the flag was off for Tasks 1 and 2: if this had been on, the briefing would not have been sitting in the conversation you switched to Debug mode.

Turn Background back off when you are finished, so the agent you committed behaves the way the rest of the lab describes.
</details>

---

### Task 6.3: Hand off the briefing agent to /in-cloud

1. In the Agents Window, click **New Chat**.

2. Type `/`, choose **in-cloud** from the Commands list, then type the morning briefing task description from Task 1.2 after it and send. A Cloud Agent clones the repository, runs on its own VM, and reports back.

3. Watch the result in the Agents Window.

<details open>
<summary>What you will most likely see</summary>

On a repository that is not linked, the cloud task shows **Couldn't start** and the agent reports one of these:

```
The Cursor app needs to be installed on your repository.
To enable them, link this repo in the Cursor dashboard, install the Cursor GitHub app on <repo>, then run /in-cloud again.
```

```
Cloud agents need a linked git remote, and this workspace has none, so I can't start one here.
```

The first appears when the remote exists but is not linked; the second when there is no remote at all. Installing the Cursor GitHub app needs admin rights on the repository. If you cloned the course repository, you do not have them: read the message, note what it asks for, and go to the debrief. If you forked the repository to your own account, link the fork at `cursor.com/dashboard`, install the app, and retry.
</details>

---

## Lab Debrief

Write answers before the room debrief begins. You will share one with the group.

---

**Question 1**

In Task 2, did Debug mode reproduce the failure? If not, what did it do instead, and would you have kept its change? What does that tell you about accepting a fix for a failure the agent could not run?

---

**Question 2**

In Task 3, did the gate agent produce the same decision on consecutive runs for `critical_failure`? If not, what instruction change made it deterministic?

---

**Question 3**

The audit log was the last mandatory step. In a real deployment, when should the audit log be designed, before or after the agent is built? Why?

---

**Question 4**

Write one rule you will add to your team's `.cursor/rules/` file this week based on something this lab revealed that your current rules do not cover.

---

**Question 5**

Write one agent use case from your real DE work that you will scope and build in the next 30 days. Write the Layer 3 test answer: why can you not write a deterministic script for this?
