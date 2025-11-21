import { Component, model, ModelSignal } from '@angular/core';
import { ModalComponent } from "../../modal/modal.component";
import { CreateTaxeComponent } from "../create-taxe/create-taxe.component";

@Component({
  selector: 'app-modification-taxes',
  imports: [ModalComponent, CreateTaxeComponent],
  templateUrl: './modification-taxes.component.html',
  styleUrl: './modification-taxes.component.scss'
})
export class ModificationTaxesComponent {


}
