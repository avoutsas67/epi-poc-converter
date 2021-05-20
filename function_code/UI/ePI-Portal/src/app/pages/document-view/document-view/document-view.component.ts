import { Component, OnInit } from '@angular/core';
import { DocumentSidebarMenuNode } from 'projects/ema-component-library/src/lib/layouts/sidebar/sidebar.model';
import { FhirService } from 'src/app/shared-services/fhir-service/fhir.service';

@Component({
  selector: 'ema-document-view',
  templateUrl: './document-view.component.html',
  styleUrls: ['./document-view.component.scss']
})
export class DocumentViewComponent implements OnInit {
  menuItems: any[];
  constructor(private readonly fhirService: FhirService) { }


  ngOnInit(): void {
    this.fhirService.getBundle().subscribe((data)=>{
      console.log(data.entry[0].resource.entry[0].resource.section)
      this.menuItems = data.entry[0].resource.entry[0].resource.section
    });
  }

}
