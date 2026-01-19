import {Component, inject, model, ModelSignal} from '@angular/core';
import {ContenerComponent} from '../../items/contener/contener.component';
import {ClientsTableComponent} from '../../items/tables/clients-table/clients-table.component';
import {ModalComponent} from '../../items/modal/modal.component';
import {CreateClientComponent} from '../../items/modals/create-client/create-client.component';

@Component({
  selector: 'app-clients',
  standalone : true,
  imports: [
    ContenerComponent,
    ClientsTableComponent,
    ModalComponent,
    CreateClientComponent
  ],
  templateUrl: './clients.component.html',
  styleUrl: './clients.component.scss'
})
export class ClientsComponent {
  activeModal : ModelSignal<boolean> = model<boolean>(false);
  
  onActiveModal(value : boolean) : void {
    this.activeModal.set(value);
  }
  
  onClientCreated(): void {
    this.activeModal.set(false);
    // La table se rechargera automatiquement via le signal
  }
}
