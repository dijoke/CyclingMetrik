import { useQuery } from "@tanstack/react-query";
import { api } from "../services/api_client";

const LABEL_STATUT: Record<string, string> = {
  valide: "",
  aberrant: "⚠ Données aberrantes",
  doublon_probable: "⚠ Doublon probable",
};

export default function HistoriqueSeances() {
  const { data: seances, isLoading } = useQuery({
    queryKey: ["seances"],
    queryFn: api.seances.lister,
  });

  if (isLoading) return <p>Chargement…</p>;
  if (!seances?.length) return <p>Aucune séance importée pour le moment.</p>;

  return (
    <section>
      <h2>Historique des séances</h2>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ textAlign: "left", borderBottom: "1px solid #e2e2e2" }}>
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
          {seances.map((seance) => (
            <tr key={seance.id} style={{ borderBottom: "1px solid #f0f0f0" }}>
              <td>{new Date(seance.date_debut).toLocaleString("fr-FR")}</td>
              <td>{Math.round(seance.duree_secondes / 60)} min</td>
              <td>{seance.distance_metres ? `${(seance.distance_metres / 1000).toFixed(1)} km` : "—"}</td>
              <td>
                {seance.puissance_moyenne_watts ? `${Math.round(seance.puissance_moyenne_watts)} W` : "—"}
              </td>
              <td>{seance.frequence_cardiaque_moyenne ? `${seance.frequence_cardiaque_moyenne} bpm` : "—"}</td>
              <td>{seance.denivele_metres ? `${Math.round(seance.denivele_metres)} m` : "—"}</td>
              <td style={{ color: "#b42318", fontSize: "0.85rem" }}>{LABEL_STATUT[seance.statut_donnees]}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
