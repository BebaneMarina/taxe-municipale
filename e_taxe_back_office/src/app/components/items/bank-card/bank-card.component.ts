import { Component } from '@angular/core';
import {cutString, hiddenLetters} from '../../../utils/utils';

@Component({
  selector: 'app-bank-card',
  imports: [],
  standalone : true,
  templateUrl: './bank-card.component.html',
  styleUrl: './bank-card.component.scss'
})
export class BankCardComponent {

  protected readonly cutString = cutString;
  protected readonly hiddenLetters = hiddenLetters;
}
