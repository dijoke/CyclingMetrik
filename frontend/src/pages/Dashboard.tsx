import { useQuery } from "@tanstack/react-query";
import type { ReactNode } from "react";
import Card from "../components/Card";
import ChargeIndicator, { STYLE_TENDANCE } from "../components/ChargeIndicator";
import StatusBadge from "../components/StatusBadge";
import TrendChart from "../components/TrendChart";
import { api } from "../services/api_client";

function TuileKpi({ titre, children }: { titre: string; children: ReactNode }) {
  return (
    <Card style={{ minWidth: 200, flex: "1 1 200px" }}>
      <div style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>{titre}</div>
      <div style={{ marginTop: "0.4rem" }}>{children}</div>
    </Card>
  );
}

function VueEnsemble() {
  const { data: charge } = useQuery({
    queryKey: ["dashboard", "charge"],
    queryFn: api.dashboard.charge,
  });
  const { data: comparaison } = useQuery({
    queryKey: ["statistiques", "comparaison"],
    queryFn: api.statistiques.comparaisonAnnuelle,
  });
  const { data: records } = useQuery({
    queryKey: ["statistiques", "records"],
    queryFn: api.statistiques.records,
  });

  const styleCharge = charge?.donnees_suffisantes ? STYLE_TENDANCE[charge.tendance ?? "stable"] : null;

  return (
    <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", marginBottom: "2rem" }}>
      <TuileKpi titre="État de charge">
        {styleCharge ? (
          <StatusBadge tone={styleCharge.tone} label={styleCharge.libelle} />
        ) : (
          <span style={{ color: "var(--text-muted)" }}>Données insuffisantes</span>
        )}
      </TuileKpi>

      <TuileKpi titre={`Volume ${comparaison?.annee_courante.annee ?? ""} (depuis le 1er janvier)`}>
        {comparaison ? (
          <>
            <div style={{ fontSize: "1.3rem", fontWeight: 600, color: "var(--text-primary)" }}>
              {(comparaison.annee_courante.distance_metres / 1000).toFixed(0)} km
            </div>
            <div style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>
              {comparaison.annee_courante.nb_seances} séances
            </div>
          </>
        ) : (
          <span style={{ color: "var(--text-muted)" }}>Chargement…</span>
        )}
      </TuileKpi>

      <TuileKpi titre="Record marquant">
        {records?.plus_longue_distance ? (
          <>
            <div style={{ fontSize: "1.3rem", fontWeight: 600, color: "var(--text-primary)" }}>
              {(records.plus_longue_distance.distance_metres! / 1000).toFixed(0)} km
            </div>
            <div style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>Plus longue distance</div>
          </>
        ) : (
          <span style={{ color: "var(--text-muted)" }}>Aucune donnée</span>
        )}
      </TuileKpi>
    </div>
  );
}

export default function Dashboard() {
  const { data: charge, isLoading } = useQuery({
    queryKey: ["dashboard", "charge"],
    queryFn: api.dashboard.charge,
  });

  if (isLoading || !charge) return <p>Chargement…</p>;

  return (
    <section>
      <h2 style={{ color: "var(--text-primary)" }}>Tableau de bord</h2>
      <VueEnsemble />

      <h3 style={{ color: "var(--text-primary)" }}>Charge d'entraînement</h3>
      <ChargeIndicator charge={charge} />
      {charge.donnees_suffisantes && (
        <div style={{ marginTop: "1.5rem" }}>
          <TrendChart historique={charge.historique} />
        </div>
      )}
    </section>
  );
}
