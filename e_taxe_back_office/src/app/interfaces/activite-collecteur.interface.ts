export interface ActiviteJour {
  date: string; // Format YYYY-MM-DD
  nombre_collectes: number;
  montant_total: number;
  premiere_collecte?: string;
  derniere_collecte?: string;
  duree_travail_minutes?: number;
}

export interface ActiviteCollecteur {
  collecteur_id: number;
  collecteur_nom: string;
  collecteur_prenom: string;
  collecteur_matricule: string;
  periode_debut?: string;
  periode_fin?: string;
  activites: ActiviteJour[];
  total_collectes: number;
  total_montant: number;
  nombre_jours_actifs: number;
  moyenne_collectes_par_jour?: number;
  moyenne_montant_par_jour?: number;
}

