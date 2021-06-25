import { Component, Input, OnInit, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'ema-button',
  templateUrl: './button.component.html',
  styleUrls: ['./button.component.scss']
})
export class ButtonComponent implements OnInit {
  @Input() label = 'Button';
  @Input() isSecondary = false;
  @Input() isDisabled = false;
  @Output() buttonClicked = new EventEmitter();

  constructor() { }

  ngOnInit(): void {
  }

  onButtonClick(){
    if(!this.isDisabled){
      this.buttonClicked.emit();
    }
  }

}
