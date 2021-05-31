import { Component, Input, OnInit } from '@angular/core';

@Component({
  selector: 'ema-document-body-tree',
  templateUrl: './document-body-tree.component.html',
  styleUrls: ['./document-body-tree.component.scss']
})
export class DocumentBodyTreeComponent implements OnInit {
  @Input() sectionData: any[];

  constructor() { }

  ngOnInit(): void {
  }

}
