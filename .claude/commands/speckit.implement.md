---
description: Execute the implementation plan by processing and executing all tasks defined in tasks.md
scripts:
  sh: .specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

1. Run `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks` from repo root and parse FEATURE_DIR and AVAILABLE_DOCS.

2. **Check checklists status** (if FEATURE_DIR/checklists/ exists): count total/completed/incomplete items per checklist, show a status table. If any checklist is incomplete, STOP and ask whether to proceed anyway.

3. Load and analyze the implementation context: tasks.md (required), plan.md (required), and any of data-model.md, contracts/, research.md, .specify/memory/constitution.md, quickstart.md that exist.

4. **Project Setup Verification**: create/verify ignore files (.gitignore etc.) based on the detected tech stack.

5. Parse tasks.md structure: phases, dependencies, task details (ID, description, file paths, [P] markers).

6. Execute implementation following the task plan:
   - Phase-by-phase execution, respecting dependencies
   - Parallel tasks [P] may run together; tasks touching the same file run sequentially
   - Follow TDD if tests were requested (tests before implementation)
   - Validate each phase completion before proceeding

7. Progress tracking: report progress after each completed task, halt on non-parallel task failure, mark completed tasks as `[X]` in tasks.md.

8. Completion validation: verify all required tasks completed, implementation matches spec, tests pass, plan followed. Report final status.

Note: This command assumes a complete task breakdown exists in tasks.md. If tasks are incomplete or missing, suggest running `/speckit.tasks` first.
