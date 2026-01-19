import {Component, inject, model, ModelSignal, OnInit} from '@angular/core';
import {ContenerComponent} from '../../items/contener/contener.component';
import {CardActionComponent} from '../../items/card-action/card-action.component';
import {H1Component} from '../../items/texts/h1/h1.component';
import {ChartComponent} from '../../items/chart/chart.component';
import {TransactionsTableComponent} from '../../items/tables/transactions-table/transactions-table.component';
import {ModalComponent} from '../../items/modal/modal.component';
import {CreatePaiementLinkComponent} from '../../items/modals/create-paiement-link/create-paiement-link.component';
import {TransactionDetailsComponent} from '../../items/modals/transaction-details/transaction-details.component';
import {ApiService} from '../../../services/api.service';
import {CommonModule} from '@angular/common';

@Component({
  selector: 'app-dashboard',
  imports: [
    ContenerComponent,
    CardActionComponent,
    H1Component,
    ChartComponent,
    TransactionsTableComponent,
    ModalComponent,
    CreatePaiementLinkComponent,
    TransactionDetailsComponent,
    CommonModule
  ],
  standalone : true,
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent implements OnInit {
  active : ModelSignal<boolean> = model<boolean>(false);
  activeModalDetail : ModelSignal<boolean> = model<boolean>(false);
  
  private apiService = inject(ApiService);
  
  // Statistiques
  totalCollecte: number = 0;
  nombreCollecteurs: number = 0;
  transactionsValidees: number = 0;
  totalClients: number = 0;
  loading: boolean = true;
  
  // Données pour les graphiques
  chartData: any = {
    labels: [],
    datasets: []
  };

  ngOnInit(): void {
    this.loadStatistics();
  }

  loadStatistics(): void {
    this.loading = true;
    
    // Charger les collectes avec relations pour calculer le total
    this.apiService.getCollectes({ limit: 1000 }).subscribe({
      next: (collectes: any[]) => {
        console.log('Collectes reçues:', collectes);
        console.log('Première collecte:', collectes[0]);
        
        // Filtrer les collectes validées (statut peut être 'completed' ou 'validee')
        const collectesValidees = collectes.filter(c => 
          (c.statut === 'completed' || c.statut === 'validee') && !c.annule
        );
        
        console.log('Collectes validées:', collectesValidees.length);
        
        this.totalCollecte = collectesValidees
          .reduce((sum, c) => sum + parseFloat(c.montant || 0), 0);
        this.transactionsValidees = collectesValidees.length;
        
        console.log('Total collecte:', this.totalCollecte);
        console.log('Transactions validées:', this.transactionsValidees);
        
        // Préparer les données pour le graphique
        this.prepareChartData(collectesValidees);
        
        this.loading = false;
      },
      error: (err) => {
        console.error('Erreur lors du chargement des collectes:', err);
        this.loading = false;
      }
    });

    // Charger les collecteurs
    this.apiService.getCollecteurs({ limit: 1000 }).subscribe({
      next: (collecteurs: any[]) => {
        this.nombreCollecteurs = collecteurs.filter(c => c.actif).length;
      },
      error: (err) => {
        console.error('Erreur lors du chargement des collecteurs:', err);
      }
    });

    // Charger les contribuables
    this.apiService.getContribuables({ limit: 1000 }).subscribe({
      next: (contribuables: any[]) => {
        this.totalClients = contribuables.filter(c => c.actif).length;
      },
      error: (err) => {
        console.error('Erreur lors du chargement des contribuables:', err);
      }
    });
  }

  prepareChartData(collectes: any[]): void {
    // Grouper par mois
    const monthlyData: { [key: string]: number } = {};
    const months = ['jan', 'fev', 'mar', 'avr', 'mai', 'jun', 'jul', 'aou', 'sep', 'oct', 'nov', 'dec'];
    
    // Filtrer les collectes validées
    const collectesValidees = collectes.filter(c => 
      (c.statut === 'completed' || c.statut === 'validee') && !c.annule
    );
    
    collectesValidees.forEach(collecte => {
      if (collecte.date_collecte) {
        const date = new Date(collecte.date_collecte);
        if (!isNaN(date.getTime())) {
          const monthKey = `${date.getFullYear()}-${date.getMonth()}`;
          if (!monthlyData[monthKey]) {
            monthlyData[monthKey] = 0;
          }
          monthlyData[monthKey] += parseFloat(collecte.montant || 0);
        }
      }
    });
    
    // Préparer les données pour le graphique (12 derniers mois)
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

  formatNumber(value: number): string {
    if (isNaN(value) || value === null || value === undefined) {
      return '0';
    }
    // Formater avec des espaces comme séparateurs de milliers
    return new Intl.NumberFormat('fr-FR', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  }

  onActiveModal(value : boolean)
  {
    this.active.set(value);
  }
  onActiveModalDetail(value : boolean)
  {
    this.active.set(value);
  }
}
