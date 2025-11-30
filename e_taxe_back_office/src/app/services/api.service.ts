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

  getActivitesCollecteur(collecteurId: number, dateDebut?: string, dateFin?: string): Observable<any> {
    const params: any = {};
    if (dateDebut) params.date_debut = dateDebut;
    if (dateFin) params.date_fin = dateFin;
    const httpParams = createHttpParams(params);
    return this.http.get(`${this.apiUrl}/collecteurs/${collecteurId}/activites`, httpParams.keys().length > 0 ? { params: httpParams } : {});
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
  getZonesReferences(actif?: boolean): Observable<any> {
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


  getUncoveredZones(typeZone?: string): Observable<any> {
    // Ne pas envoyer de paramètres si typeZone n'est pas fourni ou est vide
    if (typeZone && typeZone.trim()) {
      const params = createHttpParams({ type_zone: typeZone.trim() });
      return this.http.get(`${this.apiUrl}/zones-geographiques/uncovered-zones`, { params });
    }
    // Appel sans paramètres
    return this.http.get(`${this.apiUrl}/zones-geographiques/uncovered-zones`);
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

  // Impayés
  getImpayes(params?: any): Observable<any> {
    const httpParams = params ? createHttpParams(params) : new HttpParams();
    return this.http.get(`${this.apiUrl}/impayes`, httpParams.keys().length > 0 ? { params: httpParams } : {});
  }

  getDossierImpaye(id: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/impayes/${id}`);
  }

  createDossierImpaye(dossier: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/impayes`, dossier);
  }

  updateDossierImpaye(id: number, dossier: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/impayes/${id}`, dossier);
  }

  detecterImpayes(params?: any): Observable<any> {
    const httpParams = params ? createHttpParams(params) : new HttpParams();
    return this.http.post(`${this.apiUrl}/impayes/detecter-impayes`, {}, httpParams.keys().length > 0 ? { params: httpParams } : {});
  }

  assignerDossier(id: number, collecteurId: number): Observable<any> {
    return this.http.patch(`${this.apiUrl}/impayes/${id}/assigner?collecteur_id=${collecteurId}`, {});
  }

  cloturerDossier(id: number): Observable<any> {
    return this.http.patch(`${this.apiUrl}/impayes/${id}/cloturer`, {});
  }

  calculerPenalites(request: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/impayes/calculer-penalites`, request);
  }

  getStatistiquesImpayes(): Observable<any> {
    return this.http.get(`${this.apiUrl}/impayes/statistiques/globales`);
  }

  // ==================== PAIEMENTS CLIENT (BambooPay) ====================
  
  getTaxesPubliques(actif: boolean = true): Observable<any> {
    return this.http.get(`${this.apiUrl}/client/taxes`, { params: { actif } });
  }

  initierPaiement(transaction: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/client/paiement/initier`, transaction);
  }

  getStatutTransaction(billingId: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/client/paiement/statut/${billingId}`);
  }

  verifierStatutBambooPay(billingId: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/client/paiement/verifier/${billingId}`, {});
  }

  // ==================== CARTOGRAPHIE ====================
  
  getStatistiquesCartographie(params?: any): Observable<any> {
    const httpParams = params ? createHttpParams(params) : new HttpParams();
    return this.http.get(`${this.apiUrl}/cartographie/statistiques`, httpParams.keys().length > 0 ? { params: httpParams } : {});
  }

  getEvolutionJournaliere(jours: number = 7): Observable<any> {
    return this.http.get(`${this.apiUrl}/cartographie/evolution-journaliere`, { params: { jours } });
  }

  // Contribuables pour la carte
  getContribuablesForMap(actif: boolean = true): Observable<any> {
    return this.http.get(`${this.apiUrl}/cartographie/map/contribuables`, { params: { actif } });
  }

  // Zones géographiques
  getZones(actif?: boolean): Observable<any> {
    const params: { [key: string]: any } = {};
    if (actif !== undefined) params['actif'] = actif;
    const httpParams = createHttpParams(params);
    return this.http.get(`${this.apiUrl}/zones-geographiques`, httpParams.keys().length > 0 ? { params: httpParams } : {});
  }

  getStatsZones(): Observable<any> {
    return this.http.get(`${this.apiUrl}/cartographie/stats-zones`);
  }

  getEvolutionCollecte(): Observable<any> {
    return this.http.get(`${this.apiUrl}/cartographie/evolution-collecte`);
  }

  getStatsGlobales(): Observable<any> {
    return this.http.get(`${this.apiUrl}/cartographie/stats-globales`);
  }

  // ==================== CAISSES ====================
  getCaisses(params?: any): Observable<any> {
    const httpParams = params ? createHttpParams(params) : new HttpParams();
    return this.http.get(`${this.apiUrl}/caisses`, httpParams.keys().length > 0 ? { params: httpParams } : {});
  }

  getCaisse(id: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/caisses/${id}`);
  }

  getEtatCaisse(id: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/caisses/${id}/etat`);
  }

  ouvrirCaisse(id: number, soldeInitial: number = 0): Observable<any> {
    const params = createHttpParams({ solde_initial: soldeInitial });
    return this.http.post(`${this.apiUrl}/caisses/${id}/ouvrir`, {}, { params });
  }

  fermerCaisse(id: number, notes?: string): Observable<any> {
    const params = notes ? createHttpParams({ notes }) : new HttpParams();
    return this.http.post(`${this.apiUrl}/caisses/${id}/fermer`, {}, { params });
  }

  cloturerCaisse(id: number, montantCloture: number, notes?: string): Observable<any> {
    const payload: Record<string, string | number> = { montant_cloture: montantCloture };
    if (notes) {
      payload['notes'] = notes;
    }
    const params = createHttpParams(payload);
    return this.http.post(`${this.apiUrl}/caisses/${id}/cloturer`, {}, { params });
  }

  createOperationCaisse(caisseId: number, operation: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/caisses/${caisseId}/operations`, operation);
  }

  getOperationsCaisse(caisseId: number, params?: any): Observable<any> {
    const httpParams = params ? createHttpParams(params) : new HttpParams();
    return this.http.get(`${this.apiUrl}/caisses/${caisseId}/operations`, httpParams.keys().length > 0 ? { params: httpParams } : {});
  }

  updateCaisse(id: number, payload: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/caisses/${id}`, payload);
  }

  // Coupures de caisse
  getCoupures(params?: any): Observable<any> {
    const httpParams = params ? createHttpParams(params) : new HttpParams();
    return this.http.get(`${this.apiUrl}/caisses/coupures`, httpParams.keys().length > 0 ? { params: httpParams } : {});
  }

  createCoupure(payload: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/caisses/coupures`, payload);
  }

  updateCoupure(id: number, payload: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/caisses/coupures/${id}`, payload);
  }

  toggleCoupure(id: number): Observable<any> {
    return this.http.patch(`${this.apiUrl}/caisses/coupures/${id}/toggle`, {});
  }

  deleteCoupure(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/caisses/coupures/${id}`);
  }

  // ==================== JOURNAL & COMMISSIONS ====================
  getJournalCurrent(jour?: string): Observable<any> {
    const params = jour ? createHttpParams({ jour }) : new HttpParams();
    return this.http.get(`${this.apiUrl}/journal/travaux/current`, { params });
  }

  getJournalByDate(jour: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/journal/travaux/${jour}`);
  }

  cloturerJournal(jour: string, remarque?: string): Observable<any> {
    const params = createHttpParams({ jour });
    const body = remarque ? { remarque } : {};
    return this.http.post(`${this.apiUrl}/journal/travaux/cloturer`, body, { params });
  }

  listCommissionFiles(): Observable<any> {
    return this.http.get(`${this.apiUrl}/journal/commissions/files`);
  }

  genererCommissions(jour: string, format: 'json' | 'csv' | 'pdf' = 'json'): Observable<any> {
    const params = createHttpParams({ jour, format_fichier: format });
    return this.http.post(`${this.apiUrl}/journal/commissions/generer`, {}, { params });
  }

  getCommissions(params?: any): Observable<any> {
    const httpParams = params ? createHttpParams(params) : new HttpParams();
    return this.http.get(`${this.apiUrl}/journal/commissions`, httpParams.keys().length > 0 ? { params: httpParams } : {});
  }

  getCollectesJour(jour: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/journal/travaux/${jour}/collectes`);
  }

  getOperationsJour(jour: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/journal/travaux/${jour}/operations`);
  }

  getRelancesJour(jour: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/journal/travaux/${jour}/relances`);
  }

  getCommissionsDetails(jour: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/journal/commissions/${jour}/details`);
  }

  // ==================== RELANCES ====================
  getRelances(params?: any): Observable<any> {
    const httpParams = params ? createHttpParams(params) : new HttpParams();
    return this.http.get(`${this.apiUrl}/relances`, httpParams.keys().length > 0 ? { params: httpParams } : {});
  }

  getRelance(id: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/relances/${id}`);
  }

  createRelance(payload: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/relances`, payload);
  }

  updateRelance(id: number, payload: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/relances/${id}`, payload);
  }

  createRelancesManuelles(payload: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/relances/manuelles`, payload);
  }

  envoyerRelance(id: number): Observable<any> {
    return this.http.patch(`${this.apiUrl}/relances/${id}/envoyer`, {});
  }

  getHistoriqueRelancesContribuable(contribuableId: number, limit?: number): Observable<any> {
    const params: { [key: string]: any } = {};
    if (limit) params['limit'] = limit;
    const httpParams = createHttpParams(params);
    return this.http.get(`${this.apiUrl}/relances/contribuable/${contribuableId}/historique`, httpParams.keys().length > 0 ? { params: httpParams } : {});
  }

  getStatistiquesRelances(params?: any): Observable<any> {
    const httpParams = params ? createHttpParams(params) : new HttpParams();
    return this.http.get(`${this.apiUrl}/relances/statistiques`, httpParams.keys().length > 0 ? { params: httpParams } : {});
  }

  genererRelancesAutomatiques(body: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/relances/generer-automatique`, body);
  }
}

