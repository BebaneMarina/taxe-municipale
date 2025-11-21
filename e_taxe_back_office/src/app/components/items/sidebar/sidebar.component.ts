import { Component } from '@angular/core';
import {RouterLink} from '@angular/router';

@Component({
  selector: 'app-sidebar',
  imports: [
    RouterLink
  ],
  standalone : true,
  templateUrl: './sidebar.component.html',
  styleUrl: './sidebar.component.scss'
})
export class SidebarComponent {
  isCurrentUrl(link : string) : string{
    switch(window.location.pathname.split('/').slice(1).includes(link)){
      case true:
        return 'active';
      default:
        return '';
    }
  }
}
