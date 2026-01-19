import {Component, Input} from '@angular/core';
import {STATUS} from '../../../utils/types';

@Component({
  selector: 'app-badge',
  imports: [],
  standalone : true,
  templateUrl: './badge.component.html',
  styleUrl: './badge.component.scss'
})
export class BadgeComponent {
  @Input({required : true}) text: string | number= "succes";
  @Input() type : STATUS = "failed";


  className() : {container : string, icone : string}{
    switch(this.type){
      case 'completed':
        return {
          container : "bg-green-100 text-green-700",
          icone : "fill-green-500",
        };
      case 'pending':
        return  {
          container : "bg-gray-100 text-gray-600",
          icone : "fill-gray-400",
        };
      case 'failed':
        return  {
          container : "bg-red-100 text-red-700",
          icone : "fill-red-500",
        };
      default :
        return  {
          container : "bg-purple-100 text-purple-700",
          icone : "fill-purple-500",
        };
    }
  }
}
