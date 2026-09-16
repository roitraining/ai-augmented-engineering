# Lab 3: Build a DE Pipeline Code Review Agent
**Course:** AI-Augmented Engineering for Data Engineers
**Tool:** GitHub Copilot in VS Code
**Duration:** 75 minutes
**Day:** Day 2, following Module 4

---

## Prerequisites

- [ ] Modules 3 and 4 lectures completed
- [ ] Chapter 3 scoping exercise completed (or the scope specification template in Task 1.1 reviewed)
- [ ] Lab 2 completed or not; Task 0 loads the Lab 3 starting point either way
- [ ] The repository's `lab-workspace` folder open in VS Code with Copilot signed in, and the venv active in the terminal
- [ ] Git working in the repository; the `pr/001`, `pr/002`, `pr/003` branches present (`git branch -a` lists them under `origin/`)

---

## Lab Overview

Your team reviews dozens of Python pipeline PRs each week. Manual review is inconsistent and depends on who is available. In this lab you build a **custom agent**: a real, reusable agent that lives in a file in the repository, reviews pipeline code against DE-specific criteria, flags issues with severity ratings, and produces a structured review summary ready for human sign-off. Then you compare it with Copilot's built-in Review Changes on the same PR.

Everything you have configured so far has shaped how the agent behaves. A custom agent is the first thing you build that *is* an agent: it has its own name, its own instructions, its own tools, and it appears in the mode picker beside Agent, Ask and Plan.

**What you will produce:**
- `.github/agents/de-pipeline-reviewer.agent.md`: a scoped, read-only review agent you select from the mode picker
- Three improvements you made yourself, each one answering something you learned from a run
- A written comparison of your custom agent versus Review Changes on the same PR

**Copilot notes for this lab:** modes are on the **Agent ▾** pill at the bottom left of the chat input, and your custom agent joins that list once the file exists. A new chat (**+** at the top of the panel) keeps the previous chat's mode, so check the pill every time. Terminal commands the agent wants to run appear as an **Allow ▾** / **Skip** card; your agent runs `git diff` itself, so expect one on every review.

**How this lab is written:** each Task has numbered steps. A numbered step is something you do. Text between steps explains what you are looking at; the boxes marked "What you should see" tell you what a correct result looks like. The agent's behaviour varies from run to run: it may ask questions before acting, act at once, or describe a change and wait for your go-ahead. If it asks, answer; if it waits, reply `Go ahead`. The steps describe the end state, not every turn of the conversation.

---

## Task 0: Load the starter files and check out the first PR

Do this whether or not you completed Lab 2. It resets the workspace to a known state, then moves you onto the first of three pull-request branches that ship with the repository.

1. Open a terminal inside VS Code: menu **Terminal → New Terminal**. It opens in `lab-workspace/`; every command in this lab runs from there.

2. Make sure the prompt starts with `(venv)`. If it does not, run `source venv/bin/activate` (Windows: `venv\Scripts\activate`).

3. Put away any unfinished Lab 2 work. Run `git status --short`; if it prints anything, commit on the branch you are on:

   ```bash
   git add -A
   git commit -m "Lab 2 checkpoint"
   ```

4. Go back to `main`, which is still exactly what you cloned:

   ```bash
   git checkout main
   ```

5. Load the Lab 3 starter files:

   ```bash
   python lab.py start 3
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
  lab3       17/17 files identical, 0 extra lab file(s) present  <- matches
  lab4       ...
  solution   ...
git: uncommitted changes present
```

Only the **lab3** line matters: `17/17 files identical` and `<- matches`. `git: uncommitted changes present` is normal here; step 7 clears it.
</details>

7. Create the branch this lab's own commits go on, then commit the starting state:

   ```bash
   git checkout -B lab3
   git branch --show-current
   git add -A
   git commit -m "Lab 3 start state"
   ```

   The second command must print `lab3` before you read on. **`-B`, not `-b`.** If you are starting this lab over and the branch already exists, `-b` fails — and because the next command runs anyway, the start-state commit lands on `main` instead of on your branch. `-B` resets the branch to where you are now, so the step works the first time and every time after.

8. Switch to the first review branch:

   ```bash
   git checkout pr/001
   git branch --show-current
   ```

   The three `pr/` branches are shared with everyone in the room. You review them; you do not commit to them. Task 3.4 puts your own work back on `lab3` at the end.

9. Look at what the PR changes:

   ```bash
   git diff --stat main
   ```

<details open>
<summary>What you should see</summary>

```
 src/ingest.py    | 6 ++++++
 src/transform.py | 7 ++++++-
 src/validate.py  | 3 +++
 3 files changed, 15 insertions(+), 1 deletion(-)
```

Three files under `src/`, about fifteen added lines. Those are the changes you will review.

**If the list is much longer** — whole files like `transform.py`, `validate.py` and the tests showing as added — then the start-state commit from step 7 went onto `main` instead of onto `lab3`, and `main` is no longer what you cloned. Check with `git log --oneline -3 main`. If you see your own start-state commit on top, undo it with:

```bash
git branch -f lab3 main
git checkout main
git reset --hard HEAD~1
git checkout pr/001
```

That moves the commit onto `lab3` where it belongs, puts `main` back, and returns you here. Then re-run the `git diff --stat main` above; it should show three files.

`src/ingest.py` on this branch is the complete idiomatic conversion of `perl/ingest.pl` plus the PR's additions; it is the baseline all three sample PRs are built on.
</details>

10. Confirm the tests pass:

    ```bash
    pytest tests/ -q
    ```

    Expect `42 passed`. The planted issues are review issues, not test failures.

11. Check which model you are using. Open the chat panel (menu **View → Chat**) and click the model pill. Confirm a **named** model is selected rather than **Auto**, and leave it alone for the rest of the lab.

    This matters more than it looks. In Task 2 you change one thing at a time and re-run to see what the change did. If Auto routes consecutive chats to different models, you are measuring Copilot's routing rather than your edit.

---

## Task 1: Scope the agent and build it

### Task 1.1: Review your scope specification

1. Open your Chapter 3 scope specification document, or use the template below if you did not complete the exercise.

2. Confirm it covers all five components. Add any that are missing, using these definitions:

| Component | Definition |
|---|---|
| **Tools** | The branch diff against `main` for context. Read-only: the agent must not edit any files. |
| **Instructions** | Review against `.github/copilot-instructions.md` plus five DE criteria: schema drift handling, null safety, idempotency, logging completeness, type hint coverage. |
| **Success criteria** | Every finding has a severity (Critical, Warning, Informational), a file and line number, and a recommendation specific enough to act on in one step. |
| **Failure handling** | If the PR diff is too large to review in one pass, the agent reports what it reviewed and flags the remainder as Needs human review. |
| **Escalation path** | Any credential, secret, or key literal in source is escalated regardless of confidence and reported separately. Any finding where agent confidence is Low is also escalated. |

<details open>
<summary>Scope specification template (use if you did not complete the Chapter 3 exercise)</summary>

```
Tools: the branch diff against main for context. Read-only file access.
The agent must not edit any files.

Instructions: Review changed code against .github/copilot-instructions.md
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

Escalation path: Any credential, secret, token, or API key literal in
source code is marked ESCALATE regardless of confidence and reported in
a separate ESCALATED section. Any finding where confidence is Low is
also marked ESCALATE rather than included in the summary.

Two failure modes:
1. Non-deterministic output -- same PR produces different findings on
   consecutive runs. Mitigation: explicit output format template.
2. Scope creep -- agent comments on code outside the diff. Mitigation:
   explicit instruction to review only changed lines.
```
</details>

3. **Before you continue, note:**

   > Which of the five components can be enforced by the tool itself, and which can only be asked for in words? You check your answer in Task 1.3.

---

### Task 1.2: Create the custom agent

A custom agent is a Markdown file under `.github/agents/`, named `<name>.agent.md`. It has a name, a description, its own instructions and its own tool list, and it appears in the agent picker for anyone who opens this folder. You do not have to write the file by hand: `/create-agent` writes it from a description, the same way `/create-skill` wrote your skill in Lab 1.

Copilot has a second, related thing called a **subagent**, written in the same `.agent.md` format but marked `user-invocable: false`: the main agent starts it on its own, in an isolated context, when a job suits it. You are building the user-invocable kind, because this one you want to run deliberately and compare across three PRs.

1. Click **+** (New Chat) and set the mode pill to **Agent**.

2. Type `/` and choose **create-agent** ("Create a custom agent for a specific job") from the list. It becomes a highlighted tag. A pasted `/create-agent` is just text and does nothing; type the slash.

3. After the tag, paste the following and press Enter:

   ```
   Could you create a custom agent for me that acts as a DE pipeline code review agent.
   Context: the branch diff with main.
   The agent should review (no code changes) the changes against our defined standards.
   Additionally, check for:
   1. Schema drift handling: does the change validate incoming schema?
   2. Null safety: are None values handled on all critical fields?
   3. Idempotency: can this step run twice without duplicate records?
   4. Logging completeness: are pipeline entry, exit, and errors logged?
   5. Type hint coverage: do all functions have complete type hints?
   For each finding output: criterion violated; file and line number;
   severity: Critical / Warning / Informational; confidence: High / Medium / Low;
   specific recommendation.
   If confidence is Low, mark the finding ESCALATE.
   End with: overall recommendation APPROVE / REQUEST CHANGES / ESCALATE.
   Name it de-pipeline-reviewer.
   ```

4. Wait for it to finish, then click **Keep** in the change summary above the chat input.

<details open>
<summary>What you should see</summary>

One new file, `.github/agents/de-pipeline-reviewer.agent.md`, listed in the change summary. The `.github/agents/` folder ships with the starter files and was empty until now.

If the agent says it is "recovering" or "rebuilding" an earlier agent, it found one in the repository's history. Let it finish; the next Task checks the file it produced.
</details>

---

### Task 1.3: Read the file and finish the scoping

The generated file is a first draft of your scope specification, written by an agent that read your project. Now you make it match the specification from Task 1.1.

1. Read the **Description** field. It is not documentation: Cursor reads it to decide when to hand work to this agent on its own, without you naming it. A description that says "use proactively after any change to `src/`" is asking for exactly that.

2. Read the body below the frontmatter. Find the step where the agent collects the diff (`git diff main...HEAD`) and the step where it reads `.github/copilot-instructions.md` and `.github/instructions/perl-conversion.instructions.md`.

   Those reads are in the instructions on purpose. A custom agent runs with its own instructions, so do not assume it inherits everything that applies to your ordinary chats. Telling it which files to read is what makes it reliable.

3. Check the tools it gave itself. Just above the `tools:` line in the frontmatter there is a **Configure Tools…** link; click it. A picker opens listing the built-in capability groups: **agent**, **browser**, **edit**, **execute**, **read**, **search**, **todo**, **vscode** and **web**.

   Confirm **edit** is unticked and **read**, **search** and **execute** are ticked, then click **OK**. Your prompt said "no code changes", so `/create-agent` has usually left `edit` off already; the point of this step is that you looked and decided, rather than trusting it.

<details open>
<summary>What you should see</summary>

```yaml
tools: [read, search, execute]
user-invocable: true
```

These are capability groups, not individual functions: `read` is every file-reading tool, `execute` is every way of running something on your machine. The count in the corner of the picker ("23 Selected") is the individual tools inside the groups you ticked.

This is the Tools line of your scope specification, and it is the answer to the note in Task 1.1. Every other component is words the agent can ignore; the tool list is enforced — with `edit` unticked there is no editing tool for the agent to reach for, whatever its instructions say.

Look at what `execute` means, though. It is how the agent runs `git diff`, and it is equally how something could run `git reset`. The generated instructions narrow it, usually with a line like "ONLY use `execute` to run read-only git commands." That is the honest shape of scoping an agent: the tool list is the fence, the instructions are the rules inside the fence, and only the fence is enforced.

`user-invocable: true` is what puts the agent in the picker. The same file marked `false` becomes a subagent the main agent starts on its own.
</details>

4. Give the agent its own model. `/create-agent` usually leaves `model:` out of the frontmatter, which means the agent runs on whatever the chat happens to be set to. Add a `model:` line naming the model you confirmed in Task 0 step 11, so this agent behaves the same way whoever calls it. (The exact value depends on what your organisation has enabled; the model pill shows the names your build accepts.)

5. Check the body against the five components from Task 1.1. You are checking for **coverage, not phrasing**: `/create-agent` writes its own wording, so yours will not match the example below or your neighbour's, and the UI labels may read slightly differently between VS Code versions. Add anything genuinely missing, in the agent's own voice. Confirm it covers:

   - [ ] Review only changed lines; do not comment on code outside the diff
   - [ ] The five DE criteria
   - [ ] The output fields: criterion, file and line, severity, confidence, recommendation
   - [ ] Failure handling for a diff too large to review in one pass
   - [ ] The escalation path, including Low confidence

6. Confirm the file is saved (no dot on the tab).

<details open>
<summary>What the file should look like</summary>

```markdown
---
description: "Reviews the current branch diff against main for DE pipeline code changes.
  Use when the user asks to review, audit, or check a pipeline PR/branch/diff for schema
  drift, null safety, idempotency, logging completeness, or type hint coverage before
  merging. Read-only, does not modify code."
tools: [read, search, execute]
user-invocable: true
---

You are a Data Engineering pipeline code reviewer for this market-data batch pipeline
(ingest -> transform -> validate). You produce review findings only.
You never modify files, never commit, and never apply fixes.

## When invoked

1. Determine the review scope: the git diff of the current branch versus main.
2. Collect `git diff main...HEAD` and `git diff` (unstaged and staged working tree).
3. Read the changed Python files at the versions on disk so line numbers match.
4. Read DE standards in `.github/copilot-instructions.md`, Perl-to-Python rules in
   `.github/instructions/perl-conversion.instructions.md`,
   and the registered schema under `schemas/`.
5. Begin the review immediately. Do not implement, patch, or rewrite code.

... (criteria, output format and escalation path follow)
```

Your wording will differ from this example and from your neighbour's, because the wording is generated. The frontmatter fields and the five criteria are what should match.
</details>

7. **Do not commit the agent file yet.** It is untracked, which is what you want: untracked files stay put when you switch branches, so the same agent follows you onto `pr/002` and `pr/003` without ever landing on a shared branch. Task 3.4 commits it to your `lab3` branch at the end.

---

### Task 1.4: Run it on PR 001

1. Click **+** (New Chat), then **check the mode before you type anything**: the mode pill under
   the chat input must read **Agent**. A new chat can inherit the mode from the last one, and Ask
   mode cannot write files — `/create-agent` would describe the agent and create nothing. Confirm you are still on `pr/001` (`git branch --show-current`).

2. Click the mode pill and choose **de-pipeline-reviewer** from the list, then send:

   ```
   Review the changes on this branch.
   ```

   Your agent is now in the mode picker beside Agent, Ask and Plan, because it lives in this folder.

   The message you send can carry extra focus — "concentrate on the transform module", say — and the agent will take it alongside its own instructions. This one does not need any: everything it should do is in the file, so one plain sentence is the whole invocation. That is the test of a well-scoped agent.

3. Click **Allow** on the command card when it runs `git diff`.

4. Read every finding before going on. Expect somewhere between eight and fifteen. Some are issues your instructor planted; some are real issues nobody planted. Both are legitimate.

5. Expand the **Completed N steps** line above the findings. It shows the agent fetching the diff itself and reading the instruction files it was told to read.

<details open>
<summary>What you should see</summary>

Findings grouped by severity, each citing a file and a line, each with a confidence level and a one-sentence recommendation, and a closing `Overall recommendation: APPROVE / REQUEST CHANGES / ESCALATE`.

No change summary above the input: with no edit tool in its list there is nothing to keep or undo. If a change summary appears anyway, the `tools:` line is missing or misspelled; fix it in the agent file and run again.

If the agent reports that it has no diff to review, you are on `main` rather than `pr/001`. Check with `git branch --show-current`.
</details>

---

## Task 2: Iterate on the agent

You are not going to score this agent out of twenty. Scoring needs an answer key you do
not have at review time, and it turns a tuning exercise into a quiz. What you are going to
do instead is what you would actually do at your desk: run the agent against code whose
defects are known, find the gap, and close it by editing the file.

Three branches, three rounds. Each round you do three things — check the run against the
known list, improve the agent, and let the *next* branch's run tell you whether the
improvement worked. That last part matters for a practical reason as much as a pedagogical
one: a review run takes several minutes, so the lab is built to get two jobs out of each
one rather than re-running to admire the result.

One rule for the whole task: **every fix is a change to
`.github/agents/de-pipeline-reviewer.agent.md`.** Not a follow-up message in the chat. A message
improves one answer. The file improves every answer, in every conversation, for everyone
who clones the repository.

<details open>
<summary>Two things that will save you time</summary>

**You do not need to save a backup of the agent file.** It is a text file in an editor with
undo, in a repository with git. If an edit makes things worse, undo it.

**Do not grade the output by hand.** Task 2.1 shows you a much faster way: paste the known
defects into a plain Ask conversation along with the agent's findings, and let it do the
comparison. That takes seconds and does not cost you another review run.
</details>

---

### Task 2.1: PR 001 — check the run, then improve the output

1. Scroll back to your Task 1.4 output. If you have lost it, click **+** (New Chat), choose
   **de-pipeline-reviewer** from the mode pill and send `Review the changes on this branch.`

2. Click **+** (New Chat) and choose **Ask** from the mode pill. You want a plain chat here,
   not your reviewer: you are asking a question about a review, not running one.

3. Copy the block below into the Ask conversation, then paste your agent's findings
   underneath it and send:

   ```
   I ran a code review agent on this branch. Below are the defects I know were planted.
   Tell me which ones it caught, which it missed, and whether any of its other findings
   are real problems rather than noise. Be strict about misses.

   PR 001 known defects

   src/ingest.py - load_supplementary_records() at line 177
   1. No return type declared (copilot-instructions.md)
   2. No entry or exit logging (copilot-instructions.md)
   3. Reads a CSV with no schema check against schemas/ (the shipped rubric, Critical)
   4. Line 181 appends rows with no null check on record_id, instrument_id,
      exchange_code, price, volume or figi (copilot-instructions.md, Critical)
   5. Line 181 is not idempotent: a second call appends the same rows again
      (the shipped rubric, Critical)
   6. Mutates the caller's existing_records list in place AND returns it, so the
      caller ends up with two names for one list
   7. Line 180 is a for-append loop where extend() or a comprehension is the house
      idiom (the shipped rubric, Informational)
   8. The function is defined but never called anywhere in the codebase

   src/transform.py - compute_weighted_price() at line 133
   9.  No type hints on prices, volumes or the return value (copilot-instructions.md)
   10. No entry or exit logging (copilot-instructions.md)
   11. Line 134: sum(volumes) and p * v both crash on a None element, with no guard
       (copilot-instructions.md)
   12. The function is defined but never called anywhere in the codebase

   src/validate.py - inside validate_records()
   13. exchange_list is built and never used (the shipped rubric, Informational)
   14. It is a for-append loop where a comprehension is the house idiom
       (the shipped rubric, Informational)
   15. r.get("exchange_code") or "UNKNOWN" silently substitutes a placeholder instead
       of recording a violation, inside the function whose job is to record violations
   ```

4. Read the comparison. Note your hit count out of 15, and note any finding the Ask
   conversation says is a real problem that is not on the list. Those are not false
   positives; they are defects nobody planted, and a reviewer that surfaces them is doing
   its job.

5. Now improve the agent. Which change you make depends on what you just learned:

   **If it missed defects**, add one rule for the most serious miss. Write it in the agent's
   own voice, in the Criteria section, and name the thing to look for rather than the quality
   to have — "check for side effects" does not work, this does:

   ```
   Flag any function that modifies one of its arguments in place.
   A function that both mutates an argument and returns it is a finding: name the argument
   and say which of the two behaviours the caller is likely to miss.
   Flag any function introduced by the change that is never called anywhere in the codebase.
   ```

   **If it caught all fifteen** — which happens, this is a strong model on a small diff —
   then coverage is not your problem and there is no honest rule to add. Improve the
   *output* instead, which is the half that decides whether anyone acts on the review. Add
   this to the Output format section:

   ```
   Begin the review with a summary block before any findings:
   the count of findings at each severity, the single most serious finding in one line,
   and the overall recommendation.
   Then list the findings.
   ```

   A reviewer reading twenty findings wants the verdict first. Right now your agent buries
   it at the bottom.

6. Save the file. Do **not** re-run it on pr/001. The next branch's run will tell you whether
   the change worked, and it will tell you something a re-run cannot: whether the change
   generalises past the diff you wrote it for.

7. **Before you continue, note:**

   > Your hit count out of 15, and the one change you made.

---

### Task 2.2: PR 002 — a different class of defect

pr/001 was mostly about what the agent does not know to look for. pr/002 is about something
harder: a change that looks like a tidy-up and is actually a regression.

1. Switch branches:

   ```bash
   git checkout pr/002
   git status --short
   ```

   `git status` shows your agent file as untracked (`?? .github/agents/`). It came with you:
   untracked files stay put when you switch branches, which is why the same agent follows
   you across all three PRs without ever landing on a shared branch.

2. Click **+** (New Chat), choose **de-pipeline-reviewer** from the mode pill, and send
   `Review the changes on this branch.` Click **Allow** on the command card when it runs
   `git diff`.

   While it works, expand the trace above the findings and watch what it does. It fetches the
   diff itself, then reads `.github/copilot-instructions.md` and the schema files — everything
   you told it to read, in order, before it says anything. That trace is the difference
   between an agent and an autocomplete, and it is worth thirty seconds of your attention.

3. First, check the change you made in Task 2.1. If you added a rule, did it fire here on
   pr/002's own instances of the same pattern? If you changed the output format, is the
   summary block there? That is your answer on whether the change generalised.

4. Click **+** (New Chat), choose **Ask** from the mode pill, and compare the same way as in
   Task 2.1:

   ```
   I ran a code review agent on this branch. Below are the defects I know were planted.
   Tell me which ones it caught, which it missed, and whether any of its other findings
   are real problems rather than noise. Be strict about misses.

   PR 002 known defects

   src/transform.py
   1. except (ValueError, TypeError) was narrowed to except ValueError. A None volume
      now raises TypeError and crashes the stage instead of being skipped with a warning
      (the shipped rubric, Critical: do not narrow or remove exception types)
   2. append_to_daily_summary() opens the file in append mode with no de-duplication
      check, so running the stage twice doubles the rows (the shipped rubric, Critical)
   3. It never calls writeheader(), and takes its fieldnames from a single record's keys,
      so the column order can differ between calls
   4. It opens and closes the output file on every single record
   5. No entry or exit logging (copilot-instructions.md)
   6. No docstring
   7. The function is defined but never called anywhere in the codebase
   8. logger.info("Transform pipeline complete") was deleted
      (the shipped rubric, Warning: removing an existing log statement)

   src/validate.py
   9.  import os sits inside the function body rather than at the top of the file
   10. input_path.exists() was replaced with os.path.exists(input_file)
       (copilot-instructions.md: use pathlib.Path; never use os.path)
   11. The check now reads input_file while the error message on the next line still
       interpolates input_path, so the two disagree about what was looked at
   ```

5. The narrowed `except` is the one to watch. It is a two-character deletion that reads like
   a cleanup, it passes every test that does not feed a null volume through the stage, and it
   is the defect most review tools miss — including Copilot's own Review Changes, as you will see in Task 3.

6. Improve the agent again, by the same rule as before:

   **If it missed defects**, add a rule for the most serious miss. For the narrowed `except`:

   ```
   Treat any change to an existing except clause as a finding in its own right.
   If the change removes an exception type from the tuple, name the input that will now
   crash instead of being handled, and mark the finding Critical.
   ```

   **If it caught all eleven**, improve the output again. This one is worth adding even if
   you do not need it:

   ```
   Every finding must name the rule it comes from: the file and the clause of
   .github/copilot-instructions.md that the code violates.
   If a finding comes from no rule at all, say so and mark it as your own judgement.
   After the findings, add one line naming the criteria you checked and found clean.
   ```

   Two things happen when you add that. A finding you can trace to a rule is a finding you
   can argue with, or overrule, or take to the person who wrote the rule. And "what I checked
   and found clean" is the thing no reviewer volunteers and every reader wants: it is the
   difference between "I found nothing" and "I did not look".

7. Save the file. Again, do not re-run here.

8. **Before you continue, note:**

   > Whether your Task 2.1 change survived contact with a different branch.

---

### Task 2.3: PR 003 — no answer key until you have run it

Two rounds of tuning. Now find out whether what you built generalises to code you have not
seen. This round you get no list before the run.

1. Switch branches:

   ```bash
   git checkout pr/003
   ```

2. Click **+** (New Chat), choose **de-pipeline-reviewer** from the mode pill, and send
   `Review the changes on this branch.` Click **Allow** on the command card. Do not read ahead.

3. Write down how many findings you got and which files they are in, before you look at
   anything below.

4. Click **+** (New Chat), choose **Ask** from the mode pill, and compare:

   ```
   I ran a code review agent on this branch. Below are the defects I know were planted.
   Tell me which ones it caught, which it missed, and whether any of its other findings
   are real problems rather than noise. Be strict about misses.

   PR 003 known defects

   src/figi_client.py
   1. Line 57: or "demo-fallback-key-2026" is an API key literal in source
      (the shipped rubric, Security: blocking, including "demo" and "fallback" values)
   2. Because that fallback always resolves, the FigiClientError("No API key provided...")
      branch at line 82 is now unreachable. The guard is still in the file and no longer
      guards anything
   3. A blank line was removed before self._url

   src/ingest.py
   4. Line 90: except FigiClientError was broadened to a bare except Exception
      (the shipped rubric, Critical: do not catch exceptions silently)
   5. The logger.error(f"FigiClient request failed: {exc}") line inside it was deleted,
      so the failure is now both broader and silent (the shipped rubric, Warning)
   6. Line 179: archive_run() reads records[0].keys(), which raises IndexError on an
      empty list
   7. archive_run() appends with no writeheader() and no de-duplication check
      (the shipped rubric, Critical: idempotency)
   8. archive_run() has no docstring and no logging (copilot-instructions.md)
   9. archive_run() is defined but never called anywhere in the codebase

   src/validate.py
   10. Line 168: summarise_violations() returns by_field as an empty dict on every call.
       It is a stub shipped as though it were finished, and it will report zero for every
       field forever
   11. summarise_violations() has no type hints on its argument or its return value
       (copilot-instructions.md)
   12. summarise_violations() is defined but never called anywhere in the codebase
   13. logger.info(f"Starting validate pipeline for {input_file}") was deleted
       (the shipped rubric, Warning)
   ```

5. Coverage is not the interesting question on this branch. The interesting question is what
   your agent did with the credential on line 57. Check all three:

   - [ ] The credential is reported in a separate **ESCALATED** section, before the other findings
   - [ ] It is marked **ESCALATE**, not Critical
   - [ ] The overall recommendation is **ESCALATE**, not REQUEST CHANGES or APPROVE

6. Most agents fail at least one of those, and the reason is worth more than the defect.

   Your agent almost certainly *found* the key — it is hard to miss — and filed it as a
   Critical bug with High confidence. Look at the escalation rule in your file. If it says
   something like "escalate when confidence is Low", it will never fire on a hard-coded
   credential, because the agent is completely confident that a hard-coded credential is a
   bug. It is right about that, and it is still making the wrong call: this is not a thing to
   fix in a review comment, it is a thing to stop the PR for and tell a human about, because
   the key may already be in the history and in everyone's clone.

   Replace your escalation rule with this:

   ```
   Any credential, secret, token or API key literal in source code is a security finding:
   mark it ESCALATE regardless of confidence, report it in a separate ESCALATED section
   before the other findings, and set the overall recommendation to ESCALATE.
   Low confidence on any finding is also grounds for ESCALATE, but it is not the only
   grounds.
   ```

7. Save the file and run the agent once more on pr/003 from the mode pill, so you can see the same code
   classified differently. This is the one re-run in the lab that earns its minutes: nothing
   about the diff changed, and the verdict did.

8. **Before you continue, note:**

   > Escalate-when-unsure is not the same as escalate-when-dangerous. Which one did your
   > agent have before this step, and which categories other than credentials deserve the
   > same treatment on your own team's code?

<details open>
<summary>Why this one is a rule and not a miss</summary>

The changes you made in Tasks 2.1 and 2.2 changed what the agent *looks for* or how it
*presents* what it found. This one changes how it *classifies* something it already found —
a policy, not a detection. Those are the rules most worth writing down, because they are the
ones where a reasonable reviewer, human or not, will make a defensible call that your team
has decided against. Risk class, not confidence, is what should drive escalation:
credentials, customer data, money arithmetic, anything with a regulator attached.

Keep this agent open. Task 3 compares it against Copilot's built-in Review Changes on this
same branch, so there is nothing more to run.
</details>

---

## Task 3: The shipped rubric and Review Changes

### Task 3.1: Understand what you are comparing

Three distinct things review code in this project. Keep them separate:

| System | What it is | What it reads |
|---|---|---|
| **Your custom agent** | The file you just built; runs when you select it in the mode picker | Whatever its instructions tell it to read |
| **Review Changes** | Local in-editor review from the Source Control panel, no PR needed | `.github/copilot-instructions.md` and the file's diff |
| **Copilot code review on GitHub.com** | PR automation: Copilot as a reviewer on pull requests | `.github/copilot-instructions.md` in the repository |

One file, three readers: the instructions you wrote in Lab 1 are what the local review and the GitHub review both use, so anything you want enforced on PRs belongs there. The Cursor track ships a separate rubric file, `.cursor/BUGBOT.md`, for its own review tooling; in Task 3.2 you read it as an example rubric. Your custom agent is the third reader, and it is the only one you control completely.

---

### Task 3.2: Read the shipped review rubric

1. In the Explorer, open `.cursor/BUGBOT.md`. Copilot does not read this file; it is the Cursor track's review rubric, and it is a good example of one. Where a Copilot team would put these rules is a `## Code Review Rules` section of `.github/copilot-instructions.md`.

2. Read the Security, Critical, Warning and Informational sections and compare them with your agent's five criteria.

<details open>
<summary>What the file contains</summary>

```markdown
# DE Pipeline Review Rules

Review only the changed lines. Cite file and line for every finding. Recommendations are one sentence, starting with a verb.

## Security (blocking, always report first)
- Any credential, secret, token, or API key literal in source code, including "demo" or "fallback" values, is a blocking finding regardless of confidence
- Any change that widens network, file, or process access is a blocking finding

## Critical
- Any function reading from an external source (CSV, API response) must validate field names and types against the registered schema in schemas/ before processing records
- Null values on record_id, instrument_id, exchange_code, price, volume, and figi must be handled explicitly; no bare .get() without a default on these fields
- Do not narrow or remove exception types in existing except clauses; do not catch exceptions silently. A swallowed or narrowed handler that lets a None value crash the pipeline is Critical
- Pipeline steps that write records must be idempotent: running twice must not produce duplicate output. Opening a file in append mode without a deduplication check is Critical

## Warning
- All functions must have type hints on all arguments and the return value
- Pipeline entry and exit must be logged with the project logger in the format: Starting {function_name} with {len(records)} records / Completed {function_name} with {len(records)} records
- Removing an existing log statement is a Warning
- All file operations must use pathlib.Path; os.path and raw string paths passed to open() are Warnings

## Informational
- Use collections.Counter for counting and frequency analysis
- Use list comprehensions where they improve readability over for-append loops
- Unused variables or imports introduced by the change
```
</details>

3. **Before you continue, note:**

   > One thing the file has that your agent does not (the exception-narrowing rule and the append-mode rule are candidates), and one thing it lacks.

   Do not add it to `copilot-instructions.md` in this lab; the `pr/` branches are shared, and Task 3.3 needs the shipped instructions so everyone compares the same thing.

---

### Task 3.3: Run Review Changes on PR 003

Review Changes works on files the Source Control panel shows as changed, and only on those files. This is the whole trick: the PR's changes are already committed on `pr/003`, so the panel shows nothing but your untracked agent file, and a review run now would review that Markdown file instead of the pipeline. Put the branch's changes into the working tree on a scratch branch first.

1. Switch back to the first PR and stage its changes:

   ```bash
   git checkout pr/003
   git checkout -B review-003
   git reset --soft main
   git status --short
   ```

   Status lists the three `src/` files as staged (`M`). The code is unchanged; only the bookkeeping moved, so that Review Changes can see it.

2. Open the **Source Control** panel (the branch icon in the left bar). The three files appear under Staged Changes.

3. Right-click `src/figi_client.py` and choose **Review Changes**. Copilot reviews that file's diff and posts its comments inline in the editor. Repeat for `src/ingest.py` and `src/validate.py`.

4. Read the comments. Each has an action next to it; do not apply anything, you are comparing, not fixing. If a file comes back with no comments at all, run **Review Changes** on it again; an empty first pass happens.

5. Put the branch back the way you found it:

   ```bash
   git reset --hard pr/003
   git checkout pr/003
   git branch -D review-003
   git status --short
   ```

   Status shows only your untracked agent file, and you are on `pr/003`.

<details open>
<summary>What you should see</summary>

A handful of inline comments per file, some naming a `copilot-instructions.md` standard as the reason. Expect it to find some but not all of the thirteen planted pr/003 defects — the hard-coded key in `figi_client.py` is the one to watch for — plus a real issue nobody planted. That is not a failure; it is the data point for Task 3.4.
</details>

---

### Task 3.4: Compare, then keep your agent

1. Fill in this table from the Review Changes comments and your agent's final pr/003 output:

| | Your custom agent | Review Changes |
|---|---|---|
| Planted pr/003 defects found, out of 13 | | |
| False positives | | |
| Most actionable finding | | |
| Time to produce output | | |
| Runs on someone else's machine after a clone | | |

2. **Before you continue, note:**

   > When would you use Review Changes instead of your custom agent in your daily work, and when the custom agent instead?

<details open>
<summary>Typical answer pattern</summary>

Review Changes is a right-click and needs no setup; use it for a quick sanity check on a file before committing. Your custom agent produces more structured output with severity ratings, confidence levels and DE-specific criteria, and it is a file in the repository: a teammate who clones the repo has your reviewer, at your standard, without being told. Use it before raising a PR, or in an asynchronous review where the output must be actionable by someone who was not present. On GitHub, Copilot code review on the PR reads the same `copilot-instructions.md`, so the standards travel with the repository.

Neither replaces the other. The professional workflow is: Review Changes before committing, your agent before raising the PR.
</details>

3. Leave the `pr/` branches as you found them. If you changed a tracked file on one, put it back:

   ```bash
   git checkout -- .
   ```

4. Commit your agent on your own branch, where it belongs:

   ```bash
   git checkout lab3
   git add .github/agents/
   git commit -m "Add DE pipeline reviewer agent"
   git --no-pager log --oneline -2
   ```

   That is the deliverable of this lab: not a review, but a reviewer, versioned with the code it reviews.

---

## Lab Debrief

Write answers before the room debrief begins. You will share one with the group.

---

**Question 1**

Which of the three improvements you made was worth the most, and how did you know? Name one line you added that you would put in your own team's repository on Monday.

---

**Question 2**

Did the rule you added on pr/001 still fire on pr/002 and pr/003? A rule that only ever catches the defect you wrote it for is over-fitted to one diff. Which of yours generalised, and which did not?

---

**Question 3**

In Task 1.3 you restricted the agent's `tools:` list rather than writing "do not modify any files" in the instructions. Name one thing that protects you from that the instruction does not. Why is "escalate when unsure" not the same as "escalate when dangerous"?

---

**Question 4**

Write one new rule for a `## Code Review Rules` section of `.github/copilot-instructions.md`, based on an issue your agent found in pr/003 that the shipped rubric does not cover. Would you rather put that rule in the instructions file or in your agent file, and why?

---

**Question 5**

Your agent runs when you call it. Nothing stops you wiring it to a trigger instead — both
editors support hooks, so an agent can be told to run whenever a file under `src/` changes,
with no one asking it to.

What would have to be true before you let your reviewer run itself on your own team's code?
Consider at least: how long a review takes and what the developer is doing while it runs;
what the agent should do with what it finds, given nobody is watching the output; and which
findings should stop the work rather than be filed for later.
