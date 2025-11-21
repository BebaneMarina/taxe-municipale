import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MapInteractiveComponent } from '../../items/map-interactive/map-interactive.component';
import { ContenerComponent } from '../../items/contener/contener.component';
import { H1Component } from '../../items/texts/h1/h1.component';

@Component({
  selector: 'app-cartographie',
  standalone: true,
  imports: [
    CommonModule,
    MapInteractiveComponent,
    ContenerComponent,
    H1Component
  ],
  templateUrl: './cartographie.component.html',
  styleUrl: './cartographie.component.scss'
})
export class CartographieComponent {

}
