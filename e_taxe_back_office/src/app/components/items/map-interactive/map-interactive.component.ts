import { Component, OnInit, OnDestroy, AfterViewInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../../services/api.service';
import * as L from 'leaflet';

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
  private markers: L.Marker[] = [];
  private collecteurMarkers: L.Marker[] = [];
  private zones: L.GeoJSON[] = [];
  private uncoveredZones: L.GeoJSON[] = [];
  private refreshInterval: any = null;
  
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
  refreshIntervalSeconds = 30; // Rafraîchir toutes les 30 secondes

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
    if (this.map) {
      this.map.remove();
    }
  }

  initMap(): void {
    // Centre sur Libreville, Gabon
    this.map = L.map('map', {
      center: [0.4162, 9.4673],
      zoom: 12
    });

    // Ajouter la couche OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 19
    }).addTo(this.map);

    // Charger les données après l'initialisation de la carte
    setTimeout(() => {
      this.loadData();
      if (this.autoRefresh) {
        this.startAutoRefresh();
      }
    }, 500);
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

  updateContribuablesMarkers(): void {
    // Supprimer les anciens marqueurs
    this.markers.forEach(marker => {
      if (this.map) {
        this.map.removeLayer(marker);
      }
    });
    this.markers = [];

    if (!this.map || !this.showContribuables) return;

    // Ajouter les nouveaux marqueurs
    this.contribuables.forEach(contrib => {
      if (contrib.latitude && contrib.longitude) {
        const icon = L.divIcon({
          className: 'custom-marker',
          html: `<div class="marker-pin">
                   <span class="marker-icon">📍</span>
                 </div>`,
          iconSize: [30, 30],
          iconAnchor: [15, 30]
        });

        const marker = L.marker([contrib.latitude, contrib.longitude], { icon })
          .addTo(this.map!);

        // Popup avec informations
        const popupContent = `
          <div class="popup-content">
            <h3 class="font-bold text-lg mb-2">${contrib.nom} ${contrib.prenom || ''}</h3>
            ${contrib.nom_activite ? `<p class="text-sm text-gray-600 mb-1"><strong>Activité:</strong> ${contrib.nom_activite}</p>` : ''}
            <p class="text-sm text-gray-600 mb-1"><strong>Téléphone:</strong> ${contrib.telephone}</p>
            ${contrib.adresse ? `<p class="text-sm text-gray-600 mb-1"><strong>Adresse:</strong> ${contrib.adresse}</p>` : ''}
            <p class="text-sm text-gray-600 mb-1"><strong>Quartier:</strong> ${contrib.quartier || 'N/A'}</p>
            <p class="text-sm text-gray-600 mb-1"><strong>Zone:</strong> ${contrib.zone || 'N/A'}</p>
            ${contrib.collecteur ? `<p class="text-sm text-gray-600 mb-1"><strong>Collecteur:</strong> ${contrib.collecteur}</p>` : ''}
            ${contrib.photo_url ? `<img src="${contrib.photo_url}" alt="Photo" class="mt-2 max-w-full h-32 object-cover rounded">` : ''}
          </div>
        `;
        marker.bindPopup(popupContent);

        this.markers.push(marker);
      }
    });
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

    // Ajouter les nouvelles zones
    this.zonesGeographiques.forEach((zoneData: any) => {
      const geoJsonLayer = L.geoJSON(zoneData.geometry as any, {
        style: (feature) => {
          const color = this.getZoneColor(zoneData.type_zone);
          return {
            color: color,
            fillColor: color,
            fillOpacity: 0.2,
            weight: 2
          };
        },
        onEachFeature: (feature, layer) => {
          layer.bindPopup(`
            <div class="popup-content">
              <h3 class="font-bold text-lg mb-2">${zoneData.nom}</h3>
              <p class="text-sm text-gray-600 mb-1"><strong>Type:</strong> ${zoneData.type_zone}</p>
              ${zoneData.code ? `<p class="text-sm text-gray-600 mb-1"><strong>Code:</strong> ${zoneData.code}</p>` : ''}
            </div>
          `);
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
    this.updateContribuablesMarkers();
  }

  toggleZones(): void {
    this.showZones = !this.showZones;
    this.updateZonesLayers();
  }

  toggleCollecteurs(): void {
    this.showCollecteurs = !this.showCollecteurs;
    this.updateCollecteursMarkers();
  }

  toggleUncoveredZones(): void {
    this.showUncoveredZones = !this.showUncoveredZones;
    this.updateUncoveredZonesLayers();
  }

  updateCollecteursMarkers(): void {
    // Supprimer les anciens marqueurs
    this.collecteurMarkers.forEach(marker => {
      if (this.map) {
        this.map.removeLayer(marker);
      }
    });
    this.collecteurMarkers = [];

    if (!this.map || !this.showCollecteurs) return;

    // Ajouter les nouveaux marqueurs pour les collecteurs
    this.collecteurs.forEach((collecteur: any) => {
      if (collecteur.latitude && collecteur.longitude) {
        const icon = L.divIcon({
          className: 'custom-marker-collecteur',
          html: `<div class="marker-pin-collecteur">
                   <span class="marker-icon-collecteur">👤</span>
                 </div>`,
          iconSize: [30, 30],
          iconAnchor: [15, 30]
        });

        const marker = L.marker([collecteur.latitude, collecteur.longitude], { icon })
          .addTo(this.map!);

        // Popup avec informations
        const popupContent = `
          <div class="popup-content">
            <h3 class="font-bold text-lg mb-2">${collecteur.nom} ${collecteur.prenom || ''}</h3>
            <p class="text-sm text-gray-600 mb-1"><strong>Matricule:</strong> ${collecteur.matricule}</p>
            <p class="text-sm text-gray-600 mb-1"><strong>Téléphone:</strong> ${collecteur.telephone}</p>
            <p class="text-sm text-gray-600 mb-1"><strong>Statut:</strong> ${collecteur.statut || 'N/A'}</p>
            <p class="text-sm text-gray-600 mb-1"><strong>État:</strong> ${collecteur.etat || 'N/A'}</p>
            ${collecteur.date_derniere_connexion ? `<p class="text-sm text-gray-600 mb-1"><strong>Dernière connexion:</strong> ${new Date(collecteur.date_derniere_connexion).toLocaleString('fr-FR')}</p>` : ''}
          </div>
        `;
        marker.bindPopup(popupContent);

        this.collecteurMarkers.push(marker);
      }
    });
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

    // Ajouter les zones non couvertes avec un style différent
    this.uncoveredZonesData.forEach((zoneData: any) => {
      const geoJsonLayer = L.geoJSON(zoneData.geometry as any, {
        style: {
          color: '#EF4444', // Rouge pour zones non couvertes
          fillColor: '#EF4444',
          fillOpacity: 0.3,
          weight: 3,
          dashArray: '10, 5'
        },
        onEachFeature: (feature, layer) => {
          layer.bindPopup(`
            <div class="popup-content">
              <h3 class="font-bold text-lg mb-2 text-red-600">⚠️ Zone non couverte</h3>
              <p class="text-sm text-gray-600 mb-1"><strong>Nom:</strong> ${zoneData.nom}</p>
              <p class="text-sm text-gray-600 mb-1"><strong>Type:</strong> ${zoneData.type_zone}</p>
              <p class="text-sm text-red-600 mb-1"><strong>Contribuables:</strong> ${zoneData.contribuables_count}</p>
            </div>
          `);
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
}
