import { DOCUMENT } from '@angular/common';
import { AfterViewInit, Component, Inject, OnInit, SecurityContext } from '@angular/core';
import { DomSanitizer } from '@angular/platform-browser';
import { ActivatedRoute, Router } from '@angular/router';
import { NgbModal, NgbModalConfig } from '@ng-bootstrap/ng-bootstrap';
import { EmaActionLinks } from 'projects/ema-component-library/src/lib/molecules/action-links/action-links.model';
import { DisclaimerModalComponent } from 'projects/ema-component-library/src/lib/molecules/disclaimer-modal/disclaimer-modal.component';
import { FhirDocTypeEnum } from 'src/app/models/enums/fhir-doctype.enum';
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
  noDataText = '';
  medicineName = "";
  sectionIdOnLoad = null;
  activeDocType = null;

  constructor(private readonly fhirService: FhirService,
    private route: ActivatedRoute,
    private modalService: NgbModal,
    modalConfig: NgbModalConfig,
    private readonly disclaimerServiceService: DisclaimerServiceService,
    @Inject(DOCUMENT) private document: Document,
    private sanitizer: DomSanitizer,
    private readonly router: Router
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

    }
    return menuItems
  }
  getFhirDocTypeBundle(url) {
    // Function to get bundle based on id
    this.fhirService.getBundle(url).subscribe((data) => {
      this.showDataInUI = false;
      if (data) {
        this.containedObjData = data.entry[0].resource.contained;
        this.documentStyleSheet = this.extractStyleTagData();

        // Inject style tag into head
        this.document.head.innerHTML +=
          this.sanitizer.sanitize(SecurityContext.STYLE, this.sanitizer.bypassSecurityTrustStyle(this.documentStyleSheet));

        this.documentData = data.entry[0].resource.section;
        this.documentData = this.embedImgsIntoContent(this.documentData[0].section ? this.documentData[0].section : this.documentData);
        this.documentId = url;
        this.menuItems = this.documentData;
        this.menuItems = this.setTableOfContentsAsCollapsed(this.menuItems)


        this.showDataInUI = true;
        setTimeout(() => {
          // Scroll section into view
          if (this.sectionIdOnLoad && this.showDataInUI) {
            const element = document.getElementById(this.sectionIdOnLoad);
            if (element) {
              element.scrollIntoView({ behavior: 'smooth' });
              this.sectionIdOnLoad = null;
            }
          }
        }, 2);

      }
    },
      (error) => {
        // Error handling if document bundle not retrieved
        this.documentData = null;
        this.menuItems = null;
        this.noDataText = "Page Not Found";
        this.showDataInUI = true;
      });
  }
  getAvailableLanguages() {
    // Function to create a list of all available languages in the List bundle for a medicine
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
        actionObj.docCode = docType.extension[0].valueCoding.code;
        if (this.activeDocType && actionObj?.docCode === this.activeDocType) {
          actionObj.isActive = true;
        }
        this.docTypeList.push(actionObj)
      }
    });
    if (this.docTypeList.filter(action => action.isActive).length === 0) {
      this.docTypeList[0].isActive = true;
      this.activeDocType = this.docTypeList[0].docCode;
    }

    this.docTypeList.sort((a,b)=> a.docCode - b.docCode );

    // Retrieving bundle on page refresh and setting respective tab as active
    if (this.documentId && !this.hasLangChanged) {
      this.getFhirDocTypeBundle(this.documentId);
      this.docTypeList.forEach((item) => {

        if (item && item.routePath === this.documentId) {
          item.isActive = true;
          this.activeDocType = item.docCode;
        }
        else if(item) {
          item.isActive = false;
        }

      });
    }
    else {
      if (this.activeDocType) {
        this.documentId = this.docTypeList.filter(actionObj => actionObj && actionObj?.isActive)[0].routePath;
      }
      else {
        this.documentId = this.currentDocTypeMeta[0].reference.split('/')[1];
      }
      this.getFhirDocTypeBundle(this.documentId);
    }

    this.hasLangChanged = false;

  }
  onLanguageChange(event) {
    // Function triggerred on change of language in the language dropdown
    let requiredLangItems, bundleId, bundleMeta;
    if (this.currentLang != event.data) {
      this.hasLangChanged = true;
      this.currentLang = event.data;

      requiredLangItems = this.listEntries.filter(entry =>
        entry.item.extension[1].valueCoding.display === this.currentLang);

      bundleMeta = requiredLangItems.filter(entry =>
        entry.item.extension[0].valueCoding.code === this.activeDocType
      );
      if (bundleMeta[0]) {
        bundleId = bundleMeta[0].item.reference.split('/')[1];
        if(bundleId==='None'){
          bundleId = requiredLangItems[0].item.reference.split('/')[1];
          this.activeDocType= requiredLangItems[0].item.extension[0].valueCoding.code;
        }
      }
      else {
        bundleId = requiredLangItems[0].item.reference.split('/')[1];
        this.activeDocType= requiredLangItems[0].item.extension[0].valueCoding.code;
      }
      this.router.navigate([this.currentPath, this.listId, this.currentLang, bundleId], { replaceUrl: true })
    }
  }

  initializeView() {
    // Function to set English as default if language is not present in route parameters
    this.getAvailableLanguages();
    if (this.currentLang) {
      this.getEntriesForRequiredLang(this.currentLang);
    }
    else {
      this.getEntriesForRequiredLang('en');
    }
  }


  changeDoctype(event) {
    //Function triggered on click of document type tabs
    this.sectionIdOnLoad = null;
    this.router.navigate([this.currentPath, this.listId, this.currentLang, event.bundleId], { replaceUrl: true })
  }
  ngOnInit(): void {
    this.noDataText = 'Loading...';
    this.route.url.subscribe(url => {
      this.currentPath = url[0].path;
    })

    // Get section id on load
    this.route.fragment.subscribe(data => {
      this.sectionIdOnLoad = data;
    })
    this.route.paramMap.subscribe(params => {
      this.currentLang = params.get('langId');
      this.listId = params.get('listId');
      this.documentId = params.get('documentId');
      this.fhirService.medicineData.subscribe((data) => {
        let listData: any;
        let subjectExtension: any;

        if (data == null) {
          this.fhirService.getAllLists();
        }

        listData = data?.entry.filter((entry) => entry.resource.id === this.listId)[0].resource;
        subjectExtension = listData?.subject.extension;

        for (let k = 0; k < subjectExtension?.length; k++) {
          if (subjectExtension[k].url.includes('medicine-name')) {
            this.medicineName = subjectExtension[k].valueCoding.display;
            break;
          }
        }

        if (this.medicineName?.length === 0) {
          this.medicineName = listData?.identifier?.filter((identity) => identity.system.includes('medicine-name'))[0].value;
        }

        this.listEntries = listData?.entry;
        if (this.listEntries) {
          this.initializeView();
        }

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
