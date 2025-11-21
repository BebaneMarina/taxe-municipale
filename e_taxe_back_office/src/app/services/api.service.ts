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

  getQuartiers(zoneId?: number, actif?: boolean): Observable<any> {
    const params: { [key: string]: any } = {};
    if (zoneId) params['zone_id'] = zoneId.toString();
    if (actif !== undefined) params['actif'] = actif.toString();
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
    return this.http.get(`${this.apiUrl}/zones-geographiques`, { params });
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
}

