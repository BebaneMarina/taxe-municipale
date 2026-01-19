import { Zone } from './zone.interface';

export interface Quartier {
  id: number;
  nom: string;
  code: string;
  zone_id: number;
  description?: string;
  actif: boolean;
  zone?: Zone;
  created_at: string;
  updated_at: string;
}

