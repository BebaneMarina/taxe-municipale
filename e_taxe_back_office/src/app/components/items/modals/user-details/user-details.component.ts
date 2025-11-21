import { Component } from '@angular/core';
import {ContenerGrayComponent} from '../../contener-gray/contener-gray.component';

@Component({
  selector: 'app-user-details',
  standalone : true,
  imports: [
    ContenerGrayComponent
  ],
  templateUrl: './user-details.component.html',
  styleUrl: './user-details.component.scss'
})
export class UserDetailsComponent {

}
