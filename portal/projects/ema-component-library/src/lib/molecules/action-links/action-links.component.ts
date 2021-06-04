import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';

@Component({
  selector: 'ema-action-links',
  templateUrl: './action-links.component.html',
  styleUrls: ['./action-links.component.scss']
})
export class ActionLinksComponent implements OnInit {

  @Input()
  actionList = [{
    action: '',
    isActive: false,
    routePath:''
  }]
  @Output() onActionClick = new EventEmitter();

  constructor() { }

  ngOnInit(): void {
  }
  actionClick(routePath, index){
    let activeItems = this.actionList.filter(items => items.isActive);
    for(let i=0; i<activeItems.length;i++){
      activeItems[i].isActive = false;
    }
    this.actionList[index].isActive = true;
    this.onActionClick.emit({bundleId : routePath});
  }
}
