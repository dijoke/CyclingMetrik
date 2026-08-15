import type { ChargeEntrainement } from "../services/api_client";
import Card from "./Card";
import StatusBadge, { type StatusTone } from "./StatusBadge";

const STYLE_TENDANCE: Record<string, { tone: StatusTone; libelle: string }> = {
  surcharge: { tone: "critical", libelle: "Surcharge — repos recommandé" },
  recuperation: { tone: "good", libelle: "Récupération — charge basse" },
  progression: { tone: "good", libelle: "Progression" },
  stable: { tone: "neutral", libelle: "Stable" },
};

export default function ChargeIndicator({ charge }: { charge: ChargeEntrainement }) {
  if (!charge.donnees_suffisantes) {
    return (
      <Card tone="muted">
        Données insuffisantes : au moins 2 semaines d'historique de séances sont nécessaires pour
        afficher une analyse de charge fiable.
      </Card>
    );
  }

  const { tone, libelle } = STYLE_TENDANCE[charge.tendance ?? "stable"];

  return (
    <Card style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
      <StatusBadge tone={tone} label={libelle} />
      <span style={{ color: "var(--text-secondary)" }}>
        ratio charge aiguë/chronique : {charge.ratio_acwr}
      </span>
    </Card>
  );
}
