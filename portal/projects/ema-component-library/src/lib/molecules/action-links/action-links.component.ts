import { Component, Input, OnInit } from '@angular/core';

@Component({
  selector: 'ema-action-links',
  templateUrl: './action-links.component.html',
  styleUrls: ['./action-links.component.scss']
})
export class ActionLinksComponent implements OnInit {

  @Input()
  actionList = [{
    action: '',
    isActive: '',
    routePath:''
  }]

  constructor() { }

  ngOnInit(): void {
  }

}
