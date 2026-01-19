import { Component, OnInit, inject } from '@angular/core';
import { ApiService } from '../../../services/api.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ContenerComponent } from '../../items/contener/contener.component';
import { ChartComponent } from '../../items/chart/chart.component';

@Component({
  selector: 'app-rapports',
  imports: [CommonModule, FormsModule, ContenerComponent, ChartComponent],
  standalone: true,
  templateUrl: './rapports.component.html',
  styleUrl: './rapports.component.scss'
})
export class RapportsComponent implements OnInit {
  private apiService = inject(ApiService);
  
  loading: boolean = true;
  exportingCSV: boolean = false;
  exportingPDF: boolean = false;
  
  // Filtres
  dateDebut: string = '';
  dateFin: string = '';
  collecteurId: number | null = null;
  taxeId: number | null = null;
  
  // Statistiques générales
  statistiquesGenerales: any = {
    total_collecte: 0,
    nombre_transactions: 0,
    moyenne_par_transaction: 0,
    nombre_collecteurs_actifs: 0,
    nombre_taxes_actives: 0,
    transactions_aujourd_hui: 0,
    collecte_aujourd_hui: 0,
    transactions_ce_mois: 0,
    collecte_ce_mois: 0
  };
  
  // Statistiques détaillées
  collecteParMoyen: any[] = [];
  topCollecteurs: any[] = [];
  topTaxes: any[] = [];
  evolutionTemporelle: any[] = [];
  
  // Données pour graphiques
  chartData: any = null;
  
  // Options
  collecteurs: any[] = [];
  taxes: any[] = [];

  ngOnInit(): void {
    this.initializeDates();
    this.loadOptions();
    this.loadRapports();
  }

  initializeDates(): void {
    const today = new Date();
    const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
    this.dateDebut = firstDay.toISOString().split('T')[0];
    this.dateFin = today.toISOString().split('T')[0];
  }

  loadOptions(): void {
    this.apiService.getCollecteurs({ limit: 1000 }).subscribe({
      next: (data) => this.collecteurs = data,
      error: (err) => console.error('Erreur chargement collecteurs:', err)
    });

    this.apiService.getTaxes({ limit: 1000 }).subscribe({
      next: (data) => this.taxes = data,
      error: (err) => console.error('Erreur chargement taxes:', err)
    });
  }

  loadRapports(): void {
    this.loading = true;
    
    const params: any = {};
    if (this.dateDebut) params.date_debut = this.dateDebut;
    if (this.dateFin) params.date_fin = this.dateFin;
    if (this.collecteurId) params.collecteur_id = this.collecteurId;
    if (this.taxeId) params.taxe_id = this.taxeId;

    // Charger toutes les statistiques en parallèle
    this.apiService.getStatistiquesGenerales(params).subscribe({
      next: (data) => {
        this.statistiquesGenerales = data;
      },
      error: (err) => {
        console.error('Erreur chargement statistiques générales:', err);
      }
    });

    this.apiService.getCollecteParMoyen(params).subscribe({
      next: (data) => {
        this.collecteParMoyen = data;
      },
      error: (err) => {
        console.error('Erreur chargement collecte par moyen:', err);
      }
    });

    this.apiService.getTopCollecteurs(10, params).subscribe({
      next: (data) => {
        this.topCollecteurs = data;
      },
      error: (err) => {
        console.error('Erreur chargement top collecteurs:', err);
      }
    });

    this.apiService.getTopTaxes(10, params).subscribe({
      next: (data) => {
        this.topTaxes = data;
      },
      error: (err) => {
        console.error('Erreur chargement top taxes:', err);
      }
    });

    // Charger l'évolution temporelle pour le graphique
    const evolutionParams = { ...params, periode: 'jour' };
    this.apiService.getEvolutionTemporelle(evolutionParams).subscribe({
      next: (data) => {
        this.evolutionTemporelle = data;
        this.prepareChartData(data);
        this.loading = false;
      },
      error: (err) => {
        console.error('Erreur chargement évolution temporelle:', err);
        this.loading = false;
      }
    });
  }

  prepareChartData(evolution: any[]): void {
    if (!evolution || evolution.length === 0) {
      this.chartData = null;
      return;
    }

    const labels = evolution.map(item => {
      // Formater la date selon le format de la période
      if (item.periode.includes('-')) {
        const parts = item.periode.split('-');
        if (parts.length === 3) {
          // Format date (YYYY-MM-DD)
          const date = new Date(item.periode);
          return date.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' });
        } else if (parts.length === 2 && parts[0].startsWith('S')) {
          // Format semaine (SXX-YYYY)
          return item.periode;
        } else {
          // Format mois (YYYY-MM)
          const [year, month] = parts;
          const monthNames = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc'];
          return `${monthNames[parseInt(month) - 1]} ${year}`;
        }
      }
      return item.periode;
    });

    const data = evolution.map(item => parseFloat(item.montant_total?.toString() || '0'));

    this.chartData = {
      labels,
      datasets: [{
        label: 'Collecte quotidienne (FCFA)',
        data,
        fill: true,
        backgroundColor: 'rgba(12, 82, 156, 0.1)',
        borderColor: 'rgba(12, 82, 156, 1)',
        tension: 0.4,
        pointRadius: 3,
        pointHoverRadius: 5
      }]
    };
  }

  onFilterChange(): void {
    this.loadRapports();
  }

  exportExcel(): void {
    if (this.exportingCSV) return; // Éviter les doubles clics
    
    this.exportingCSV = true;
    const params: any = {};
    if (this.dateDebut) params.date_debut = this.dateDebut;
    if (this.dateFin) params.date_fin = this.dateFin;
    if (this.collecteurId) params.collecteur_id = this.collecteurId;
    if (this.taxeId) params.taxe_id = this.taxeId;
    
    this.apiService.exportRapportCSV(params).subscribe({
      next: (blob: Blob) => {
        // Créer un lien de téléchargement
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        
        // Générer le nom de fichier avec la date
        const dateStr = new Date().toISOString().split('T')[0];
        link.download = `rapport_collecte_${dateStr}.csv`;
        
        // Déclencher le téléchargement
        document.body.appendChild(link);
        link.click();
        
        // Nettoyer
        setTimeout(() => {
          document.body.removeChild(link);
          window.URL.revokeObjectURL(url);
          this.exportingCSV = false;
        }, 100);
      },
      error: (err) => {
        console.error('Erreur lors de l\'export CSV:', err);
        this.exportingCSV = false;
        const errorMsg = err.error?.detail || err.message || 'Erreur lors de l\'export CSV. Veuillez réessayer.';
        alert(errorMsg);
      }
    });
  }

  exportPDF(): void {
    if (this.exportingPDF) return; // Éviter les doubles clics
    
    this.exportingPDF = true;
    const params: any = {};
    if (this.dateDebut) params.date_debut = this.dateDebut;
    if (this.dateFin) params.date_fin = this.dateFin;
    if (this.collecteurId) params.collecteur_id = this.collecteurId;
    if (this.taxeId) params.taxe_id = this.taxeId;
    
    this.apiService.exportRapportPDF(params).subscribe({
      next: (blob: Blob) => {
        // Vérifier que le blob n'est pas vide
        if (blob.size === 0) {
          this.exportingPDF = false;
          alert('Le fichier PDF généré est vide. Veuillez réessayer.');
          return;
        }
        
        // Créer un lien de téléchargement
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        
        // Générer le nom de fichier avec la date
        const dateStr = new Date().toISOString().split('T')[0];
        link.download = `rapport_collecte_${dateStr}.pdf`;
        
        // Déclencher le téléchargement
        document.body.appendChild(link);
        link.click();
        
        // Nettoyer
        setTimeout(() => {
          document.body.removeChild(link);
          window.URL.revokeObjectURL(url);
          this.exportingPDF = false;
        }, 100);
      },
      error: (err) => {
        console.error('Erreur lors de l\'export PDF:', err);
        this.exportingPDF = false;
        const errorMsg = err.error?.detail || err.message || 'Erreur lors de l\'export PDF. Veuillez réessayer.';
        alert(errorMsg);
      }
    });
  }

  formatNumber(value: number | string | null | undefined): string {
    if (value === null || value === undefined) return '0';
    const num = typeof value === 'string' ? parseFloat(value) : value;
    if (isNaN(num)) return '0';
    return new Intl.NumberFormat('fr-FR').format(num);
  }

  getMoyenPaiementLabel(moyen: string): string {
    const labels: { [key: string]: string } = {
      'especes': 'Espèces',
      'mobile_money': 'Mobile Money',
      'carte': 'Carte bancaire',
      'virement': 'Virement',
      'autre': 'Autre'
    };
    return labels[moyen.toLowerCase()] || moyen;
  }

  getCollecteurFullName(collecteur: any): string {
    if (!collecteur) return '';
    return `${collecteur.collecteur_nom || ''} ${collecteur.collecteur_prenom || ''}`.trim() || `Collecteur ${collecteur.collecteur_id}`;
  }
}
