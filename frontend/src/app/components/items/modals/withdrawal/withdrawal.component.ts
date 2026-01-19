import { Component } from '@angular/core';
import {DemandeRetraitComponent} from '../demande-retrait/demande-retrait.component';
import {RecapTransactionComponent} from '../recap-transaction/recap-transaction.component';
import {OtpCodeComponent} from '../otp-code/otp-code.component';
import {StatusModalComponent} from '../status-modal/status-modal.component';

@Component({
  selector: 'app-withdrawal',
  standalone : true,
  imports: [
    DemandeRetraitComponent,
    RecapTransactionComponent,
    OtpCodeComponent,
    StatusModalComponent
  ],
  templateUrl: './withdrawal.component.html',
  styleUrl: './withdrawal.component.scss'
})
export class WithdrawalComponent {
  index : number = 1;
  setIndex(index: number) {
    this.index = index;
  }
  checkIndex(index: number) : "active" | ""
  {
    if (index == this.index) return  "active";
    return ""
  }
}
