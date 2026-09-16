# Lab 4: Pipeline Monitoring and CI/CD Gate Agent
**Course:** AI-Augmented Engineering for Data Engineers
**Tool:** GitHub Copilot in VS Code
**Duration:** 75 minutes
**Day:** Day 2, following Modules 5 and 6

---

## Prerequisites

- [ ] Modules 5 and 6 lectures completed
- [ ] Lab 3 completed, or not; Task 0 loads the Lab 4 starting point either way
- [ ] The repository's `lab-workspace` folder open in VS Code with Copilot signed in, and the venv active in the terminal
- [ ] pytest accessible from the terminal
- [ ] Optional, for Task 6.2 only: a fork of the repo under your own GitHub account with the Copilot coding agent enabled

---

## Lab Overview

Your pipeline runs overnight. Your on-call engineer arrives each morning to a directory of Airflow failure logs with no clear starting point. Build an observability agent that generates a prioritized incident briefing, investigate the top failure evidence-first, implement a CI/CD gate agent with deterministic PASS/FAIL/ESCALATE output, add schema drift detection, and keep an audit log that records every agent decision.

**Copilot notes for this lab:** everything runs in Agent mode (the **Agent ▾** pill at the bottom left of the chat input). Copilot has no Debug mode; Task 2 uses the evidence-first prompt from Lab 2. Terminal commands the agent wants to run appear as an **Allow ▾** / **Skip** card; the gate agent appends to the audit file that way, so expect several cards in Task 3. Cursor's Agents Window and `/in-cloud` become the chat panel's full-screen **Sessions** view and the **Local ▾** run-target pill in Task 6.

This is the capstone lab. It applies content from Chapters 3 through 6 in one integrated build.

**What you will produce:**
- `.github/agents/incident-briefing.agent.md`: a read-only briefing agent with severity-sorted output
- An evidence-first investigation of the top failure with a two-sentence root cause summary
- A CI/CD gate agent with deterministic PASS/FAIL/ESCALATE decisions
- Schema drift detection integrated into the gate decision
- `audit/agent_decisions.jsonl` with a record for every agent decision in this lab

**How this lab is written:** each Task has numbered steps. A numbered step is something you do. Text between steps explains what you are looking at; the boxes marked "What you should see" tell you what a correct result looks like. The agent's behaviour varies from run to run: it may ask questions before acting, act at once, or describe a change and wait for your go-ahead. If it asks, answer; if it waits, reply `Go ahead`. The steps describe the end state, not every turn of the conversation.

---

## Task 0: Load the starter files

Do this whether or not you completed Lab 3. It resets the workspace to the Lab 4 starting point, including the `audit/` folder this lab writes to.

1. Open a terminal inside VS Code: menu **Terminal → New Terminal**. It opens in `lab-workspace/`; every command in this lab runs from there.

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

9. In the Explorer, open `audit/agent_decisions.jsonl` and leave the tab open. It holds one sample record showing the format; you add records to it by hand in Tasks 1 and 2. (An open file rides along as context in Copilot chats; that is fine here.)

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

### Task 1.2: Build the briefing agent

In Lab 3 you built a reviewer as a custom agent instead of a prompt, so it survived the chat that made it. Do the same here: the morning briefing is the most repeated job on this list, and it is read-only, which makes it the easiest agent you will ever scope.

1. Open the chat panel (**View → Chat**), click **+** (New Chat) at the top of it, and set the mode pill to **Agent**.

2. Type `/`, choose **create-agent**, and after the tag paste the following:

   ```
   Create a custom agent named incident-briefing.
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

   ### Investigation entry point
   [one paragraph bug description for the highest-severity failure,
   ready to paste into a debugging prompt]
   ```

3. Click **Keep** in the change summary. The new file is `.github/agents/incident-briefing.agent.md`.

4. Open it and check its tools the same way you did in Lab 3: click **Configure Tools…** above the `tools:` line and leave only **read** and **search** ticked.

   ```yaml
   tools: [read, search]
   ```

   A briefing reads logs and writes nothing, so take the editing tools away rather than asking it not to use them. This one needs no **execute** either, which makes it a shorter list than the reviewer's in Lab 3. Scope each agent to its job, not to a house default.

5. Click **+** (New Chat), note the time, set the mode pill to **incident-briefing** and send `Generate this morning's briefing.`

6. Read the full briefing. Expand the **Completed N steps** line above it and check the **Read** pills for all four logs; if it read only some, send `Read all four files in logs/ and redo the briefing.` (If it asked to run `cat` or `ls`, click **Allow**.)

<details open>
<summary>What you should see</summary>

A briefing with the four failures sorted into severity sections and a final "Investigation entry point" paragraph. The severity split is the model's judgment; a typical result is one Critical, two Warning, one Informational, with the schema drift on top.

No change summary: with no edit tool in its list there is nothing to keep or undo. If one appears, the `tools:` line is missing or misspelled.

From pressing Enter to knowing what to fix first should be under five minutes. If it took longer because the recommended actions were long or vague, send this and read the re-run:

```
Each recommended action must be a single sentence starting with a verb. Maximum 20 words.
If you cannot describe the action in 20 words, the action is not specific enough.
```
</details>

---

### Task 1.3: Add the briefing decision to the audit log

1. In the `audit/agent_decisions.jsonl` tab, add this record on a new line at the end of the file, filling in the bracketed values from your session:

   ```json
   {"agent": "morning_briefing", "timestamp": "[ISO 8601]", "inputs_reviewed": ["logs/failure_001.log", "logs/failure_002.log", "logs/failure_003.log", "logs/failure_004.log"], "decision": "Briefing generated: [X] Critical, [Y] Warning, [Z] Informational", "confidence": "High", "human_review_triggered": false, "model_used": "[model name from the model picker, e.g. Cursor Grok 4.6 High Fast]"}
   ```

   The whole record is one line.

2. Press **Enter** after it so the file ends with a newline. The gate agent in Task 3 appends to the end of the file; without that newline its first record is glued onto yours. Auto Save saves the file.

---

## Task 2: Evidence-first investigation

**Read this before you start, because it decides what "success" looks like.**

The failure you are about to investigate is a **transient**. It happened at 02:14 against the
vendor's API, and by the time you sit down it has cleared: the vendor is answering again and the
pipeline runs clean. So the most likely result is that your agent reproduces the run, finds nothing
wrong, and tells you there is nothing to fix. **That is the expected answer and the task is not
broken.** Do not go hunting for a bug.

If you want the mechanism: this repository answers FIGI lookups from a local fixture file whenever
no API key is set, which is what makes the overnight failure impossible to recreate here. But the
situation it is standing in for is one you will meet for real — a timeout, a rate limit, a
dependency that was down for nine minutes — and the shape of the morning is the same either way.

That shape is the actual subject of this task. **A failure you cannot reproduce is the normal case,
not the broken one**, and it leaves you with two jobs, neither of which is fixing code:

- **Record it.** A transient that nobody writes down never happened, so when it happens again in
  three weeks nobody knows it is the second time. This is why Task 2.4 exists, and it is the most
  realistic thing in the lab.
- **Refuse the fix.** Some agents, told to investigate a failure, will change something rather than
  come back empty-handed. Changing working code to close a ticket is how a transient becomes a real
  outage. Watch for it and undo it.

---

### Task 2.1: Send the entry point with a reproduce-first instruction

1. Stay in the briefing chat, Agent mode.

2. Send these lines, with the placeholders filled in from the briefing above. You do not paste
   the briefing paragraph back in — it is already in this chat, a few messages up, and the agent
   can read it:

   ```
   Investigate the failure described in the Investigation entry point above.

   To reproduce: run the failed pipeline stage against data/sample_input.csv
   Expected: [what a successful run produces]
   Actual: [what the failure log shows]

   Reproduce it first. Then tell me the root cause. Do not change any file yet.
   ```

3. Click **Allow** on the command cards as it runs the stage.

---

### Task 2.2: Decide what to do with the result

This failure came from an overnight Airflow run, and the log names things that may not exist in this repository. The agent will try to run the stage; what it reports next is the point of the Task.

1. Read everything it says before you type anything.

2. Answer what it asks, and keep clicking **Allow** on the command cards as it runs things. The
   agent may also narrate its way around something missing — "the debug log file is missing, so
   I'll confirm the instrumentation is still in place" is a real example. Nothing is broken and
   nothing is missing from the repository; the pipeline logs to the console, not to a file, so an
   agent that went looking for a log file was reasoning about its own run. Let it work.

3. Identify which of four outcomes you got, and act on it:

   - **It reproduces the run cleanly, finds nothing wrong, and reports that no changes are needed.**
     This is the most likely outcome and it is the right answer. Nothing to keep, nothing to undo.
     Go to Task 2.3 and write that down as your root cause.
   - It reproduces the failure and names the line that raises it. Send `Apply the smallest fix for that root cause.`, read the inline diff, then **Keep**.
   - It says the failure cannot be reproduced here and asks what to do. Send: `The DAG is not in this repo. Using the log as evidence, name the function in src/ that would raise this error and propose the smallest fix. Do not apply it.` Then read the proposal and decide as in the next line.
   - It reports that the failure cannot be reproduced and **changes the code anyway**. Do not Keep a change to code that is not failing. Click **Undo** in the change summary.

<details open>
<summary>What you should see</summary>

**"No changes needed" is a pass, not a failure of the lab.** The failure cleared before you got
here, so a clean run is the honest result, and an agent that reports one and stops has just done the
hardest thing an agent does: decline to act.

The fourth outcome is the other common one: it runs `validate.py`, reports that the failure does not reproduce, and still writes a null-handling change (often with tests) into `src/`. The change summary lists two or three files. The "do not change any file yet" line in the prompt reduces this; it does not eliminate it. Undo it.

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

   If the agent found nothing wrong, that is your root cause and it makes a perfectly good record:
   "Root cause: transient vendor API failure at 02:14; the dependency has since recovered and the
   stage runs clean, so the failure does not reproduce. Fix applied: none — no code change was
   warranted." An audit log that only records the times something was changed is not an audit log,
   and a transient nobody wrote down is a transient nobody can spot the second time.

---

### Task 2.4: Add the investigation to the audit log

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
   {"agent": "debug_investigation", "timestamp": "[ISO 8601]", "inputs_reviewed": ["logs/[top failure log]", "src/[affected file]"], "decision": "[your Task 2.3 sentences, on one line]", "confidence": "High", "human_review_triggered": [true if you rejected a proposed fix, otherwise false], "model_used": "[model name]"}


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

1. Click **+** (New Chat), Agent mode.

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

   Notice what this agent is not. You built the briefing agent as a read-only custom agent; this one stays an instruction in a chat, and it would be wrong to strip its tools, because appending to the audit log is half its job. The tool list is a scoping decision you make per agent from what the agent has to do, not a safety setting you turn on everywhere. Watching it choose and run the append command is also the point of Task 3.4, and that is easier to see here than inside a custom agent's own trace.

<details open>
<summary>What you should see</summary>

The agent may evaluate all three runs straight away, wait for you to name one, or ask whether it should write to the audit file. Either is fine; answer `Yes, append` if it asks. It usually appends the audit records with a short terminal command rather than the file editor, so you may not see a change summary; the `audit/agent_decisions.jsonl` tab updates instead. Each command comes as an **Allow ▾** / **Skip** card; click **Allow** (the ▾ can allow the same command for the rest of the session).
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
   - [ ] The investigation (added by hand in Task 2)
   - [ ] Each CI/CD gate evaluation (appended by the gate agent in Tasks 3 and 4)

<details open>
<summary>What you should see</summary>

Each line is a complete JSON object, like this:

```jsonl
{"agent": "morning_briefing", "timestamp": "2026-08-28T07:00:00Z", "inputs_reviewed": ["logs/failure_001.log", "logs/failure_002.log", "logs/failure_003.log", "logs/failure_004.log"], "decision": "Briefing generated: 1 Critical, 2 Warning, 1 Informational", "confidence": "High", "human_review_triggered": false, "model_used": "Cursor Grok 4.6 High Fast"}
{"agent": "debug_investigation", "timestamp": "2026-08-28T07:15:00Z", "inputs_reviewed": ["logs/failure_001.log", "src/validate.py"], "decision": "Root cause: null rate on exchange_code exceeded threshold due to upstream schema change at 02:14 UTC. Fix applied: none; the failure does not reproduce in this repo and the proposed change was rejected.", "confidence": "High", "human_review_triggered": true, "model_used": "Cursor Grok 4.6 High Fast"}
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

Everything in this lab argues that a job you will repeat belongs in a file rather than in a chat.
The gate work is still in a chat. Fix that.

1. Stay in the gate agent chat, the one with the whole Task 3 and Task 4 history in it. Confirm the
   mode pill reads **Agent**.

2. Type `/`, choose **create-agent**, and after the tag send:

   ```
   Create a custom agent named cicd-gate from what we did in this chat.
   It should read metrics/quality_metrics.json, evaluate every run in the file against the
   thresholds, and return PASS, ESCALATE or FAIL per run with the violations that drove each
   decision.
   It should apply the schema drift rules we added, comparing the columns present against
   schemas/expected_schema.json.
   It should append one record per evaluation to audit/agent_decisions.jsonl in the format
   already used in that file, one JSON object per line.
   Keep the decision rules exactly as we settled them in this chat.
   ```

3. Click **Keep**. Open `.github/agents/cicd-gate.agent.md` and read what it wrote.

4. Check its `tools:` line. This agent appends to the audit log, so it needs **edit** — unlike the
   two read-only agents you built earlier. Click **Configure Tools…** and confirm **read**,
   **search**, **execute** and **edit** are ticked. The tool list follows the job, not the habit.

5. Check one more thing before you trust it: are the thresholds and the decision rules in the file,
   or does the file assume whoever runs it already knows them? An agent built from a chat inherits
   the chat's assumptions, and the chat is about to end.

6. Commit it:

   ```bash
   git add .github/agents/cicd-gate.agent.md
   git commit -m "Add CI/CD gate custom agent"
   ```

<details open>
<summary>What you should see</summary>

A file with the thresholds, the three decisions, the drift rules and the audit format written out —
or one that leans on context that no longer exists, which is the more interesting result and the
reason for step 5. Either way you now have the thing this whole lab has been arguing for: the
morning's work as a file, versioned with the pipeline it watches, runnable by whoever is on call
tomorrow.
</details>

---

## Task 6: Sessions view and the cloud agent (optional)

Do this Task only if Tasks 1 through 5 are finished. Task 6.1 works on any clone. Task 6.2 stops at a dialog on the shared course repository, and reading that dialog is the lesson; only run it through on a fork you own.

Do not hand off work to a cloud agent when the code's tests need on-premises services (an Oracle database, say). The cloud agent cannot reach them. The Lab 4 starter files run without external connectivity.

**Setting this up for the first time is an administration job, and this course does not cover it.**
Most people will read Task 6.2 rather than run it, which is fine — the dialog it stops on is the
lesson. If you want to set it up afterwards on a repository you own, these are the pages to start
from:

- [Copilot coding agent](https://docs.github.com/en/copilot/using-github-copilot/coding-agent) — what it is and what it runs on
- [Enabling the coding agent](https://docs.github.com/en/copilot/using-github-copilot/coding-agent/enabling-copilot-coding-agent) — the organisation and repository settings, which is the step that needs an administrator
- [Customising the agent's environment](https://docs.github.com/en/copilot/customizing-copilot/customizing-the-development-environment-for-copilot-coding-agent) — dependencies and setup steps for the VM

Read those before you ask your platform team for anything; the request lands much better when you
already know what is being enabled and what it can see.

### Task 6.1: See the day's agents in one place

1. Click the **maximize** icon in the chat panel header (next to the ✕). The chat fills the window and a **Sessions** column appears on the right: every chat from this lab, auto-titled, with the lines it changed ("+6 −5") and when it ran. This is the twin of Cursor's Agents Window.

2. Click the briefing session, then the gate-agent session. Each opens with its full transcript, including the **Completed N steps** traces and the command cards you allowed.

3. Click **New Session** and send, in Agent mode:

   ```
   Run the CI/CD gate check from metrics/quality_metrics.json for the soft_breach run only.
   Report the decision and violations. Do not write to any file.
   ```

4. Click the maximize icon again to return to the panel.

   Cursor has a per-agent Background flag that runs an agent you defined without blocking you. Copilot's equivalent for "keep working while this runs" is the cloud handoff in Task 6.2, which takes the job off your machine entirely.

<details open>
<summary>What you should see</summary>

The new session runs independently of the others and reports ESCALATE with two warnings. Nothing is written: `git status --short` shows no new change. The Sessions list is also your audit trail for the day: which chat touched which files, in order.
</details>

---

### Task 6.2: Hand off the briefing agent to the cloud

1. Click **+** (New Session or New Chat), Agent mode, and paste the morning briefing prompt from Task 1.2 into the input without sending it.

2. Click the run-target pill (**Local ▾**) at the bottom of the input and read the menu: **Continue In: Local · Cloud · Copilot · Claude**. Hover **Cloud**: "Delegate tasks to the GitHub Copilot coding agent … works asynchronously in the cloud to implement changes and pull requests."

3. Choose **Cloud**. Read the dialog that appears.

<details open>
<summary>What you should see</summary>

A **Delegate to cloud agent** dialog: "Cloud agent works asynchronously to create a pull request with your requested changes. This chat's history will be summarized and appended to the pull request as context." It may add that the workspace has uncommitted changes and ask whether to push them, with **Commit Changes and Delegate** · **Delegate** · **Cancel**.

Click **Cancel**. On the shared course repository you cannot push a branch, so the handoff would fail, and even where it succeeds, every delegation opens a pull request on GitHub; that is the design (Cursor's `/in-cloud` runs on a VM and reports back to the editor instead). If you forked the repository to your own account and the Copilot coding agent is enabled there, you may **Delegate** and watch the PR appear on GitHub.
</details>

---

## Lab Debrief

Write answers before the room debrief begins. You will share one with the group.

---

**Question 1**

In Task 2, did the agent reproduce the failure? If not, what did it do instead, and would you have kept its change? What does that tell you about accepting a fix for a failure the agent could not run?

---

**Question 2**

In Task 3, did the gate agent produce the same decision on consecutive runs for `critical_failure`? If not, what instruction change made it deterministic?

---

**Question 3**

The audit log was the last mandatory step. In a real deployment, when should the audit log be designed, before or after the agent is built? Why?

---

**Question 4**

Write one instruction you will add to your team's `.github/copilot-instructions.md` this week based on something this lab revealed that your current instructions do not cover.

---

**Question 5**

Write one agent use case from your real DE work that you will scope and build in the next 30 days. Write the Layer 3 test answer: why can you not write a deterministic script for this?
