import { Component } from '@angular/core';

@Component({
  selector: 'app-profil',
  imports: [],
  standalone : true,
  templateUrl: './profil.component.html',
  styleUrl: './profil.component.scss'
})
export class ProfilComponent {
  disableInput : boolean = true;

  onEnableInput() : void
  {
    console.log("enableInput");
    this.disableInput = false;
  }
}
