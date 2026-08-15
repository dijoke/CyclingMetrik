import type { ChargeEntrainement } from "../services/api_client";

const STYLE_TENDANCE: Record<string, { couleur: string; libelle: string }> = {
  surcharge: { couleur: "#b42318", libelle: "Surcharge — repos recommandé" },
  recuperation: { couleur: "#1a7f37", libelle: "Récupération — charge basse" },
  progression: { couleur: "#0b5fff", libelle: "Progression" },
  stable: { couleur: "#666666", libelle: "Stable" },
};

export default function ChargeIndicator({ charge }: { charge: ChargeEntrainement }) {
  if (!charge.donnees_suffisantes) {
    return (
      <div style={{ padding: "1rem", border: "1px dashed #ccc", borderRadius: 8, color: "#666" }}>
        Données insuffisantes : au moins 2 semaines d'historique de séances sont nécessaires pour
        afficher une analyse de charge fiable.
      </div>
    );
  }

  const style = STYLE_TENDANCE[charge.tendance ?? "stable"];

  return (
    <div
      style={{
        padding: "1rem",
        borderRadius: 8,
        border: `2px solid ${style.couleur}`,
        color: style.couleur,
        fontWeight: 600,
      }}
    >
      {style.libelle} — ratio charge aiguë/chronique : {charge.ratio_acwr}
    </div>
  );
}
