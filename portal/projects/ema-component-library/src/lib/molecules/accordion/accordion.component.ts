import { Component, Input, OnInit } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'ema-accordion',
  templateUrl: './accordion.component.html',
  styleUrls: ['./accordion.component.scss']
})
export class AccordionComponent implements OnInit {
  @Input() accordionData: any[] = [];
  constructor(private router: Router) { }

  ngOnInit(): void {
  }

  toggleAccordion(event, medicine) {
    let el = event.target;

    if (!el.classList.contains('ema-accordion-link')) {
      if (!el.classList.contains('ema-accordion')) {
        el = el.closest('.ema-accordion')
      }

      el.getElementsByClassName('ema-accordion-toggle')[0].classList.toggle('ema-accordion-toggle--down')

      el.classList.toggle("active");
      let panel = el.nextSibling;
      while (panel && !panel.classList?.contains('ema-accordion-panel')) {
        panel = panel.nextElementSibling;
      }
      if (panel.style.maxHeight) {
        panel.style.maxHeight = null;
        panel.classList.remove('ema-accordion-panel--border');

      } else {
        panel.style.maxHeight = panel.scrollHeight + "px";
        panel.classList.add('ema-accordion-panel--border');
      }
    }
    else {
      const url = this.router.serializeUrl(this.router.createUrlTree(['/View', medicine.listId, medicine.routeLanguage, medicine.routeReference]));
      window.open(url, '_blank');
    }

  }

}
