import { AfterViewInit, Component, OnDestroy, OnInit } from '@angular/core';
import { NgbModal, NgbModalConfig } from '@ng-bootstrap/ng-bootstrap';
import { CompareModalComponent } from 'projects/ema-component-library/src/lib/molecules/compare-modal/compare-modal.component';
import { DisclaimerModalComponent } from 'projects/ema-component-library/src/lib/molecules/disclaimer-modal/disclaimer-modal.component';
import { FhirCompareDocTypeEnum } from 'src/app/models/enums/fhir-compare-doctype-dropdown.enum';
import { FhirDocTypeEnum } from 'src/app/models/enums/fhir-doctype.enum';
import { FhirMessageSection } from 'src/app/models/fhir-message-section.model';
import { CompareSectionService } from 'src/app/shared-services/compare-section-service/compare-section.service';
import { DisclaimerServiceService } from 'src/app/shared-services/disclaimer-service/disclaimer-service.service';
import { FhirService } from 'src/app/shared-services/fhir-service/fhir.service';
import { SearchMedicine } from './search-medicine.model';

@Component({
  selector: 'ema-search-page',
  templateUrl: './search-page.component.html',
  styleUrls: ['./search-page.component.scss']
})
export class SearchPageComponent implements OnInit, AfterViewInit, OnDestroy {

  constructor(private modalService: NgbModal,
    modalConfig: NgbModalConfig,
    private readonly disclaimerServiceService: DisclaimerServiceService,
    private readonly fhirService: FhirService,
    private readonly compareSectionService: CompareSectionService
  ) {
    modalConfig.backdrop = 'static';
    modalConfig.keyboard = false;
  }
  medicineList: SearchMedicine[] = [];
  resultsText = "";
  compareResultsText = ""
  invalidKeys = [];
  inCompareState = false;
  showCompare = false;
  searchTagList = [];
  noDataRetrieved = false;

  ngOnInit(): void {
    this.setResultCount();
  }

  ngAfterViewInit() {
    this.disclaimerServiceService.getDisclaimerStatus().subscribe((status) => {
      if (!status) {
        // Opening disclaimer modal on page load if Accept has not been clicked
        const modalRef = this.modalService.open(DisclaimerModalComponent, { scrollable: true, centered: true });
      }
    });
  }

  ngOnDestroy() {
    // Closing all modal instances
    this.modalService.dismissAll();
  }
  setResultCount() {
    // Function to show result label
    this.resultsText = this.medicineList ?
      this.medicineList?.length === 1 ? this.medicineList?.length + ' result' : this.medicineList?.length + ' results' : '0 results';
  }
  createSearchItem(data) {
    // Create data structure with required information of one medicine
    let resourceData = data.entry[0].resource;
    let requiredEntry: any;
    let medicine: SearchMedicine = {};
    let subjectExtension = data.entry[0].resource.subject.extension;

    medicine.lastUpdated = new Date(data.meta.lastUpdated).toLocaleString('en-GB');
    medicine.searchName = data.entry[0].resource.identifier.filter((identity) => identity.system.includes('medicine-name'))[0].value;
    for (let i = 0; i < subjectExtension.length; i++) {
      if (subjectExtension[i].url.includes('medicine-name')) {
        medicine.name = subjectExtension[i].valueCoding.display;
      }
      if (subjectExtension[i].url.includes('marketing-authorization-holder')) {
        medicine.authorizationHolder = subjectExtension[i].valueCoding.display;
      }
      if (subjectExtension[i].url.includes('active-substance')) {
        if (!medicine.activeSubstances) {
          medicine.activeSubstances = subjectExtension[i].valueCoding.display;
          continue;
        }
        medicine.activeSubstances += ', ' + subjectExtension[i].valueCoding.display;
      }
    }

    medicine.listId = data.entry[0].resource.id;
    medicine.entry = resourceData.entry;
    requiredEntry = resourceData.entry.filter((entry) => entry.item.extension[0].valueCoding.code === FhirDocTypeEnum.SMPC && entry.item.extension[1].valueCoding.display === 'en')[0];
    if (requiredEntry) {
      medicine.routeReference = requiredEntry.item.reference.split('/')[1];
      medicine.routeLanguage = 'en';
    }
    else {
      medicine.routeReference = resourceData.entry[0].item.reference.split('/')[1];
      medicine.routeLanguage = resourceData.entry[0].item.extension[1].valueCoding.display;
    }
    return medicine
  }

  compareMedicineResults() {
    // Function to compare sections in different medicine in a particular document type

    const modalRef = this.modalService.open(CompareModalComponent, { scrollable: true, centered: true });
    this.compareSectionService.getCompareMeta().subscribe((compareSectionMeta) => {
      if(compareSectionMeta){
        for (let i = 0; i < this.medicineList.length; i++) {
          if (this.medicineList[i].entry) {
              let requiredDoctypeEntry;
              switch(compareSectionMeta.docType) { 
                case FhirCompareDocTypeEnum.SMPC: { 
                  requiredDoctypeEntry = this.medicineList[i].entry.filter((entry) => entry?.item?.extension[0].valueCoding.code === FhirDocTypeEnum.SMPC && entry?.item?.extension[1].valueCoding.display === 'en')[0];
                  break; 
                } 
                case FhirCompareDocTypeEnum.ANNEX_II: { 
                  requiredDoctypeEntry = this.medicineList[i].entry.filter((entry) => entry?.item?.extension[0].valueCoding.code === FhirDocTypeEnum.ANNEX_II && entry?.item?.extension[1].valueCoding.display === 'en')[0];
                  break; 
                }
                case FhirCompareDocTypeEnum.LABELLING: { 
                  requiredDoctypeEntry = this.medicineList[i].entry.filter((entry) => entry?.item?.extension[0].valueCoding.code === FhirDocTypeEnum.LABELLING && entry?.item?.extension[1].valueCoding.display === 'en')[0];
                  break; 
                } 
                case FhirCompareDocTypeEnum.PACKAGE_LEAFLET: { 
                  requiredDoctypeEntry = this.medicineList[i].entry.filter((entry) => entry?.item?.extension[0].valueCoding.code === FhirDocTypeEnum.PACKAGE_LEAFLET && entry?.item?.extension[1].valueCoding.display === 'en')[0];
                  break; 
                } 
             } 
  
            let leafletBundleId = requiredDoctypeEntry?.item?.reference.split('/')[1];
            if (leafletBundleId && leafletBundleId != 'None') {
              this.fhirService.getBundle(leafletBundleId).subscribe((data) => {
                this.medicineList[i].sectionsCompareResults = this.getSectionsWithKey(data.entry[0].resource.section, [], compareSectionMeta.searchKey.toLowerCase());
  
              }, (error) => {
                console.error('Could not load bundle');
              });
            }
          }
          this.inCompareState = true;
        }
        this.compareResultsText = "Comparing " + this.medicineList.length + " products for key: " + compareSectionMeta.searchKey;
      }
    });
  }

  getSectionsWithKey(sectionData: FhirMessageSection[], resultsList: FhirMessageSection[], key: string) {
    // Function to retrieve section with required key
    if (!sectionData)
      return []
    for (let sectionIndex = 0; sectionIndex < sectionData?.length; sectionIndex++) {
      if (sectionData[sectionIndex].title.toLowerCase().includes(key)) {
        resultsList.push(sectionData[sectionIndex]);
      }
      resultsList.concat(this.getSectionsWithKey(sectionData[sectionIndex].section, resultsList, key));
    }
    return resultsList
  }

  getAllMedicines() {
    // Function to get all medicines from the List bundle and populate the UI
    this.fhirService.getAllLists();
    this.fhirService.medicineData.subscribe((data) => {
      if (data && data.entry?.length>0) {
        this.medicineList = null;
        for (let i = 0; i < data.entry?.length; i++) {
          let resourceData = data.entry[i].resource;
          let requiredEntry: any;
          let medicine: SearchMedicine = {};
          let subjectExtension = data.entry[i].resource.subject.extension;

          medicine.lastUpdated = new Date(data.meta.lastUpdated).toLocaleString('en-GB');
          medicine.searchName = data.entry[i].resource.identifier.filter((identity) => identity.system.includes('medicine-name'))[0].value;

          for (let k = 0; k < subjectExtension.length; k++) {
            if (subjectExtension[k].url.includes('medicine-name')) {
              medicine.name = subjectExtension[k].valueCoding.display;
            }
            if (subjectExtension[k].url.includes('marketing-authorization-holder')) {
              medicine.authorizationHolder = subjectExtension[k].valueCoding.display;
            }
            if (subjectExtension[k].url.includes('active-substance')) {
              if (!medicine.activeSubstances) {
                medicine.activeSubstances = subjectExtension[k].valueCoding.display;
                continue;
              }
              medicine.activeSubstances += ", " + subjectExtension[k].valueCoding.display;
            }
          }
          medicine.listId = data.entry[i].resource.id;
          medicine.entry = resourceData.entry;
          requiredEntry = resourceData.entry.filter((entry) => entry.item.extension[0].valueCoding.code === FhirDocTypeEnum.SMPC && entry.item.extension[1].valueCoding.display === 'en')[0];
          if (requiredEntry) {
            medicine.routeReference = requiredEntry.item.reference.split('/')[1];
            medicine.routeLanguage = 'en';
          }
          else {
            medicine.routeReference = resourceData.entry[0].item.reference.split('/')[1];
            medicine.routeLanguage = resourceData.entry[0].item.extension[1].valueCoding.display;
          }
          if (!this.medicineList) {
            this.medicineList = [];
          }
          this.medicineList.push(medicine);
          this.showCompareButton();
          this.setResultCount();
        }
      }
      else{
        if(data){
          this.noDataRetrieved = true;
        }
      }
    });
  }

  showCompareButton() {
    // Function to show compare button for more than one medicine.
    if (this.medicineList.length > 1) {
      this.showCompare = true;
    }
    else {
      this.showCompare = false;
    }
  }

  backToSearchView() {
    // Changing view to search results
    this.inCompareState = false;
    this.compareSectionService.clearCompareMeta();
  }

  searchChanged(event) {
    /* Function to perform different operations on search
      The following cases are handled in this function:
        Case 1: Search for a keyword
        Case 2: Clearing all search keywords
        Case 3: Clearing specific keyword
    */
    if (event.operation === 'add') {
      // Case 1: Search for a keyword
      this.searchTagList = event.keyList;

      for (let listIdx = 0; listIdx < this.searchTagList.length; listIdx++) {
        if (this.searchTagList[listIdx] == '*') {
          this.medicineList = [];
          this.setResultCount();
          this.getAllMedicines();
          this.searchTagList = [];
          this.searchTagList.push('*');
          break;
        }
        else if (!(this.medicineList.filter((medicine) => medicine.searchName === this.searchTagList[listIdx].toLowerCase()).length > 0) &&
          !(this.invalidKeys.filter((key) => key === this.searchTagList[listIdx]).length > 0)) {
          this.fhirService.getListWithIdentifier(this.searchTagList[listIdx].toLowerCase()).subscribe(data => {
            if (data && data.entry) {
              this.medicineList.push(this.createSearchItem(data));
              this.setResultCount();
            }
            else if (!data.entry) {
              this.invalidKeys.push(this.searchTagList[listIdx]);
            }

            this.showCompareButton();
          }, (error) => {
            console.error('Could not load list with identifer');
          });
        }
      }

    }
    else if (event.operation === 'clearAll') {
      // Case 2: Clearing all search keywords
      this.medicineList = [];
      this.searchTagList = [];
      this.setResultCount();
      this.showCompare = false;
      this.noDataRetrieved = false;
    }
    else if (event.operation === 'clearSelected') {
      // Case 3: Clearing specific keyword
      this.searchTagList = event.keyList;

      if (event.keyToDelete == '*') {
        this.medicineList = [];
        this.searchTagList = [];
        this.showCompare = false;
        this.noDataRetrieved = false;
      }
      else {
        for (let idx = 0; idx < this.medicineList.length; idx++) {
          if (this.medicineList[idx].searchName === event.keyToDelete.toLowerCase()) {
            this.medicineList.splice(idx, 1);
          }
          this.showCompareButton();
        }
      }
      this.setResultCount();
    }
  }
}
