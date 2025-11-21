import { Component, model, ModelSignal } from '@angular/core';
import { ContenerComponent } from '../../items/contener/contener.component';
import { ModalComponent } from '../../items/modal/modal.component';
import { AdministrationsTableComponent } from '../../items/tables/administrations-table/administrations-table.component';

@Component({
  selector: 'app-administrations',
  imports: [ ContenerComponent, ModalComponent,AdministrationsTableComponent],
  templateUrl: './administrations.component.html',
  styleUrl: './administrations.component.scss'
})
export class AdministrationsComponent {
 activeModal : ModelSignal<boolean> = model<boolean>(false);
  onActiveModal(value : boolean) : void
  {
    this.activeModal.set(value);
  }
}
