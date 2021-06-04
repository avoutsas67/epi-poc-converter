import { DOCUMENT, Location } from '@angular/common';
import { AfterViewInit, Component, Inject, OnInit, SecurityContext } from '@angular/core';
import { DomSanitizer } from '@angular/platform-browser';
import { ActivatedRoute } from '@angular/router';
import { NgbModal, NgbModalConfig } from '@ng-bootstrap/ng-bootstrap';
import { Guid } from 'guid-typescript';
import { EmaActionLinks } from 'projects/ema-component-library/src/lib/molecules/action-links/action-links.model';
import { DisclaimerModalComponent } from 'projects/ema-component-library/src/lib/molecules/disclaimer-modal/disclaimer-modal.component';
import { FhirEntryItem, FhirMessageEntry } from 'src/app/models/fhir-message-entry.model';
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
  docTypeList: any[] = [];
  currentPath: string;
  listId: string;
  documentId: string;
  documentData: FhirMessageSection[];
  containedObjData: any[];
  documentStyleSheet: any;
  listEntries: FhirMessageEntry[];
  currentDocTypeMeta: Array<FhirEntryItem> = [];
  availableLanguages: string[] = []
  currentLang = "";
  hasLangChanged = false;
  showDataInUI = false;
  noDataText='';

  constructor(private readonly fhirService: FhirService,
    private route: ActivatedRoute,
    private modalService: NgbModal,
    modalConfig: NgbModalConfig,
    private readonly disclaimerServiceService: DisclaimerServiceService,
    @Inject(DOCUMENT) private document: Document,
    private sanitizer: DomSanitizer,
    private location: Location
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
  setTableOfContentsAsCollapsed(menuItems) {
    // Function to set all heading in Table of contents to collapsed state
    if (!menuItems)
      return
    for (let sectionIndex = 0; sectionIndex < menuItems?.length; sectionIndex++) {
      menuItems[sectionIndex].showChildren = false;

      menuItems[sectionIndex].section = this.setIdForHeadings(menuItems[sectionIndex].section);
    }
    return menuItems
  }
  getFhirDocTypeBundle(url) {
    this.fhirService.getBundle(url).subscribe((data) => {
      this.showDataInUI = false;
      if(data){
        this.containedObjData = data.entry[0].resource.entry[0].resource.contained;
        this.documentStyleSheet = this.extractStyleTagData();
  
        // Inject style tag into head
        this.document.head.innerHTML +=
          this.sanitizer.sanitize(SecurityContext.STYLE, this.sanitizer.bypassSecurityTrustStyle(this.documentStyleSheet));
  
        this.documentData = data.entry[0].resource.entry[0].resource.section;
        this.documentData = this.setIdForHeadings(this.documentData)
        this.documentData = this.embedImgsIntoContent(this.documentData[0].section ? this.documentData[0].section : this.documentData);
        this.menuItems = this.documentData;
        this.menuItems = this.setTableOfContentsAsCollapsed(this.menuItems)

        if(this.documentId != url){
          this.location.replaceState(this.currentPath + '/' + this.listId + '/' + this.currentLang  + '/' + url);
        }
        this.documentId = url;
        this.showDataInUI = true;
      }
    }, 
    (error)=>{
     this.documentData = null;
     this.menuItems = null;
     this.noDataText = "Page Not Found";
     this.location.replaceState(this.currentPath + '/' + this.listId + '/' + this.currentLang  + '/' + url);
     this.showDataInUI = true;
    });
  }
  getAvailableLanguages() {
    this.listEntries?.forEach(entry => {
      if (!this.availableLanguages.includes(entry.item.extension[1].valueCoding.display)) {
        this.availableLanguages.push(entry.item.extension[1].valueCoding.display)
      }
    })
  }

  getEntriesForRequiredLang(lang: string) {
    this.currentDocTypeMeta = [];
    this.currentLang = lang;
    this.listEntries.forEach(entry => {
      if (entry.item.extension[1].valueCoding.display === lang) {
        this.currentDocTypeMeta.push(entry.item)
      }
    })
    
    this.docTypeList = []

    // Populating Document type tabs
    this.currentDocTypeMeta.forEach((docType) => {
      let parsedReference = docType.reference.split('/');
      if (parsedReference[1] !== 'None') {
        let actionObj = new EmaActionLinks();
        actionObj.action = docType.extension[0].valueCoding.display;
        actionObj.isActive = false;
        actionObj.routePath = parsedReference[1];
        if (this.docTypeList.length === 0) {
          actionObj.isActive = true;
        }
        this.docTypeList.push(actionObj)
      }
    });
  
    // Retrieving bundle on page refresh and setting respective tab as active
    if (this.documentId && !this.hasLangChanged) { 
      this.getFhirDocTypeBundle(this.documentId);
      this.docTypeList.forEach((item) => {
      
        if (item.routePath===this.documentId) {
         item.isActive = true;
        }
        else{
          item.isActive = false;
        }
  
      });
    }
    else {
      this.getFhirDocTypeBundle(this.currentDocTypeMeta[0].reference.split('/')[1]);
    }

    this.hasLangChanged = false;

  }
  onLanguageChange(event) {
    if (this.currentLang != event.language) {
      this.hasLangChanged = true;
      this.getEntriesForRequiredLang(event.language)
    }
  }

  initializeView(){
    // Function to set English as default if language is not present in route parameters
    this.getAvailableLanguages();
    if (this.currentLang) {
      this.getEntriesForRequiredLang(this.currentLang);
    }
    else {
      this.getEntriesForRequiredLang('en');
    }
  }


  getFhirList(listId) {
    this.fhirService.getList(listId).subscribe((listData =>{
      setTimeout(()=>{
          if(listData){
            this.listEntries = listData.entry;
          }
          
          if(this.listEntries){
            this.initializeView();
          }
      }, 1000);
    }));
  }

  changeDoctype(event) {
    this.getFhirDocTypeBundle(event.bundleId)
  }
  ngOnInit(): void {
    this.noDataText = 'Loading...';
    this.route.url.subscribe(url => {
      this.currentPath = url[0].path;
    })
    this.route.paramMap.subscribe(params => {
      this.currentLang = params.get('langId');
      this.listId = params.get('listId');
      this.documentId = params.get('documentId');
      this.getFhirList(this.listId);

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
  embedImgsIntoContent(sectionData: FhirMessageSection[]) {
    // Function to embed images from <Binary> onto the html
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
        this.embedImgsIntoContent(sectionData[sectionIndex].section);
      }
    }
    return sectionData
  }

}
