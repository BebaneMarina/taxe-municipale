import { Component, OnInit, OnDestroy, AfterViewInit, inject, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../../services/api.service';
import * as L from 'leaflet';
import 'leaflet.markercluster';
import 'leaflet.markercluster/dist/MarkerCluster.css';
import 'leaflet.markercluster/dist/MarkerCluster.Default.css';

// Types pour MarkerCluster
declare module 'leaflet' {
  namespace markerClusterGroup {
    interface MarkerClusterGroupOptions extends L.LayerOptions {
      chunkedLoading?: boolean;
      chunkInterval?: number;
      chunkDelay?: number;
      maxClusterRadius?: number;
      spiderfyOnMaxZoom?: boolean;
      showCoverageOnHover?: boolean;
      zoomToBoundsOnClick?: boolean;
      disableClusteringAtZoom?: number;
      removeOutsideVisibleBounds?: boolean;
      iconCreateFunction?: (cluster: any) => L.DivIcon;
    }
  }
  
  function markerClusterGroup(options?: markerClusterGroup.MarkerClusterGroupOptions): any;
}

@Component({
  selector: 'app-map-interactive',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './map-interactive.component.html',
  styleUrl: './map-interactive.component.scss'
})
export class MapInteractiveComponent implements OnInit, AfterViewInit, OnDestroy {
  private apiService: ApiService = inject(ApiService);
  
  private map: L.Map | null = null;
  private baseLayers: Record<'light' | 'dark', L.TileLayer> | null = null;
  private currentBaseLayer: L.TileLayer | null = null;
  private contribuableCluster: L.MarkerClusterGroup | null = null;
  private collecteurCluster: L.MarkerClusterGroup | null = null;
  private zones: L.GeoJSON[] = [];
  private uncoveredZones: L.GeoJSON[] = [];
  private refreshInterval: any = null;
  private lastBoundsUpdate = 0;
  private allContribuablesMarkers: L.Marker[] = [];
  
  // EventEmitter pour communiquer avec le parent
  @Output() contribuablesLoaded = new EventEmitter<any[]>();
  
  // Coordonnées approximatives de Libreville pour validation
  private readonly LIBREVILLE_BOUNDS = {
    minLat: 0.25,
    maxLat: 0.65,
    minLng: 9.25,
    maxLng: 9.65
  };
  
  loading = false;
  contribuables: any[] = [];
  collecteurs: any[] = [];
  zonesGeographiques: any[] = [];
  uncoveredZonesData: any[] = [];
  
  // Filtres
  showContribuables = true;
  showZones = true;
  showUncoveredZones = true;
  showCollecteurs = true;
  filterActif = true;
  autoRefresh = true;
  refreshIntervalSeconds = 30;
  mapStyle: 'light' | 'dark' = 'dark';
  controlsCollapsed = false;
  statsCollapsed = false;
  legendCollapsed = false;

  ngOnInit(): void {
    // Ne pas charger les données ici, attendre que la carte soit initialisée
  }

  ngAfterViewInit(): void {
    this.initMap();
  }

  ngOnDestroy(): void {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
    if (this.contribuableCluster) {
      this.contribuableCluster.clearLayers();
    }
    if (this.collecteurCluster) {
      this.collecteurCluster.clearLayers();
    }
    if (this.map) {
      this.map.remove();
    }
  }

  initMap(): void {
    // Centre sur Libreville, Gabon
    this.map = L.map('map', {
      center: [0.4162, 9.4673],
      zoom: 12,
      preferCanvas: true,
      zoomControl: true,
      attributionControl: true,
      maxZoom: 19,
      minZoom: 10
    });

    // Initialiser les clusters
    this.initClusters();

    // Ajouter la couche OpenStreetMap
    this.initBaseLayers();
    this.setBaseLayer(this.mapStyle);

    // Forcer le redimensionnement de la carte après un court délai
    setTimeout(() => {
      if (this.map) {
        this.map.invalidateSize();
        this.map.setZoom(this.map.getZoom());
      }
      this.loadData();
      if (this.autoRefresh) {
        this.startAutoRefresh();
      }
    }, 500);
  }

  private initClusters(): void {
    // Cluster pour les contribuables avec nuages de points (inspiré de la carte PM2.5)
    this.contribuableCluster = L.markerClusterGroup({
      chunkedLoading: true,
      chunkDelay: 100, // Plus rapide pour un rendu fluide
      maxClusterRadius: 50, // Encore plus réduit pour des nuages très denses comme PM2.5
      spiderfyOnMaxZoom: true,
      showCoverageOnHover: true,
      zoomToBoundsOnClick: false, // Désactiver le zoom automatique pour permettre la popup
      disableClusteringAtZoom: 13, // Désactiver le clustering plus tôt pour voir les points individuels (comme PM2.5)
      iconCreateFunction: (cluster: any) => {
        const count = cluster.getChildCount();
        const markers = cluster.getAllChildMarkers();
        
        // Calculer les statistiques du cluster
        let payeCount = 0;
        let nonPayeCount = 0;
        let totalCollecte = 0;
        
        markers.forEach((marker: any) => {
          const contrib = marker.contribuableData;
          if (contrib) {
            if (contrib.a_paye !== false) {
              payeCount++;
            } else {
              nonPayeCount++;
            }
            if (contrib.total_collecte) {
              totalCollecte += contrib.total_collecte;
            }
          }
        });
        
        const payeRatio = count > 0 ? (payeCount / count) * 100 : 0;
        
        // Déterminer la couleur du cluster selon le ratio payé/non payé
        let clusterColor = '#10B981'; // Vert par défaut (tous payés)
        let borderColor = '#059669';
        let className = 'cluster-marker cluster-paye';
        
        if (payeRatio < 50) {
          clusterColor = '#EF4444'; // Rouge si majoritairement non payé
          borderColor = '#DC2626';
          className = 'cluster-marker cluster-non-paye';
        } else if (payeRatio < 100) {
          clusterColor = '#F59E0B'; // Orange si mixte
          borderColor = '#D97706';
          className = 'cluster-marker cluster-mixte';
        }
        
        // Taille dynamique selon le nombre
        let size = 'small';
        let iconSize = 50;
        if (count > 200) {
          size = 'xlarge';
          iconSize = 70;
        } else if (count > 100) {
          size = 'large';
          iconSize = 60;
        } else if (count > 20) {
          size = 'medium';
          iconSize = 55;
        }
        
        // Créer le contenu HTML du cluster avec effet de nuage
        const html = `
          <div class="${className} cluster-${size}" style="background: ${clusterColor}; border-color: ${borderColor};">
            <div class="cluster-inner">
              <span class="cluster-count">${count}</span>
              <div class="cluster-stats">
                <span class="cluster-paye-stat">✓ ${payeCount}</span>
                <span class="cluster-non-paye-stat">✗ ${nonPayeCount}</span>
              </div>
            </div>
            <div class="cluster-pulse" style="background: ${clusterColor};"></div>
          </div>
        `;
        
        const icon = L.divIcon({
          html: html,
          className: 'marker-cluster',
          iconSize: L.point(iconSize, iconSize),
          iconAnchor: L.point(iconSize / 2, iconSize / 2)
        });
        
        // Stocker les données du cluster pour la popup
        (cluster as any).clusterData = {
          count,
          payeCount,
          nonPayeCount,
          totalCollecte,
          markers
        };
        
        return icon;
      }
    });

    // Ajouter un gestionnaire d'événement pour les clics sur les clusters
    if (this.contribuableCluster) {
      (this.contribuableCluster as any).on('clusterclick', (e: any) => {
        const cluster = e.layer;
        const clusterData = (cluster as any).clusterData;
        
        if (clusterData) {
          const popupContent = this.createClusterPopup(
            clusterData.count,
            clusterData.payeCount,
            clusterData.nonPayeCount,
            clusterData.totalCollecte,
            clusterData.markers
          );
          
          // Créer et ouvrir la popup
          const popup = L.popup({
            maxWidth: 350,
            minWidth: 280,
            className: 'custom-popup improved-popup-wrapper cluster-popup-wrapper',
            closeButton: true,
            autoPan: true,
            autoPanPadding: [30, 30],
            keepInView: true
          })
          .setLatLng(e.latlng)
          .setContent(popupContent)
          .openOn(this.map!);
        }
      });
    }

    // Cluster pour les collecteurs
    this.collecteurCluster = L.markerClusterGroup({
      chunkedLoading: true,
      chunkDelay: 200,
      maxClusterRadius: 100,
      spiderfyOnMaxZoom: true,
      showCoverageOnHover: true,
      zoomToBoundsOnClick: true,
      disableClusteringAtZoom: 16,
      iconCreateFunction: (cluster) => {
        const count = cluster.getChildCount();
        let size = 'small';
        if (count > 50) size = 'large';
        else if (count > 10) size = 'medium';
        
        return L.divIcon({
          html: `<div class="cluster-marker-collecteur cluster-${size}">
                   <span class="cluster-count">${count}</span>
                 </div>`,
          className: 'marker-cluster-collecteur',
          iconSize: L.point(40, 40)
        });
      }
    });
  }

  private initBaseLayers(): void {
    if (!this.map) return;

    this.baseLayers = {
      light: L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors © CARTO',
        maxZoom: 20,
        tileSize: 256,
        zoomOffset: 0,
        crossOrigin: true
      }),
      dark: L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/dark_all/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors © CARTO',
        maxZoom: 20,
        tileSize: 256,
        zoomOffset: 0,
        crossOrigin: true
      })
    };
  }

  setBaseLayer(style: 'light' | 'dark'): void {
    if (!this.map || !this.baseLayers) return;

    if (this.currentBaseLayer) {
      this.map.removeLayer(this.currentBaseLayer);
    }

    this.currentBaseLayer = this.baseLayers[style];
    this.currentBaseLayer.addTo(this.map);
    this.mapStyle = style;
  }

  onMapStyleChange(style: 'light' | 'dark'): void {
    if (style === this.mapStyle) return;
    this.setBaseLayer(style);
  }

  startAutoRefresh(): void {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
    this.refreshInterval = setInterval(() => {
      this.loadData();
    }, this.refreshIntervalSeconds * 1000);
  }

  stopAutoRefresh(): void {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
      this.refreshInterval = null;
    }
  }

  loadData(): void {
    this.loading = true;
    let requestsCount = 0;
    let completedRequests = 0;
    
    const checkComplete = () => {
      completedRequests++;
      if (completedRequests >= requestsCount) {
        this.loading = false;
      }
    };
    
    // Charger les contribuables
    if (this.showContribuables) {
      requestsCount++;
      this.apiService.getContribuablesForMap(this.filterActif).subscribe({
        next: (data: any[]) => {
          console.log(`✅ Données récupérées de la base: ${data.length} contribuables`);
          this.contribuables = data;
          this.updateContribuablesMarkers();
          // Émettre l'événement pour le composant parent
          this.contribuablesLoaded.emit(data);
          checkComplete();
        },
        error: (err: any) => {
          console.error('❌ Erreur chargement contribuables depuis la base:', err);
          checkComplete();
        }
      });
    }

    // Charger les collecteurs
    if (this.showCollecteurs) {
      requestsCount++;
      this.apiService.getCollecteursForMap(this.filterActif).subscribe({
        next: (data: any[]) => {
          this.collecteurs = data;
          this.updateCollecteursMarkers();
          checkComplete();
        },
        error: (err: any) => {
          console.error('Erreur chargement collecteurs:', err);
          checkComplete();
        }
      });
    }

    // Charger les zones géographiques
    if (this.showZones) {
      requestsCount++;
      this.apiService.getZonesGeographiques({ actif: true, limit: 1000 }).subscribe({
        next: (data: any[]) => {
          this.zonesGeographiques = data;
          this.updateZonesLayers();
          checkComplete();
        },
        error: (err: any) => {
          console.error('Erreur chargement zones:', err);
          checkComplete();
        }
      });
    }

    // Charger les zones non couvertes (avec gestion d'erreur améliorée)
    if (this.showUncoveredZones) {
      requestsCount++;
      this.apiService.getUncoveredZones().subscribe({
        next: (data: any[]) => {
          this.uncoveredZonesData = Array.isArray(data) ? data : [];
          this.updateUncoveredZonesLayers();
          checkComplete();
        },
        error: (err: any) => {
          // Ne pas bloquer l'affichage si cette requête échoue
          console.warn('⚠️ Zones non couvertes non disponibles:', err);
          this.uncoveredZonesData = [];
          checkComplete();
        }
      });
    } else {
      // Si les zones non couvertes sont désactivées, s'assurer qu'elles sont vides
      this.uncoveredZonesData = [];
    }

    if (requestsCount === 0) {
      this.loading = false;
    }
  }

  private createContribuableIcon(contrib: any): L.DivIcon {
    const isActive = contrib.actif !== false;
    // Couleur basée sur le statut de paiement : vert si payé, rouge si non payé
    // Style inspiré de la carte PM2.5 : points ronds simples et colorés
    const aPaye = contrib.a_paye !== false;
    
    // Couleurs similaires à PM2.5 : vert foncé (payé), rouge (non payé)
    const iconColor = aPaye ? '#10B981' : '#EF4444';
    const borderColor = aPaye ? '#059669' : '#DC2626';
    
    // Point rond simple comme sur la carte PM2.5 (plus petit et dense)
    return L.divIcon({
      className: 'custom-marker pm25-style',
      html: `<div class="point-marker ${aPaye ? 'paye' : 'non-paye'}" 
                   style="background: ${iconColor}; 
                          border: 2px solid ${borderColor};
                          width: 12px; 
                          height: 12px; 
                          border-radius: 50%;
                          box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                          cursor: pointer;
                          transition: transform 0.2s;">
             </div>`,
      iconSize: [12, 12],
      iconAnchor: [6, 6],
      popupAnchor: [0, -6]
    });
  }

  private createCollecteurIcon(collecteur: any): L.DivIcon {
    const svgIcon = `
      <svg width="32" height="40" viewBox="0 0 32 40" xmlns="http://www.w3.org/2000/svg">
        <path d="M16 0C7.164 0 0 7.164 0 16c0 8.836 16 24 16 24s16-15.164 16-24C32 7.164 24.836 0 16 0z" 
              fill="#3B82F6" 
              stroke="#1E40AF" 
              stroke-width="2"/>
        <path d="M16 10c-2.209 0-4 1.791-4 4s1.791 4 4 4 4-1.791 4-4-1.791-4-4-4zm0 10c-3.314 0-6 2.686-6 6v2h12v-2c0-3.314-2.686-6-6-6z" 
              fill="white"/>
      </svg>
    `;
    
    return L.divIcon({
      className: 'custom-marker-collecteur',
      html: `<div class="marker-pin collecteur-marker">
               ${svgIcon}
               <div class="marker-pulse"></div>
             </div>`,
      iconSize: [32, 40],
      iconAnchor: [16, 40],
      popupAnchor: [0, -40]
    });
  }

  // Méthode utilitaire pour échapper le HTML
  private escapeHtml(text: string): string {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  private isValidCoordinate(lat: number, lng: number, quartier?: string): boolean {
    // Vérification de base : coordonnées numériques valides
    if (isNaN(lat) || isNaN(lng)) {
      return false;
    }

    // Vérification géographique : dans les limites de Libreville
    if (lat < this.LIBREVILLE_BOUNDS.minLat || lat > this.LIBREVILLE_BOUNDS.maxLat ||
        lng < this.LIBREVILLE_BOUNDS.minLng || lng > this.LIBREVILLE_BOUNDS.maxLng) {
      return false;
    }

    // Si on a le quartier, on pourrait vérifier que le point est dans la zone
    // Pour l'instant, on se base sur les coordonnées approximatives
    return true;
  }

  private createContribuablePopup(contrib: any): string {
    const aPaye = contrib.a_paye !== false;
    const headerColor = aPaye ? '#10B981' : '#EF4444';
    const headerGradient = aPaye 
      ? 'linear-gradient(135deg, #10B981 0%, #059669 100%)'
      : 'linear-gradient(135deg, #EF4444 0%, #DC2626 100%)';
    
    const statusBadge = contrib.actif 
      ? '<span class="status-badge active">✓ Actif</span>' 
      : '<span class="status-badge inactive">✗ Inactif</span>';
    
    const paiementBadge = aPaye 
      ? '<span class="status-badge paye">✓ Payé</span>' 
      : '<span class="status-badge non-paye">✗ Non payé</span>';
    
    // Section taxes impayées améliorée
    const taxesImpayeesSection = contrib.taxes_impayees && contrib.taxes_impayees.length > 0
      ? `
        <div class="alert-section taxes-alert">
          <div class="alert-header">
            <svg class="alert-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
            </svg>
            <strong>Taxes impayées (${contrib.taxes_impayees.length})</strong>
          </div>
          <ul class="taxes-list">
            ${contrib.taxes_impayees.map((taxe: string) => `<li>${taxe}</li>`).join('')}
          </ul>
        </div>
      `
      : '';
    
    // Section statistiques améliorée avec design moderne
    const statsSection = contrib.nombre_collectes > 0
      ? `
        <div class="stats-section">
          <h4 class="section-title">Statistiques de collecte</h4>
          <div class="stats-grid">
            <div class="stat-card-mini">
              <div class="stat-icon-mini">💰</div>
              <div class="stat-content-mini">
                <div class="stat-value-mini">${(contrib.total_collecte || 0).toLocaleString('fr-FR')}</div>
                <div class="stat-label-mini">FCFA</div>
              </div>
            </div>
            <div class="stat-card-mini">
              <div class="stat-icon-mini">📊</div>
              <div class="stat-content-mini">
                <div class="stat-value-mini">${contrib.nombre_collectes || 0}</div>
                <div class="stat-label-mini">Collectes</div>
              </div>
            </div>
            ${contrib.derniere_collecte ? `
              <div class="stat-card-mini">
                <div class="stat-icon-mini">📅</div>
                <div class="stat-content-mini">
                  <div class="stat-value-mini">${new Date(contrib.derniere_collecte).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' })}</div>
                  <div class="stat-label-mini">Dernière</div>
                </div>
              </div>
            ` : ''}
          </div>
        </div>
      `
      : '';
    
    return `
      <div class="popup-content contribuable-popup improved-popup">
        <div class="popup-header-improved" style="background: ${headerGradient};">
          <div class="header-main">
            <div class="header-avatar">
              ${contrib.photo_url 
                ? `<img src="${contrib.photo_url}" alt="${contrib.nom}" class="avatar-img">`
                : `<div class="avatar-placeholder" style="background: rgba(255,255,255,0.2);">${(contrib.nom?.[0] || 'C').toUpperCase()}</div>`
              }
            </div>
            <div class="header-info">
              <h3 class="popup-title">${contrib.nom} ${contrib.prenom || ''}</h3>
              ${contrib.nom_activite ? `<p class="popup-subtitle">${contrib.nom_activite}</p>` : ''}
            </div>
          </div>
          <div class="header-badges">
            ${statusBadge}
            ${paiementBadge}
          </div>
        </div>
        
        <div class="popup-body-improved">
          ${contrib.photo_url && !contrib.photo_url.includes('avatar') ? `
            <div class="photo-section">
              <img src="${contrib.photo_url}" alt="Photo" class="popup-photo-improved">
            </div>
          ` : ''}
          
          <div class="info-sections">
            <div class="info-section">
              <h4 class="section-title">Informations de contact</h4>
              <div class="info-list">
                <div class="info-item-improved">
                  <div class="info-icon-wrapper">
                    <svg class="info-icon-improved" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path>
                    </svg>
                  </div>
                  <div class="info-text">
                    <span class="info-label">Téléphone</span>
                    <span class="info-value">${contrib.telephone}</span>
                  </div>
                </div>
                ${contrib.adresse ? `
                  <div class="info-item-improved">
                    <div class="info-icon-wrapper">
                      <svg class="info-icon-improved" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                      </svg>
                    </div>
                    <div class="info-text">
                      <span class="info-label">Adresse</span>
                      <span class="info-value">${contrib.adresse}</span>
                    </div>
                  </div>
                ` : ''}
              </div>
            </div>
            
            <div class="info-section">
              <h4 class="section-title">Localisation</h4>
              <div class="info-list">
                <div class="info-item-improved">
                  <div class="info-icon-wrapper">
                    <svg class="info-icon-improved" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                    </svg>
                  </div>
                  <div class="info-text">
                    <span class="info-label">Quartier</span>
                    <span class="info-value">${contrib.quartier || 'N/A'}</span>
                  </div>
                </div>
                ${contrib.zone ? `
                  <div class="info-item-improved">
                    <div class="info-icon-wrapper">
                      <svg class="info-icon-improved" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"></path>
                      </svg>
                    </div>
                    <div class="info-text">
                      <span class="info-label">Zone</span>
                      <span class="info-value">${contrib.zone}</span>
                    </div>
                  </div>
                ` : ''}
                ${contrib.collecteur ? `
                  <div class="info-item-improved">
                    <div class="info-icon-wrapper">
                      <svg class="info-icon-improved" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                      </svg>
                    </div>
                    <div class="info-text">
                      <span class="info-label">Collecteur</span>
                      <span class="info-value">${contrib.collecteur}</span>
                    </div>
                  </div>
                ` : ''}
              </div>
            </div>
            
            ${taxesImpayeesSection}
            ${statsSection}
          </div>
        </div>
      </div>
    `;
  }

  private createClusterPopup(count: number, payeCount: number, nonPayeCount: number, totalCollecte: number, markers: any[]): string {
    const payeRatio = count > 0 ? Math.round((payeCount / count) * 100) : 0;
    const statusColor = payeRatio >= 80 ? '#10B981' : payeRatio >= 50 ? '#F59E0B' : '#EF4444';
    const statusGradient = payeRatio >= 80 
      ? 'linear-gradient(135deg, #10B981 0%, #059669 100%)'
      : payeRatio >= 50 
      ? 'linear-gradient(135deg, #F59E0B 0%, #D97706 100%)'
      : 'linear-gradient(135deg, #EF4444 0%, #DC2626 100%)';
    const statusText = payeRatio >= 80 ? 'Bien payé' : payeRatio >= 50 ? 'Partiellement payé' : 'Majoritairement impayé';
    const statusIcon = payeRatio >= 80 ? '✓' : payeRatio >= 50 ? '⚠' : '✗';
    
    // Récupérer quelques exemples de contribuables du cluster
    const sampleContribuables = markers.slice(0, 5).map((marker: any) => {
      const contrib = marker.contribuableData;
      if (contrib) {
        return {
          nom: `${contrib.nom} ${contrib.prenom || ''}`.trim(),
          a_paye: contrib.a_paye !== false,
          telephone: contrib.telephone
        };
      }
      return null;
    }).filter((c: any) => c !== null);
    
    return `
      <div class="popup-content cluster-popup improved-popup">
        <div class="popup-header-improved" style="background: ${statusGradient};">
          <div class="header-main">
            <div class="header-avatar">
              <div class="avatar-placeholder" style="background: rgba(255,255,255,0.2); font-size: 1.25rem;">
                ${statusIcon}
              </div>
            </div>
            <div class="header-info">
              <h3 class="popup-title">Nuage de ${count} contribuable${count > 1 ? 's' : ''}</h3>
              <p class="popup-subtitle">${statusText}</p>
            </div>
          </div>
          <div class="header-badges">
            <span class="status-badge" style="background: rgba(255, 255, 255, 0.25); color: white;">
              ${payeRatio}% payé
            </span>
          </div>
        </div>
        
        <div class="popup-body-improved">
          <div class="info-sections">
            <div class="info-section">
              <h4 class="section-title">Statistiques du nuage</h4>
              <div class="cluster-stats-grid-improved">
                <div class="stat-item-improved stat-paye">
                  <div class="stat-icon-wrapper-improved" style="background: #D1FAE5;">
                    <svg class="stat-icon-svg" fill="none" stroke="#10B981" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                  </div>
                  <div class="stat-content-improved">
                    <div class="stat-value-improved">${payeCount}</div>
                    <div class="stat-label-improved">Payé${payeCount > 1 ? 's' : ''}</div>
                  </div>
                </div>
                <div class="stat-item-improved stat-non-paye">
                  <div class="stat-icon-wrapper-improved" style="background: #FEE2E2;">
                    <svg class="stat-icon-svg" fill="none" stroke="#EF4444" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                  </div>
                  <div class="stat-content-improved">
                    <div class="stat-value-improved">${nonPayeCount}</div>
                    <div class="stat-label-improved">Non payé${nonPayeCount > 1 ? 's' : ''}</div>
                  </div>
                </div>
                <div class="stat-item-improved stat-total">
                  <div class="stat-icon-wrapper-improved" style="background: #DBEAFE;">
                    <svg class="stat-icon-svg" fill="none" stroke="#3B82F6" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                  </div>
                  <div class="stat-content-improved">
                    <div class="stat-value-improved">${totalCollecte.toLocaleString('fr-FR')}</div>
                    <div class="stat-label-improved">FCFA</div>
                  </div>
                </div>
                <div class="stat-item-improved stat-ratio">
                  <div class="stat-icon-wrapper-improved" style="background: #FEF3C7;">
                    <svg class="stat-icon-svg" fill="none" stroke="#F59E0B" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                    </svg>
                  </div>
                  <div class="stat-content-improved">
                    <div class="stat-value-improved">${payeRatio}%</div>
                    <div class="stat-label-improved">Taux</div>
                  </div>
                </div>
              </div>
            </div>
            
            ${sampleContribuables.length > 0 ? `
              <div class="info-section">
                <h4 class="section-title">Exemples de contribuables (${sampleContribuables.length})</h4>
                <div class="sample-list-improved">
                  ${sampleContribuables.map((c: any) => `
                    <div class="sample-item-improved">
                      <div class="sample-status-improved ${c.a_paye ? 'paye' : 'non-paye'}">
                        ${c.a_paye ? '✓' : '✗'}
                      </div>
                      <div class="sample-info-improved">
                        <div class="sample-name-improved">${c.nom}</div>
                        <div class="sample-phone-improved">${c.telephone}</div>
                      </div>
                    </div>
                  `).join('')}
                </div>
                ${count > 5 ? `
                  <div class="more-info">
                    <p>+ ${count - 5} autre${count - 5 > 1 ? 's' : ''} contribuable${count - 5 > 1 ? 's' : ''} dans ce nuage</p>
                  </div>
                ` : ''}
              </div>
            ` : ''}
            
            <div class="info-section hint-section">
              <div class="hint-content">
                <svg class="hint-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <p>Cliquez sur le cluster pour zoomer ou utilisez le zoom pour voir les points individuels</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  private createCollecteurPopup(collecteur: any): string {
    return `
      <div class="popup-content collecteur-popup">
        <div class="popup-header">
          <h3>${collecteur.nom} ${collecteur.prenom || ''}</h3>
          <span class="badge-collecteur">Collecteur</span>
        </div>
        <div class="popup-body">
          <div class="popup-info">
            <div class="info-row">
              <svg class="info-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2"></path>
              </svg>
              <span><strong>Matricule:</strong> ${collecteur.matricule}</span>
            </div>
            <div class="info-row">
              <svg class="info-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path>
              </svg>
              <span>${collecteur.telephone}</span>
            </div>
            ${collecteur.statut ? `
              <div class="info-row">
                <svg class="info-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <span><strong>Statut:</strong> ${collecteur.statut}</span>
              </div>
            ` : ''}
            ${collecteur.date_derniere_connexion ? `
              <div class="info-row">
                <svg class="info-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <span><strong>Dernière connexion:</strong> ${new Date(collecteur.date_derniere_connexion).toLocaleString('fr-FR')}</span>
              </div>
            ` : ''}
          </div>
        </div>
      </div>
    `;
  }

  // Méthode publique pour définir les contribuables filtrés depuis le parent
  setFilteredContribuables(contribuables: any[]): void {
    // Éviter les mises à jour inutiles
    if (JSON.stringify(this.contribuables) === JSON.stringify(contribuables)) {
      return;
    }
    
    this.contribuables = contribuables;
    
    // Utiliser setTimeout pour éviter les conflits avec les autres opérations de la carte
    setTimeout(() => {
      this.updateContribuablesMarkers();
    }, 100);
  }

  // Méthode publique pour zoomer sur un point spécifique
  zoomToPoint(latitude: number, longitude: number, zoom: number = 16): void {
    if (this.map) {
      this.map.setView([latitude, longitude], zoom, { animate: true });
    }
  }

  updateContribuablesMarkers(): void {
    if (!this.map || !this.contribuableCluster) {
      console.warn('⚠️ Carte ou cluster non initialisé');
      return;
    }

    try {
      // Supprimer les anciens marqueurs de manière sécurisée
      if (this.contribuableCluster) {
        this.contribuableCluster.clearLayers();
      }
      this.allContribuablesMarkers = [];

      if (!this.showContribuables || !this.contribuables || this.contribuables.length === 0) {
        return;
      }

      console.log(`📍 Création de ${this.contribuables.length} marqueurs pour la carte`);

      // Ajouter les nouveaux marqueurs avec validation améliorée
      let validMarkers = 0;
      this.contribuables.forEach((contrib, index) => {
        try {
          const lat = parseFloat(contrib.latitude);
          const lng = parseFloat(contrib.longitude);
          
          // Validation améliorée des coordonnées
          if (this.isValidCoordinate(lat, lng, contrib.quartier)) {
            const icon = this.createContribuableIcon(contrib);
            const marker = L.marker([lat, lng], { icon });
            
            // Stocker les données du contribuable dans le marqueur pour les clusters
            (marker as any).contribuableData = contrib;
            
                // Popup améliorée avec gestion d'erreur robuste
            try {
              const popupContent = this.createContribuablePopup(contrib);
              if (popupContent && popupContent.trim().length > 0) {
                marker.bindPopup(popupContent, {
                  maxWidth: 400,
                  minWidth: 280,
                  className: 'custom-popup improved-popup-wrapper',
                  closeButton: true,
                  autoPan: true,
                  autoPanPadding: [50, 50],
                  keepInView: true
                });
              } else {
                throw new Error('Popup content is empty');
              }
            } catch (popupError) {
              console.warn(`⚠️ Erreur création popup pour ${contrib.nom}:`, popupError);
              // Popup de secours simple mais fonctionnelle
              const fallbackPopup = `
                <div class="popup-content contribuable-popup improved-popup">
                  <div class="popup-header-improved" style="background: ${contrib.a_paye !== false ? 'linear-gradient(135deg, #10B981 0%, #059669 100%)' : 'linear-gradient(135deg, #EF4444 0%, #DC2626 100%)'}; padding: 1.25rem;">
                    <h3 class="popup-title" style="margin: 0; font-size: 1.25rem; font-weight: 700; color: white;">${this.escapeHtml(contrib.nom || 'Contribuable')} ${this.escapeHtml(contrib.prenom || '')}</h3>
                  </div>
                  <div class="popup-body-improved" style="padding: 1.25rem; background: #fafafa;">
                    <div class="info-section" style="background: white; border-radius: 12px; padding: 1rem; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);">
                      <div class="info-item-improved" style="display: flex; align-items: flex-start; gap: 0.75rem; padding: 0.5rem;">
                        <div class="info-icon-wrapper" style="width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; background: #f3f4f6; border-radius: 8px;">
                          <svg style="width: 20px; height: 20px; color: #6b7280;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path>
                          </svg>
                        </div>
                        <div class="info-text" style="flex: 1; display: flex; flex-direction: column; gap: 0.25rem;">
                          <span class="info-label" style="font-size: 0.75rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">Téléphone</span>
                          <span class="info-value" style="font-size: 0.9375rem; color: #1f2937; font-weight: 500;">${this.escapeHtml(contrib.telephone || 'N/A')}</span>
                        </div>
                      </div>
                      <div class="info-item-improved" style="display: flex; align-items: flex-start; gap: 0.75rem; padding: 0.5rem;">
                        <div class="info-icon-wrapper" style="width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; background: #f3f4f6; border-radius: 8px;">
                          <svg style="width: 20px; height: 20px; color: #6b7280;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                          </svg>
                        </div>
                        <div class="info-text" style="flex: 1; display: flex; flex-direction: column; gap: 0.25rem;">
                          <span class="info-label" style="font-size: 0.75rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">Quartier</span>
                          <span class="info-value" style="font-size: 0.9375rem; color: #1f2937; font-weight: 500;">${this.escapeHtml(contrib.quartier || 'N/A')}</span>
                        </div>
                      </div>
                      <div class="info-item-improved" style="display: flex; align-items: flex-start; gap: 0.75rem; padding: 0.5rem;">
                        <div class="info-icon-wrapper" style="width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; background: ${contrib.a_paye !== false ? '#D1FAE5' : '#FEE2E2'}; border-radius: 8px;">
                          <svg style="width: 20px; height: 20px; color: ${contrib.a_paye !== false ? '#10B981' : '#EF4444'};" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                          </svg>
                        </div>
                        <div class="info-text" style="flex: 1; display: flex; flex-direction: column; gap: 0.25rem;">
                          <span class="info-label" style="font-size: 0.75rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">Statut</span>
                          <span class="info-value" style="font-size: 0.9375rem; color: #1f2937; font-weight: 500;">${contrib.a_paye !== false ? '✓ Payé' : '✗ Non payé'}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              `;
              marker.bindPopup(fallbackPopup, {
                maxWidth: 350,
                minWidth: 280,
                className: 'custom-popup improved-popup-wrapper',
                closeButton: true,
                autoPan: true,
                autoPanPadding: [50, 50],
                keepInView: true
              });
            }

            this.contribuableCluster!.addLayer(marker);
            this.allContribuablesMarkers.push(marker);
            validMarkers++;
          } else {
            console.warn(`⚠️ Coordonnées invalides pour ${contrib.nom}: lat=${lat}, lng=${lng}`);
          }
        } catch (markerError) {
          console.warn(`⚠️ Erreur création marqueur ${index}:`, markerError);
        }
      });

      console.log(`✅ ${validMarkers} marqueurs valides ajoutés au cluster`);

      // Ajouter le cluster à la carte de manière stable
      if (this.map && this.showContribuables && validMarkers > 0) {
        // Vérifier si le cluster n'est pas déjà sur la carte
        if (!this.map.hasLayer(this.contribuableCluster)) {
          this.contribuableCluster.addTo(this.map);
        }
      }

      // Ajuster la vue seulement si nécessaire
      if (validMarkers > 0) {
        // Utiliser requestAnimationFrame pour une mise à jour fluide
        requestAnimationFrame(() => {
          this.adjustMapView();
        });
      }
    } catch (error) {
      console.error('❌ Erreur lors de la mise à jour des marqueurs:', error);
    }
  }

  updateCollecteursMarkers(): void {
    if (!this.map || !this.collecteurCluster) return;

    // Supprimer les anciens marqueurs
    this.collecteurCluster.clearLayers();

    if (!this.showCollecteurs) {
      return;
    }

    // Ajouter les nouveaux marqueurs
    this.collecteurs.forEach((collecteur: any) => {
      const lat = parseFloat(collecteur.latitude);
      const lng = parseFloat(collecteur.longitude);
      
      if (this.isValidCoordinate(lat, lng)) {
        const icon = this.createCollecteurIcon(collecteur);
        const marker = L.marker([lat, lng], { icon });
        
        // Popup améliorée
        const popupContent = this.createCollecteurPopup(collecteur);
        marker.bindPopup(popupContent, {
          maxWidth: 350,
          className: 'custom-popup'
        });

        this.collecteurCluster!.addLayer(marker);
      }
    });

    // Ajouter le cluster à la carte
    if (this.map && this.showCollecteurs) {
      this.collecteurCluster.addTo(this.map);
    }

    this.adjustMapView();
  }

  updateZonesLayers(): void {
    // Supprimer les anciennes zones
    this.zones.forEach(zone => {
      if (this.map) {
        this.map.removeLayer(zone);
      }
    });
    this.zones = [];

    if (!this.map || !this.showZones) return;

    // Ajouter les nouvelles zones avec styles améliorés
    this.zonesGeographiques.forEach((zoneData: any) => {
      const geoJsonLayer = L.geoJSON(zoneData.geometry as any, {
        style: (feature) => {
          const color = this.getZoneColor(zoneData.type_zone);
          return {
            color: color,
            fillColor: color,
            fillOpacity: 0.15,
            weight: 2.5,
            opacity: 0.8,
            dashArray: zoneData.type_zone === 'quartier' ? '5, 5' : undefined
          };
        },
        onEachFeature: (feature, layer) => {
          layer.bindPopup(`
            <div class="popup-content zone-popup">
              <h3 class="font-bold text-lg mb-2">${zoneData.nom}</h3>
              <div class="info-row">
                <svg class="info-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path>
                </svg>
                <span><strong>Type:</strong> ${zoneData.type_zone}</span>
              </div>
              ${zoneData.code ? `
                <div class="info-row">
                  <svg class="info-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14"></path>
                  </svg>
                  <span><strong>Code:</strong> ${zoneData.code}</span>
                </div>
              ` : ''}
            </div>
          `, {
            maxWidth: 300,
            className: 'custom-popup'
          });
        }
      }).addTo(this.map!);

      this.zones.push(geoJsonLayer);
    });
  }

  getZoneColor(typeZone: string): string {
    switch (typeZone) {
      case 'arrondissement': return '#3B82F6'; // Bleu
      case 'secteur': return '#10B981'; // Vert
      case 'quartier': return '#F59E0B'; // Orange
      default: return '#6B7280'; // Gris
    }
  }

  toggleContribuables(): void {
    this.showContribuables = !this.showContribuables;
    if (this.contribuableCluster && this.map) {
      if (this.showContribuables) {
        this.contribuableCluster.addTo(this.map);
      } else {
        this.map.removeLayer(this.contribuableCluster);
      }
    }
    this.updateContribuablesMarkers();
  }

  toggleZones(): void {
    this.showZones = !this.showZones;
    this.updateZonesLayers();
  }

  toggleCollecteurs(): void {
    this.showCollecteurs = !this.showCollecteurs;
    if (this.collecteurCluster && this.map) {
      if (this.showCollecteurs) {
        this.collecteurCluster.addTo(this.map);
      } else {
        this.map.removeLayer(this.collecteurCluster);
      }
    }
    this.updateCollecteursMarkers();
  }

  toggleUncoveredZones(): void {
    this.showUncoveredZones = !this.showUncoveredZones;
    this.updateUncoveredZonesLayers();
  }

  toggleLegend(): void {
    this.legendCollapsed = !this.legendCollapsed;
  }

  updateUncoveredZonesLayers(): void {
    // Supprimer les anciennes zones non couvertes
    this.uncoveredZones.forEach(zone => {
      if (this.map) {
        this.map.removeLayer(zone);
      }
    });
    this.uncoveredZones = [];

    if (!this.map || !this.showUncoveredZones) return;

    // Ajouter les zones non couvertes avec un style amélioré
    this.uncoveredZonesData.forEach((zoneData: any) => {
      const geoJsonLayer = L.geoJSON(zoneData.geometry as any, {
        style: {
          color: '#EF4444',
          fillColor: '#EF4444',
          fillOpacity: 0.25,
          weight: 3,
          opacity: 0.9,
          dashArray: '10, 5'
        },
        onEachFeature: (feature, layer) => {
          layer.bindPopup(`
            <div class="popup-content uncovered-zone-popup">
              <h3 class="font-bold text-lg mb-2 text-red-600">⚠️ Zone non couverte</h3>
              <div class="info-row">
                <svg class="info-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                </svg>
                <span><strong>Nom:</strong> ${zoneData.nom}</span>
              </div>
              <div class="info-row">
                <svg class="info-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path>
                </svg>
                <span><strong>Type:</strong> ${zoneData.type_zone}</span>
              </div>
              <div class="info-row">
                <svg class="info-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                </svg>
                <span class="text-red-600"><strong>Contribuables:</strong> ${zoneData.contribuables_count || 0}</span>
              </div>
            </div>
          `, {
            maxWidth: 300,
            className: 'custom-popup'
          });
        }
      }).addTo(this.map!);

      this.uncoveredZones.push(geoJsonLayer);
    });
  }

  onFilterChange(): void {
    this.loadData();
  }

  onAutoRefreshChange(): void {
    if (this.autoRefresh) {
      this.startAutoRefresh();
    } else {
      this.stopAutoRefresh();
    }
  }

  toggleControls(): void {
    this.controlsCollapsed = !this.controlsCollapsed;
  }

  toggleStats(): void {
    this.statsCollapsed = !this.statsCollapsed;
  }

  private adjustMapView(): void {
    if (!this.map) return;

    const now = Date.now();
    if (now - this.lastBoundsUpdate < 2000) {
      return;
    }

    const points: L.LatLngExpression[] = [];

    // Récupérer les points des contribuables
    if (this.contribuableCluster && this.showContribuables) {
      this.contribuableCluster.eachLayer((layer: any) => {
        if (layer instanceof L.Marker) {
          const latLng = layer.getLatLng();
          points.push([latLng.lat, latLng.lng]);
        }
      });
    }

    // Récupérer les points des collecteurs
    if (this.collecteurCluster && this.showCollecteurs) {
      this.collecteurCluster.eachLayer((layer: any) => {
        if (layer instanceof L.Marker) {
          const latLng = layer.getLatLng();
          points.push([latLng.lat, latLng.lng]);
        }
      });
    }

    if (points.length === 0) return;

    if (points.length === 1) {
      this.map.setView(points[0] as L.LatLngExpression, 14);
    } else {
      const bounds = L.latLngBounds(points as L.LatLngBoundsLiteral);
      this.map.fitBounds(bounds.pad(0.15), { animate: true });
    }

    this.lastBoundsUpdate = now;
  }
}
