import { Component, OnInit, OnDestroy, AfterViewInit, OnChanges, SimpleChanges, inject, Input, Output, EventEmitter } from '@angular/core';
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
export class MapInteractiveComponent implements OnInit, AfterViewInit, OnDestroy, OnChanges {
  private apiService: ApiService = inject(ApiService);
  
  private map: L.Map | null = null;
  private markerLayer: L.LayerGroup | null = null;
  private markers: L.Marker[] = [];
  private hasInitialFit = false;
  private readonly librevilleBounds = L.latLngBounds([0.15, 9.2], [0.6, 9.8]);
  
  @Input() filteredContribuables: any[] | null = null;
  
  @Output() contribuablesLoaded = new EventEmitter<any[]>();
  
  loading = false;
  contribuables: any[] = [];
  
  // Statistiques
  totalContribuables = 0;
  payes = 0;
  nonPayes = 0;
  tauxPaiement = 0;
  montantCollecteTotal = 0;
  nombreCollectesTotal = 0;
  ticketMoyen = 0;

  ngOnInit(): void {}

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['filteredContribuables'] && !changes['filteredContribuables'].firstChange) {
      const value = changes['filteredContribuables'].currentValue;
      if (Array.isArray(value)) {
        this.setFilteredContribuables(value);
      }
    }
  }

  ngAfterViewInit(): void {
    this.initMap();
    // Ne charger que si filteredContribuables n'est pas fourni
    if (!this.filteredContribuables) {
      this.loadContribuables();
    } else if (this.filteredContribuables.length > 0) {
      this.setFilteredContribuables(this.filteredContribuables);
    }
  }

  ngOnDestroy(): void {
    if (this.map) {
      this.map.remove();
    }
  }

  private initMap(): void {
    // Initialiser la carte centrée sur Libreville
    this.map = L.map('map', {
      center: this.librevilleBounds.getCenter(), // Libreville
      zoom: 13,
      zoomControl: true
    });

    // Ajouter la couche de tuiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 19
    }).addTo(this.map);

    this.markerLayer = L.layerGroup().addTo(this.map);
    this.hasInitialFit = false;
  }

  private loadContribuables(): void {
    this.loading = true;
    this.apiService.getContribuablesForMap(true).subscribe({
      next: (data: any[]) => {
        this.contribuables = data;
        this.calculateStats(data);
        this.updateMarkers();
        this.contribuablesLoaded.emit(data);
        this.loading = false;
      },
      error: (err: any) => {
        console.error('Erreur chargement contribuables:', err);
        this.loading = false;
      }
    });
  }

  private calculateStats(contribuables: any[]): void {
    this.totalContribuables = contribuables.length;
    this.payes = contribuables.filter(c => c.a_paye !== false).length;
    this.nonPayes = contribuables.filter(c => c.a_paye === false).length;
    this.tauxPaiement = this.totalContribuables > 0 
      ? Math.round((this.payes / this.totalContribuables) * 100) 
      : 0;

    this.montantCollecteTotal = contribuables.reduce((sum, c) => {
      const montant = typeof c.total_collecte === 'string'
        ? parseFloat(c.total_collecte)
        : Number(c.total_collecte || 0);
      return sum + (isNaN(montant) ? 0 : montant);
    }, 0);

    this.nombreCollectesTotal = contribuables.reduce((sum, c) => {
      const nb = Number(c.nombre_collectes || 0);
      return sum + (isNaN(nb) ? 0 : nb);
    }, 0);

    this.ticketMoyen = this.nombreCollectesTotal > 0
      ? this.montantCollecteTotal / this.nombreCollectesTotal
      : 0;
  }

  private updateMarkers(): void {
    if (!this.map || !this.markerLayer) return;

    // Nettoyer les anciens marqueurs
    this.markerLayer.clearLayers();
    this.markers = [];

    // Créer des marqueurs stylisés avec popup
    for (const contrib of this.contribuables) {
      const lat = parseFloat(contrib.latitude);
      const lng = parseFloat(contrib.longitude);

      if (isNaN(lat) || isNaN(lng)) continue;

      const aPaye = contrib.a_paye !== false;
      const markerColor = aPaye ? '#10B981' : '#EF4444';
      const markerBorder = aPaye ? '#059669' : '#DC2626';
      const pulseColor = aPaye ? 'rgba(16,185,129,0.35)' : 'rgba(239,68,68,0.35)';

      const icon = L.divIcon({
        html: `
          <div class="map-marker">
            <span class="marker-dot" style="
              background:${markerColor};
              border:3px solid ${markerBorder};
            "></span>
            <span class="marker-pulse" style="background:${pulseColor};"></span>
          </div>
        `,
        className: 'contribuable-marker',
        iconSize: [22, 22],
        iconAnchor: [11, 11]
      });

      const marker = L.marker([lat, lng], {
        icon
      });
      
      // Stocker les données pour les statistiques du cluster et les popups
      (marker as any).contribuableData = contrib;

      const popupContent = this.createPopup(contrib);
      marker.bindPopup(popupContent, {
        maxWidth: 320,
        className: 'custom-popup'
      });

      this.markers.push(marker);
      this.markerLayer.addLayer(marker);
    }

    if (this.map) {
      if (this.markers.length === 1) {
        const point = this.markers[0].getLatLng();
        this.map.setView(point, 16, { animate: this.hasInitialFit });
        this.hasInitialFit = true;
      } else if (this.markers.length > 1) {
        const bounds = L.featureGroup(this.markers).getBounds().pad(0.15);
        const safeBounds = bounds.isValid() ? bounds : this.librevilleBounds;
        this.map.fitBounds(safeBounds, { animate: this.hasInitialFit, maxZoom: 16 });
        this.hasInitialFit = true;
      } else {
        this.map.fitBounds(this.librevilleBounds, { animate: this.hasInitialFit });
      }
    }
  }

  private createPopup(contrib: any): string {
    const aPaye = contrib.a_paye !== false;
    const statusColor = aPaye ? '#10B981' : '#EF4444';
    const statusText = aPaye ? 'Payé' : 'Non payé';
    const statusIcon = aPaye ? '✓' : '✗';

    return `
      <div style="padding: 12px; font-family: system-ui, -apple-system, sans-serif;">
        <div style="
          background: ${statusColor};
          color: white;
          padding: 8px 12px;
          border-radius: 8px 8px 0 0;
          margin: -12px -12px 12px -12px;
          font-weight: bold;
        ">
          ${statusIcon} ${statusText}
        </div>
        <div style="margin-bottom: 8px;">
          <strong style="font-size: 16px; color: #1f2937;">${contrib.nom} ${contrib.prenom || ''}</strong>
        </div>
        <div style="font-size: 14px; color: #6b7280; line-height: 1.6;">
          <div><strong>Téléphone:</strong> ${contrib.telephone || 'N/A'}</div>
          <div><strong>Quartier:</strong> ${contrib.quartier || 'N/A'}</div>
          ${contrib.zone ? `<div><strong>Zone:</strong> ${contrib.zone}</div>` : ''}
          ${contrib.total_collecte ? `<div><strong>Total collecté:</strong> ${contrib.total_collecte.toLocaleString('fr-FR')} FCFA</div>` : ''}
          ${contrib.nombre_collectes ? `<div><strong>Nombre de collectes:</strong> ${contrib.nombre_collectes}</div>` : ''}
        </div>
      </div>
    `;
  }

  // Méthode publique pour définir les contribuables filtrés
  setFilteredContribuables(contribuables: any[]): void {
    const list = Array.isArray(contribuables) ? contribuables : [];
    this.contribuables = list;
    this.hasInitialFit = false;
    this.calculateStats(list);
    this.updateMarkers();
    this.refreshView();
  }

  // Méthode pour zoomer sur un point
  zoomToPoint(latitude: number, longitude: number, zoom: number = 16): void {
    if (this.map) {
      this.map.setView([latitude, longitude], zoom, { animate: true });
    }
  }

  refreshView(): void {
    if (this.map) {
      setTimeout(() => {
        this.map?.invalidateSize();
      }, 50);
    }
  }

  formatCurrency(amount: number): string {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'XAF',
      minimumFractionDigits: 0
    }).format(amount || 0);
  }

  formatNumber(value: number): string {
    return new Intl.NumberFormat('fr-FR').format(value || 0);
  }
}
