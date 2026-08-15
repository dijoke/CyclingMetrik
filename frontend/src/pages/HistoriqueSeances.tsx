import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import SeanceIntensiteBar, { scoreIntensiteApproximatif } from "../components/SeanceIntensiteBar";
import StatusBadge from "../components/StatusBadge";
import { type Seance, type StatutDonneesSeance, api } from "../services/api_client";

const BADGE_STATUT: Record<string, { label: string } | undefined> = {
  aberrant: { label: "Données aberrantes" },
  doublon_probable: { label: "Doublon probable" },
};

type CleTri =
  | "date_debut"
  | "duree_secondes"
  | "distance_metres"
  | "denivele_metres"
  | "puissance_moyenne_watts"
  | "puissance_max_1min"
  | "puissance_max_3min"
  | "puissance_max_5min"
  | "puissance_max_10min"
  | "puissance_max_20min";

const COLONNES_TRIABLES: { cle: CleTri; label: string }[] = [
  { cle: "date_debut", label: "Date" },
  { cle: "duree_secondes", label: "Durée" },
  { cle: "distance_metres", label: "Distance" },
  { cle: "puissance_moyenne_watts", label: "Puissance moy." },
  { cle: "denivele_metres", label: "Dénivelé" },
];

const COLONNES_RECORDS: { cle: CleTri; label: string }[] = [
  { cle: "puissance_max_1min", label: "Max 1'" },
  { cle: "puissance_max_3min", label: "Max 3'" },
  { cle: "puissance_max_5min", label: "Max 5'" },
  { cle: "puissance_max_10min", label: "Max 10'" },
  { cle: "puissance_max_20min", label: "Max 20'" },
];

function valeurTri(seance: Seance, cle: CleTri): number {
  if (cle === "date_debut") return new Date(seance.date_debut).getTime();
  return seance[cle] ?? -Infinity;
}

export default function HistoriqueSeances() {
  const navigate = useNavigate();
  const { data: seances, isLoading } = useQuery({
    queryKey: ["seances"],
    queryFn: api.seances.lister,
  });

  const [triCle, setTriCle] = useState<CleTri>("date_debut");
  const [triDesc, setTriDesc] = useState(true);
  const [filtreStatut, setFiltreStatut] = useState<StatutDonneesSeance | "tous">("tous");
  const [filtreDepuis, setFiltreDepuis] = useState("");
  const [filtreJusqua, setFiltreJusqua] = useState("");

  const seancesFiltreesEtTriees = useMemo(() => {
    if (!seances) return [];
    let resultat = seances;
    if (filtreStatut !== "tous") {
      resultat = resultat.filter((s) => s.statut_donnees === filtreStatut);
    }
    if (filtreDepuis) {
      const depuis = new Date(filtreDepuis).getTime();
      resultat = resultat.filter((s) => new Date(s.date_debut).getTime() >= depuis);
    }
    if (filtreJusqua) {
      const jusqua = new Date(filtreJusqua).getTime();
      resultat = resultat.filter((s) => new Date(s.date_debut).getTime() <= jusqua);
    }
    return [...resultat].sort((a, b) => {
      const diff = valeurTri(a, triCle) - valeurTri(b, triCle);
      return triDesc ? -diff : diff;
    });
  }, [seances, triCle, triDesc, filtreStatut, filtreDepuis, filtreJusqua]);

  if (isLoading) return <p>Chargement…</p>;
  if (!seances?.length) return <p>Aucune séance importée pour le moment.</p>;

  const scoreMax = Math.max(...seances.map(scoreIntensiteApproximatif));

  function trierPar(cle: CleTri) {
    if (cle === triCle) {
      setTriDesc((d) => !d);
    } else {
      setTriCle(cle);
      setTriDesc(true);
    }
  }

  const filtresActifs = filtreStatut !== "tous" || filtreDepuis || filtreJusqua;

  return (
    <section>
      <h2 style={{ color: "var(--text-primary)" }}>Historique des séances</h2>

      <div style={{ display: "flex", gap: "1rem", alignItems: "end", flexWrap: "wrap", marginBottom: "1rem" }}>
        <label
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "0.25rem",
            color: "var(--text-secondary)",
            fontSize: "0.85rem",
          }}
        >
          Statut
          <select
            value={filtreStatut}
            onChange={(e) => setFiltreStatut(e.target.value as StatutDonneesSeance | "tous")}
          >
            <option value="tous">Tous</option>
            <option value="valide">Valide</option>
            <option value="aberrant">Données aberrantes</option>
            <option value="doublon_probable">Doublon probable</option>
          </select>
        </label>
        <label
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "0.25rem",
            color: "var(--text-secondary)",
            fontSize: "0.85rem",
          }}
        >
          Depuis
          <input type="date" value={filtreDepuis} onChange={(e) => setFiltreDepuis(e.target.value)} />
        </label>
        <label
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "0.25rem",
            color: "var(--text-secondary)",
            fontSize: "0.85rem",
          }}
        >
          Jusqu'au
          <input type="date" value={filtreJusqua} onChange={(e) => setFiltreJusqua(e.target.value)} />
        </label>
        {filtresActifs && (
          <button
            type="button"
            onClick={() => {
              setFiltreStatut("tous");
              setFiltreDepuis("");
              setFiltreJusqua("");
            }}
          >
            Réinitialiser les filtres
          </button>
        )}
        <span style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>
          {seancesFiltreesEtTriees.length} / {seances.length} séances
        </span>
      </div>

      <div style={{ overflowX: "auto" }}>
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
              {COLONNES_TRIABLES.map((colonne) => (
                <th
                  key={colonne.cle}
                  style={{ cursor: "pointer", userSelect: "none", whiteSpace: "nowrap" }}
                  onClick={() => trierPar(colonne.cle)}
                >
                  {colonne.label} {triCle === colonne.cle ? (triDesc ? "▼" : "▲") : ""}
                </th>
              ))}
              <th>FC moy.</th>
              {COLONNES_RECORDS.map((colonne) => (
                <th
                  key={colonne.cle}
                  style={{ cursor: "pointer", userSelect: "none", whiteSpace: "nowrap" }}
                  onClick={() => trierPar(colonne.cle)}
                >
                  {colonne.label} {triCle === colonne.cle ? (triDesc ? "▼" : "▲") : ""}
                </th>
              ))}
              <th></th>
            </tr>
          </thead>
          <tbody>
            {seancesFiltreesEtTriees.map((seance) => {
              const badge = BADGE_STATUT[seance.statut_donnees];
              return (
                <tr
                  key={seance.id}
                  onClick={() => navigate(`/seances/${seance.id}`)}
                  style={{ borderBottom: "1px solid var(--gridline)", cursor: "pointer" }}
                >
                  <td style={{ padding: "0.5rem 0.5rem 0.5rem 0" }}>
                    <SeanceIntensiteBar seance={seance} scoreMax={scoreMax} />
                  </td>
                  <td>{new Date(seance.date_debut).toLocaleString("fr-FR")}</td>
                  <td>{Math.round(seance.duree_secondes / 60)} min</td>
                  <td>{seance.distance_metres ? `${(seance.distance_metres / 1000).toFixed(1)} km` : "—"}</td>
                  <td>
                    {seance.puissance_moyenne_watts ? `${Math.round(seance.puissance_moyenne_watts)} W` : "—"}
                  </td>
                  <td>{seance.denivele_metres ? `${Math.round(seance.denivele_metres)} m` : "—"}</td>
                  <td>{seance.frequence_cardiaque_moyenne ? `${seance.frequence_cardiaque_moyenne} bpm` : "—"}</td>
                  {COLONNES_RECORDS.map((colonne) => (
                    <td key={colonne.cle}>
                      {seance[colonne.cle] !== null ? `${Math.round(seance[colonne.cle] as number)} W` : "—"}
                    </td>
                  ))}
                  <td>{badge && <StatusBadge tone="warning" label={badge.label} />}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}
