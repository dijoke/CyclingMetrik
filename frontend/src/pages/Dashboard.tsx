import { useQuery } from "@tanstack/react-query";
import ChargeIndicator from "../components/ChargeIndicator";
import TrendChart from "../components/TrendChart";
import { api } from "../services/api_client";

export default function Dashboard() {
  const { data: charge, isLoading } = useQuery({
    queryKey: ["dashboard", "charge"],
    queryFn: api.dashboard.charge,
  });

  if (isLoading || !charge) return <p>Chargement…</p>;

  return (
    <section>
      <h2 style={{ color: "var(--text-primary)" }}>Charge d'entraînement</h2>
      <ChargeIndicator charge={charge} />
      {charge.donnees_suffisantes && (
        <div style={{ marginTop: "1.5rem" }}>
          <TrendChart historique={charge.historique} />
        </div>
      )}
    </section>
  );
}
