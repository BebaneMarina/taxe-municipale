import { Component, model, ModelSignal } from '@angular/core';

@Component({
  selector: 'app-creation-role-back-office',
  imports: [],
  templateUrl: './creation-role-back-office.component.html',
  styleUrl: './creation-role-back-office.component.scss'
})
export class CreationRoleBackOfficeComponent {
 activeModalCreationRole:ModelSignal<boolean> = model<boolean>(false);
  activeModalDetailRole:ModelSignal<boolean> = model<boolean>(false);

  // appel modal modification taxe de la taxe
  onactiveModalCreationRole(value : boolean):void{
  this.activeModalCreationRole.set(value);
  console.log(value);
  }
  // appel modal detail role
  onactiveModalDetailRole(value : boolean):void{
  this.activeModalDetailRole.set(value);
  console.log(value);
  }
}
