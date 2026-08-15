<!-- SPECKIT START -->
## Active Specification

No plan generated yet. Run `/speckit.plan` after `/speckit.specify` to populate this section.
<!-- SPECKIT END -->

# appli-web-coaching

Application web de coaching pour cyclisme de compétition : import des séances (Garmin Connect / Strava / Nolio), analyse de charge d'entraînement, et conseils personnalisés (récupération, nutrition, apports).

This project uses [Spec-Driven Development](https://github.com/github/spec-kit) via Spec Kit. Use the `/speckit.*` slash commands (see `.claude/commands/`) to drive development:

1. `/speckit.constitution` — define project principles
2. `/speckit.specify` — describe a feature (what/why)
3. `/speckit.plan` — define the technical approach
4. `/speckit.tasks` — break the plan into tasks
5. `/speckit.implement` — execute the tasks

## Git Workflow

Remote: `https://github.com/dijoke/CyclingMetrik` (origin).

- `main` holds only the shared Spec Kit scaffold and completed/merged features. Never commit feature work directly to `main` — always work on a feature branch.
- Each feature gets its own branch named after its `specs/` directory (e.g. `001-coaching-velo-garmin-strava`), matching the branch `.specify/scripts/bash/create-new-feature.sh` creates.
- Commit in small logical increments — e.g. after each completed `tasks.md` task or small group of related tasks — not one giant commit at the end of a session.
- Push the current feature branch to `origin` regularly (at minimum: after `/speckit.plan`, after `/speckit.tasks`, and after every few completed tasks during `/speckit.implement`) so work isn't left local-only.
- Merge a feature branch into `main` via a pull request once its user stories are validated (per its `quickstart.md`) — don't push straight to `main`.
