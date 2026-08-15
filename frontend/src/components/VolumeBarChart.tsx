import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

// Recharts passe fill comme attribut SVG brut, qui ne résout pas var(...) — cet hex
// duplique donc volontairement --sequential-500 de tokens.css.
const COULEUR_BARRE = "#256abf";
const COULEUR_GRIDLINE = "#e1e0d9";
const COULEUR_MUTED = "#898781";

interface PointVolume {
  etiquette: string;
  distanceKm: number;
}

export default function VolumeBarChart({ donnees }: { donnees: PointVolume[] }) {
  return (
    <div style={{ height: 240 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={donnees}>
          <CartesianGrid strokeDasharray="3 3" stroke={COULEUR_GRIDLINE} vertical={false} />
          <XAxis dataKey="etiquette" stroke={COULEUR_MUTED} fontSize={12} />
          <YAxis stroke={COULEUR_MUTED} fontSize={12} unit=" km" />
          <Tooltip formatter={(valeur: number) => [`${valeur.toFixed(0)} km`, "Distance"]} />
          <Bar dataKey="distanceKm" fill={COULEUR_BARRE} radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
