const BASE_URL = "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail ?? `Erreur ${response.status}`);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export type Plateforme = "garmin_connect" | "strava" | "nolio";
export type StatutConnexion = "actif" | "expire" | "revoque";
export type StatutDonneesSeance = "valide" | "aberrant" | "doublon_probable";
export type TypeRecommandation = "recuperation" | "nutrition";
export type StatutRecommandation = "disponible" | "donnees_insuffisantes";

export interface ConnexionPlateforme {
  id: string;
  plateforme: Plateforme;
  statut: StatutConnexion;
  date_derniere_synchronisation: string | null;
  date_connexion: string;
}

export interface Seance {
  id: string;
  date_debut: string;
  duree_secondes: number;
  distance_metres: number | null;
  puissance_moyenne_watts: number | null;
  frequence_cardiaque_moyenne: number | null;
  denivele_metres: number | null;
  statut_donnees: StatutDonneesSeance;
  seance_doublon_de_id: string | null;
  puissance_max_1min: number | null;
  puissance_max_3min: number | null;
  puissance_max_5min: number | null;
  puissance_max_10min: number | null;
  puissance_max_20min: number | null;
}

export interface PointChargeHistorique {
  date: string;
  charge_aigue_7j: number | null;
  charge_chronique_28j: number | null;
}

export interface ChargeEntrainement {
  date_calcul: string;
  charge_aigue_7j: number | null;
  charge_chronique_28j: number | null;
  ratio_acwr: number | null;
  tendance: "progression" | "surcharge" | "recuperation" | "stable" | null;
  donnees_suffisantes: boolean;
  historique: PointChargeHistorique[];
}

export interface Recommandation {
  id: string;
  type: TypeRecommandation;
  date_generation: string;
  statut: StatutRecommandation;
  contenu: Record<string, unknown> | null;
  motif_donnees_insuffisantes: string | null;
  justification: Record<string, unknown> | null;
}

export interface Athlete {
  id: string;
  email: string;
  poids_kg: number | null;
  taille_cm: number | null;
  objectifs: string | null;
  contraintes_alimentaires: string[];
}

export interface AthleteProfilInput {
  poids_kg?: number | null;
  taille_cm?: number | null;
  objectifs?: string | null;
  contraintes_alimentaires?: string[] | null;
}

export interface StatAnnuelle {
  annee: number;
  distance_metres: number;
  denivele_metres: number;
  duree_secondes: number;
  nb_seances: number;
}

export interface StatMensuelle {
  mois: number;
  distance_metres: number;
  denivele_metres: number;
  duree_secondes: number;
  nb_seances: number;
}

export interface SeanceResume {
  date_debut: string;
  distance_metres: number | null;
  denivele_metres: number | null;
  duree_secondes: number;
  puissance_moyenne_watts: number | null;
}

export interface RecordsPersonnels {
  plus_longue_distance: SeanceResume | null;
  plus_de_denivele: SeanceResume | null;
  plus_longue_duree: SeanceResume | null;
  puissance_moyenne_max: SeanceResume | null;
}

export interface ComparaisonAnnuelle {
  annee_courante: StatAnnuelle;
  annee_precedente: StatAnnuelle | null;
}

export const api = {
  connexions: {
    lister: () => request<ConnexionPlateforme[]>("/connexions"),
    autoriser: (plateforme: Plateforme) =>
      request<{ url_autorisation: string }>(`/connexions/${plateforme}/autoriser`, {
        method: "POST",
      }),
    callback: (plateforme: Plateforme, code: string) =>
      request<ConnexionPlateforme>(`/connexions/${plateforme}/callback`, {
        method: "POST",
        body: JSON.stringify({ code }),
      }),
    deconnecter: (plateforme: Plateforme) =>
      request<void>(`/connexions/${plateforme}`, { method: "DELETE" }),
  },
  seances: {
    lister: () => request<Seance[]>("/seances"),
    detail: (id: string) => request<Seance>(`/seances/${id}`),
  },
  dashboard: {
    charge: () => request<ChargeEntrainement>("/dashboard/charge"),
  },
  statistiques: {
    annuelles: () => request<StatAnnuelle[]>("/statistiques/annuelles"),
    mensuelles: (annee: number) =>
      request<StatMensuelle[]>(`/statistiques/annuelles/${annee}/mensuelles`),
    records: () => request<RecordsPersonnels>("/statistiques/records"),
    comparaisonAnnuelle: () => request<ComparaisonAnnuelle>("/statistiques/comparaison-annuelle"),
  },
  recommandations: {
    lister: (type?: TypeRecommandation) =>
      request<Recommandation[]>(`/recommandations${type ? `?type=${type}` : ""}`),
  },
  athlete: {
    profil: () => request<Athlete>("/athlete/profil"),
    modifierProfil: (payload: AthleteProfilInput) =>
      request<Athlete>("/athlete/profil", { method: "PUT", body: JSON.stringify(payload) }),
    export: () => request<Record<string, unknown>>("/athlete/export"),
    supprimer: () => request<void>("/athlete", { method: "DELETE" }),
  },
};
