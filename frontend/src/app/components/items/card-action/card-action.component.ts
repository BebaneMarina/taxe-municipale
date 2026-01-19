import {Component, Input, model, ModelSignal} from '@angular/core';

@Component({
  selector: 'app-card-action',
  imports: [],
  standalone : true,
  templateUrl: './card-action.component.html',
  styleUrl: './card-action.component.scss'
})
export class CardActionComponent {
  @Input() title : string = "Revevoir un paiement";
  @Input() buttonText : string = "Créer un lien de paiement";
  active : ModelSignal<boolean> = model<boolean>(false);
  onActiveModal() : void
  {
    this.active.set(true);
  }
}
