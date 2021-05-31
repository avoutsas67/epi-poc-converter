import { ChangeDetectorRef, Component, Input, OnInit } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'ema-tree',
  templateUrl: './tree.component.html',
  styleUrls: ['./tree.component.scss']
})
export class TreeComponent implements OnInit {

  @Input() treeData: any[];
  constructor(private router: Router,
    private cd: ChangeDetectorRef) { }

  ngOnInit(): void {
  }

  toggleChild(node) {
    node.showChildren = !node.showChildren;
  }
  public scrollToAnchor(location: string, wait = 1): void {
    const element = document.getElementById(location);
    if (element) {
      
      setTimeout(() => {
      element.scrollIntoView({ behavior: 'smooth'});
      this.cd.detectChanges();
      }, wait);
    }
  }
}
