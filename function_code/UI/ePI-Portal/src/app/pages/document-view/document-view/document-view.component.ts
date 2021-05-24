import { AfterViewInit, Component, OnInit, TemplateRef, ViewChild } from '@angular/core';
import { ActivatedRoute, NavigationEnd, Router } from '@angular/router';
import { NgbModal, NgbModalConfig } from '@ng-bootstrap/ng-bootstrap';
import { DocumentSidebarMenuNode } from 'projects/ema-component-library/src/lib/layouts/sidebar/sidebar.model';
import { FhirService } from 'src/app/shared-services/fhir-service/fhir.service';

@Component({
  selector: 'ema-document-view',
  templateUrl: './document-view.component.html',
  styleUrls: ['./document-view.component.scss']
})
export class DocumentViewComponent implements OnInit {
  menuItems: any[];
  docTypeList: any[];
  currentPath: string;
  documentId: string;

  constructor(private readonly fhirService: FhirService,
    private route: ActivatedRoute
  ) {
  }

  ngOnInit(): void {
    this.route.url.subscribe(url => {
      this.currentPath = url[0].path;
    })
    this.route.paramMap.subscribe(params => {
      this.documentId = params.get('id');
      this.fhirService.getBundle(this.documentId).subscribe((data) => {
        this.menuItems = data.entry[0].resource.entry[0].resource.section;
        this.docTypeList = [
          {
            action: data.entry[0].resource.entry[0].resource.section[0].title,
            isActive: true,
            routePath: ['../../'+this.currentPath,this.documentId]
          }
        ]
      });

    });
  }

}
