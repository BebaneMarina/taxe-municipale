import { Component } from '@angular/core';
import {ContenerGrayComponent} from '../../contener-gray/contener-gray.component';

@Component({
  selector: 'app-recap-transaction',
  imports: [
    ContenerGrayComponent
  ],
  standalone : true,
  templateUrl: './recap-transaction.component.html',
  styleUrl: './recap-transaction.component.scss'
})
export class RecapTransactionComponent {

}
