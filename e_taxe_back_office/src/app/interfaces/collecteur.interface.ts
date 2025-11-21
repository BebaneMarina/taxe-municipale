export interface Collecteur {
  id: number;
  nom: string;
  prenom: string;
  email: string;
  telephone: string;
  matricule: string;
  statut: 'active' | 'desactive';
  etat: 'connecte' | 'deconnecte';
  zone_id?: number;
  date_derniere_connexion?: string;
  date_derniere_deconnexion?: string;
  heure_cloture?: string;
  actif: boolean;
  created_at: string;
  updated_at: string;
}

export interface CollecteurCreate {
  nom: string;
  prenom: string;
  email: string;
  telephone: string;
  matricule: string;
  zone_id?: number;
  heure_cloture?: string;
}

export interface CollecteurUpdate {
  nom?: string;
  prenom?: string;
  email?: string;
  telephone?: string;
  zone_id?: number;
  heure_cloture?: string;
  statut?: string;
  actif?: boolean;
}

