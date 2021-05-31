import { DOCUMENT } from '@angular/common';
import { AfterViewInit, Component, Inject,  OnInit, Renderer2, SecurityContext} from '@angular/core';
import { DomSanitizer } from '@angular/platform-browser';
import { ActivatedRoute, NavigationEnd, Router } from '@angular/router';
import { NgbModal, NgbModalConfig } from '@ng-bootstrap/ng-bootstrap';
import { Guid } from 'guid-typescript';
import { DisclaimerModalComponent } from 'projects/ema-component-library/src/lib/molecules/disclaimer-modal/disclaimer-modal.component';
import { FhirMessageSection } from 'src/app/models/fhir-message-section.model';
import { DisclaimerServiceService } from 'src/app/shared-services/disclaimer-service/disclaimer-service.service';
import { FhirService } from 'src/app/shared-services/fhir-service/fhir.service';

@Component({
  selector: 'ema-document-view',
  templateUrl: './document-view.component.html',
  styleUrls: ['./document-view.component.scss']
})
export class DocumentViewComponent implements OnInit, AfterViewInit {
  menuItems: any[];
  docTypeList: any[];
  currentPath: string;
  documentId: string;
  documentData: any[];
  containedObjData: any[];
  documentStyleSheet: any;
  
  constructor(private readonly fhirService: FhirService,
    private route: ActivatedRoute,
    private modalService: NgbModal,
    modalConfig: NgbModalConfig,
    private readonly disclaimerServiceService: DisclaimerServiceService,
    @Inject(DOCUMENT) private document: Document,
    private sanitizer: DomSanitizer,
    private renderer: Renderer2
  ) {
    modalConfig.backdrop = 'static';
    modalConfig.keyboard = false;
  }

  extractStyleTagData() {
    /* Extract style information of the document from a binary object with id stylesheet0 present in contained object */

    for (let index = 0; index < this.containedObjData.length; index++) {
      let contained = this.containedObjData[index];
      if (contained.id === "stylesheet0") {
        this.containedObjData.splice(index, 1);
        return atob(contained.data);
      }
    }
  }

  ngOnInit(): void {
    this.route.url.subscribe(url => {
      this.currentPath = url[0].path;
    })
    this.route.paramMap.subscribe(params => {
      this.documentId = params.get('id');

      this.fhirService.getBundle(this.documentId).subscribe((data) => {

        this.containedObjData = data.entry[0].resource.entry[0].resource.contained;
        this.documentStyleSheet = this.extractStyleTagData();

        // Inject style tag into head
        this.document.head.innerHTML +=
          this.sanitizer.sanitize(SecurityContext.STYLE, this.sanitizer.bypassSecurityTrustStyle(this.documentStyleSheet));

        this.documentData = data.entry[0].resource.entry[0].resource.section;
        this.documentData = this.setIdForHeadings(this.documentData)
        this.documentData = this.embedIdsAndImgsIntoContent(this.documentData);
        this.menuItems = this.documentData;

        // Extract style information of the document 
        this.docTypeList = [
          {
            action: data.entry[0].resource.entry[0].resource.section[0].title,
            isActive: true,
            routePath: ['../../' + this.currentPath, this.documentId]
          }
        ]
      });

    });
  }

  ngAfterViewInit() {
    this.disclaimerServiceService.getDisclaimerStatus().subscribe((status) => {
      if (!status) {
        const modalRef = this.modalService.open(DisclaimerModalComponent, { scrollable: true, centered: true });
      }
    });
  }
  
  ngOnDestroy() {
    this.modalService.dismissAll();
  }
  setIdForHeadings(sectionData: FhirMessageSection[]) {
    if (!sectionData)
      return
    for (let sectionIndex = 0; sectionIndex < sectionData?.length; sectionIndex++) {
      sectionData[sectionIndex].id = Guid.create();
      
      sectionData[sectionIndex].section = this.setIdForHeadings(sectionData[sectionIndex].section);
    }
    return sectionData
  }
  embedIdsAndImgsIntoContent(sectionData: FhirMessageSection[]) {
    let prefixOfSearchStr = 'src="#'
    if (!sectionData) {
      return

    }
    for (let containedIndex = 0; containedIndex < this.containedObjData.length; containedIndex++) {
      let containedObj = this.containedObjData[containedIndex];
      for (let sectionIndex = 0; sectionIndex < sectionData?.length; sectionIndex++) {
        if (sectionData[sectionIndex].text.div.toString().indexOf(prefixOfSearchStr + containedObj.id + '"')) {
          sectionData[sectionIndex].text.div = sectionData[sectionIndex].text.div.toString().replace("#" + containedObj.id, "data:" + containedObj.contentType + "image/gif;base64," + containedObj.data).toString();
        }
        this.embedIdsAndImgsIntoContent(sectionData[sectionIndex].section);
      }
    }
    return sectionData
  }

}
