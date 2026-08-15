import type { Seance } from "../services/api_client";

// Encodage visuel d'intensité RELATIVE aux séances affichées dans la liste courante —
// purement présentationnel (pas le moteur de charge d'entraînement du backend,
// cf. research.md Decision 4 / Principe IV : aucune logique d'analyse dupliquée ici).
const PALIERS = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#184f95"]; // --sequential-100..600

export function scoreIntensiteApproximatif(seance: Seance): number {
  const dureeH = seance.duree_secondes / 3600;
  if (seance.puissance_moyenne_watts) return dureeH * seance.puissance_moyenne_watts;
  if (seance.frequence_cardiaque_moyenne) return dureeH * seance.frequence_cardiaque_moyenne;
  return dureeH * 100;
}

export default function SeanceIntensiteBar({
  seance,
  scoreMax,
}: {
  seance: Seance;
  scoreMax: number;
}) {
  const ratio = scoreMax > 0 ? scoreIntensiteApproximatif(seance) / scoreMax : 0;
  const palier = Math.min(PALIERS.length - 1, Math.floor(ratio * PALIERS.length));
  const largeurPct = Math.max(8, Math.round(ratio * 100));

  return (
    <div
      title="Intensité relative de la séance"
      style={{
        width: 60,
        height: 8,
        background: "var(--gridline)",
        borderRadius: 4,
        overflow: "hidden",
      }}
    >
      <div style={{ width: `${largeurPct}%`, height: "100%", background: PALIERS[palier] }} />
    </div>
  );
}
