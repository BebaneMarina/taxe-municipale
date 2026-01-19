import { Component, model, ModelSignal } from '@angular/core';
import { ModalComponent } from "../../modal/modal.component";
import { CreationRoleBackOfficeComponent } from "../../modals/creation-role-back-office/creation-role-back-office.component";

@Component({
  selector: 'app-administrations-table',
  imports: [ModalComponent, CreationRoleBackOfficeComponent],
  templateUrl: './administrations-table.component.html',
  styleUrl: './administrations-table.component.scss'
})
export class AdministrationsTableComponent {
[x: string]: any;
  activeModal : ModelSignal<boolean> = model<boolean>(false);
  activeModalCreationRole:ModelSignal<boolean> = model<boolean>(false);


  onActiveModal(value : boolean) : void
  {
    this.activeModal.set(value);
  }
  onactiveModalCreationRole(value : boolean):void{
    this.activeModalCreationRole.set(value);

  }
}
