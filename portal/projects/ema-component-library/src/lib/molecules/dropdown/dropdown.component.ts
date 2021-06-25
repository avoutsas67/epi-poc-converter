import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';

@Component({
  selector: 'ema-dropdown',
  templateUrl: './dropdown.component.html',
  styleUrls: ['./dropdown.component.scss']
})
export class DropdownComponent implements OnInit {
  @Input()
  selectedOption = null;
  @Input() dropdownOptions = []

  @Output() onSelectionChange = new EventEmitter();
  @Output() onToggle = new EventEmitter();

  constructor() { }

  ngOnInit(): void {
  }

  changeSelection(option) {
    this.selectedOption = option;
    this.onSelectionChange.emit({ data: this.selectedOption })
  }

  dropdownToggled(event, dropdown) {
    this.onToggle.emit(event);
  }

}
