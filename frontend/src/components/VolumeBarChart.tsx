import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useTheme } from "../hooks/useTheme";

// Recharts passe fill comme attribut SVG brut, qui ne résout pas var(...) — ces hex dupliquent
// donc volontairement tokens.css, avec une paire claire/sombre (research.md Decision 2, feature 006).
const COULEURS = {
  light: { barre: "#256abf", gridline: "#e1e0d9", muted: "#898781" },
  dark: { barre: "#3987e5", gridline: "#2c2c2a", muted: "#898781" },
};

interface PointVolume {
  etiquette: string;
  distanceKm: number;
}

export default function VolumeBarChart({ donnees }: { donnees: PointVolume[] }) {
  const { theme } = useTheme();
  const couleurs = COULEURS[theme];

  return (
    <div style={{ height: 240 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={donnees}>
          <CartesianGrid strokeDasharray="3 3" stroke={couleurs.gridline} vertical={false} />
          <XAxis dataKey="etiquette" stroke={couleurs.muted} fontSize={12} />
          <YAxis stroke={couleurs.muted} fontSize={12} unit=" km" />
          <Tooltip formatter={(valeur: number) => [`${valeur.toFixed(0)} km`, "Distance"]} />
          <Bar dataKey="distanceKm" fill={couleurs.barre} radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
