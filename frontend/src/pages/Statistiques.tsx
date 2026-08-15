import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import Card from "../components/Card";
import VolumeBarChart from "../components/VolumeBarChart";
import { type SeanceResume, api } from "../services/api_client";

const NOMS_MOIS = [
  "Janvier",
  "Février",
  "Mars",
  "Avril",
  "Mai",
  "Juin",
  "Juillet",
  "Août",
  "Septembre",
  "Octobre",
  "Novembre",
  "Décembre",
];

function formaterKm(metres: number) {
  return `${(metres / 1000).toFixed(0)} km`;
}

function formaterHeures(secondes: number) {
  return `${(secondes / 3600).toFixed(0)} h`;
}

function formaterDate(date: string) {
  return new Date(date).toLocaleDateString("fr-FR", { day: "2-digit", month: "short", year: "numeric" });
}

function CarteRecord({ titre, seance, valeur }: { titre: string; seance: SeanceResume | null; valeur: string }) {
  return (
    <Card tone={seance ? "default" : "muted"} style={{ minWidth: 200 }}>
      <div style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>{titre}</div>
      {seance ? (
        <>
          <div style={{ fontSize: "1.4rem", fontWeight: 600, color: "var(--text-primary)", marginTop: "0.25rem" }}>
            {valeur}
          </div>
          <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>{formaterDate(seance.date_debut)}</div>
        </>
      ) : (
        <div style={{ marginTop: "0.25rem" }}>Aucune donnée</div>
      )}
    </Card>
  );
}

export default function Statistiques() {
  const { data: annuelles, isLoading: chargementAnnuelles } = useQuery({
    queryKey: ["statistiques", "annuelles"],
    queryFn: api.statistiques.annuelles,
  });
  const { data: records, isLoading: chargementRecords } = useQuery({
    queryKey: ["statistiques", "records"],
    queryFn: api.statistiques.records,
  });
  const { data: comparaison, isLoading: chargementComparaison } = useQuery({
    queryKey: ["statistiques", "comparaison"],
    queryFn: api.statistiques.comparaisonAnnuelle,
  });

  const [anneeSelectionnee, setAnneeSelectionnee] = useState<number | null>(null);
  const annee = anneeSelectionnee ?? annuelles?.at(-1)?.annee ?? null;

  const { data: mensuelles } = useQuery({
    queryKey: ["statistiques", "mensuelles", annee],
    queryFn: () => api.statistiques.mensuelles(annee as number),
    enabled: annee !== null,
  });

  if (chargementAnnuelles || chargementRecords || chargementComparaison) return <p>Chargement…</p>;

  return (
    <section>
      <h2 style={{ color: "var(--text-primary)" }}>Statistiques</h2>

      {annuelles && annuelles.length > 0 ? (
        <>
          <h3 style={{ color: "var(--text-primary)" }}>Volume par année</h3>
          <VolumeBarChart
            donnees={annuelles.map((s) => ({ etiquette: String(s.annee), distanceKm: s.distance_metres / 1000 }))}
          />

          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginTop: "1.5rem" }}>
            <label htmlFor="annee-select" style={{ color: "var(--text-secondary)" }}>
              Détail mensuel :
            </label>
            <select
              id="annee-select"
              value={annee ?? ""}
              onChange={(evenement) => setAnneeSelectionnee(Number(evenement.target.value))}
            >
              {annuelles.map((s) => (
                <option key={s.annee} value={s.annee}>
                  {s.annee}
                </option>
              ))}
            </select>
          </div>

          {mensuelles && (
            <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "1rem" }}>
              <thead>
                <tr style={{ textAlign: "left", borderBottom: "1px solid var(--gridline)", color: "var(--text-secondary)" }}>
                  <th>Mois</th>
                  <th>Distance</th>
                  <th>Dénivelé</th>
                  <th>Durée</th>
                  <th>Séances</th>
                </tr>
              </thead>
              <tbody>
                {mensuelles.map((s) => (
                  <tr key={s.mois} style={{ borderBottom: "1px solid var(--gridline)" }}>
                    <td>{NOMS_MOIS[s.mois - 1]}</td>
                    <td>{formaterKm(s.distance_metres)}</td>
                    <td>{s.denivele_metres.toFixed(0)} m</td>
                    <td>{formaterHeures(s.duree_secondes)}</td>
                    <td>{s.nb_seances}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </>
      ) : (
        <Card tone="muted">Aucune séance importée pour le moment.</Card>
      )}

      <h3 style={{ color: "var(--text-primary)", marginTop: "2rem" }}>Records personnels</h3>
      <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
        <CarteRecord
          titre="Plus longue distance"
          seance={records?.plus_longue_distance ?? null}
          valeur={records?.plus_longue_distance ? formaterKm(records.plus_longue_distance.distance_metres!) : ""}
        />
        <CarteRecord
          titre="Plus de dénivelé"
          seance={records?.plus_de_denivele ?? null}
          valeur={records?.plus_de_denivele ? `${records.plus_de_denivele.denivele_metres!.toFixed(0)} m` : ""}
        />
        <CarteRecord
          titre="Plus longue durée"
          seance={records?.plus_longue_duree ?? null}
          valeur={records?.plus_longue_duree ? formaterHeures(records.plus_longue_duree.duree_secondes) : ""}
        />
        <CarteRecord
          titre="Puissance moyenne max"
          seance={records?.puissance_moyenne_max ?? null}
          valeur={
            records?.puissance_moyenne_max ? `${records.puissance_moyenne_max.puissance_moyenne_watts!.toFixed(0)} W` : ""
          }
        />
      </div>

      <h3 style={{ color: "var(--text-primary)", marginTop: "2rem" }}>Comparaison année sur année</h3>
      {comparaison && (
        <Card style={{ display: "flex", gap: "2rem" }}>
          <div>
            <div style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
              {comparaison.annee_courante.annee} (depuis le 1er janvier)
            </div>
            <div style={{ fontSize: "1.4rem", fontWeight: 600, color: "var(--text-primary)" }}>
              {formaterKm(comparaison.annee_courante.distance_metres)}
            </div>
            <div style={{ color: "var(--text-muted)" }}>{comparaison.annee_courante.nb_seances} séances</div>
          </div>
          {comparaison.annee_precedente ? (
            <div>
              <div style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                {comparaison.annee_precedente.annee} (même période)
              </div>
              <div style={{ fontSize: "1.4rem", fontWeight: 600, color: "var(--text-primary)" }}>
                {formaterKm(comparaison.annee_precedente.distance_metres)}
              </div>
              <div style={{ color: "var(--text-muted)" }}>{comparaison.annee_precedente.nb_seances} séances</div>
            </div>
          ) : (
            <div style={{ color: "var(--text-secondary)" }}>
              Pas de données pour la même période l'année précédente.
            </div>
          )}
        </Card>
      )}
    </section>
  );
}
