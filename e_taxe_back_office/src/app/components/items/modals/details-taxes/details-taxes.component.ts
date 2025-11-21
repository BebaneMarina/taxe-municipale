import { Component, model, ModelSignal } from '@angular/core';
import { ContenerGrayComponent } from "../../contener-gray/contener-gray.component";
import { ModalComponent } from "../../modal/modal.component";
import { ModificationTaxesComponent } from "../modification-taxes/modification-taxes.component";

@Component({
  selector: 'app-details-taxes',
  imports: [ContenerGrayComponent, ModalComponent, ModificationTaxesComponent],
  templateUrl: './details-taxes.component.html',
  styleUrl: './details-taxes.component.scss'
})
export class DetailsTaxesComponent {
 activeModalModifTaxe:ModelSignal<boolean> = model<boolean>(false);
  // appel modal modification taxe de la taxe
  onactiveModalModifTaxe(value : boolean):void{
  this.activeModalModifTaxe.set(value);
  console.log(value);
  }
}
