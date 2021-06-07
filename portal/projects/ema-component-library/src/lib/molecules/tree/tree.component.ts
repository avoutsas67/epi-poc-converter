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

  toggleChild(node, arrowNode) {
    arrowNode = arrowNode.target.closest('.ema-tree-toggle');
    arrowNode.classList.contains('ema-tree-toggle--down')?  arrowNode.classList.remove('ema-tree-toggle--down'):arrowNode.classList.add('ema-tree-toggle--down');
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
