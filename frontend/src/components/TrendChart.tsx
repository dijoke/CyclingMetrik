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
import { useTheme } from "../hooks/useTheme";
import type { PointChargeHistorique } from "../services/api_client";

// Recharts passe stroke/fill comme attributs SVG bruts, qui ne résolvent pas les custom
// properties CSS (var(...)) — ces hex dupliquent donc volontairement tokens.css, avec une
// paire claire/sombre par couleur (research.md Decision 2, feature 006).
const COULEURS = {
  light: { chronique: "#6da7ec", aigue: "#184f95", gridline: "#e1e0d9", muted: "#898781" },
  dark: { chronique: "#86b6ef", aigue: "#3987e5", gridline: "#2c2c2a", muted: "#898781" },
};

function formaterDate(date: string) {
  return new Date(date).toLocaleDateString("fr-FR", { day: "2-digit", month: "2-digit" });
}

export default function TrendChart({ historique }: { historique: PointChargeHistorique[] }) {
  const { theme } = useTheme();
  const couleurs = COULEURS[theme];

  const donnees = historique.map((point) => ({
    date: formaterDate(point.date),
    "Charge chronique (28j)": point.charge_chronique_28j,
    "Charge aiguë (7j)": point.charge_aigue_7j,
  }));

  return (
    <div style={{ height: 260 }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={donnees}>
          <CartesianGrid strokeDasharray="3 3" stroke={couleurs.gridline} />
          <XAxis dataKey="date" stroke={couleurs.muted} fontSize={12} />
          <YAxis stroke={couleurs.muted} fontSize={12} />
          <Tooltip />
          <Legend />
          <Line
            type="monotone"
            dataKey="Charge chronique (28j)"
            stroke={couleurs.chronique}
            strokeWidth={2}
            dot={false}
          />
          <Line
            type="monotone"
            dataKey="Charge aiguë (7j)"
            stroke={couleurs.aigue}
            strokeWidth={2}
            dot={{ r: 3 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
