# appli-web-coaching

Démo Spec-Driven Development (méthode [Spec Kit](https://github.com/github/spec-kit)) pour une application web de coaching cyclisme : import des séances (Garmin Connect / Strava / Nolio), analyse de la charge d'entraînement, conseils de récupération et de nutrition.

## Ce qui a été mis en place

- `.specify/memory/constitution.md` — les principes du projet (v1.0.0), déjà rédigés (sécurité de l'athlète avant tout, confidentialité des données, MVP incrémental, test-first, simplicité).
- `.specify/templates/` — les templates officiels Spec Kit (spec, plan, tasks, checklist, constitution).
- `.specify/scripts/bash/` — les scripts d'automatisation officiels (résolution de chemins, création de feature, setup plan/tasks).
- `.claude/commands/speckit.*.md` — les slash commands Spec Kit pour Claude Code (`/speckit.constitution`, `/speckit.specify`, `/speckit.plan`, `/speckit.tasks`, `/speckit.implement`).
- `specs/001-coaching-velo-garmin-strava/spec.md` — la première spécification, déjà rédigée avec 3 user stories priorisées (P1 import, P2 analyse de charge, P3 conseils récup/nutrition), avec son checklist qualité dans `checklists/requirements.md`.

## Une limitation technique à savoir

L'environnement sandboxé de cette session bloque les installations réseau (pip/npm/git clone) vers GitHub et PyPI — impossible d'installer le vrai CLI `specify` ici. À la place, j'ai récupéré les templates et scripts **officiels** du dépôt `github/spec-kit` via HTTP et reconstruit à la main un scaffold identique à celui que produit `specify init --ai claude`. Le contenu est fidèle à l'original, mais je n'ai pas pu exécuter `specify` lui-même pour le générer automatiquement.

Le dossier `.git` a aussi posé problème (le point de montage entre ce sandbox et ton Mac ne permet pas certaines opérations git). Si tu veux un historique git propre, le plus simple est de supprimer `.git` depuis le Finder/Terminal sur ton Mac puis de relancer `git init` localement.

## Pour continuer avec Claude Code (recommandé)

1. Installe le vrai CLI si tu veux garder le projet à jour ou ajouter d'autres agents/extensions :
   ```bash
   uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
   ```
2. Ouvre ce dossier avec Claude Code (`claude` dans le terminal, depuis `appli-web-coaching/`).
3. Les commandes `/speckit.*` sont déjà disponibles (dossier `.claude/commands/`). Prochaine étape logique :
   ```
   /speckit.clarify
   ```
   pour trancher les 2 points encore ouverts dans le spec (durée de rétention des données, cadre réglementaire — RGPD ?), puis :
   ```
   /speckit.plan
   /speckit.tasks
   /speckit.implement
   ```

## Workflow Spec Kit

```
/speckit.constitution   → principes du projet (déjà fait, v1.0.0)
/speckit.specify        → décrire une feature (déjà fait pour la v1)
/speckit.clarify        → lever les [NEEDS CLARIFICATION] restants
/speckit.plan           → choix techniques (stack, architecture)
/speckit.tasks          → découpage en tâches actionnables
/speckit.implement      → exécution des tâches
```
