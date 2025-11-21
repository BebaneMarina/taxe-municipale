import {Component, model, ModelSignal, signal} from '@angular/core';
import {ContenerComponent} from '../../items/contener/contener.component';
import {ProfilComponent} from '../../items/settings/profil/profil.component';
import {NotificationComponent} from '../../items/settings/notification/notification.component';
import {SecuriteComponent} from '../../items/settings/securite/securite.component';
import {EquipeComponent} from '../../items/settings/equipe/equipe.component';
import {ModalComponent} from '../../items/modal/modal.component';
import {UserInvitationComponent} from '../../items/modals/user-invitation/user-invitation.component';
import {UserDetailsComponent} from '../../items/modals/user-details/user-details.component';
import {ParametrageComponent} from '../../items/settings/parametrage/parametrage.component';

@Component({
  selector: 'app-settings',
  standalone : true,
  imports: [
    ContenerComponent,
    ProfilComponent,
    NotificationComponent,
    SecuriteComponent,
    EquipeComponent,
    ModalComponent,
    UserInvitationComponent,
    UserDetailsComponent,
    ParametrageComponent
  ],
  templateUrl: './settings.component.html',
  styleUrl: './settings.component.scss'
})
export class SettingsComponent {
  activeModal : ModelSignal<boolean>= model<boolean>(false);
  activeModalUser : ModelSignal<boolean> = model<boolean>(false);
  index : number = 0;
  setIndex (index: number) {
    this.index = index;
  }
  checkIndex (index: number) : "active" | "" | string
  {
    if (index == this.index) {
      return "active"
    }
    return "";
  }
  openModal(value : boolean)
  {
    this.activeModal.set(value);
  }
  onActiveModalUser(value : boolean) : void
  {
    this.activeModalUser.set(value);
  }
}
