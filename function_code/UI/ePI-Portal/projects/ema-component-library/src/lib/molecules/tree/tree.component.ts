import { Component, Input, OnInit } from '@angular/core';

@Component({
  selector: 'ema-tree',
  templateUrl: './tree.component.html',
  styleUrls: ['./tree.component.scss']
})
export class TreeComponent implements OnInit {

  @Input() treeData: any[];
  constructor() { }

  ngOnInit(): void {
  }

  toggleChild(node) {
    node.showChildren = !node.showChildren;
  }
}
