import { Component, Input, OnInit } from '@angular/core';
import { DocumentSidebarMenuNode } from './sidebar.model';

@Component({
  selector: 'ema-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.scss']
})
export class SidebarComponent implements OnInit {
  title = 'Table of contents';
  constructor() { }

  @Input()
  menuNodes: DocumentSidebarMenuNode[] = [];

  ngOnInit(): void {
  }

}
