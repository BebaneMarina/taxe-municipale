import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

// Helper function pour créer des HttpParams
function createHttpParams(params: { [key: string]: any }): HttpParams {
  let httpParams = new HttpParams();
  Object.keys(params).forEach(key => {
    if (params[key] !== undefined && params[key] !== null) {
      httpParams = httpParams.set(key, params[key].toString());
    }
  });
  return httpParams;
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = environment.apiUrl || 'http://localhost:8000/api';

  constructor(private http: HttpClient) {}

  // Taxes
  getTaxes(params?: any): Observable<any> {
    return this.http.get(`${this.apiUrl}/taxes`, { params });
  }

  getTaxe(id: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/taxes/${id}`);
  }

  createTaxe(taxe: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/taxes`, taxe);
  }

  updateTaxe(id: number, taxe: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/taxes/${id}`, taxe);
  }

  deleteTaxe(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/taxes/${id}`);
  }

  // Contribuables
  getContribuables(params?: any): Observable<any> {
    return this.http.get(`${this.apiUrl}/contribuables`, { params });
  }

  getContribuable(id: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/contribuables/${id}`);
  }

  createContribuable(contribuable: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/contribuables`, contribuable);
  }

  updateContribuable(id: number, contribuable: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/contribuables/${id}`, contribuable);
  }

  transfertContribuable(id: number, nouveauCollecteurId: number): Observable<any> {
    return this.http.patch(`${this.apiUrl}/contribuables/${id}/transfert?nouveau_collecteur_id=${nouveauCollecteurId}`, {});
  }

  deleteContribuable(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/contribuables/${id}`);
  }

  // Collecteurs
  getCollecteurs(params?: any): Observable<any> {
    return this.http.get(`${this.apiUrl}/collecteurs`, { params });
  }

  getCollecteur(id: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/collecteurs/${id}`);
  }

  createCollecteur(collecteur: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/collecteurs`, collecteur);
  }

  updateCollecteur(id: number, collecteur: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/collecteurs/${id}`, collecteur);
  }

  connexionCollecteur(id: number): Observable<any> {
    return this.http.patch(`${this.apiUrl}/collecteurs/${id}/connexion`, {});
  }

  deconnexionCollecteur(id: number): Observable<any> {
    return this.http.patch(`${this.apiUrl}/collecteurs/${id}/deconnexion`, {});
  }

  deleteCollecteur(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/collecteurs/${id}`);
  }

  // Collectes
  getCollectes(params?: any): Observable<any> {
    const httpParams = createHttpParams(params || {});
    return this.http.get(`${this.apiUrl}/collectes`, httpParams.keys().length > 0 ? { params: httpParams } : {});
  }

  getCollecte(id: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/collectes/${id}`);
  }

  createCollecte(collecte: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/collectes`, collecte);
  }

  updateCollecte(id: number, collecte: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/collectes/${id}`, collecte);
  }

  annulerCollecte(id: number, raison: string): Observable<any> {
    return this.http.patch(`${this.apiUrl}/collectes/${id}/annuler?raison=${encodeURIComponent(raison)}`, {});
  }

  deleteCollecte(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/collectes/${id}`);
  }

  // Références
  getZones(actif?: boolean): Observable<any> {
    const params: { [key: string]: any } = {};
    if (actif !== undefined) {
      params['actif'] = actif.toString();
    }
    const httpParams = createHttpParams(params);
    return this.http.get(`${this.apiUrl}/references/zones`, httpParams.keys().length > 0 ? { params: httpParams } : {});
  }

  getQuartiers(zoneId?: number, actif?: boolean, additionalParams?: any): Observable<any> {
    const params: { [key: string]: any } = {};
    if (zoneId) params['zone_id'] = zoneId.toString();
    if (actif !== undefined) params['actif'] = actif.toString();
    // Ajouter les paramètres additionnels (comme arrondissement_id)
    if (additionalParams) {
      Object.keys(additionalParams).forEach(key => {
        if (additionalParams[key] !== undefined && additionalParams[key] !== null) {
          params[key] = additionalParams[key].toString();
        }
      });
    }
    const httpParams = createHttpParams(params);
    return this.http.get(`${this.apiUrl}/references/quartiers`, httpParams.keys().length > 0 ? { params: httpParams } : {});
  }

  getTypesContribuables(actif?: boolean): Observable<any> {
    const params: { [key: string]: any } = {};
    if (actif !== undefined) {
      params['actif'] = actif.toString();
    }
    const httpParams = createHttpParams(params);
    return this.http.get(`${this.apiUrl}/references/types-contribuables`, httpParams.keys().length > 0 ? { params: httpParams } : {});
  }

  getTypesTaxes(actif?: boolean): Observable<any> {
    const params: { [key: string]: any } = {};
    if (actif !== undefined) {
      params['actif'] = actif.toString();
    }
    const httpParams = createHttpParams(params);
    return this.http.get(`${this.apiUrl}/references/types-taxes`, httpParams.keys().length > 0 ? { params: httpParams } : {});
  }

  getServices(actif?: boolean): Observable<any> {
    const params: { [key: string]: any } = {};
    if (actif !== undefined) {
      params['actif'] = actif.toString();
    }
    const httpParams = createHttpParams(params);
    return this.http.get(`${this.apiUrl}/references/services`, httpParams.keys().length > 0 ? { params: httpParams } : {});
  }

  // Zones géographiques
  getZonesGeographiques(params?: any): Observable<any> {
    const httpParams = params ? createHttpParams(params) : new HttpParams();
    return this.http.get(`${this.apiUrl}/zones-geographiques/`, httpParams.keys().length > 0 ? { params: httpParams } : {});
  }

  getZoneGeographique(id: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/zones-geographiques/${id}`);
  }

  createZoneGeographique(zone: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/zones-geographiques`, zone);
  }

  updateZoneGeographique(id: number, zone: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/zones-geographiques/${id}`, zone);
  }

  deleteZoneGeographique(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/zones-geographiques/${id}`);
  }

  locatePoint(latitude: number, longitude: number, typeZone?: string): Observable<any> {
    const body = { latitude, longitude, type_zone: typeZone };
    return this.http.post(`${this.apiUrl}/zones-geographiques/locate-point`, body);
  }

  getContribuablesForMap(actif?: boolean): Observable<any> {
    const params = actif !== undefined ? createHttpParams({ actif }) : undefined;
    return this.http.get(`${this.apiUrl}/zones-geographiques/map/contribuables`, { params });
  }

  getUncoveredZones(typeZone?: string): Observable<any> {
    const params = typeZone ? createHttpParams({ type_zone: typeZone }) : undefined;
    return this.http.get(`${this.apiUrl}/zones-geographiques/uncovered-zones`, { params });
  }

  getCollecteursForMap(actif?: boolean): Observable<any> {
    const params = actif !== undefined ? createHttpParams({ actif }) : undefined;
    return this.http.get(`${this.apiUrl}/zones-geographiques/map/collecteurs`, { params });
  }

  // Uploads
  uploadPhoto(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post(`${this.apiUrl}/uploads/photo`, formData);
  }

  deletePhoto(filename: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/uploads/photo/${filename}`);
  }

  // ==================== PARAMÉTRAGE ====================
  
  // Rôles
  getRoles(params?: any): Observable<any> {
    const httpParams = params ? createHttpParams(params) : new HttpParams();
    return this.http.get(`${this.apiUrl}/parametrage/roles`, httpParams.keys().length > 0 ? { params: httpParams } : {});
  }

  getRole(id: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/parametrage/roles/${id}`);
  }

  createRole(role: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/parametrage/roles`, role);
  }

  updateRole(id: number, role: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/parametrage/roles/${id}`, role);
  }

  deleteRole(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/parametrage/roles/${id}`);
  }

  // Villes
  getVilles(params?: any): Observable<any> {
    const httpParams = params ? createHttpParams(params) : new HttpParams();
    return this.http.get(`${this.apiUrl}/parametrage/villes`, httpParams.keys().length > 0 ? { params: httpParams } : {});
  }

  getVille(id: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/parametrage/villes/${id}`);
  }

  createVille(ville: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/parametrage/villes`, ville);
  }

  updateVille(id: number, ville: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/parametrage/villes/${id}`, ville);
  }

  deleteVille(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/parametrage/villes/${id}`);
  }

  // Communes
  getCommunes(villeId?: number, params?: any): Observable<any> {
    let httpParams = params ? createHttpParams(params) : new HttpParams();
    if (villeId) {
      httpParams = httpParams.set('ville_id', villeId.toString());
    }
    return this.http.get(`${this.apiUrl}/parametrage/communes`, httpParams.keys().length > 0 ? { params: httpParams } : {});
  }

  getCommune(id: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/parametrage/communes/${id}`);
  }

  createCommune(commune: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/parametrage/communes`, commune);
  }

  updateCommune(id: number, commune: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/parametrage/communes/${id}`, commune);
  }

  deleteCommune(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/parametrage/communes/${id}`);
  }

  // Arrondissements
  getArrondissements(communeId?: number, params?: any): Observable<any> {
    let httpParams = params ? createHttpParams(params) : new HttpParams();
    if (communeId) {
      httpParams = httpParams.set('commune_id', communeId.toString());
    }
    return this.http.get(`${this.apiUrl}/parametrage/arrondissements`, httpParams.keys().length > 0 ? { params: httpParams } : {});
  }

  getArrondissement(id: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/parametrage/arrondissements/${id}`);
  }

  createArrondissement(arrondissement: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/parametrage/arrondissements`, arrondissement);
  }

  updateArrondissement(id: number, arrondissement: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/parametrage/arrondissements/${id}`, arrondissement);
  }

  deleteArrondissement(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/parametrage/arrondissements/${id}`);
  }

  // Quartiers (avec support arrondissement)
  createQuartier(quartier: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/parametrage/quartiers`, quartier);
  }

  updateQuartier(id: number, quartier: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/parametrage/quartiers/${id}`, quartier);
  }

  deleteQuartier(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/parametrage/quartiers/${id}`);
  }

  // Secteurs d'activité
  getSecteursActivite(params?: any): Observable<any> {
    const httpParams = params ? createHttpParams(params) : new HttpParams();
    return this.http.get(`${this.apiUrl}/parametrage/secteurs-activite`, httpParams.keys().length > 0 ? { params: httpParams } : {});
  }

  getSecteurActivite(id: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/parametrage/secteurs-activite/${id}`);
  }

  createSecteurActivite(secteur: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/parametrage/secteurs-activite`, secteur);
  }

  updateSecteurActivite(id: number, secteur: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/parametrage/secteurs-activite/${id}`, secteur);
  }

  deleteSecteurActivite(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/parametrage/secteurs-activite/${id}`);
  }

  // ==================== RAPPORTS ====================
  
  // Statistiques générales
  getStatistiquesGenerales(params?: any): Observable<any> {
    const httpParams = params ? createHttpParams(params) : new HttpParams();
    return this.http.get(`${this.apiUrl}/rapports/statistiques-generales`, httpParams.keys().length > 0 ? { params: httpParams } : {});
  }

  // Collecte par moyen de paiement
  getCollecteParMoyen(params?: any): Observable<any> {
    const httpParams = params ? createHttpParams(params) : new HttpParams();
    return this.http.get(`${this.apiUrl}/rapports/collecte-par-moyen`, httpParams.keys().length > 0 ? { params: httpParams } : {});
  }

  // Top collecteurs
  getTopCollecteurs(limit: number = 10, params?: any): Observable<any> {
    const queryParams: any = { limit, ...params };
    const httpParams = createHttpParams(queryParams);
    return this.http.get(`${this.apiUrl}/rapports/top-collecteurs`, { params: httpParams });
  }

  // Top taxes
  getTopTaxes(limit: number = 10, params?: any): Observable<any> {
    const queryParams: any = { limit, ...params };
    const httpParams = createHttpParams(queryParams);
    return this.http.get(`${this.apiUrl}/rapports/top-taxes`, { params: httpParams });
  }

  // Évolution temporelle
  getEvolutionTemporelle(params?: any): Observable<any> {
    const httpParams = params ? createHttpParams(params) : new HttpParams();
    return this.http.get(`${this.apiUrl}/rapports/evolution-temporelle`, httpParams.keys().length > 0 ? { params: httpParams } : {});
  }

  // Rapport complet
  getRapportComplet(params?: any): Observable<any> {
    const httpParams = params ? createHttpParams(params) : new HttpParams();
    return this.http.get(`${this.apiUrl}/rapports/complet`, httpParams.keys().length > 0 ? { params: httpParams } : {});
  }
}

