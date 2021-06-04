import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';

@Component({
  selector: 'ema-document-header',
  templateUrl: './document-header.component.html',
  styleUrls: ['./document-header.component.scss']
})
export class DocumentHeaderComponent implements OnInit {
  @Input() dropdownOptions = [];
  @Input() languageSelected = 'en';
  @Output() changeLang  = new EventEmitter();

  constructor() { }

  ngOnInit(): void {
  }
  onLangChange(event){
    this.changeLang.emit(event);
  }

}
