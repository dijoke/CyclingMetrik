import { useQuery } from "@tanstack/react-query";
import SeanceIntensiteBar, { scoreIntensiteApproximatif } from "../components/SeanceIntensiteBar";
import StatusBadge from "../components/StatusBadge";
import { api } from "../services/api_client";

const BADGE_STATUT: Record<string, { label: string } | undefined> = {
  aberrant: { label: "Données aberrantes" },
  doublon_probable: { label: "Doublon probable" },
};

export default function HistoriqueSeances() {
  const { data: seances, isLoading } = useQuery({
    queryKey: ["seances"],
    queryFn: api.seances.lister,
  });

  if (isLoading) return <p>Chargement…</p>;
  if (!seances?.length) return <p>Aucune séance importée pour le moment.</p>;

  const scoreMax = Math.max(...seances.map(scoreIntensiteApproximatif));

  return (
    <section>
      <h2 style={{ color: "var(--text-primary)" }}>Historique des séances</h2>
      <table style={{ width: "100%", borderCollapse: "collapse", color: "var(--text-primary)" }}>
        <thead>
          <tr
            style={{
              textAlign: "left",
              borderBottom: "1px solid var(--gridline)",
              color: "var(--text-secondary)",
              fontSize: "0.9rem",
            }}
          >
            <th style={{ padding: "0.5rem 0.5rem 0.5rem 0" }}>Intensité</th>
            <th>Date</th>
            <th>Durée</th>
            <th>Distance</th>
            <th>Puissance moy.</th>
            <th>FC moy.</th>
            <th>Dénivelé</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {seances.map((seance) => {
            const badge = BADGE_STATUT[seance.statut_donnees];
            return (
              <tr key={seance.id} style={{ borderBottom: "1px solid var(--gridline)" }}>
                <td style={{ padding: "0.5rem 0.5rem 0.5rem 0" }}>
                  <SeanceIntensiteBar seance={seance} scoreMax={scoreMax} />
                </td>
                <td>{new Date(seance.date_debut).toLocaleString("fr-FR")}</td>
                <td>{Math.round(seance.duree_secondes / 60)} min</td>
                <td>{seance.distance_metres ? `${(seance.distance_metres / 1000).toFixed(1)} km` : "—"}</td>
                <td>
                  {seance.puissance_moyenne_watts ? `${Math.round(seance.puissance_moyenne_watts)} W` : "—"}
                </td>
                <td>{seance.frequence_cardiaque_moyenne ? `${seance.frequence_cardiaque_moyenne} bpm` : "—"}</td>
                <td>{seance.denivele_metres ? `${Math.round(seance.denivele_metres)} m` : "—"}</td>
                <td>{badge && <StatusBadge tone="warning" label={badge.label} />}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </section>
  );
}
