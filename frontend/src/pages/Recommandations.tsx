import { useQuery } from "@tanstack/react-query";
import { type Recommandation, api } from "../services/api_client";

function CarteRecommandation({ recommandation }: { recommandation: Recommandation }) {
  const titre = recommandation.type === "nutrition" ? "Nutrition" : "Récupération";

  if (recommandation.statut === "donnees_insuffisantes") {
    return (
      <div style={{ padding: "1rem", border: "1px dashed #ccc", borderRadius: 8, color: "#666" }}>
        <strong>{titre}</strong>
        <p style={{ margin: "0.5rem 0 0" }}>{recommandation.motif_donnees_insuffisantes}</p>
      </div>
    );
  }

  return (
    <div style={{ padding: "1rem", border: "1px solid #e2e2e2", borderRadius: 8 }}>
      <strong>{titre}</strong>
      <pre style={{ whiteSpace: "pre-wrap", fontFamily: "inherit", margin: "0.5rem 0 0" }}>
        {JSON.stringify(recommandation.contenu, null, 2)}
      </pre>
    </div>
  );
}

export default function Recommandations() {
  const { data: recommandations, isLoading } = useQuery({
    queryKey: ["recommandations"],
    queryFn: () => api.recommandations.lister(),
  });

  if (isLoading) return <p>Chargement…</p>;
  if (!recommandations?.length) return <p>Aucune recommandation pour le moment.</p>;

  return (
    <section>
      <h2>Recommandations</h2>
      <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        {recommandations.map((recommandation) => (
          <CarteRecommandation key={recommandation.id} recommandation={recommandation} />
        ))}
      </div>
    </section>
  );
}
