import { TypeContribuable } from './type-contribuable.interface';
import { Quartier } from './quartier.interface';
import { Collecteur } from './collecteur.interface';

export interface Contribuable {
  id: number;
  nom: string;
  prenom?: string;
  email?: string;
  telephone: string;
  type_contribuable_id: number;
  quartier_id: number;
  collecteur_id: number;
  adresse?: string;
  latitude?: number;
  longitude?: number;
  nom_activite?: string;
  photo_url?: string;
  numero_identification?: string;
  qr_code?: string;
  actif: boolean;
  type_contribuable?: TypeContribuable;
  quartier?: Quartier;
  collecteur?: Collecteur;
  created_at: string;
  updated_at: string;
}

export interface ContribuableCreate {
  nom: string;
  prenom?: string;
  email?: string;
  telephone: string;
  type_contribuable_id: number;
  quartier_id: number;
  collecteur_id: number;
  adresse?: string;
  latitude?: number;
  longitude?: number;
  nom_activite?: string;
  photo_url?: string;
  numero_identification?: string;
  actif?: boolean;
}

export interface ContribuableUpdate {
  nom?: string;
  prenom?: string;
  email?: string;
  telephone?: string;
  type_contribuable_id?: number;
  quartier_id?: number;
  collecteur_id?: number;
  adresse?: string;
  latitude?: number;
  longitude?: number;
  nom_activite?: string;
  photo_url?: string;
  actif?: boolean;
}

