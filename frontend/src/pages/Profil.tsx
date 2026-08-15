import { useQuery, useQueryClient } from "@tanstack/react-query";
import { type FormEvent, useState } from "react";
import { api } from "../services/api_client";

export default function Profil() {
  const queryClient = useQueryClient();
  const { data: athlete, isLoading } = useQuery({
    queryKey: ["athlete", "profil"],
    queryFn: api.athlete.profil,
  });
  const [enregistrement, setEnregistrement] = useState(false);

  if (isLoading || !athlete) return <p>Chargement…</p>;

  async function enregistrer(evenement: FormEvent<HTMLFormElement>) {
    evenement.preventDefault();
    const formData = new FormData(evenement.currentTarget);
    const poids = formData.get("poids_kg");
    const taille = formData.get("taille_cm");

    setEnregistrement(true);
    try {
      await api.athlete.modifierProfil({
        poids_kg: poids ? Number(poids) : null,
        taille_cm: taille ? Number(taille) : null,
        objectifs: (formData.get("objectifs") as string) || null,
      });
      queryClient.invalidateQueries({ queryKey: ["athlete", "profil"] });
    } finally {
      setEnregistrement(false);
    }
  }

  async function exporterDonnees() {
    const donnees = await api.athlete.export();
    const blob = new Blob([JSON.stringify(donnees, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const lien = document.createElement("a");
    lien.href = url;
    lien.download = "mes-donnees-coaching-velo.json";
    lien.click();
    URL.revokeObjectURL(url);
  }

  async function supprimerCompte() {
    if (confirm("Supprimer définitivement toutes vos données ? Cette action est irréversible.")) {
      await api.athlete.supprimer();
      queryClient.invalidateQueries();
    }
  }

  return (
    <section>
      <h2>Profil athlète</h2>
      <form
        onSubmit={enregistrer}
        style={{ display: "flex", flexDirection: "column", gap: "1rem", maxWidth: 360 }}
      >
        <label>
          Poids (kg)
          <input type="number" step="0.1" name="poids_kg" defaultValue={athlete.poids_kg ?? ""} />
        </label>
        <label>
          Taille (cm)
          <input type="number" name="taille_cm" defaultValue={athlete.taille_cm ?? ""} />
        </label>
        <label>
          Objectifs
          <textarea name="objectifs" defaultValue={athlete.objectifs ?? ""} />
        </label>
        <button type="submit" disabled={enregistrement}>
          Enregistrer
        </button>
      </form>

      <hr style={{ margin: "2rem 0" }} />

      <h3>Vos données (RGPD)</h3>
      <div style={{ display: "flex", gap: "1rem" }}>
        <button onClick={exporterDonnees}>Exporter mes données</button>
        <button style={{ color: "#b42318" }} onClick={supprimerCompte}>
          Supprimer mon compte
        </button>
      </div>
    </section>
  );
}
