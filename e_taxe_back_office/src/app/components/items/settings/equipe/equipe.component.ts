import {Component, model, ModelSignal} from '@angular/core';

@Component({
  selector: 'app-equipe',
  imports: [],
  standalone : true,
  templateUrl: './equipe.component.html',
  styleUrl: './equipe.component.scss'
})
export class EquipeComponent {
  active : ModelSignal<boolean> = model<boolean>(true);
  activeModalUser : ModelSignal<boolean> = model<boolean>(false);
  onActiveChange()
  {
    this.active.set(true);
  }
  onActiveModalUser (value : boolean) : void
  {
    this.activeModalUser.set(value);
  }
}
