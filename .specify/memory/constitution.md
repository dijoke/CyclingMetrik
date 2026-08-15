<!--
Sync Impact Report
Version change: N/A → 1.0.0 (initial ratification)
Modified principles: N/A (initial version)
Added sections: Core Principles (5), Contraintes & Confidentialité, Workflow de développement, Governance
Removed sections: none
Templates requiring updates:
  - ✅ .specify/templates/plan-template.md (Constitution Check section is generic, compatible)
  - ✅ .specify/templates/spec-template.md (no changes required)
  - ✅ .specify/templates/tasks-template.md (no changes required)
Follow-up TODOs: none
-->

# appli-web-coaching Constitution

## Core Principles

### I. Athlete Safety Over Cleverness (NON-NEGOTIABLE)
Aucune recommandation de récupération ou de nutrition ne DOIT être affichée sans données suffisantes pour la fonder. En cas de doute ou de données manquantes, le système DOIT afficher un message indiquant l'absence de recommandation plutôt qu'une estimation non fiable. Toute recommandation DOIT rester explicable : l'athlète peut voir sur quelles données elle s'appuie. Le produit fournit des estimations informatives, jamais des prescriptions médicales ou diététiques individualisées.

### II. Data-First & Privacy by Design
Les données d'entraînement et de santé de l'athlète (séances, poids, fréquence cardiaque) sont sensibles. Aucun identifiant de plateforme tierce (Garmin, Strava, Nolio) n'est stocké en clair ; les flux d'autorisation utilisent les mécanismes standard (OAuth ou équivalent) de chaque plateforme. L'athlète DOIT pouvoir consulter, exporter et supprimer ses données à tout moment.

### III. MVP Incrémental par User Story
Chaque fonctionnalité est découpée en user stories indépendamment livrables et testables (import de séances → analyse de charge → conseils). Aucune story de priorité inférieure ne DOIT bloquer la livraison d'une story de priorité supérieure. On valide et on démontre chaque story avant de passer à la suivante.

### IV. Test-First sur la logique d'analyse
Toute logique de calcul (charge d'entraînement, agrégation de séances, génération de recommandations) DOIT être couverte par des tests écrits avant l'implémentation. Les intégrations avec les APIs externes (Garmin Connect, Strava, Nolio) DOIVENT avoir des tests de contrat pour détecter les changements de format de données en amont.

### V. Simplicité & Dette Justifiée
On préfère la solution la plus simple qui satisfait la user story courante. Toute complexité additionnelle (nouvelle dépendance, nouveau service, abstraction supplémentaire) DOIT être justifiée explicitement dans le plan technique (section Complexity Tracking) — sinon elle est refusée.

## Contraintes & Confidentialité

- Les données de santé/entraînement ne sont jamais partagées avec un tiers sans consentement explicite de l'athlète.
- Les clés et secrets d'intégration (API Garmin/Strava/Nolio) sont gérés via variables d'environnement / secret manager, jamais commités dans le dépôt.
- La plateforme cible de la v1 est le web ; le mobile natif est hors périmètre tant qu'il n'est pas explicitement priorisé.

## Workflow de développement

- Chaque feature suit le cycle Spec Kit : `/speckit.specify` → `/speckit.clarify` (si besoin) → `/speckit.plan` → `/speckit.tasks` → `/speckit.implement`.
- Toute story touchant à la génération de recommandations (récupération/nutrition) DOIT être revue au regard du Principe I avant merge.
- Les tâches de type "polish" (perf, refactor) ne DOIVENT pas retarder la livraison de la story P1 en cours.

## Governance

Cette constitution prévaut sur toute autre pratique ou préférence individuelle. Toute modification DOIT être documentée dans ce fichier avec un Sync Impact Report, et propagée aux templates (`spec-template.md`, `plan-template.md`, `tasks-template.md`) si elle affecte leurs exigences. Les revues de plan (`/speckit.plan`) DOIVENT vérifier la conformité au Principe I (Athlete Safety) et au Principe II (Data-First & Privacy) avant de passer en phase d'implémentation.

**Version**: 1.0.0 | **Ratified**: 2026-08-15 | **Last Amended**: 2026-08-15
