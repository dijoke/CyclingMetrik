import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { type Plateforme, api } from "../services/api_client";

const PLATEFORMES: { id: Plateforme; label: string }[] = [
  { id: "strava", label: "Strava" },
  { id: "garmin_connect", label: "Garmin Connect" },
  { id: "nolio", label: "Nolio" },
];

const LABEL_STATUT: Record<string, string> = {
  actif: "Connecté",
  expire: "Expiré — reconnexion nécessaire",
  revoque: "Déconnecté",
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
      <h2>Connexions plateformes</h2>
      <ul
        style={{ listStyle: "none", padding: 0, display: "flex", flexDirection: "column", gap: "1rem" }}
      >
        {PLATEFORMES.map((plateforme) => {
          const connexion = connexionPour(plateforme.id);
          return (
            <li
              key={plateforme.id}
              style={{
                border: "1px solid #e2e2e2",
                borderRadius: 8,
                padding: "1rem",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <div>
                <strong>{plateforme.label}</strong>
                <div
                  style={{
                    fontSize: "0.9rem",
                    color: connexion?.statut === "actif" ? "#1a7f37" : "#b42318",
                  }}
                >
                  {connexion ? LABEL_STATUT[connexion.statut] : "Non connecté"}
                </div>
              </div>
              {connexion && connexion.statut === "actif" ? (
                <button onClick={() => deconnecter(plateforme.id)}>Déconnecter</button>
              ) : (
                <button disabled={enCours === plateforme.id} onClick={() => connecter(plateforme.id)}>
                  {connexion ? "Reconnecter" : "Connecter"}
                </button>
              )}
            </li>
          );
        })}
      </ul>
    </section>
  );
}
