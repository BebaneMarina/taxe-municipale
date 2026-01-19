import {Component, model, ModelSignal} from '@angular/core';
import {BadgeComponent} from '../../badge/badge.component';
import {dates, statusBilling} from '../../../../utils/seeder';
import {dateFormater, hiddenLetters, parseMount} from '../../../../utils/utils';
import { ModalComponent } from "../../modal/modal.component";
import { ClientDetailsComponent } from "../../modals/client-details/client-details.component";
import { CreateClientComponent } from "../../modals/create-client/create-client.component";

@Component({
  selector: 'app-balance-table',
  imports: [
    BadgeComponent,
    ModalComponent,
    ClientDetailsComponent,
    CreateClientComponent
],
  standalone : true,
  templateUrl: './balance-table.component.html',
  styleUrl: './balance-table.component.scss'
})
export class BalanceTableComponent {
  activeModalClient : ModelSignal<boolean> = model<boolean>(false);
  // activeModalAddClient:ModelSignal<boolean>= model<boolean>(false);
  protected readonly hiddenLetters = hiddenLetters;
  protected readonly parseMount = parseMount;
  protected readonly statusBilling = statusBilling;
  protected readonly dateFormater = dateFormater;
  protected readonly dates = dates;

  onActiveModalClient(value : boolean): void {
    this.activeModalClient.set(value);
  }
  // permet d'appeler la modal(contenu de la modal pour ajouter un client)
  // onactiveModalAddClient(value:boolean):void{
  //   this.activeModalAddClient.set(value);

  // }
}
