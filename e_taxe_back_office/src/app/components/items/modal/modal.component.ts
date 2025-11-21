import {Component, Input, model, ModelSignal} from '@angular/core';
import {ContenerComponent} from '../contener/contener.component';

@Component({
  selector: 'app-modal',
  imports: [],
  standalone : true,
  templateUrl: './modal.component.html',
  styleUrl: './modal.component.scss'
})
export class ModalComponent {
  active : ModelSignal<boolean> = model<boolean>(true);
  @Input() title : string | null = null;
  toggleActive()
  {
    this.active.set(false);
  }
}
