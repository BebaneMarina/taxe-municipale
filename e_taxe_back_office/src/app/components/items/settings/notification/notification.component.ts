import { Component } from '@angular/core';
import {H1Component} from '../../texts/h1/h1.component';
import {InputRadioComponent} from '../../input-radio/input-radio.component';

@Component({
  selector: 'app-notification',
  imports: [
    H1Component,
    InputRadioComponent
  ],
  standalone : true,
  templateUrl: './notification.component.html',
  styleUrl: './notification.component.scss'
})
export class NotificationComponent {

}
