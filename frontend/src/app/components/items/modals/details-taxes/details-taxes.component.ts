import { Component, model, ModelSignal, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ContenerGrayComponent } from "../../contener-gray/contener-gray.component";
import { ModalComponent } from "../../modal/modal.component";
import { ModificationTaxesComponent } from "../modification-taxes/modification-taxes.component";
import { Taxe } from '../../../../interfaces/taxe.interface';

@Component({
  selector: 'app-details-taxes',
  imports: [CommonModule, ContenerGrayComponent, ModalComponent, ModificationTaxesComponent],
  templateUrl: './details-taxes.component.html',
  styleUrl: './details-taxes.component.scss'
})
export class DetailsTaxesComponent {
  @Input() taxe: Taxe | null = null;
  
  activeModalModifTaxe: ModelSignal<boolean> = model<boolean>(false);
  
  // appel modal modification taxe de la taxe
  onactiveModalModifTaxe(value: boolean): void {
    this.activeModalModifTaxe.set(value);
  }

  formatDate(dateString: string): string {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  formatNumber(value: number): string {
    if (isNaN(value) || value === null || value === undefined) {
      return '0';
    }
    return new Intl.NumberFormat('fr-FR', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  }

  getPeriodiciteLabel(periodicite: string): string {
    const labels: { [key: string]: string } = {
      'journaliere': 'Journalière',
      'hebdomadaire': 'Hebdomadaire',
      'mensuelle': 'Mensuelle',
      'trimestrielle': 'Trimestrielle'
    };
    return labels[periodicite] || periodicite;
  }
}
