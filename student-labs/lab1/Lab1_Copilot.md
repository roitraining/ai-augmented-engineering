# Lab 1: Configure Before You Convert
**Course:** AI-Augmented Engineering for Data Engineers
**Tool:** GitHub Copilot Enterprise (VS Code)
**Duration:** 60 minutes
**Day:** Day 1, following Module 1

---

## Prerequisites

- [ ] Module 1 lecture completed
- [ ] VS Code installed with the GitHub Copilot and GitHub Copilot Chat extensions active
- [ ] GitHub Copilot Enterprise license active (verify: the Copilot icon appears in the VS Code status bar without an error indicator)
- [ ] Sample pipeline repository cloned and open in VS Code
- [ ] Git configured with your name and email (`git config --global user.name` returns a value)
- [ ] pytest installed and accessible from the terminal (`pytest --version` returns a version)

---

## A Note on Coverage

This lab follows the same five-task structure and learning objectives as the Cursor version. Where GitHub Copilot Enterprise has a direct equivalent to a Cursor feature, this lab uses it. Where no equivalent exists, this lab uses the closest available approach and states the difference explicitly.

**What is different in this version:**

| Cursor feature | Copilot equivalent used in this lab |
|---|---|
| Four named modes (Agent, Ask, Plan, Debug) | One Agent mode with prompt-based constraints |
| `.cursor/rules/*.mdc` with four activation modes | `.github/copilot-instructions.md` (always-on) and `.github/instructions/*.instructions.md` (path-scoped) |
| `.cursor/skills/` invoked with `/skill-name` | `.github/skills/` invoked with `/skill-name` (identical command and file structure) |
| Context ring showing token usage | Not available in Copilot -- context is managed implicitly |

The mode differences are the most significant. Copilot has one Agent mode that adapts based on the task. The read-only protection that Cursor's Ask mode provides structurally must be achieved through explicit prompt constraints in Copilot. This lab teaches both approaches so you understand the difference.

---

## Lab Overview

Your team is about to start converting a production Perl pipeline to Python. Before anyone touches code, this lab establishes the shared configuration that makes every engineer's Copilot output consistent and standards-compliant.

Every artifact you build here is used directly in Labs 2, 3, and 4. Do not skip tasks or use different file names from the ones specified.

**What you will build:**
- `.github/copilot-instructions.md` -- team DE coding standards applied to every Copilot conversation
- `.github/instructions/perl-conversion.instructions.md` -- conversion-specific instructions that activate on Perl and Python files
- `.github/skills/pipeline-review/SKILL.md` -- an invocable code review checklist

**What you will observe:**
- The measurable difference in Copilot output before and after instructions are active
- How prompt constraints substitute for Cursor's read-only Ask mode
- The behavioral difference between `/pipeline-review` (run as workflow) and referencing the skill criteria directly in a prompt

---

## Step 0: Load Starter Files

Run this before anything else. This overwrites any existing files at these paths. That is intentional.

Open a terminal inside VS Code (`` Ctrl+` ``) and run the following from the `sample_pipeline/` project root:

```powershell
cp -r copilot-starters\lab1\.github .
```

**macOS/Linux:**
```bash
cp -r copilot-starters/lab1/.github .
```

Verify the copy succeeded:

```powershell
ls .github\
```

**macOS/Linux:**
```bash
ls .github/
```

<details>
<summary>Expected output</summary>

You should see the following directory structure:

```
.github/
  copilot-instructions.md      ← empty, ready for your rules
  instructions/
    perl-conversion.instructions.md   ← pre-built, ready to read and extend
  skills/
    (empty directory, ready for /create-skill output)
  prompts/
    (empty directory, for future use)
```

If `.github/` does not exist or is empty, re-run the copy command from the correct project root directory.
</details>

> **Why the starter files matter:** VS Code and Copilot look for `.github/copilot-instructions.md` at the repository root. If the directory does not exist when you open the repository, Copilot has no project-level instructions. The starter files ensure the structure is in place before you begin writing content.

---

## Part 1: Mode Familiarization

### Step 1.1: Open Copilot Chat

Press `Ctrl+Shift+I` (Windows) or `Cmd+Shift+I` (Mac) to open the Copilot Chat panel.

Confirm the mode selector shows **Agent**. If it shows a different mode, click the selector and choose Agent.

<details>
<summary>About Copilot's single mode</summary>

GitHub Copilot Enterprise uses one Agent mode that adapts its behaviour based on the task and the prompt. There are no named Ask, Plan, or Debug modes as there are in Cursor.

The practical implication: the protection that Cursor's Ask mode provides (the agent structurally cannot modify files) does not exist as a built-in safeguard in Copilot. In Copilot, read-only behaviour is achieved through explicit prompt constraints -- you tell the agent not to edit files, and it follows that instruction.

This is one of the coverage gaps noted in the lab overview. This step is designed to make that difference concrete rather than abstract.
</details>

---

### Step 1.2: Simulate read-only exploration using a prompt constraint

In Copilot Chat (Agent mode), type the following and press Enter:

```
Do not edit any files. Answer only.

Look at src/ingest.py in this project.
What does the process_records function do?
What would you change to make it meet professional Python standards?
```

Read the full response. Because of the explicit constraint, Copilot should describe the changes without making them.

**Write down your answer before continuing:**

> What did Copilot tell you about `process_records`? What changes did it suggest?

---

Now send the same prompt **without** the constraint. Start a new conversation by clicking the **+** icon in the Copilot Chat panel, then send:

```
Look at src/ingest.py in this project.
What does the process_records function do?
What would you change to make it meet professional Python standards?
```

Watch what happens. Copilot may begin suggesting or making changes to the file.

If files were changed, use `Ctrl+Z` to undo, or right-click the file in the explorer and select **Discard Changes**.

**Write down your answer before continuing:**

> What was the difference between the constrained prompt and the unconstrained prompt? What does this tell you about how read-only behaviour works in Copilot versus Cursor?

<details>
<summary>What to expect from each prompt</summary>

**With the constraint** (`Do not edit any files. Answer only.`): Copilot should return a description of what `process_records` does and a list of suggested improvements -- missing type hints, no logging, `os.path` instead of `pathlib` -- without touching any file.

**Without the constraint**: Copilot may immediately suggest inline edits, open a diff, or begin applying changes directly to `src/ingest.py`.

**The key observation:** In Cursor, Ask mode is a structural safeguard -- the mode itself prevents file edits regardless of the prompt. In Copilot, the protection comes from the prompt discipline. Both approaches achieve the same result. The Cursor approach is more robust because it does not depend on the prompt author remembering to include the constraint every time.

This is the practical reason the explore-before-changing discipline matters more in Copilot: without a named read-only mode, the habit of explicitly constraining exploration prompts is what prevents accidental edits.
</details>

---

## Part 2: Build the DE Standards Instructions File

### Step 2.1: Understand the file you are about to populate

The starter files created `.github/copilot-instructions.md` at the repository root. This file is empty and ready for content. Open it now:

```powershell
code .github\copilot-instructions.md
```

**macOS/Linux:**
```bash
code .github/copilot-instructions.md
```

<details>
<summary>How copilot-instructions.md works</summary>

`.github/copilot-instructions.md` is GitHub Copilot Enterprise's always-on instruction file. Its contents are automatically included in every Copilot Chat interaction for anyone working in this workspace. No frontmatter or activation settings are required -- the file applies automatically by virtue of existing at this path.

This is equivalent to a Cursor rules file with `alwaysApply: true`. The key differences from Cursor:
- Plain Markdown only. No YAML frontmatter.
- One file for always-on instructions (versus Cursor's ability to have many rules files with different activation modes).
- Path-scoped instructions are handled by separate files in `.github/instructions/` (covered in Part 3).

The file applies to all Copilot Chat conversations in VS Code and to Copilot code review on GitHub.com. It does not apply to inline code completion suggestions.
</details>

---

### Step 2.2: Add the six DE coding standards

Add the following six rules to `.github/copilot-instructions.md`. Write each as a direct instruction to the agent.

```markdown
# DE Team Coding Standards

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

Save the file: `Ctrl+S` (Windows) or `Cmd+S` (Mac).

<details>
<summary>Complete copilot-instructions.md reference</summary>

Your completed file should look exactly like this:

```markdown
# DE Team Coding Standards

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

No frontmatter. No YAML. Plain Markdown is all that is required.
</details>

---

### Step 2.3: Verify the instructions change Copilot output

Open a new Copilot Chat conversation (click the **+** icon).

Send this prompt exactly:

```
Write a Python function that reads a list of log file paths
and counts how many times each IP address appears across all files.
```

Read the output carefully. With `.github/copilot-instructions.md` active, the output should include all of the following:

- [ ] Type hints on all function arguments and the return type
- [ ] `pathlib.Path` for file handling
- [ ] `collections.Counter` for counting
- [ ] `logger.info` calls on entry and exit

**Write down your answer before continuing:**

> What specific differences do you observe compared to what Copilot produced before the instructions file existed? Name at least two concrete differences in the code output.

<details>
<summary>What to do if the instructions are not applying</summary>

Check these in order:

1. **File location:** The file must be at `.github/copilot-instructions.md` at the repository root. A file at `copilot-instructions.md` at the root (without `.github/`) is not read.
2. **File saved:** Press `Ctrl+S` and open a completely new Copilot Chat conversation. Copilot picks up instruction file changes at conversation start, not mid-conversation.
3. **Workspace trust:** VS Code must trust the workspace. Check the bottom-left status bar for a shield icon indicating restricted mode. If present, click it and choose **Trust Workspace**.
4. **Copilot extension version:** Confirm the GitHub Copilot Chat extension is up to date. Open Extensions (`Ctrl+Shift+X`), find GitHub Copilot Chat, and check for updates.
</details>

---

## Part 3: Read and Extend the Perl Conversion Instructions File

### Step 3.1: Open and read the file

The starter files created `.github/instructions/perl-conversion.instructions.md`. Open it now:

```powershell
code .github\instructions\perl-conversion.instructions.md
```

**macOS/Linux:**
```bash
code .github/instructions/perl-conversion.instructions.md
```

Read the frontmatter first. Note the `applyTo:` field -- this file activates automatically when Copilot is working with `.pl` or `.py` files, but not for every conversation. This is path-scoped activation, equivalent to Cursor's `globs` field.

Read each instruction in the file body.

<details>
<summary>What the perl-conversion.instructions.md file contains</summary>

```markdown
---
applyTo: "**/*.pl,**/*.py"
---

# Perl to Python Conversion Standards

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

The `applyTo:` field in the frontmatter is the only required metadata. The value is a glob pattern. Multiple patterns are comma-separated.
</details>

<details>
<summary>How path-scoped instructions differ from always-on instructions</summary>

`.github/copilot-instructions.md` applies to every Copilot Chat conversation in this workspace regardless of which files are open.

`.github/instructions/perl-conversion.instructions.md` applies only when the file being discussed or edited matches the `applyTo:` pattern -- in this case, any `.pl` or `.py` file.

Use always-on for standards that should never be bypassed. Use path-scoped for standards that are specific to a file type, directory, or workflow.

This is equivalent to the difference between `alwaysApply: true` and a `globs` field in Cursor's rules frontmatter.
</details>

**Write down your answer before continuing:**

> Which instruction in `perl-conversion.instructions.md` covers something you were not expecting? Or: what instruction do you think is missing?

---

### Step 3.2: Add one instruction based on your team's conventions

Below the last existing instruction in `perl-conversion.instructions.md`, add one new instruction that covers a Python pattern your team uses that is not already in the file.

<details>
<summary>Examples of instructions you might add</summary>

These are examples only. Write an instruction that reflects your team's actual conventions.

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

Verify the instruction is being applied by opening a new Copilot Chat conversation, then attaching `perl/ingest.pl` using the paperclip icon or by typing `#file:perl/ingest.pl` in the chat input, and sending:

```
#file:perl/ingest.pl

Review this Perl file against our conversion standards.
What would the key differences be in the Python equivalent?
```

The response should mention your new instruction alongside the existing ones.

<details>
<summary>What to do if your instruction does not appear in the response</summary>

1. Confirm the file is saved.
2. Confirm the `applyTo:` field in the frontmatter includes `**/*.pl`.
3. Confirm you attached or referenced `perl/ingest.pl` in the prompt -- path-scoped instructions only activate when the conversation references a matching file.
4. Try explicitly referencing the instructions file: add `#file:.github/instructions/perl-conversion.instructions.md` to your prompt.
</details>

---

## Part 4: Build the Pipeline-Review Skill

### Step 4.1: Create the skill using /create-skill

Open a new Copilot Chat conversation.

Type the following and press Enter:

```
/create-skill Review Python pipeline code against DE team standards.
Check for: schema drift handling, null safety on critical fields,
idempotency, logging completeness, and type hint coverage.
Flag each issue as Critical, Warning, or Informational.
Produce a structured review summary grouped by severity.
```

Copilot opens a **Questions** dialog. Answer each question and click **Continue**.

<details>
<summary>What questions to expect and how to answer them</summary>

The `/create-skill` command is identical in VS Code Copilot and Cursor (confirmed February 2026 release). The question flow is dynamic -- a specific description produces fewer questions. You will always see at least the storage location question:

**Where should this skill be stored?**
- A: Personal (`~/.copilot/skills/`) -- available in all projects on this machine
- B: Project (`.github/skills/`) -- this repo only
- C: Other

**Select B: Project (`.github/skills/`).** This stores the skill in the repository so every team member has access after cloning, and so the skill automatically extends Copilot code review on GitHub.com PRs.
</details>

> **Copilot advantage worth noting:** Skills stored in `.github/skills/` automatically extend Copilot's code review on GitHub.com pull requests. When Copilot reviews a PR in this repository, it invokes your `pipeline-review` skill as part of the review. This happens without additional configuration. In Cursor, skills are invoked on demand in the editor but do not automatically extend Bugbot's PR review in the same way.

---

### Step 4.2: Inspect and verify the skill file

Open `.github/skills/pipeline-review/SKILL.md` in the editor.

Confirm the file has frontmatter with at least a `name` field and a `description` field.

Read the skill body. Confirm it covers all five review criteria:

- [ ] Schema drift handling
- [ ] Null safety on critical fields
- [ ] Idempotency
- [ ] Logging completeness
- [ ] Type hint coverage

If any criterion is missing, add it as a numbered item in the skill body. Save the file.

<details>
<summary>Complete SKILL.md reference</summary>

Your skill file should look similar to this. The exact wording may differ based on how `/create-skill` generated it, but all five criteria must be present:

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

### Step 4.3: Invoke the skill with /pipeline-review

Open a new Copilot Chat conversation.

Type `/pipeline-review` and press Enter. When prompted, type:

```
Review src/ingest.py
```

Read the structured output. It should be grouped by severity: Critical, Warning, Informational.

---

### Step 4.4: Use the skill criteria as context in a follow-up prompt

Open another new Copilot Chat conversation.

Attach the skill file as context by typing:

```
#file:.github/skills/pipeline-review/SKILL.md

Using the pipeline-review criteria in the attached skill file as your guide,
what are the three highest-priority issues in src/ingest.py and why?
```

Press Enter and read the response.

**Write down your answer before continuing:**

> What is the specific behavioral difference between `/pipeline-review` and referencing the skill file directly via `#file:`? Describe what each approach did differently.

<details>
<summary>The expected difference and the Copilot-specific note</summary>

**`/pipeline-review`** runs the skill as a complete workflow. Copilot follows the skill's procedure from start to finish, reads `src/ingest.py`, applies all five criteria, and produces the structured review output.

**`#file:.github/skills/pipeline-review/SKILL.md`** attaches the skill as reference context. Copilot draws on the skill's criteria while answering your specific question about the three highest-priority issues, rather than running the full structured review.

**Copilot-specific note:** In Cursor, skills can be attached with `@skill-name` which shows them in the autocomplete menu. In Copilot, the equivalent is `#file:` with the skill file path. The `#file:` approach is more explicit but less discoverable -- your team should document the skill paths in `copilot-instructions.md` so colleagues know what skills exist and how to reference them.

Use `/pipeline-review` when you want the full procedure executed. Use `#file:` when you want the criteria available while asking a different question.
</details>

---

## Part 5: Apply -- The Integrating Workflow

### Step 5.1: Explore first with a constrained prompt

In Copilot Chat (Agent mode), type the following and press Enter:

```
Do not edit any files. Answer only.

Look at src/ingest.py. Identify the single function that most needs
improvement against our team standards. Name the function, describe
what is wrong with it, and tell me exactly what you would change.
```

Read the full response. The constraint prevents Copilot from making changes while it explores.

**Before removing the constraint and switching to execution mode, write a one-sentence description of what the function does and why the suggested change makes it better.**

> Write your sentence here before continuing. This is the explore-before-changing gate.

<details>
<summary>Why this gate matters in Copilot specifically</summary>

In Cursor, Ask mode enforces the explore-before-changing discipline structurally -- the mode itself prevents edits. In Copilot, the discipline is enforced by the prompt constraint `Do not edit any files. Answer only.`

The risk in Copilot is that without this constraint, Agent mode may begin applying changes immediately. By requiring yourself to write one sentence before removing the constraint, you create the same cognitive gate that Cursor's mode switch creates mechanically.

If you cannot describe in one sentence what the function does and why the change is an improvement, you do not yet understand what you are about to change. Send more constrained exploration prompts before proceeding.
</details>

---

### Step 5.2: Remove the constraint and execute

Open a new Copilot Chat conversation.

Send the following prompt, replacing `[function name]` with the function identified in Step 5.1:

```
Apply the improvements you described to [function name] in src/ingest.py.
Follow the standards in our .github/copilot-instructions.md throughout.
After making the changes, run /pipeline-review on the updated
function and report the remaining issues.
```

Press Enter and watch Copilot work.

When Copilot proposes changes, review the diff in the editor before accepting. Click **Accept** only after reading every changed line.

<details>
<summary>What to look for in the diff</summary>

The diff should show changes corresponding to the instructions in `.github/copilot-instructions.md`:

- Type hints added to all function arguments and the return type
- `pathlib.Path` replacing any `os.path` or raw string paths
- `collections.Counter` replacing any manual dict counting
- `logger.info` calls added at function entry and exit
- `None` checks added on critical fields

If the diff shows changes that are not explained by your instructions file, read each one and ask Copilot to explain before accepting.
</details>

**Write down your answer before continuing:**

> What specific changes did Copilot make? Which of the copilot-instructions.md standards are visible in the diff? What did /pipeline-review report as remaining issues?

---

### Step 5.3: Capture learning as an instruction

If `/pipeline-review` flagged anything as Critical or Warning that your `.github/copilot-instructions.md` does not already cover, open `copilot-instructions.md` now.

Add one new instruction addressing the gap. Write it as a direct instruction to the agent.

Save the file.

> If pipeline-review found nothing that copilot-instructions.md did not already cover, your instructions file is well-calibrated for this function. Note that in the debrief -- it is a valid and good outcome.

---

## Lab Debrief

Write answers to these prompts before the room debrief begins. You will share one answer with the group.

---

**Question 1**

In Step 1.2 you used a prompt constraint to simulate read-only exploration, then removed it. What was the most significant behavioral difference you observed? How does this compare to what Cursor's Ask mode provides structurally?

---

**Question 2**

In Step 2.3 you verified that `.github/copilot-instructions.md` changed Copilot output. What specific code construct changed? Name the before and after explicitly.

---

**Question 3**

In Step 4.4 you used `/pipeline-review` and also referenced the skill file via `#file:`. In your own words, when would you use each approach in your daily work?

---

**Question 4**

In Step 3.2 you added an instruction to `perl-conversion.instructions.md`. What instruction did you add? Why does your team need it and why was it not already in the file?

---

## Instructor Notes

> This section is for instructors only and is not distributed to participants.

**Coverage gaps acknowledged in this lab:**

- No named Ask/Plan/Debug modes in Copilot. The prompt-constraint approach in Steps 1.2 and 5.1 is the documented substitute. Participants should leave understanding why this matters, not just that it is different.
- No context ring. Copilot does not surface token usage. This is not taught as a missing feature in this lab -- it is simply not present and does not affect the learning objectives.
- Skill invocation via `#file:` is less discoverable than Cursor's `@skill-name` autocomplete. Document skill paths in `copilot-instructions.md` for real team deployments.

**Copilot-specific advantages to highlight during delivery:**

- `.github/skills/` automatically extends Copilot code review on GitHub.com PRs. This is a meaningful advantage over Cursor skills for teams using GitHub as their SCM.
- No frontmatter required for always-on instructions. Simpler authoring than Cursor's YAML-gated rules.
- `/create-skill` is identical to Cursor's command. Participants who have done the Cursor lab will find this immediately familiar.

**Verification gaps requiring instructor test run before delivery:**

- `/create-skill` question flow: run the exact prompt in Step 4.1 on the delivery VS Code build with the Copilot extension and record the actual questions shown.
- `#file:` skill invocation: confirm that attaching `.github/skills/pipeline-review/SKILL.md` via `#file:` makes the skill criteria available to Copilot in the response.
- `applyTo:` activation: confirm that `perl-conversion.instructions.md` activates when a `.pl` file is referenced. Test by attaching `#file:perl/ingest.pl` and confirming the conversion instructions appear in the response.

**Starter file dependencies:**

The `copilot-starters/lab1/` directory must contain:
- `.github/copilot-instructions.md` (empty except for an optional `# DE Team Coding Standards` header)
- `.github/instructions/perl-conversion.instructions.md` (pre-built with five rules and `applyTo: "**/*.pl,**/*.py"` frontmatter)
- `.github/skills/.gitkeep`
- `.github/prompts/.gitkeep`

The copy command in Step 0 must work from the `sample_pipeline/` project root without requiring any additional directory creation by participants.
