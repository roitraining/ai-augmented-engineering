# Instructor Notes — Lab1 Cursor


**Verification gaps requiring instructor test run before delivery:**

- `/create-skill` question flow is dynamic. Run the exact prompt in Step 4.1 on the delivery build and record the actual questions shown. Update Step 4.2 if the question sequence differs.
- Confirm the `@pipeline-review` autocomplete works in the installed Cursor version. If the skill appears under a different path after generation, update Step 4.4.
- Confirm Agent mode is accessible on the client's Cursor plan tier. Free tier does not have full Agent mode.

**Common failure points:**

- `.md` instead of `.mdc` in Step 2.1: walk the room after Step 2.1 and check file extensions before participants reach the verification step.
- YAML frontmatter with smart quotes or extra whitespace: most common source of rules not applying. Check raw file content if a participant reports no change in agent output.
- `@pipeline-review` not appearing in autocomplete: skill was saved to Personal scope instead of Project scope. The file will be at `~/.cursor/skills/pipeline-review/SKILL.md` instead of `.cursor/skills/pipeline-review/SKILL.md`. It can be moved manually.

**What this lab replaces:**

The previous Lab 1 design included Custom Mode configuration as a core task. Custom Mode was removed from Cursor in version 2.1. This design replaces it with confirmed features: mode switching via dropdown and SHIFT+TAB, rules file authoring with the `.mdc` extension, and the `/create-skill` dynamic question flow.
