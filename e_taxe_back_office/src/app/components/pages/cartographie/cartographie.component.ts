import { Component, OnInit, ViewChild, AfterViewInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MapInteractiveComponent } from '../../items/map-interactive/map-interactive.component';
import { ApiService } from '../../../services/api.service';
import { Chart, ChartConfiguration, ChartType, registerables } from 'chart.js';
import { firstValueFrom } from 'rxjs';

Chart.register(...registerables);

interface DashboardStats {
  total_contribuables: number;
  contribuables_payes: number;
  contribuables_impayes: number;
  taux_paiement: number;
  total_collecte: number;
  collecte_aujourd_hui: number;
  collecte_ce_mois: number;
  nombre_collecteurs: number;
  zones_couvertes: number;
  zones_non_couvertes: number;
}

interface ZoneStats {
  nom: string;
  total_contribuables: number;
  contribuables_payes: number;
  taux_paiement: number;
  total_collecte: number;
}

@Component({
  selector: 'app-cartographie',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MapInteractiveComponent
  ],
  templateUrl: './cartographie.component.html',
  styleUrl: './cartographie.component.scss'
})
export class CartographieComponent implements OnInit, AfterViewInit {
  @ViewChild(MapInteractiveComponent) mapComponent!: MapInteractiveComponent;
  
  private apiService = inject(ApiService);

  // Statistiques du dashboard
  stats: DashboardStats = {
    total_contribuables: 0,
    contribuables_payes: 0,
    contribuables_impayes: 0,
    taux_paiement: 0,
    total_collecte: 0,
    collecte_aujourd_hui: 0,
    collecte_ce_mois: 0,
    nombre_collecteurs: 0,
    zones_couvertes: 0,
    zones_non_couvertes: 0
  };

  zoneStats: ZoneStats[] = [];
  loading = true;
  error = '';

  // Filtres
  searchTerm = '';
  showPayes = true;
  showNonPayes = true;
  selectedZone: string = '';

  // Données
  allContribuables: any[] = [];
  filteredContribuables: any[] = [];
  zones: any[] = [];
  quartiers: any[] = [];

  // Charts
  paiementChart: Chart | null = null;
  collecteChart: Chart | null = null;
  zonesChart: Chart | null = null;

  // Vue active
  activeView: 'dashboard' | 'map' | 'analytics' = 'dashboard';

  ngOnInit(): void {
    this.loadData();
  }

  ngAfterViewInit(): void {
    // Les graphiques seront initialisés après le chargement des données
  }

  async loadData(): Promise<void> {
    this.loading = true;
    this.error = '';
    try {
      const [
        contribuablesResult,
        zonesResult,
        collecteursResult,
        statsResult,
        evolutionResult
      ] = await Promise.allSettled([
        firstValueFrom(this.apiService.getContribuablesForMap(true)),
        firstValueFrom(this.apiService.getZones(true)),
        firstValueFrom(this.apiService.getCollecteurs({ actif: true })),
        this.fetchCartographieStats(),
        firstValueFrom(this.apiService.getEvolutionJournaliere(7)).catch(() => null)
      ]);

      this.allContribuables = contribuablesResult.status === 'fulfilled' && contribuablesResult.value
        ? contribuablesResult.value
        : [];
      this.filteredContribuables = [...this.allContribuables];
      this.scheduleMapRefresh();

      this.zones = zonesResult.status === 'fulfilled' && zonesResult.value
        ? zonesResult.value
        : [];

      const collecteurs = collecteursResult.status === 'fulfilled' && Array.isArray(collecteursResult.value)
        ? collecteursResult.value
        : [];

      const statsCarto = statsResult.status === 'fulfilled' && statsResult.value
        ? statsResult.value
        : {};

      const evolutionData = evolutionResult.status === 'fulfilled'
        ? evolutionResult.value
        : null;

      if (statsCarto && statsCarto.stats_par_zone) {
        this.stats = {
          total_contribuables: statsCarto.total_contribuables || 0,
          contribuables_payes: statsCarto.contribuables_payes || 0,
          contribuables_impayes: statsCarto.contribuables_impayes || 0,
          taux_paiement: statsCarto.taux_paiement || 0,
          total_collecte: Number(statsCarto.total_collecte || 0),
          collecte_aujourd_hui: Number(statsCarto.collecte_aujourd_hui || 0),
          collecte_ce_mois: Number(statsCarto.collecte_ce_mois || 0),
          nombre_collecteurs: statsCarto.nombre_collecteurs || collecteurs.length,
          zones_couvertes: statsCarto.zones_couvertes || 0,
          zones_non_couvertes: statsCarto.zones_non_couvertes || 0
        };
        this.zoneStats = (statsCarto.stats_par_zone || []).map((z: any) => ({
          nom: z.nom,
          total_contribuables: z.total_contribuables,
          contribuables_payes: z.contribuables_payes,
          taux_paiement: z.taux_paiement,
          total_collecte: Number(z.total_collecte || 0)
        }));
      } else {
        this.calculateStats(this.allContribuables, statsCarto, collecteurs);
        this.calculateZoneStats();
      }

      if (evolutionData && this.collecteChart) {
        this.updateCollecteChart(evolutionData);
      }

      setTimeout(() => {
        this.initCharts();
      }, 300);
    } catch (err: any) {
      this.error = 'Erreur lors du chargement des données';
      console.error('Erreur:', err);
    } finally {
      this.loading = false;
    }
  }

  calculateStats(contribuables: any[], statsGen: any, collecteurs: any[]): void {
    const total = contribuables.length;
    const payes = contribuables.filter(c => c.a_paye).length;
    const impayes = total - payes;
    const taux = total > 0 ? (payes / total) * 100 : 0;

    this.stats = {
      total_contribuables: total,
      contribuables_payes: payes,
      contribuables_impayes: impayes,
      taux_paiement: taux,
      total_collecte: parseFloat(statsGen?.total_collecte || 0),
      collecte_aujourd_hui: parseFloat(statsGen?.collecte_aujourd_hui || 0),
      collecte_ce_mois: parseFloat(statsGen?.collecte_ce_mois || 0),
      nombre_collecteurs: collecteurs.length,
      zones_couvertes: this.zones.length,
      zones_non_couvertes: 0
    };
  }

  calculateZoneStats(): void {
    const zoneMap = new Map<string, ZoneStats>();

    this.allContribuables.forEach(contrib => {
      const zoneName = contrib.zone || 'Non assigné';
      if (!zoneMap.has(zoneName)) {
        zoneMap.set(zoneName, {
          nom: zoneName,
          total_contribuables: 0,
          contribuables_payes: 0,
          taux_paiement: 0,
          total_collecte: 0
        });
      }

      const zone = zoneMap.get(zoneName)!;
      zone.total_contribuables++;
      if (contrib.a_paye) {
        zone.contribuables_payes++;
      }
      zone.total_collecte += contrib.total_collecte || 0;
    });

    // Calculer les taux
    zoneMap.forEach(zone => {
      zone.taux_paiement = zone.total_contribuables > 0 
        ? (zone.contribuables_payes / zone.total_contribuables) * 100 
        : 0;
    });

    this.zoneStats = Array.from(zoneMap.values())
      .sort((a, b) => b.total_collecte - a.total_collecte)
      .slice(0, 10);
  }

  initCharts(): void {
    this.initPaiementChart();
    this.initCollecteChart();
    this.initZonesChart();
  }

  initPaiementChart(): void {
    if (this.paiementChart) {
      this.paiementChart.destroy();
    }
    const ctx = document.getElementById('paiementChart') as HTMLCanvasElement;
    if (!ctx) return;

    const config: ChartConfiguration = {
      type: 'doughnut',
      data: {
        labels: ['Payés', 'Impayés'],
        datasets: [{
          data: [this.stats.contribuables_payes, this.stats.contribuables_impayes],
          backgroundColor: ['#10b981', '#ef4444'],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              padding: 15,
              font: { size: 12 }
            }
          }
        }
      }
    };

    this.paiementChart = new Chart(ctx, config);
  }

  initCollecteChart(): void {
    if (this.collecteChart) {
      this.collecteChart.destroy();
    }
    const ctx = document.getElementById('collecteChart') as HTMLCanvasElement;
    if (!ctx) return;

    // Labels par défaut (7 derniers jours)
    const labels = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'];
    const data = [0, 0, 0, 0, 0, 0, 0];

    const config: ChartConfiguration = {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: 'Collecte (FCFA)',
          data: data,
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          tension: 0.4,
          fill: true,
          pointRadius: 4,
          pointHoverRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                return new Intl.NumberFormat('fr-FR', { 
                  style: 'currency', 
                  currency: 'XAF',
                  minimumFractionDigits: 0 
                }).format(context.parsed.y);
              }
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: function(value) {
                const numValue = typeof value === 'number' ? value : Number(value);
                if (numValue >= 1000000) {
                  return (numValue / 1000000).toFixed(1) + 'M';
                } else if (numValue >= 1000) {
                  return (numValue / 1000).toFixed(0) + 'K';
                }
                return numValue.toString();
              }
            }
          }
        }
      }
    };

    this.collecteChart = new Chart(ctx, config);
  }

  updateCollecteChart(evolutionData: any): void {
    if (!this.collecteChart || !evolutionData) return;

    // Formater les labels de dates
    const labels = evolutionData.jours?.map((jour: string) => {
      const date = new Date(jour);
      return date.toLocaleDateString('fr-FR', { weekday: 'short' });
    }) || ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'];

    this.collecteChart.data.labels = labels;
    this.collecteChart.data.datasets[0].data = evolutionData.montants || [0, 0, 0, 0, 0, 0, 0];
    this.collecteChart.update();
  }

  initZonesChart(): void {
    if (this.zonesChart) {
      this.zonesChart.destroy();
    }
    const ctx = document.getElementById('zonesChart') as HTMLCanvasElement;
    if (!ctx) return;

    const topZones = this.zoneStats.slice(0, 5);

    const config: ChartConfiguration = {
      type: 'bar',
      data: {
        labels: topZones.map(z => z.nom),
        datasets: [{
          label: 'Taux de paiement (%)',
          data: topZones.map(z => z.taux_paiement),
          backgroundColor: '#8b5cf6',
          borderRadius: 8
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            max: 100,
            ticks: {
              callback: function(value) {
                return value + '%';
              }
            }
          }
        }
      }
    };

    this.zonesChart = new Chart(ctx, config);
  }

  applyFilters(): void {
    let filtered = [...this.allContribuables];

    // Filtre par recherche
    if (this.searchTerm) {
      const term = this.searchTerm.toLowerCase();
      filtered = filtered.filter(c => 
        c.nom?.toLowerCase().includes(term) ||
        c.prenom?.toLowerCase().includes(term) ||
        c.telephone?.includes(term) ||
        c.nom_activite?.toLowerCase().includes(term)
      );
    }

    // Le filtre payés / impayés est géré au niveau de la carte via les couches

    // Filtre par zone
    if (this.selectedZone) {
      filtered = filtered.filter(c => c.zone === this.selectedZone);
    }

    this.filteredContribuables = filtered;
    
    // Mettre à jour la carte
    if (this.mapComponent) {
      this.mapComponent.setFilteredContribuables(filtered);
        this.scheduleMapRefresh();
    }
  }

  clearFilters(): void {
    this.searchTerm = '';
    this.showPayes = true;
    this.showNonPayes = true;
    this.selectedZone = '';
    this.applyFilters();
  }

  switchView(view: 'dashboard' | 'map' | 'analytics'): void {
    this.activeView = view;
    if (view === 'map' && this.mapComponent) {
      setTimeout(() => {
        this.mapComponent.setFilteredContribuables(this.filteredContribuables ?? []);
        this.mapComponent.refreshView();
      }, 100);
    }
  }

  formatNumber(num: number): string {
    return new Intl.NumberFormat('fr-FR').format(num);
  }

  formatCurrency(amount: number): string {
    return new Intl.NumberFormat('fr-FR', { 
      style: 'currency', 
      currency: 'XAF',
      minimumFractionDigits: 0 
    }).format(amount);
  }

  getProgressColor(value: number): string {
    if (value >= 80) return 'bg-green-500';
    if (value >= 50) return 'bg-yellow-500';
    return 'bg-red-500';
  }

  getZoneColor(taux: number): string {
    if (taux >= 80) return '#10b981';
    if (taux >= 50) return '#f59e0b';
    return '#ef4444';
  }

  private async fetchCartographieStats(): Promise<any> {
    try {
      const stats = await firstValueFrom(this.apiService.getStatistiquesCartographie());
      return stats || {};
    } catch (err) {
      console.warn('Erreur chargement stats cartographie:', err);
      try {
        const statsGen = await firstValueFrom(this.apiService.getStatistiquesGenerales());
        if (statsGen) {
          return {
            total_collecte: statsGen.total_collecte || 0,
            collecte_aujourd_hui: statsGen.collecte_aujourd_hui || 0,
            collecte_ce_mois: statsGen.collecte_ce_mois || 0
          };
        }
      } catch (e) {
        console.error('Erreur fallback stats:', e);
      }
      return {};
    }
  }

  private scheduleMapRefresh(): void {
    if (this.mapComponent) {
      setTimeout(() => this.mapComponent?.refreshView(), 80);
    }
  }
}
