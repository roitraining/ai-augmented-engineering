# Instructor Notes — Lab1 Copilot


**Coverage gaps acknowledged in this lab:**

- No named Ask/Plan/Debug modes in Copilot. The prompt-constraint approach in Steps 1.2 and 5.1 is the documented substitute. Participants should leave understanding why this matters, not just that it is different.
- No context ring. Copilot does not surface token usage. This is not taught as a missing feature in this lab—it is simply not present and does not affect the learning objectives.
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
