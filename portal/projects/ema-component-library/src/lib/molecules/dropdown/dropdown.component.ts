import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';

@Component({
  selector: 'ema-dropdown',
  templateUrl: './dropdown.component.html',
  styleUrls: ['./dropdown.component.scss']
})
export class DropdownComponent implements OnInit {
  @Input() dropdownOptions = []
  @Output() onLangChange = new EventEmitter();
  @Input()
  selectedOption = "en";

  constructor() { }

  ngOnInit(): void {
  }

  changeSelection(option){
    this.selectedOption = option;
    this.onLangChange.emit({language: this.selectedOption})
  }

}
