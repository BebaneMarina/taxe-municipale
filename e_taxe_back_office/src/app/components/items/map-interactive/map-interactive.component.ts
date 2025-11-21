import { Component, OnInit, OnDestroy, AfterViewInit, inject } from '@angular/core';
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
    // Cluster pour les contribuables
    this.contribuableCluster = L.markerClusterGroup({
      chunkedLoading: true,
      chunkDelay: 200,
      maxClusterRadius: 80,
      spiderfyOnMaxZoom: true,
      showCoverageOnHover: true,
      zoomToBoundsOnClick: true,
      disableClusteringAtZoom: 16,
      iconCreateFunction: (cluster: any) => {
        const count = cluster.getChildCount();
        let size = 'small';
        if (count > 100) size = 'large';
        else if (count > 20) size = 'medium';
        
        return L.divIcon({
          html: `<div class="cluster-marker cluster-${size}">
                   <span class="cluster-count">${count}</span>
                 </div>`,
          className: 'marker-cluster',
          iconSize: L.point(40, 40)
        });
      }
    });

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
          this.contribuables = data;
          this.updateContribuablesMarkers();
          checkComplete();
        },
        error: (err: any) => {
          console.error('Erreur chargement contribuables:', err);
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

    // Charger les zones non couvertes
    if (this.showUncoveredZones) {
      requestsCount++;
      this.apiService.getUncoveredZones().subscribe({
        next: (data: any[]) => {
          this.uncoveredZonesData = data;
          this.updateUncoveredZonesLayers();
          checkComplete();
        },
        error: (err: any) => {
          console.error('Erreur chargement zones non couvertes:', err);
          checkComplete();
        }
      });
    }

    if (requestsCount === 0) {
      this.loading = false;
    }
  }

  private createContribuableIcon(contrib: any): L.DivIcon {
    const isActive = contrib.actif !== false;
    const iconColor = isActive ? '#10B981' : '#6B7280';
    const borderColor = isActive ? '#059669' : '#4B5563';
    
    const svgIcon = `
      <svg width="32" height="40" viewBox="0 0 32 40" xmlns="http://www.w3.org/2000/svg">
        <path d="M16 0C7.164 0 0 7.164 0 16c0 8.836 16 24 16 24s16-15.164 16-24C32 7.164 24.836 0 16 0z" 
              fill="${iconColor}" 
              stroke="${borderColor}" 
              stroke-width="2"/>
        <circle cx="16" cy="12" r="5" fill="white"/>
        <path d="M8 22c0-4.418 3.582-8 8-8s8 3.582 8 8" fill="white"/>
      </svg>
    `;
    
    return L.divIcon({
      className: 'custom-marker',
      html: `<div class="marker-pin contribuable-marker" style="background: ${iconColor}; border-color: ${borderColor};">
               ${svgIcon}
               <div class="marker-pulse"></div>
             </div>`,
      iconSize: [32, 40],
      iconAnchor: [16, 40],
      popupAnchor: [0, -40]
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
    const statusBadge = contrib.actif 
      ? '<span class="status-badge active">Actif</span>' 
      : '<span class="status-badge inactive">Inactif</span>';
    
    return `
      <div class="popup-content contribuable-popup">
        <div class="popup-header">
          <h3>${contrib.nom} ${contrib.prenom || ''}</h3>
          ${statusBadge}
        </div>
        <div class="popup-body">
          ${contrib.photo_url ? `<img src="${contrib.photo_url}" alt="Photo" class="popup-photo">` : ''}
          <div class="popup-info">
            ${contrib.nom_activite ? `
              <div class="info-row">
                <svg class="info-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                </svg>
                <span><strong>Activité:</strong> ${contrib.nom_activite}</span>
              </div>
            ` : ''}
            <div class="info-row">
              <svg class="info-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path>
              </svg>
              <span>${contrib.telephone}</span>
            </div>
            ${contrib.adresse ? `
              <div class="info-row">
                <svg class="info-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                </svg>
                <span>${contrib.adresse}</span>
              </div>
            ` : ''}
            <div class="info-row">
              <svg class="info-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                </svg>
                <span><strong>Quartier:</strong> ${contrib.quartier || 'N/A'}</span>
            </div>
            ${contrib.zone ? `
              <div class="info-row">
                <svg class="info-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"></path>
                </svg>
                <span><strong>Zone:</strong> ${contrib.zone}</span>
              </div>
            ` : ''}
            ${contrib.collecteur ? `
              <div class="info-row">
                <svg class="info-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                </svg>
                <span><strong>Collecteur:</strong> ${contrib.collecteur}</span>
              </div>
            ` : ''}
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

  updateContribuablesMarkers(): void {
    if (!this.map || !this.contribuableCluster) return;

    // Supprimer les anciens marqueurs
    this.contribuableCluster.clearLayers();

    if (!this.showContribuables) {
      return;
    }

    // Ajouter les nouveaux marqueurs avec validation améliorée
    this.contribuables.forEach(contrib => {
      const lat = parseFloat(contrib.latitude);
      const lng = parseFloat(contrib.longitude);
      
      // Validation améliorée des coordonnées
      if (this.isValidCoordinate(lat, lng, contrib.quartier)) {
        const icon = this.createContribuableIcon(contrib);
        const marker = L.marker([lat, lng], { icon });
        
        // Popup améliorée
        const popupContent = this.createContribuablePopup(contrib);
        marker.bindPopup(popupContent, {
          maxWidth: 350,
          className: 'custom-popup'
        });

        this.contribuableCluster!.addLayer(marker);
      } else {
        console.warn(`Coordonnées invalides pour ${contrib.nom}: lat=${lat}, lng=${lng}, quartier=${contrib.quartier}`);
      }
    });

    // Ajouter le cluster à la carte
    if (this.map && this.showContribuables) {
      this.contribuableCluster.addTo(this.map);
    }

    this.adjustMapView();
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
