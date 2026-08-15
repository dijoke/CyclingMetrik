---
description: Generate an actionable, dependency-ordered tasks.md for the feature based on available design artifacts.
scripts:
  sh: .specify/scripts/bash/setup-tasks.sh --json
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

1. **Setup**: Run `.specify/scripts/bash/setup-tasks.sh --json` from repo root and parse FEATURE_DIR, TASKS_TEMPLATE, AVAILABLE_DOCS.

2. **Load design documents**: Read plan.md (required), spec.md (required), and any of data-model.md, contracts/, research.md, quickstart.md that exist.

3. **Execute task generation workflow**:
   - Load plan.md and extract tech stack, libraries, project structure
   - Load spec.md and extract user stories with priorities (P1, P2, P3...)
   - Map entities/contracts/decisions to the relevant user story
   - Generate tasks organized by user story (see Task Generation Rules below)
   - Generate dependency graph and parallel execution examples per user story
   - Validate task completeness (each user story independently testable)

4. **Generate tasks.md** using `.specify/templates/tasks-template.md` as structure. Fill with:
   - Phase 1: Setup tasks
   - Phase 2: Foundational tasks (blocking prerequisites)
   - Phase 3+: One phase per user story (priority order from spec.md)
   - Final Phase: Polish & cross-cutting concerns

5. **Report**: Output path to tasks.md, total task count, task count per story, parallel opportunities, suggested MVP scope.

## Task Generation Rules

**CRITICAL**: Tasks MUST be organized by user story to enable independent implementation and testing.

**Tests are OPTIONAL**: Only generate test tasks if explicitly requested in the feature specification or if user requests TDD.

### Checklist Format (REQUIRED)

```text
- [ ] [TaskID] [P?] [Story?] Description with file path
```

- **Checkbox**: ALWAYS `- [ ]`
- **Task ID**: Sequential (T001, T002...)
- **[P] marker**: Only if parallelizable (different files, no dependencies on incomplete tasks)
- **[Story] label**: REQUIRED for user story phase tasks only (e.g. [US1]); NOT used in Setup/Foundational/Polish

### Phase Structure

- **Phase 1**: Setup (project initialization)
- **Phase 2**: Foundational (blocking prerequisites - MUST complete before user stories)
- **Phase 3+**: User Stories in priority order (P1, P2, P3...)
- **Final Phase**: Polish & Cross-Cutting Concerns
