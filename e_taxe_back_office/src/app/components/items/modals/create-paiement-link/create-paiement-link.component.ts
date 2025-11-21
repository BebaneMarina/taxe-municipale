import { Component } from '@angular/core';
import {H1Component} from '../../texts/h1/h1.component';

@Component({
  selector: 'app-create-paiement-link',
  imports: [
    H1Component
  ],
  standalone : true,
  templateUrl: './create-paiement-link.component.html',
  styleUrl: './create-paiement-link.component.scss'
})
export class CreatePaiementLinkComponent {
  activeEmail : boolean = false;
  onToggleActiveEmail(active : boolean) : void
  {
    this.activeEmail = active;
  }
}
