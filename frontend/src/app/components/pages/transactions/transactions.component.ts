import {Component, model, ModelSignal, ViewChild} from '@angular/core';
import {ContenerComponent} from '../../items/contener/contener.component';
import {TransactionsTableComponent} from '../../items/tables/transactions-table/transactions-table.component';
import {ModalComponent} from '../../items/modal/modal.component';
import {TransactionDetailsComponent} from '../../items/modals/transaction-details/transaction-details.component';
import {CreateCollecteComponent} from '../../items/modals/create-collecte/create-collecte.component';
import {FormsModule} from '@angular/forms';
import {CommonModule} from '@angular/common';

@Component({
  selector: 'app-transactions',
  imports: [
    ContenerComponent,
    TransactionsTableComponent,
    ModalComponent,
    TransactionDetailsComponent,
    CreateCollecteComponent,
    FormsModule,
    CommonModule
  ],
  standalone : true,
  templateUrl: './transactions.component.html',
  styleUrl: './transactions.component.scss'
})
export class TransactionsComponent {
  activeModal : ModelSignal<boolean> = model<boolean>(false);
  activeModalCreate = model<boolean>(false);
  @ViewChild(TransactionsTableComponent) transactionsTable!: TransactionsTableComponent;
  
  filters = {
    telephone: '',
    dateDebut: '',
    dateFin: '',
    statut: ''
  };
  
  openCreateModal(): void {
    this.activeModalCreate.set(true);
  }
  
  onCollecteCreated(): void {
    this.activeModalCreate.set(false);
    // Recharger les collectes dans le tableau
    if (this.transactionsTable) {
      this.transactionsTable.loadCollectes();
    }
  }
  
  onActiveModal(value : boolean) : void
  {
    this.activeModal.set(value);
  }

  applyFilters(): void {
    if (this.transactionsTable) {
      this.transactionsTable.applyFilters(this.filters);
    }
  }

  resetFilters(): void {
    this.filters = {
      telephone: '',
      dateDebut: '',
      dateFin: '',
      statut: ''
    };
    this.applyFilters();
  }
}
