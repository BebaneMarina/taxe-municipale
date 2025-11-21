// Interfaces pour le paramétrage

// ==================== RÔLES UTILISATEURS ====================
export interface Role {
  id: number;
  nom: string;
  code: string;
  description?: string;
  permissions: string[];
  actif: boolean;
  created_at: string;
  updated_at: string;
}

export interface RoleCreate {
  nom: string;
  code: string;
  description?: string;
  permissions: string[];
  actif?: boolean;
}

// ==================== DIVISIONS ADMINISTRATIVES ====================
export interface Ville {
  id: number;
  nom: string;
  code: string;
  description?: string;
  pays: string; // "Gabon" par défaut
  actif: boolean;
  communes?: Commune[];
  created_at: string;
  updated_at: string;
}

export interface VilleCreate {
  nom: string;
  code: string;
  description?: string;
  pays?: string;
  actif?: boolean;
}

export interface Commune {
  id: number;
  nom: string;
  code: string;
  ville_id: number;
  description?: string;
  actif: boolean;
  ville?: Ville;
  arrondissements?: Arrondissement[];
  created_at: string;
  updated_at: string;
}

export interface CommuneCreate {
  nom: string;
  code: string;
  ville_id: number;
  description?: string;
  actif?: boolean;
}

export interface Arrondissement {
  id: number;
  nom: string;
  code: string;
  commune_id: number;
  description?: string;
  actif: boolean;
  commune?: Commune;
  quartiers?: Quartier[];
  created_at: string;
  updated_at: string;
}

export interface ArrondissementCreate {
  nom: string;
  code: string;
  commune_id: number;
  description?: string;
  actif?: boolean;
}

export interface Quartier {
  id: number;
  nom: string;
  code: string;
  arrondissement_id?: number;
  zone_id?: number; // Pour compatibilité avec l'ancien système
  description?: string;
  actif: boolean;
  arrondissement?: Arrondissement;
  zone?: any;
  created_at: string;
  updated_at: string;
}

export interface QuartierCreate {
  nom: string;
  code: string;
  arrondissement_id?: number;
  zone_id?: number; // Pour compatibilité
  description?: string;
  actif?: boolean;
}

// ==================== SECTEURS D'ACTIVITÉ ====================
export interface SecteurActivite {
  id: number;
  nom: string;
  code: string;
  description?: string;
  actif: boolean;
  created_at: string;
  updated_at: string;
}

export interface SecteurActiviteCreate {
  nom: string;
  code: string;
  description?: string;
  actif?: boolean;
}

