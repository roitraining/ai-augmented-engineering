# Lab 3: Build a DE Pipeline Code Review Agent
**Course:** AI-Augmented Engineering for Data Engineers
**Tool:** Cursor (Pro or Teams plan)
**Duration:** 75 minutes
**Day:** Day 2, following Module 4

---

## Prerequisites

- [ ] Modules 3 and 4 lectures completed
- [ ] Chapter 3 scoping exercise completed (or the scope specification template in Task 1.1 reviewed)
- [ ] Lab 2 completed or not; Task 0 loads the Lab 3 starting point either way
- [ ] The repository's `lab-workspace` folder open in the Cursor IDE, with the venv active in the terminal
- [ ] Git working in the repository; the `pr/001`, `pr/002`, `pr/003` branches present (`git branch -a` lists them under `origin/`)

---

## Lab Overview

Your team reviews dozens of Python pipeline PRs each week. Manual review is inconsistent and depends on who is available. In this lab you build a **subagent**: a real, reusable agent that lives in a file in the repository, reviews pipeline code against DE-specific criteria, flags issues with severity ratings, and produces a structured review summary ready for human sign-off. Then you compare it with Cursor's built-in Agent Review on the same PR.

Everything you have configured so far has shaped how the agent behaves. A subagent is the first thing you build that *is* an agent: it has its own name, its own instructions, its own permissions, and its own model.

**What you will produce:**
- `.cursor/agents/de-pipeline-reviewer.md`: a scoped, read-only review agent you invoke with `/de-pipeline-reviewer`
- Three improvements you made yourself, each one answering something you learned from a run
- A written comparison of your subagent versus Agent Review on the same PR

**How this lab is written:** each Task has numbered steps. A numbered step is something you do. Text between steps explains what you are looking at; the boxes marked "What you should see" tell you what a correct result looks like. The agent's behaviour varies from run to run: it may ask questions before acting, act at once, or describe a change and wait for your go-ahead. If it asks, answer; if it waits, reply `Go ahead`. The steps describe the end state, not every turn of the conversation.

---

## Task 0: Load the starter files and check out the first PR

Do this whether or not you completed Lab 2. It resets the workspace to a known state, then moves you onto the first of three pull-request branches that ship with the repository.

1. Open a terminal inside Cursor: menu **Terminal → New Terminal**. It opens in `lab-workspace/`; every command in this lab runs from there.

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

11. Check which model you are using. At the bottom of the chat input, click the effort and speed picker (it reads something like **High Fast**). The panel that opens has **Fast**, **Effort** and **Model**; click **Model**.

    Confirm a **named** model is selected rather than **Auto**. The default on a Teams seat is usually Cursor's own Grok, which is exactly what you want; if you want the room on the same footing, pick the latest **Cursor Grok**. Whatever it is, leave it alone for the rest of the lab.

    This matters more than it looks. In Task 2 you change one thing at a time and re-run to see what the change did. If Auto routes consecutive conversations to different models, you are measuring Cursor's routing rather than your edit. On some models, subagent calls do not run at all.

---

## Task 1: Scope the agent and build it

### Task 1.1: Review your scope specification

1. Open your Chapter 3 scope specification document, or use the template below if you did not complete the exercise.

2. Confirm it covers all five components. Add any that are missing, using these definitions:

| Component | Definition |
|---|---|
| **Tools** | The branch diff against `main` for context. Read-only: the agent must not edit any files. |
| **Instructions** | Review against `.cursor/rules/de-standards.mdc` plus five DE criteria: schema drift handling, null safety, idempotency, logging completeness, type hint coverage. |
| **Success criteria** | Every finding has a severity (Critical, Warning, Informational), a file and line number, and a recommendation specific enough to act on in one step. |
| **Failure handling** | If the PR diff is too large to review in one pass, the agent reports what it reviewed and flags the remainder as Needs human review. |
| **Escalation path** | Any credential, secret, or key literal in source is escalated regardless of confidence and reported separately. Any finding where agent confidence is Low is also escalated. |

<details open>
<summary>Scope specification template (use if you did not complete the Chapter 3 exercise)</summary>

```
Tools: the branch diff against main for context. Read-only file access.
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

### Task 1.2: Create the subagent

A subagent is a Markdown file under `.cursor/agents/`. It has a name, a description, its own instructions, and its own permissions, and every conversation in this project can call it. You do not have to write the file by hand: `/create-subagent` writes it from a description, the same way `/create-skill` wrote your skill in Lab 1.

1. Click **+** for a new conversation, then **check the mode before you type anything**. Open the
   mode picker (∞) at the bottom of the chat input and confirm it reads **Agent**.

   A new conversation can inherit the mode from the last one in that window, so a window you last
   used in Ask mode opens in Ask mode — and Ask mode cannot write files. `/create-subagent` would
   describe the agent it *would* build and create nothing.

2. Type `/` and choose **create-subagent** from the list. It becomes a highlighted tag. A pasted `/create-subagent` is just text and does nothing; type the slash.

3. After the tag, paste the following and press Enter:

   ```
   Could you create a subagent for me that acts as a DE pipeline code review agent.
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

4. Wait for it to finish, then click **Keep** in the change summary at the bottom of the chat.

<details open>
<summary>What you should see</summary>

One new file, `.cursor/agents/de-pipeline-reviewer.md`, listed in the change summary. The `.cursor/agents/` folder did not exist a moment ago; the command created it.

The file opens in the editor with a form above the text: **Name**, **Model**, **Description**, and two toggles, **Read-only** and **Background**. That form and the text below it are the same thing, the way the rules editor in Lab 1 showed `alwaysApply` as a dropdown: change the form and the frontmatter follows.

If the agent says it is "recovering" or "rebuilding" an earlier agent, it found one in the repository's history. Let it finish; the next Task checks the file it produced.
</details>

---

### Task 1.3: Read the file and finish the scoping

The generated file is a first draft of your scope specification, written by an agent that read your project. Now you make it match the specification from Task 1.1.

1. Read the **Description** field. It is not documentation: Cursor reads it to decide when to hand work to this agent on its own, without you naming it. A description that says "use proactively after any change to `src/`" is asking for exactly that.

2. Read the body below the frontmatter. Find the step where the agent collects the diff (`git diff main...HEAD`) and the step where it reads `.cursor/rules/de-standards.mdc`, `.cursor/rules/perl-to-python.mdc` and `.cursor/BUGBOT.md`.

   Those reads are in the instructions on purpose. A subagent runs in its own context, so do not assume it inherits the rules that apply to your chat. Telling it which files to read is what makes it reliable.

3. Turn **Read-only** on.

   This is the Tools line of your scope specification, and it is the answer to the note in Task 1.1. Every other component is words the agent can ignore. Read-only is enforced: no file edits and no state-changing shell commands. Reading the diff still works, because reading changes nothing.

4. Leave **Background** off. A background subagent returns immediately and works on its own; you want this one to hand its findings back before you do anything else. You turn it on in Lab 4, where it earns its keep.

5. Set the agent's own **Model**. It is created as **Inherit from parent**, which means this agent behaves differently depending on which conversation happens to call it — the opposite of what a file full of fixed instructions is for. Open the dropdown and choose a specific model; the latest **Cursor Grok** is a sensible default and matches what you confirmed in Task 0 step 11.

   Do this yourself, here, rather than asking the chat to do it for you. Cursor writes your choice into the frontmatter as a `model:` line, and from now on the agent runs on that model no matter who calls it.

   Now look at the line it wrote. On some builds the picker writes the model name with empty
   brackets after it:

   ```yaml
   model: grok-4.6[]
   ```

   If yours has them, delete the `[]` so the line names the model and nothing else. Leave it
   as it is if the picker wrote a clean value. This is the first payoff of building the agent
   as a file rather than a dialogue: you can see what the tool wrote, and correct it.

6. Check the body against the five components from Task 1.1. You are checking for **coverage, not phrasing**: `/create-subagent` writes its own wording, so yours will not match the example below or your neighbour's, and that is fine. Add anything genuinely missing, in the agent's own voice. Confirm it covers:

   - [ ] Review only changed lines; do not comment on code outside the diff
   - [ ] The five DE criteria
   - [ ] The output fields: criterion, file and line, severity, confidence, recommendation
   - [ ] Failure handling for a diff too large to review in one pass
   - [ ] The escalation path, including Low confidence

7. Confirm the file is saved (no dot on the tab).

<details open>
<summary>What the file should look like</summary>

```markdown
---
name: de-pipeline-reviewer
description: DE pipeline code review specialist. Use proactively after any change to
  src/, tests/, schemas/, or Perl-to-Python conversion work. Reviews the current branch
  diff against main with no code changes.
readonly: true
---

You are a Data Engineering pipeline code reviewer for this market-data batch pipeline
(ingest -> transform -> validate). You produce review findings only.
You never modify files, never commit, and never apply fixes.

## When invoked

1. Determine the review scope: the git diff of the current branch versus main.
2. Collect `git diff main...HEAD` and `git diff` (unstaged and staged working tree).
3. Read the changed Python files at the versions on disk so line numbers match.
4. Read DE standards in `.cursor/rules/de-standards.mdc`, Perl-to-Python rules in
   `.cursor/rules/perl-to-python.mdc`, review rules in `.cursor/BUGBOT.md`,
   and the registered schema under `schemas/`.
5. Begin the review immediately. Do not implement, patch, or rewrite code.

... (criteria, output format and escalation path follow)
```

Your wording will differ from this example and from your neighbour's, because the wording is generated. The frontmatter fields and the five criteria are what should match.
</details>

8. **Do not commit the agent file yet.** It is untracked, which is what you want: untracked files stay put when you switch branches, so the same agent follows you onto `pr/002` and `pr/003` without ever landing on a shared branch. Task 3.4 commits it to your `lab3` branch at the end.

---

### Task 1.4: Run it on PR 001

1. Click **+** for a new conversation (Agent mode). Confirm you are still on `pr/001` (`git branch --show-current`).

2. Type `/` and choose **de-pipeline-reviewer** from the list, then press Enter.

   Your agent is now in the list beside Cursor's own commands, because it lives in this project.

   You *could* type extra instructions after the tag — "focus on the transform module", say — and the agent would take them alongside its own. This one does not need any: everything it should do is in the file. Pressing Enter with nothing after the name is the whole invocation, and that is the test of a well-scoped agent.

3. Read every finding before going on. Expect somewhere between eight and fifteen. Some are issues your instructor planted; some are real issues nobody planted. Both are legitimate.

4. Expand the trace above the findings. It shows the agent fetching the diff itself and reading the rules files it was told to read.

<details open>
<summary>What you should see</summary>

Findings grouped by severity, each citing a file and a line, each with a confidence level and a one-sentence recommendation, and a closing `Overall recommendation: APPROVE / REQUEST CHANGES / ESCALATE`.

No change summary at the bottom of the chat: Read-only means there is nothing to keep or undo. If a change summary appears anyway, Read-only is off; turn it on in the agent file and run again.

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
`.cursor/agents/de-pipeline-reviewer.md`.** Not a follow-up message in the chat. A message
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

1. Scroll back to your Task 1.4 output. If you have lost it, click **+** for a fresh
   conversation, type `/`, choose **de-pipeline-reviewer** and press Enter.

2. Click **+** for a new conversation and switch it to **Ask** mode using the mode picker at
   the bottom left of the chat input. You want a plain conversation here, not your reviewer:
   you are asking a question about a review, not running one.

3. Copy the block below into the Ask conversation, then paste your agent's findings
   underneath it and send:

   ```
   I ran a code review agent on this branch. Below are the defects I know were planted.
   Tell me which ones it caught, which it missed, and whether any of its other findings
   are real problems rather than noise. Be strict about misses.

   PR 001 known defects

   src/ingest.py - load_supplementary_records() at line 177
   1. No return type declared (de-standards.mdc)
   2. No entry or exit logging (de-standards.mdc)
   3. Reads a CSV with no schema check against schemas/ (BUGBOT.md, Critical)
   4. Line 181 appends rows with no null check on record_id, instrument_id,
      exchange_code, price, volume or figi (de-standards.mdc, BUGBOT.md Critical)
   5. Line 181 is not idempotent: a second call appends the same rows again
      (BUGBOT.md, Critical)
   6. Mutates the caller's existing_records list in place AND returns it, so the
      caller ends up with two names for one list
   7. Line 180 is a for-append loop where extend() or a comprehension is the house
      idiom (BUGBOT.md, Informational)
   8. The function is defined but never called anywhere in the codebase

   src/transform.py - compute_weighted_price() at line 133
   9.  No type hints on prices, volumes or the return value (de-standards.mdc)
   10. No entry or exit logging (de-standards.mdc)
   11. Line 134: sum(volumes) and p * v both crash on a None element, with no guard
       (de-standards.mdc)
   12. The function is defined but never called anywhere in the codebase

   src/validate.py - inside validate_records()
   13. exchange_list is built and never used (BUGBOT.md, Informational)
   14. It is a for-append loop where a comprehension is the house idiom
       (BUGBOT.md, Informational)
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

   `git status` shows your agent file as untracked (`?? .cursor/agents/`). It came with you:
   untracked files stay put when you switch branches, which is why the same agent follows
   you across all three PRs without ever landing on a shared branch.

2. Click **+** for a fresh conversation, type `/`, choose **de-pipeline-reviewer** and press
   Enter.

   While it works, expand the trace above the findings and watch what it does. It fetches the
   diff itself, then reads `de-standards.mdc`, `BUGBOT.md` and the schema files — everything
   you told it to read, in order, before it says anything. That trace is the difference
   between an agent and an autocomplete, and it is worth thirty seconds of your attention.

3. First, check the change you made in Task 2.1. If you added a rule, did it fire here on
   pr/002's own instances of the same pattern? If you changed the output format, is the
   summary block there? That is your answer on whether the change generalised.

4. Open a new **Ask** conversation and compare, the same way as Task 2.1:

   ```
   I ran a code review agent on this branch. Below are the defects I know were planted.
   Tell me which ones it caught, which it missed, and whether any of its other findings
   are real problems rather than noise. Be strict about misses.

   PR 002 known defects

   src/transform.py
   1. except (ValueError, TypeError) was narrowed to except ValueError. A None volume
      now raises TypeError and crashes the stage instead of being skipped with a warning
      (BUGBOT.md, Critical: do not narrow or remove exception types)
   2. append_to_daily_summary() opens the file in append mode with no de-duplication
      check, so running the stage twice doubles the rows (BUGBOT.md, Critical)
   3. It never calls writeheader(), and takes its fieldnames from a single record's keys,
      so the column order can differ between calls
   4. It opens and closes the output file on every single record
   5. No entry or exit logging (de-standards.mdc)
   6. No docstring
   7. The function is defined but never called anywhere in the codebase
   8. logger.info("Transform pipeline complete") was deleted
      (BUGBOT.md, Warning: removing an existing log statement)

   src/validate.py
   9.  import os sits inside the function body rather than at the top of the file
   10. input_path.exists() was replaced with os.path.exists(input_file)
       (de-standards.mdc: use pathlib.Path; never use os.path)
   11. The check now reads input_file while the error message on the next line still
       interpolates input_path, so the two disagree about what was looked at
   ```

5. The narrowed `except` is the one to watch. It is a two-character deletion that reads like
   a cleanup, it passes every test that does not feed a null volume through the stage, and it
   is the defect most review tools miss — including Cursor's own, as you will see in Task 3.

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
   .cursor/rules/de-standards.mdc or .cursor/BUGBOT.md that the code violates.
   If a finding comes from neither file, say so and mark it as your own judgement.
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

2. Click **+** for a fresh conversation, type `/`, choose **de-pipeline-reviewer** and press
   Enter. Do not read ahead.

3. Write down how many findings you got and which files they are in, before you look at
   anything below.

4. Open a new **Ask** conversation and compare:

   ```
   I ran a code review agent on this branch. Below are the defects I know were planted.
   Tell me which ones it caught, which it missed, and whether any of its other findings
   are real problems rather than noise. Be strict about misses.

   PR 003 known defects

   src/figi_client.py
   1. Line 57: or "demo-fallback-key-2026" is an API key literal in source
      (BUGBOT.md, Security: blocking, including "demo" and "fallback" values)
   2. Because that fallback always resolves, the FigiClientError("No API key provided...")
      branch at line 82 is now unreachable. The guard is still in the file and no longer
      guards anything
   3. A blank line was removed before self._url

   src/ingest.py
   4. Line 90: except FigiClientError was broadened to a bare except Exception
      (BUGBOT.md, Critical: do not catch exceptions silently)
   5. The logger.error(f"FigiClient request failed: {exc}") line inside it was deleted,
      so the failure is now both broader and silent (BUGBOT.md, Warning)
   6. Line 179: archive_run() reads records[0].keys(), which raises IndexError on an
      empty list
   7. archive_run() appends with no writeheader() and no de-duplication check
      (BUGBOT.md, Critical: idempotency)
   8. archive_run() has no docstring and no logging (de-standards.mdc)
   9. archive_run() is defined but never called anywhere in the codebase

   src/validate.py
   10. Line 168: summarise_violations() returns by_field as an empty dict on every call.
       It is a stub shipped as though it were finished, and it will report zero for every
       field forever
   11. summarise_violations() has no type hints on its argument or its return value
       (de-standards.mdc)
   12. summarise_violations() is defined but never called anywhere in the codebase
   13. logger.info(f"Starting validate pipeline for {input_file}") was deleted
       (BUGBOT.md, Warning)
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

7. Save the file and run the agent once more on pr/003, so you can see the same code
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

Keep this agent open. Task 3 compares it against Cursor's built-in review on this same
branch, so there is nothing more to run.
</details>

---

## Task 3: BUGBOT.md and Agent Review

### Task 3.1: Understand what you are comparing

Three distinct things review code in this project. Keep them separate:

| System | What it is | What it reads |
|---|---|---|
| **Your subagent** | The file you just built; runs when you call it, or when Cursor delegates to it | Whatever its instructions tell it to read |
| **Agent Review** | Local in-editor review from the Source Control panel, no GitHub connection needed | `.cursor/BUGBOT.md`, found by walking upward from each changed file |
| **Bugbot** | PR automation on GitHub, configured under Automations in the Agents Window; needs the repo linked in the Cursor dashboard | `.cursor/BUGBOT.md` (whether it also reads rules is unverified) |

`BUGBOT.md` is the file that matters here, and Cursor finds it by walking upward from each changed file — so a rubric inside `lab-workspace` applies to changes inside `lab-workspace`, whichever folder you have open. It is also the rubric *shared* with Bugbot in the cloud, so anything you want enforced on GitHub PRs belongs in it.

Your `.cursor/rules/*.mdc` files are a different matter: Cursor's documentation says project rules do **not** apply to Bugbot runs, and Agent Review's findings on this build quote `BUGBOT.md` — its wording and its severity labels — rather than anything from the rules file. So the rules you wrote in Lab 1 shape what *you* and your subagent do, and `BUGBOT.md` is what shapes the two built-in reviewers. Knowing which file reaches which reader is most of what this task is for.

One more thing to notice in Task 3.3, because it comes back in Task 3.4: Agent Review's explanation cards paraphrase the rule they are applying, but they never name the file. Your subagent names it, because you told it to.

One sentence to remember: same rubric file, two readers, one in your editor and one on GitHub. Your subagent is the third reader, and it is the only one you control completely.

---

### Task 3.2: Read .cursor/BUGBOT.md

1. In the Explorer, open `.cursor/BUGBOT.md`.

   The path is `.cursor/BUGBOT.md`: not `BUGBOT.md` at the project root, and not `.cursor/rules/BUGBOT.md`. A file at the wrong path is silently ignored.

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

   Do not edit the file in this lab; the `pr/` branches are shared, and Task 3.3 needs the shipped version so everyone compares the same thing.

---

### Task 3.3: Run Agent Review

You are staying on `pr/003`. Your agent's output on this branch is what you will compare
against, so neither tool needs another run on another branch for the comparison to be fair.

This task has one wrinkle, and it is worth more than the review itself.

**Agent Review scopes to your workspace root.** Not to the git repository — to the folder
you opened in Cursor. This course opens `lab-workspace/`, and the repository root is the
folder above it. Run Agent Review from here and it reports **"Not enough changes to
review"** on a PR with three changed files, because from where it is standing there is
nothing to compare. So for this one task you open the repository root, run the review, and
come back.

Remember the rule rather than the workaround: if your repository root is not your workspace
root, Agent Review has nothing to work with. Anyone who works in a monorepo and opens one
package will meet this.

1. Open Cursor Settings: click the gear icon at the top right of the window. Choose
   **Git & PRs** in the left list and scroll to the **Agent Review** section. Confirm
   **Default Approach** is **Quick**; that is what the panel's **Approach** setting will show in
   step 5. Leave **Start Agent Review on Commit** off; you run the
   review by hand. Close Settings.

2. Confirm you are still on the third PR:

   ```bash
   git branch --show-current
   ```

   It prints `pr/003`. Branches are a property of the repository, not of the folder you have
   open, so the branch comes with you in the next step.

3. Open the repository root: menu **File → Open Folder**, then choose
   **ai-augmented-engineering** — the folder that *contains* `lab-workspace`, one level up
   from where you have been working. Cursor reloads the window.

4. Take thirty seconds to notice what changed, because three of these will worry you and
   none of them is a problem:

   - The Explorer now shows the course folders: `student-labs/`, `lab-starters/`,
     `instructor-notes.zip`. Leave them alone. You are here for one button.
   - Your subagent is gone from the `/` menu. It lives in `lab-workspace/.cursor/agents/`,
     and you are no longer rooted there. Nothing was lost — it comes back when you go back.
     This is the same rule as the one above, applied to agents instead of reviews: a
     configuration file belongs to the folder it sits in.
   - A new terminal here opens at the repository root, with no `venv` active. Do not run lab
     commands from this window. If you must, `cd lab-workspace` and re-activate first.
   - Your `.cursor/BUGBOT.md` still applies. Cursor walks upward from each changed file
     looking for one, so a rubric inside `lab-workspace` is still found when the changed
     files are inside `lab-workspace`. That is the one piece of this that works in your favour.

5. Open the **Source Control** panel (third icon in the left bar). Find the **Agent Review**
   section. **Do not click Find Issues yet.** Click the chevron on the right-hand end of the
   button to open its panel.

   Three things are in there:

   - **Optional Instructions**, a free-text box at the top
   - **Approach**, set to **Quick**
   - **Diff Against…**, a dropdown listing your branches — `main`, `pr/001`, `pr/002`,
     `pr/003`, `lab3` and any others you have

6. Open **Diff Against…** and make sure **main** is ticked.

   This is the setting that decides whether the whole task works, so it is worth
   understanding rather than just doing.

   Agent Review does not automatically know which branch this PR was cut from. It reviews the
   difference between where you are and the base you name here, and if that base is wrong —
   or if it is left looking at your uncommitted changes — you get a review of the wrong thing,
   or a review of nothing at all. Every PR branch in this repository was cut from `main`, so
   `main` is the base.

   There is a second reason, and it is the one that matters for Task 3.4. Your subagent
   reviewed `git diff main...HEAD`, because that is what you told it to read. If Agent Review
   looks at a different set of changes, you are not comparing two reviewers, you are comparing
   two different questions. Same diff, two readers: that is the only way the comparison means
   anything.

   While you are in here, notice **Optional Instructions**. You can steer this review with a
   sentence — "focus on error handling", say — the same way you *could* have typed extra
   instructions after your agent's name in Task 1.4. The difference is where the instruction
   lives. What you type here applies to this run and then is gone. What you wrote in your
   agent file applies to every run, for everyone who clones the repository. Leave the box
   empty; you want the built-in review at its defaults for the comparison.

7. Click the button to start the review. It reads **Reviewing** with a progress ring, and
   Quick takes a couple of minutes.

   There is a **Deep** option in the same dropdown. Cursor documents it only as slower and
   more expensive, recommended for "complex logic, security-sensitive code, or large
   refactors", and says nothing about what it does differently. In practice people report
   Deep finding the same or fewer issues than Quick on a small diff. The diff base is what
   changes your result; the depth mostly changes your bill.

8. A prompt appears offering to **review every commit automatically**. Dismiss it. Leave it off.

   It is a real feature and a reasonable thing to turn on in your own repository. We leave it
   off here because you are on shared `pr/` branches the rest of the room is also checking
   out, and because you want to see exactly what triggered this run.

9. Read the findings. Clicking one opens a diff view with an explanation card, **Fix with
   Agent**, and **Dismiss**. Do not click **Fix**, **Fix All Issues**, or **Fix with Agent**:
   you are comparing, not fixing.

10. The button now reads **Review Again**. Click it once, with the same diff base, and note
    whether the second pass finds anything the first did not. Agent Review varies run to run,
    the same way your subagent does.

11. Write down the findings, or leave the panel open. You need them in Task 3.4 and they do
    not follow you back.

12. Go back to your workspace: menu **File → Open Folder**, then choose **lab-workspace**.
    Your subagent, your rules and your terminal all come back.

<details open>
<summary>What you should see</summary>

Around half a dozen findings against `lab-workspace/src/figi_client.py`,
`lab-workspace/src/ingest.py` and `lab-workspace/src/validate.py` — the hard-coded API key,
the narrowed exception handler, the archive function's missing de-duplication and its
`IndexError` on an empty list, the missing type hints, the deleted log statement. Note how
cleanly those map onto `BUGBOT.md`'s tiers: one Security, some Critical, some Warning. The
rubric file is doing the work.

That is a genuinely good showing on the thirteen planted pr/003 defects, from one click and
no setup — which is the honest half of the comparison you are about to write in Task 3.4.

**If it says "Not enough changes to review"**, you are still rooted at `lab-workspace`. Go
back to step 3.

**If every finding names a Markdown file rather than a `.py` file**, the diff base is still
set to your uncommitted changes. Go back to step 5.
</details>

---

### Task 3.4: Compare, then keep your agent

1. Fill in this table from the Agent Review output and your agent's final pr/003 output:

| | Your subagent | Agent Review |
|---|---|---|
| Planted pr/003 defects found, out of 13 | | |
| False positives | | |
| Most actionable finding | | |
| Names the rule behind each finding | | |
| Time to produce output | | |
| Runs on someone else's machine after a clone | | |

2. **Before you continue, note:**

   > When would you use Agent Review instead of your subagent in your daily work, and when the subagent instead?

<details open>
<summary>Typical answer pattern</summary>

Agent Review is one click and needs no setup; use it for a quick sanity check before pushing. Your subagent produces more structured output with severity ratings, confidence levels and DE-specific criteria, and it is a file in the repository: a teammate who clones the repo has your reviewer, at your standard, without being told. Use it before raising a PR, or in an asynchronous review where the output must be actionable by someone who was not present.

Neither replaces the other. The professional workflow is: Agent Review before pushing, your agent before raising the PR.
</details>

3. Leave the `pr/` branches as you found them. If you changed a tracked file on one, put it back:

   ```bash
   git checkout -- .
   ```

4. Commit your agent on your own branch, where it belongs:

   ```bash
   git checkout lab3
   git add .cursor/agents/
   git commit -m "Add DE pipeline reviewer subagent"
   git log --no-pager --oneline -2
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

In Task 1.3 you turned Read-only on rather than writing "do not modify any files" in the instructions. Name one thing that protects you from that the instruction does not. Why is "escalate when unsure" not the same as "escalate when dangerous"?

---

**Question 4**

Write one new rule for `.cursor/BUGBOT.md` based on an issue your agent found in pr/003 that the current file does not cover. Would you rather put that rule in BUGBOT.md or in your agent file, and why?

---

**Question 5**

Your agent runs when you call it. Nothing stops you wiring it to a trigger instead — both
editors support hooks, so an agent can be told to run whenever a file under `src/` changes,
with no one asking it to.

What would have to be true before you let your reviewer run itself on your own team's code?
Consider at least: how long a review takes and what the developer is doing while it runs;
what the agent should do with what it finds, given nobody is watching the output; and which
findings should stop the work rather than be filed for later.
