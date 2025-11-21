export interface Taxe {
  id: number;
  nom: string;
  code: string;
  description?: string;
  montant: number;
  montant_variable: boolean;
  periodicite: 'journaliere' | 'hebdomadaire' | 'mensuelle' | 'trimestrielle';
  type_taxe_id: number;
  service_id: number;
  commission_pourcentage: number;
  actif: boolean;
  type_taxe?: TypeTaxe;
  service?: Service;
  created_at: string;
  updated_at: string;
}

export interface TypeTaxe {
  id: number;
  nom: string;
  code: string;
  description?: string;
  actif: boolean;
  created_at: string;
  updated_at: string;
}

export interface Service {
  id: number;
  nom: string;
  code: string;
  description?: string;
  actif: boolean;
  created_at: string;
  updated_at: string;
}

export interface TaxeCreate {
  nom: string;
  code: string;
  description?: string;
  montant: number;
  montant_variable: boolean;
  periodicite: string;
  type_taxe_id: number;
  service_id: number;
  commission_pourcentage: number;
  actif?: boolean;
}

export interface TaxeUpdate {
  nom?: string;
  description?: string;
  montant?: number;
  montant_variable?: boolean;
  periodicite?: string;
  commission_pourcentage?: number;
  actif?: boolean;
}

