---
description: Create or update the feature specification from a natural language feature description.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

The text the user typed after `/speckit.specify` in the triggering message **is** the feature description. Assume you always have it available in this conversation even if `{ARGS}` appears literally below. Do not ask the user to repeat it unless they provided an empty command.

Given that feature description, do this:

1. **Generate a concise short name** (2-4 words) for the feature.

2. **Create the spec feature directory**: Specs live under `specs/`.
   - `mkdir -p specs/<NNN>-<short-name>`
   - Copy `.specify/templates/spec-template.md` to `specs/<NNN>-<short-name>/spec.md`

3. Load `.specify/templates/spec-template.md` to understand required sections.

4. Follow this execution flow:
    1. Parse user description from arguments. If empty: ERROR "No feature description provided"
    2. Extract key concepts from description: actors, actions, data, constraints
    3. For unclear aspects: make informed guesses based on context and industry standards. Only mark with [NEEDS CLARIFICATION: specific question] if the choice significantly impacts scope/UX, multiple reasonable interpretations exist, or no reasonable default exists. LIMIT: max 3 markers.
    4. Fill User Scenarios & Testing section
    5. Generate Functional Requirements (each testable)
    6. Define Success Criteria (measurable, technology-agnostic)
    7. Identify Key Entities (if data involved)
    8. Return: SUCCESS (spec ready for planning)

5. Write the specification to the spec file using the template structure, replacing placeholders with concrete details derived from the feature description, preserving section order and headings.

6. **Specification Quality Validation**: After writing the initial spec, validate it against quality criteria and generate a checklist at `specs/<NNN>-<short-name>/checklists/requirements.md`.

7. **Report completion** to the user with the feature directory path, spec file path, and readiness for the next phase (`/speckit.plan`).

## Quick Guidelines

- Focus on **WHAT** users need and **WHY**.
- Avoid HOW to implement (no tech stack, APIs, code structure).
- Written for business stakeholders, not developers.
- DO NOT create any checklists that are embedded in the spec. That will be a separate command.

### For AI Generation

1. **Make informed guesses**: Use context, industry standards, and common patterns to fill gaps
2. **Document assumptions**: Record reasonable defaults in the Assumptions section
3. **Limit clarifications**: Maximum 3 [NEEDS CLARIFICATION] markers - use only for critical decisions
4. **Prioritize clarifications**: scope > security/privacy > user experience > technical details
5. **Think like a tester**: Every vague requirement should fail the "testable and unambiguous" checklist item

### Success Criteria Guidelines

Success criteria must be measurable, technology-agnostic, user-focused, and verifiable without implementation details.
