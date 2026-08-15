import { useQuery } from "@tanstack/react-query";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import ChargeIndicator from "../components/ChargeIndicator";
import { api } from "../services/api_client";

export default function Dashboard() {
  const { data: charge, isLoading } = useQuery({
    queryKey: ["dashboard", "charge"],
    queryFn: api.dashboard.charge,
  });

  if (isLoading || !charge) return <p>Chargement…</p>;

  const donnees = [
    { nom: "Chronique (28j)", valeur: charge.charge_chronique_28j ?? 0 },
    { nom: "Aiguë (7j)", valeur: charge.charge_aigue_7j ?? 0 },
  ];

  return (
    <section>
      <h2>Charge d'entraînement</h2>
      <ChargeIndicator charge={charge} />
      {charge.donnees_suffisantes && (
        <div style={{ marginTop: "2rem", height: 260 }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={donnees}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="nom" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="valeur" stroke="#0b5fff" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </section>
  );
}
