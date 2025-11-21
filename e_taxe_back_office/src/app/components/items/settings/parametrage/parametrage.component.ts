import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../../../services/api.service';
import { GestionRolesComponent } from './gestion-roles/gestion-roles.component';
import { GestionDivisionsComponent } from './gestion-divisions/gestion-divisions.component';
import { GestionSecteursComponent } from './gestion-secteurs/gestion-secteurs.component';

@Component({
  selector: 'app-parametrage',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    GestionRolesComponent,
    GestionDivisionsComponent,
    GestionSecteursComponent
  ],
  templateUrl: './parametrage.component.html',
  styleUrl: './parametrage.component.scss'
})
export class ParametrageComponent implements OnInit {
  currentTab: number = 0;

  constructor() {}

  ngOnInit(): void {}

  setTab(index: number): void {
    this.currentTab = index;
  }

  isActiveTab(index: number): boolean {
    return this.currentTab === index;
  }
}

