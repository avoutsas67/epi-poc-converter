import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';

@Component({
  selector: 'ema-tags',
  templateUrl: './tags.component.html',
  styleUrls: ['./tags.component.scss']
})
export class TagsComponent implements OnInit {
  @Input() name = ""
  @Output() onCrossClick = new EventEmitter();
  constructor() { }

  ngOnInit(): void {
  }

  crossClicked(name){
    this.onCrossClick.emit({name: name});
  }
}
