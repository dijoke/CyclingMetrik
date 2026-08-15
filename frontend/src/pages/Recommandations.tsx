import { useQuery } from "@tanstack/react-query";
import Card from "../components/Card";
import { type Recommandation, api } from "../services/api_client";

const LABEL_INTENSITE: Record<string, string> = {
  repos_complet: "Repos complet",
  seance_legere: "Séance légère",
  entrainement_normal: "Entraînement normal",
};

function ContenuRecuperation({ contenu }: { contenu: Record<string, unknown> }) {
  const intensite = contenu.intensite_lendemain as string | undefined;
  return (
    <div>
      {intensite && (
        <div style={{ fontWeight: 600, color: "var(--text-primary)" }}>
          {LABEL_INTENSITE[intensite] ?? intensite}
        </div>
      )}
      <p style={{ margin: "0.35rem 0 0", color: "var(--text-secondary)" }}>
        {contenu.repos_recommande as string}
      </p>
    </div>
  );
}

function ContenuNutrition({ contenu }: { contenu: Record<string, unknown> }) {
  const stats: { label: string; valeur: string }[] = [
    { label: "Calories", valeur: `${contenu.calories_kcal} kcal` },
    { label: "Glucides", valeur: `${contenu.glucides_g} g` },
    { label: "Protéines", valeur: `${contenu.proteines_g} g` },
    { label: "Lipides", valeur: `${contenu.lipides_g} g` },
  ];
  return (
    <div style={{ display: "flex", gap: "1.5rem", flexWrap: "wrap" }}>
      {stats.map((stat) => (
        <div key={stat.label}>
          <div style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>{stat.label}</div>
          <div style={{ fontWeight: 600, color: "var(--text-primary)" }}>{stat.valeur}</div>
        </div>
      ))}
    </div>
  );
}

function CarteRecommandation({ recommandation }: { recommandation: Recommandation }) {
  const titre = recommandation.type === "nutrition" ? "Nutrition" : "Récupération";

  if (recommandation.statut === "donnees_insuffisantes") {
    return (
      <Card tone="muted">
        <strong>{titre}</strong>
        <p style={{ margin: "0.5rem 0 0" }}>{recommandation.motif_donnees_insuffisantes}</p>
      </Card>
    );
  }

  return (
    <Card>
      <strong style={{ color: "var(--text-primary)" }}>{titre}</strong>
      <div style={{ marginTop: "0.5rem" }}>
        {recommandation.contenu &&
          (recommandation.type === "nutrition" ? (
            <ContenuNutrition contenu={recommandation.contenu} />
          ) : (
            <ContenuRecuperation contenu={recommandation.contenu} />
          ))}
      </div>
    </Card>
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
      <h2 style={{ color: "var(--text-primary)" }}>Recommandations</h2>
      <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        {recommandations.map((recommandation) => (
          <CarteRecommandation key={recommandation.id} recommandation={recommandation} />
        ))}
      </div>
    </section>
  );
}
