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
  
  // Filtres
  dateDebut: string = '';
  dateFin: string = '';
  collecteurId: number | null = null;
  taxeId: number | null = null;
  
  // Statistiques
  totalCollecte: number = 0;
  nombreTransactions: number = 0;
  collecteParMoyen: any = {};
  collecteParCollecteur: any[] = [];
  collecteParTaxe: any[] = [];
  
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
    const params: any = {
      limit: 1000,
      date_debut: this.dateDebut,
      date_fin: this.dateFin
    };
    
    if (this.collecteurId) {
      params.collecteur_id = this.collecteurId;
    }
    if (this.taxeId) {
      params.taxe_id = this.taxeId;
    }

    this.apiService.getCollectes(params).subscribe({
      next: (collectes: any[]) => {
        this.processData(collectes);
        this.loading = false;
      },
      error: (err) => {
        console.error('Erreur lors du chargement des rapports:', err);
        this.loading = false;
      }
    });
  }

  processData(collectes: any[]): void {
    const validees = collectes.filter(c => c.statut === 'validee');
    
    // Total collecte
    this.totalCollecte = validees.reduce((sum, c) => sum + parseFloat(c.montant || 0), 0);
    this.nombreTransactions = validees.length;
    
    // Par moyen de paiement
    this.collecteParMoyen = {};
    validees.forEach(c => {
      const moyen = c.type_paiement || 'autre';
      if (!this.collecteParMoyen[moyen]) {
        this.collecteParMoyen[moyen] = 0;
      }
      this.collecteParMoyen[moyen] += parseFloat(c.montant || 0);
    });
    
    // Par collecteur
    const parCollecteur: { [key: number]: { nom: string, montant: number } } = {};
    validees.forEach(c => {
      const id = c.collecteur_id;
      if (!parCollecteur[id]) {
        parCollecteur[id] = {
          nom: c.collecteur?.nom || `Collecteur ${id}`,
          montant: 0
        };
      }
      parCollecteur[id].montant += parseFloat(c.montant || 0);
    });
    this.collecteParCollecteur = Object.values(parCollecteur)
      .sort((a, b) => b.montant - a.montant)
      .slice(0, 10);
    
    // Par taxe
    const parTaxe: { [key: number]: { nom: string, montant: number } } = {};
    validees.forEach(c => {
      const id = c.taxe_id;
      if (!parTaxe[id]) {
        parTaxe[id] = {
          nom: c.taxe?.nom || `Taxe ${id}`,
          montant: 0
        };
      }
      parTaxe[id].montant += parseFloat(c.montant || 0);
    });
    this.collecteParTaxe = Object.values(parTaxe)
      .sort((a, b) => b.montant - a.montant)
      .slice(0, 10);
    
    // Préparer les données pour le graphique
    this.prepareChartData(validees);
  }

  prepareChartData(collectes: any[]): void {
    const monthlyData: { [key: string]: number } = {};
    const months = ['jan', 'fev', 'mar', 'avr', 'mai', 'jun', 'jul', 'aou', 'sep', 'oct', 'nov', 'dec'];
    
    collectes.forEach(collecte => {
      const date = new Date(collecte.date_collecte);
      const monthKey = `${date.getFullYear()}-${date.getMonth()}`;
      if (!monthlyData[monthKey]) {
        monthlyData[monthKey] = 0;
      }
      monthlyData[monthKey] += parseFloat(collecte.montant || 0);
    });
    
    const labels = months;
    const data = months.map((_, index) => {
      const date = new Date();
      date.setMonth(date.getMonth() - (11 - index));
      const key = `${date.getFullYear()}-${date.getMonth()}`;
      return monthlyData[key] || 0;
    });
    
    this.chartData = {
      labels,
      datasets: [{
        label: 'Collecte mensuelle (FCFA)',
        data,
        fill: true,
        borderColor: "rgba(12, 82, 156, 1)",
        tension: 0.1,
      }]
    };
  }

  onFilterChange(): void {
    this.loadRapports();
  }

  exportExcel(): void {
    // TODO: Implémenter l'export Excel
    alert('Export Excel - À implémenter');
  }

  exportPDF(): void {
    // TODO: Implémenter l'export PDF
    alert('Export PDF - À implémenter');
  }

  formatNumber(value: number): string {
    return new Intl.NumberFormat('fr-FR').format(value);
  }

  getMoyenPaiementLabel(moyen: string): string {
    const labels: { [key: string]: string } = {
      'especes': 'Espèces',
      'mobile_money': 'Mobile Money',
      'carte': 'Carte'
    };
    return labels[moyen] || moyen;
  }

  // Exposer Object pour le template
  Object = Object;
  
  getCollecteParMoyenKeys(): string[] {
    return Object.keys(this.collecteParMoyen);
  }
}

