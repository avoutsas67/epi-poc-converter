import { Component, Input, OnInit } from '@angular/core';

@Component({
  selector: 'ema-cross-with-cirle',
  templateUrl: './cross-with-cirle.component.html',
  styleUrls:['./cross-with-cirle.scss']
})
export class CrossWithCirleComponent implements OnInit {
  @Input() width = '14';
  @Input() height = '14';

  constructor() { }

  ngOnInit(): void {
  }

}
