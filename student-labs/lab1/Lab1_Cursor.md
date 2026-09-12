# Lab 1: Configure Before You Convert
**Course:** AI-Augmented Engineering for Data Engineers
**Tool:** Cursor (Pro plan)
**Duration:** 60 minutes
**Day:** Day 1, following Module 1

---

## Prerequisites

- [ ] Module 1 lecture completed
- [ ] Cursor installed and signed in with a Pro plan license
- [ ] Sample pipeline repository cloned and open in Cursor
- [ ] Git configured with your name and email (`git config --global user.name` returns a value)
- [ ] pytest installed and accessible from the terminal (`pytest --version` returns a version)

---

## Lab Overview

Your team is about to start converting a production Perl pipeline to Python. Before anyone touches code, this lab establishes the shared configuration that makes every engineer's agent output consistent and standards-compliant.

Every artifact you build here is used directly in Labs 2, 3, and 4. Do not skip tasks or use different file names from the ones specified.

**What you will build:**
- `.cursor/rules/de-standards.mdc` —team DE coding standards enforced on every agent conversation
- `.cursor/rules/perl-to-python.mdc` —conversion-specific rules that activate on Perl and Python files
- `.cursor/skills/pipeline-review/SKILL.md` —an invocable code review checklist

**What you will observe:**
- The measurable difference in agent output before and after rules are active
- The behavioral difference between `/skill-name` (run as workflow) and `@skill-name` (attach as context)

---

## Step 0: Load Starter Files

Run this before anything else. This overwrites any existing files at these paths. That is intentional.

Open a terminal inside Cursor (`Ctrl+`` ` `` `) and run the following from the `sample_pipeline/` project root:

```powershell
cp -r lab-starters/lab1/.cursor .
```

**macOS/Linux:**
```bash
cp -r lab-starters/lab1/.cursor .
```

Verify the copy succeeded:

```powershell
ls .cursor\rules\
```

**macOS/Linux:**
```bash
ls .cursor/rules/
```

<details>
<summary>Expected output</summary>

You should see two files listed:

```
de-standards.mdc
perl-to-python.mdc
```

If the directory is empty or does not exist, re-run the copy command from the correct project root directory.
</details>

---

## Part 1: Mode Familiarization

### Step 1.1: Open the mode dropdown

Make sure the Cursor chat panel is open. If it is not visible, press `Ctrl+I` (Windows) or `Cmd+I` (Mac).

Click the mode name at the bottom left of the chat input. The dropdown opens showing all four modes.

<details>
<summary>What you should see in the dropdown</summary>

The four modes listed are:

| Mode | What it does |
|---|---|
| **Agent** | Default mode. Plans, edits files, runs terminal commands, iterates autonomously. |
| **Plan** | Researches the codebase, asks clarifying questions, produces a plan before writing code. |
| **Debug** | Gathers runtime evidence before proposing a fix. Adds instrumentation to the code. |
| **Ask** | Read-only. Answers questions without making any changes to files. |

Switch between modes using the dropdown or press `Shift+Tab` to cycle through them.
</details>

Note the current mode. It is most likely **Agent**. Do not change it yet.

---

### Step 1.2: Run the same prompt in Ask mode, then Agent mode

Switch to **Ask mode** by clicking it in the dropdown.

Type the following prompt exactly and press Enter:

```
Look at src/ingest.py in this project.
What does the process_records function do?
What would you change to make it meet professional Python standards?
```

Read the full response. Ask mode is read-only—no files have changed.

**Write down your answer before continuing:**

> What did Ask mode tell you about `process_records`? What changes did it suggest?

---

Now switch to **Agent mode** using the dropdown.

Send the identical prompt. Press Enter.

Watch what happens. Agent mode will likely begin making changes to the file.

When the agent finishes, click **Undo All** in the file change summary that appears at the top of the editor. You are not ready to accept agent changes yet.

**Write down your answer before continuing:**

> What did Agent mode do differently from Ask mode? Did files change? What did the agent attempt?

<details>
<summary>What to expect from each mode</summary>

**Ask mode** should have returned a description of what `process_records` does and a list of suggested improvements—type hints missing, no logging, os.path instead of pathlib -- without touching any file.

**Agent mode** should have immediately started editing `src/ingest.py`, applying changes based on its judgment of what "professional Python standards" means.

The key observation: Ask mode is structurally read-only. Agent mode acts. The mode discipline this course teaches—explore with Ask, then switch to Agent when you are ready—exists because of this difference.

If Agent mode also only described changes without editing, check that you are on a Pro plan. Free tier users may not have full Agent mode access.
</details>

---

## Part 2: Build the DE Standards Rules File

### Step 2.1: Understand the file you are about to create

The rules file at `.cursor/rules/de-standards.mdc` was copied from the starter files in Step 0. It currently exists but is empty except for the frontmatter header.

Open it now in the Cursor editor:

```powershell
code .cursor\rules\de-standards.mdc
```

**macOS/Linux:**
```bash
code .cursor/rules/de-standards.mdc
```

<details>
<summary>What the starter file contains</summary>

The starter file has this frontmatter already in place:

```yaml
---
description: DE team coding standards for Python pipeline development
alwaysApply: true
---
```

The `alwaysApply: true` setting means every agent conversation in this project will include these rules automatically. You do not need to reference the file in each prompt.

**Important:** The file must have the `.mdc` extension. A file named `de-standards.md` in the same directory is silently ignored by Cursor. The extension is not optional.
</details>

---

### Step 2.2: Add the six DE coding standards

Open `team-de-standards.md` from your lab materials. Read it in full before writing any rules.

Add the following six rules below the frontmatter in `de-standards.mdc`. Write each as a direct instruction to the agent, not a policy description.

**Rule 1: Type hints**
```
All Python function arguments must have type hints.
All return types must be declared. Use the typing module for complex types.
```

**Rule 2: Logging**
```
Every pipeline function must log on entry and exit using the project logger.
Format: logger.info(f'Starting {function_name} with {len(records)} records')
```

**Rule 3: File handling**
```
Use pathlib.Path for all file operations.
Never use os.path or raw string paths passed directly to open().
```

**Rule 4: Null safety**
```
Handle None explicitly on all critical fields.
Never use bare .get() without a default value on any pipeline field.
```

**Rule 5: Counting patterns**
```
Use collections.Counter for all counting and frequency analysis.
Never use manual dictionary increment patterns.
```

**Rule 6: Perl conversion**
```
When converting Perl to Python, do not produce a line-by-line translation.
Produce idiomatic Python: list comprehensions, Counter, pathlib, type hints, re module.
```

Save the file: `Ctrl+S` (Windows) or `Cmd+S` (Mac).

<details>
<summary>Complete `de-standards.mdc` reference</summary>

Your completed file should look exactly like this:

```
---
description: DE team coding standards for Python pipeline development
alwaysApply: true
---

All Python function arguments must have type hints.
All return types must be declared. Use the typing module for complex types.

Every pipeline function must log on entry and exit using the project logger.
Format: logger.info(f'Starting {function_name} with {len(records)} records')

Use pathlib.Path for all file operations.
Never use os.path or raw string paths passed directly to open().

Handle None explicitly on all critical fields.
Never use bare .get() without a default value on any pipeline field.

Use collections.Counter for all counting and frequency analysis.
Never use manual dictionary increment patterns.

When converting Perl to Python, do not produce a line-by-line translation.
Produce idiomatic Python: list comprehensions, Counter, pathlib, type hints, re module.
```
</details>

---

### Step 2.3: Verify the rules change agent output

Open a new Agent mode conversation.

Send this prompt exactly:

```
Write a Python function that reads a list of log file paths
and counts how many times each IP address appears across all files.
```

Read the output carefully. With `de-standards.mdc` active and `alwaysApply: true` set, the output should include all of the following:

- [ ] Type hints on all function arguments and the return type
- [ ] `pathlib.Path` for file handling
- [ ] `collections.Counter` for counting
- [ ] `logger.info` calls on entry and exit

<details>
<summary>What to do if the rules are not applying</summary>

Check three things in order:

1. **File extension:** The file must be `.mdc`, not `.md`. Check the filename in the file explorer.
2. **Frontmatter syntax:** Open the file and confirm the dashes and field names match exactly. Smart quotes or extra spaces before the dashes will break the parser.
3. **File saved:** Press `Ctrl+S` and try the verification prompt again in a fresh conversation.

If none of these fix it, close and reopen Cursor entirely, then try again.
</details>

**Write down your answer before continuing:**

> What specific difference do you observe compared to what the agent produced without the rules file? Name at least two concrete differences in the code output.

---

## Part 3: Read and Extend the Perl-to-Python Rules File

### Step 3.1: Open and read the file

The starter files copied a pre-built `perl-to-python.mdc` into `.cursor/rules/`. Open it now:

```powershell
code .cursor\rules\perl-to-python.mdc
```

**macOS/Linux:**
```bash
code .cursor/rules/perl-to-python.mdc
```

Read the frontmatter first. Note the `globs` field—this file activates automatically for `*.pl` and `*.py` files, but not for every conversation. This is different from `de-standards.mdc` which uses `alwaysApply: true`.

Read each rule in the file body.

<details>
<summary>What the perl-to-python.mdc file contains</summary>

```
---
description: Perl to Python conversion standards for the DE pipeline modernisation project
globs: ["**/*.pl", "**/*.py"]
---

Translate Perl regex using Python's re module.
Convert /.../g patterns to re.finditer() or re.findall().
Pre-compile patterns that are used inside loops: pattern = re.compile(r'...')

Do not translate Perl sigils literally.
Use collections.Counter for counting patterns.
Use dict for hash mappings.
Use set for membership tests.

Use pathlib.Path for all file operations.
No os.path. No raw string paths passed to open().

All function arguments must have type hints.
All return types must be declared.

When you see a Perl construct, ask what it is trying to accomplish.
Then write the Python that accomplishes the same thing idiomatically.
Do not produce a line-by-line translation.
```
</details>

**Write down your answer before continuing:**

> Which rule in `perl-to-python.mdc` covers something you were not expecting? Or: what rule do you think is missing?

---

### Step 3.2: Add one rule based on your team's conventions

Below the last existing rule in `perl-to-python.mdc`, add one new rule that covers a Python pattern your team uses that is not already in the file.

<details>
<summary>Examples of rules you might add</summary>

These are examples only. Write a rule that reflects your team's actual conventions.

```
Use structlog for all logging. Never use the standard library logging module directly.
```

```
All pipeline functions that process records must include a try/except block
that catches Exception, logs the error with logger.exception(), and re-raises.
```

```
Database connection strings must be read from environment variables using os.environ.get().
Never hardcode connection strings in pipeline code.
```
</details>

Save the file.

Verify the rule is being read by opening a new Agent mode conversation, attaching `@perl/ingest.pl`, and sending:

```
Review this Perl file against the conversion rules in
.cursor/rules/perl-to-python.mdc. What would the key
differences be in the Python equivalent?
```

The response should mention your new rule alongside the existing ones.

<details>
<summary>What to do if your rule does not appear in the response</summary>

1. Confirm the file is saved.
2. Confirm the frontmatter `globs` field includes `"**/*.pl"`.
3. Confirm you attached `@perl/ingest.pl` in the prompt -- the globs activation requires the agent to be working with a matching file.
4. Try referencing the rule file explicitly: add `@perl-to-python` to your prompt.
</details>

---

## Part 4: Build the Pipeline-Review Skill

### Step 4.1: Create the skill using /create-skill

Open a new Agent mode conversation.

Type the following and press Enter:

```
/create-skill Review Python pipeline code against DE team standards.
Check for: schema drift handling, null safety on critical fields,
idempotency, logging completeness, and type hint coverage.
Flag each issue as Critical, Warning, or Informational.
Produce a structured review summary grouped by severity.
```

Cursor opens a **Questions** dialog. Answer each question and click **Continue**.

<details>
<summary>What questions to expect and how to answer them</summary>

The questions are dynamic -- a specific description produces fewer questions. You will always see at least the storage location question:

**Where should this skill be stored?**
- A: Personal (`~/.cursor/skills/`) -- available in all projects
- B: Project (`.cursor/skills/`) -- this repo only
- C: Other

**Select B: Project (`.cursor/skills/)`.** This stores the skill in the repository so every team member has access to it after cloning.

If Cursor asks additional questions about the skill name or description, answer them specifically. The more detail you provide, the better the generated skill body will be.
</details>

---

### Step 4.2: Inspect and verify the skill file

Open `.cursor/skills/pipeline-review/SKILL.md` in the editor.

Confirm the file has YAML frontmatter with at least a `name` field and a `description` field.

Read the skill body. Confirm it covers all five review criteria:

- [ ] Schema drift handling
- [ ] Null safety on critical fields
- [ ] Idempotency
- [ ] Logging completeness
- [ ] Type hint coverage

If any criterion is missing, add it as a numbered item in the skill body. Save the file.

<details>
<summary>Complete SKILL.md reference</summary>

Your skill file should look similar to this. The exact wording may differ based on how /create-skill generated it, but all five criteria must be present:

```markdown
---
name: pipeline-review
description: Reviews Python pipeline code against DE team standards. Flags schema drift handling, null safety, idempotency, logging completeness, and type hint coverage.
---

Review the provided Python pipeline code against the following criteria.
For each finding, state the criterion violated, the file and line number,
and a specific recommendation.

Group findings by severity:

## Critical
Issues that will cause data loss, silent failures, or incorrect pipeline output.
- Missing schema validation on incoming data
- None values not handled on customer_id, transaction_date, or amount fields
- Pipeline steps that are not idempotent

## Warning
Issues that reduce reliability or violate team standards.
- Functions missing type hints on arguments or return values
- Missing logger.info calls on function entry or exit
- File operations not using pathlib.Path

## Informational
Style issues and improvement opportunities.
- for-append loops that could be list comprehensions
- dict counting patterns that should use collections.Counter
```
</details>

---

### Step 4.3: Invoke with / and observe the output

Open a new Agent mode conversation.

Type `/pipeline-review` and press Enter. When prompted, type:

```
Review src/ingest.py
```

Read the structured output. It should be grouped by severity: Critical, Warning, Informational.

---

### Step 4.4: Invoke with @ and compare

Open another new Agent mode conversation.

Type `@` in the chat input. Look for `pipeline-review` in the autocomplete and select it.

Add this message and press Enter:

```
Using the pipeline-review criteria as your guide, what are the
three highest-priority issues in src/ingest.py and why?
```

**Write down your answer before continuing:**

> What is the specific behavioral difference between `/pipeline-review` and `@pipeline-review`? Describe what each one did differently in your own words.

<details>
<summary>The expected difference</summary>

**`/pipeline-review`** runs the skill as a complete workflow. The agent follows the skill's procedure from start to finish, reads the file, applies all five criteria, and produces the structured review output. You are handing control to the skill.

**`@pipeline-review`** attaches the skill as reference context. The agent draws on the skill's criteria while answering your specific question -- "what are the three highest-priority issues" -- rather than running the full structured review. You are keeping control and using the skill as a lens.

Use `/` when you want the full procedure executed. Use `@` when you want the criteria available while you ask a different question.
</details>

---

## Part 5: Apply—The Integrating Workflow

### Step 5.1: Explore first in Ask mode

Switch to **Ask mode** using the mode dropdown.

Send the following prompt and press Enter:

```
Look at src/ingest.py. Identify the single function that most needs
improvement against our team standards. Name the function, describe
what is wrong with it, and tell me exactly what you would change.
```

Read the full response.

**Before switching to Agent mode, write a one-sentence description of what the function does and why the suggested change makes it better.**

> Write your sentence here before continuing. This is the explore-before-changing gate.

<details>
<summary>Why this gate matters</summary>

The explore-before-changing discipline is the professional habit this course builds on. The agent is faster at execution than any human. The human advantage is judgment about what to execute.

If you cannot describe in one sentence what the function does and why the change is an improvement, you do not yet understand what you are about to change. Switch back to Ask mode and ask more questions before proceeding.
</details>

---

### Step 5.2: Switch to Agent mode and execute

Switch to **Agent mode** using the mode dropdown.

Send the following prompt, replacing `[function name]` with the function Ask mode identified:

```
Apply the improvements you described to [function name] in src/ingest.py.
Follow the standards in our .cursor/rules/ files throughout.
After making the changes, run /pipeline-review on the updated
function and report the remaining issues.
```

Press Enter and watch the agent work.

When the agent finishes, click **Review** in the file change summary to examine the diff before accepting.

<details>
<summary>What to look for in the diff</summary>

The diff should show changes corresponding to the rules in `de-standards.mdc`:

- Type hints added to all function arguments and the return type
- `pathlib.Path` replacing any `os.path` or raw string paths
- `collections.Counter` replacing any manual dict counting
- `logger.info` calls added at function entry and exit
- `None` checks added on critical fields

If the diff shows changes that are not explained by your rules files, read each one and ask the agent to explain before accepting.

Accept using **Keep All** only after reviewing every changed line.
</details>

**Write down your answer before continuing:**

> What specific changes did the agent make? Which of the de-standards.mdc rules are visible in the diff? What did /pipeline-review report as remaining issues?

---

### Step 5.3: Capture learning as a rule

If the `/pipeline-review` skill flagged anything as Critical or Warning that your `de-standards.mdc` file does not already cover, open `de-standards.mdc` now.

Add one new rule addressing the gap. Write it as a direct instruction to the agent.

Save the file.

> If the pipeline-review found nothing that de-standards.mdc did not already cover, your rules file is well-calibrated for this function. Note that in the debrief—it is a valid and good outcome.

---

## Lab Debrief

Write answers to these prompts before the room debrief begins. You will share one answer with the group.

---

**Question 1**

In Step 1.2 you ran the same prompt in Ask mode and Agent mode. What was the most significant behavioral difference you observed? Why does that difference matter for the Perl conversion work in Lab 2?

---

**Question 2**

In Step 2.3 you verified that `de-standards.mdc` changed agent output. What specific code construct changed? Name the before and after explicitly.

---

**Question 3**

In Step 4.4 you invoked `/pipeline-review` and also used `@pipeline-review`. In your own words, when would you use each invocation method in your daily work?

---

**Question 4**

In Step 3.2 you added a rule to `perl-to-python.mdc`. What rule did you add? Why does your team need it and why was it not already in the file?
