import {Component, Input} from '@angular/core';

@Component({
  selector: 'app-input-radio',
  imports: [],
  standalone : true,
  templateUrl: './input-radio.component.html',
  styleUrl: './input-radio.component.scss'
})
export class InputRadioComponent {
  @Input() title : string = "";
  active : boolean = false;
  toggleActive () : void
  {
    this.active = !this.active;
  }
}
