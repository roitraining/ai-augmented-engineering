---
name: rework-commits
description: Reorganises the commit history on the current branch into clean, semantic commits. Resets to main, reads all changes, plans a logical commit sequence, creates commits with descriptive messages, and verifies the final diff matches the original branch exactly.
---

Reorganise the commit history on this branch into clean, semantic commits.

Follow these steps exactly in this order:

1. Run: git log --oneline main..HEAD
   Read the current commit list so you understand what work was done.

2. Run: git diff main > /tmp/original_diff.patch
   Save the complete diff against main before making any changes.

3. Run: git reset --soft main
   This preserves all changes in the staging area while removing the commits.
   Do not use --hard. Do not lose any changes.

4. Run: git diff --cached --stat
   Confirm all modified files are staged. If any files are missing, stop and
   report which files are not staged before continuing.

5. Plan a logical commit sequence. Each commit must:
   - Contain one coherent change with a single clear purpose
   - Have a commit message in the format: <type>(<scope>): <description>
     where type is one of: feat, fix, test, refactor, docs, chore
   - Be orderable so earlier commits do not depend on later ones

   Required ordering for Perl conversion work:
   - tests/ files must be committed BEFORE any src/ implementation files
   - docs/ files (pipeline-map.md, conversion-plan.md) should come first
   - The Debug mode fix commit message must explain the root cause

6. Create each commit in sequence using git add <specific files> and git commit.
   Do not use git add -A for the entire working tree in one commit.

7. After all commits are created, run:
   git diff main > /tmp/final_diff.patch
   diff /tmp/original_diff.patch /tmp/final_diff.patch

   If the diff of diffs is not empty, stop and report what changed.
   The final diff against main must be byte-identical to the original.

8. Run: git log --oneline main..HEAD
   Report the final commit list.
