import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import Card from "../components/Card";
import StatusBadge from "../components/StatusBadge";
import { api } from "../services/api_client";

const LABEL_STATUT: Record<string, { label: string } | undefined> = {
  aberrant: { label: "Données aberrantes" },
  doublon_probable: { label: "Doublon probable" },
};

const DUREES_RECORD: { cle: "puissance_max_1min" | "puissance_max_3min" | "puissance_max_5min" | "puissance_max_10min" | "puissance_max_20min"; label: string }[] = [
  { cle: "puissance_max_1min", label: "1 min" },
  { cle: "puissance_max_3min", label: "3 min" },
  { cle: "puissance_max_5min", label: "5 min" },
  { cle: "puissance_max_10min", label: "10 min" },
  { cle: "puissance_max_20min", label: "20 min" },
];

function Champ({ titre, valeur }: { titre: string; valeur: string }) {
  return (
    <div>
      <div style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>{titre}</div>
      <div style={{ fontSize: "1.1rem", color: "var(--text-primary)" }}>{valeur}</div>
    </div>
  );
}

export default function SeanceDetail() {
  const { id } = useParams<{ id: string }>();
  const {
    data: seance,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["seance", id],
    queryFn: () => api.seances.detail(id as string),
    enabled: !!id,
    retry: false,
  });

  if (isLoading) return <p>Chargement…</p>;
  if (isError || !seance) {
    return (
      <section>
        <Card tone="muted">Séance introuvable.</Card>
        <p style={{ marginTop: "1rem" }}>
          <Link to="/seances">← Retour à l'historique</Link>
        </p>
      </section>
    );
  }

  const badge = LABEL_STATUT[seance.statut_donnees];
  const auMoinsUnRecord = DUREES_RECORD.some((d) => seance[d.cle] !== null);

  return (
    <section>
      <p>
        <Link to="/seances" style={{ color: "var(--text-secondary)" }}>
          ← Retour à l'historique
        </Link>
      </p>
      <h2 style={{ color: "var(--text-primary)" }}>
        Séance du {new Date(seance.date_debut).toLocaleString("fr-FR")}
      </h2>
      {badge && (
        <div style={{ marginBottom: "1rem" }}>
          <StatusBadge tone="warning" label={badge.label} />
        </div>
      )}

      <Card style={{ display: "flex", gap: "2rem", flexWrap: "wrap" }}>
        <Champ titre="Durée" valeur={`${Math.round(seance.duree_secondes / 60)} min`} />
        <Champ
          titre="Distance"
          valeur={seance.distance_metres ? `${(seance.distance_metres / 1000).toFixed(1)} km` : "—"}
        />
        <Champ titre="Dénivelé" valeur={seance.denivele_metres ? `${Math.round(seance.denivele_metres)} m` : "—"} />
        <Champ
          titre="Puissance moyenne"
          valeur={seance.puissance_moyenne_watts ? `${Math.round(seance.puissance_moyenne_watts)} W` : "—"}
        />
        <Champ
          titre="FC moyenne"
          valeur={seance.frequence_cardiaque_moyenne ? `${seance.frequence_cardiaque_moyenne} bpm` : "—"}
        />
      </Card>

      <h3 style={{ color: "var(--text-primary)", marginTop: "2rem" }}>Records de puissance</h3>
      {auMoinsUnRecord ? (
        <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
          {DUREES_RECORD.map((duree) => (
            <Card key={duree.cle} style={{ minWidth: 120 }}>
              <div style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>{duree.label}</div>
              <div style={{ fontSize: "1.2rem", fontWeight: 600, color: "var(--text-primary)" }}>
                {seance[duree.cle] !== null ? `${Math.round(seance[duree.cle] as number)} W` : "—"}
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <Card tone="muted">
          Aucun record de puissance disponible pour cette séance (pas de capteur de puissance, séance trop
          courte, ou traitement pas encore effectué).
        </Card>
      )}
    </section>
  );
}
