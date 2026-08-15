import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import Card from "../components/Card";
import StatusBadge, { type StatusTone } from "../components/StatusBadge";
import { type Plateforme, api } from "../services/api_client";

const PLATEFORMES: { id: Plateforme; label: string }[] = [
  { id: "strava", label: "Strava" },
  { id: "garmin_connect", label: "Garmin Connect" },
  { id: "nolio", label: "Nolio" },
];

const STYLE_STATUT: Record<string, { tone: StatusTone; label: string }> = {
  actif: { tone: "good", label: "Connecté" },
  expire: { tone: "warning", label: "Expiré — reconnexion nécessaire" },
  revoque: { tone: "neutral", label: "Déconnecté" },
};

export default function Connexions() {
  const queryClient = useQueryClient();
  const { data: connexions, isLoading } = useQuery({
    queryKey: ["connexions"],
    queryFn: api.connexions.lister,
  });
  const [enCours, setEnCours] = useState<Plateforme | null>(null);

  const connexionPour = (id: Plateforme) => connexions?.find((c) => c.plateforme === id);

  async function connecter(plateforme: Plateforme) {
    setEnCours(plateforme);
    try {
      const { url_autorisation } = await api.connexions.autoriser(plateforme);
      window.location.href = url_autorisation;
    } finally {
      setEnCours(null);
    }
  }

  async function deconnecter(plateforme: Plateforme) {
    await api.connexions.deconnecter(plateforme);
    queryClient.invalidateQueries({ queryKey: ["connexions"] });
  }

  if (isLoading) return <p>Chargement…</p>;

  return (
    <section>
      <h2 style={{ color: "var(--text-primary)" }}>Connexions plateformes</h2>
      <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        {PLATEFORMES.map((plateforme) => {
          const connexion = connexionPour(plateforme.id);
          const style = connexion ? STYLE_STATUT[connexion.statut] : { tone: "neutral" as const, label: "Non connecté" };
          return (
            <Card
              key={plateforme.id}
              style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}
            >
              <div style={{ display: "flex", flexDirection: "column", gap: "0.35rem" }}>
                <strong style={{ color: "var(--text-primary)" }}>{plateforme.label}</strong>
                <StatusBadge tone={style.tone} label={style.label} />
              </div>
              {connexion && connexion.statut === "actif" ? (
                <button onClick={() => deconnecter(plateforme.id)}>Déconnecter</button>
              ) : (
                <button disabled={enCours === plateforme.id} onClick={() => connecter(plateforme.id)}>
                  {connexion ? "Reconnecter" : "Connecter"}
                </button>
              )}
            </Card>
          );
        })}
      </div>
    </section>
  );
}
