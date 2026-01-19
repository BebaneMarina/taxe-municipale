import { Contribuable } from './contribuable.interface';
import { Taxe } from './taxe.interface';
import { Collecteur } from './collecteur.interface';

export interface InfoCollecte {
  id: number;
  contribuable_id: number;
  taxe_id: number;
  collecteur_id: number;
  montant: number;
  commission: number;
  type_paiement: 'especes' | 'mobile_money' | 'carte';
  statut: 'pending' | 'completed' | 'failed' | 'cancelled';
  reference: string;
  billetage?: string;
  date_collecte: string;
  date_cloture?: string;
  sms_envoye: boolean;
  ticket_imprime: boolean;
  annule: boolean;
  raison_annulation?: string;
  created_at: string;
  updated_at: string;
  // Relations complètes
  contribuable?: Contribuable;
  taxe?: Taxe;
  collecteur?: Collecteur;
  // Géolocalisation
  location?: {
    id: number;
    latitude: number;
    longitude: number;
    accuracy?: number;
    timestamp?: string;
  };
}

export type Collecte = InfoCollecte;

export interface InfoCollecteCreate {
  contribuable_id: number;
  taxe_id: number;
  collecteur_id: number;
  montant: number;
  type_paiement: string;
  billetage?: string;
  date_collecte?: string;
}

export interface InfoCollecteUpdate {
  statut?: string;
  annule?: boolean;
  raison_annulation?: string;
  sms_envoye?: boolean;
  ticket_imprime?: boolean;
}
