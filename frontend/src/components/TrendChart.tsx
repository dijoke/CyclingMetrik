import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { PointChargeHistorique } from "../services/api_client";

// Recharts passe stroke/fill comme attributs SVG bruts, qui ne résolvent pas les custom
// properties CSS (var(...)) — ces hex dupliquent donc volontairement tokens.css.
const COULEUR_CHRONIQUE = "#6da7ec"; // --sequential-300
const COULEUR_AIGUE = "#184f95"; // --sequential-600
const COULEUR_GRIDLINE = "#e1e0d9"; // --gridline
const COULEUR_MUTED = "#898781"; // --text-muted

function formaterDate(date: string) {
  return new Date(date).toLocaleDateString("fr-FR", { day: "2-digit", month: "2-digit" });
}

export default function TrendChart({ historique }: { historique: PointChargeHistorique[] }) {
  const donnees = historique.map((point) => ({
    date: formaterDate(point.date),
    "Charge chronique (28j)": point.charge_chronique_28j,
    "Charge aiguë (7j)": point.charge_aigue_7j,
  }));

  return (
    <div style={{ height: 260 }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={donnees}>
          <CartesianGrid strokeDasharray="3 3" stroke={COULEUR_GRIDLINE} />
          <XAxis dataKey="date" stroke={COULEUR_MUTED} fontSize={12} />
          <YAxis stroke={COULEUR_MUTED} fontSize={12} />
          <Tooltip />
          <Legend />
          <Line
            type="monotone"
            dataKey="Charge chronique (28j)"
            stroke={COULEUR_CHRONIQUE}
            strokeWidth={2}
            dot={false}
          />
          <Line
            type="monotone"
            dataKey="Charge aiguë (7j)"
            stroke={COULEUR_AIGUE}
            strokeWidth={2}
            dot={{ r: 3 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
