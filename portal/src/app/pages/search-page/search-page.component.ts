import { AfterViewInit, Component, OnDestroy, OnInit } from '@angular/core';
import { NgbModal, NgbModalConfig } from '@ng-bootstrap/ng-bootstrap';
import { DisclaimerModalComponent } from 'projects/ema-component-library/src/lib/molecules/disclaimer-modal/disclaimer-modal.component';
import { FhirMessageSection } from 'src/app/models/fhir-message-section.model';
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
    private readonly fhirService: FhirService
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

  ngOnInit(): void {
    this.setResultCount();
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
  setResultCount() {
    this.resultsText = this.medicineList ?
      this.medicineList?.length === 1 ? this.medicineList?.length + ' result' : this.medicineList?.length + ' results' : '0 results';
  }
  createSearchItem(data) {
    let resourceData = data.entry[0].resource;
    let requiredEntry: any;
    let medicine: SearchMedicine = {};
    medicine.name = data.entry[0].resource.identifier[0].value;
    medicine.listId = data.entry[0].resource.id;
    medicine.entry = resourceData.entry;
    requiredEntry = resourceData.entry.filter((entry) => entry.item.extension[0].valueCoding.display === 'SmPC' && entry.item.extension[1].valueCoding.display === 'en')[0];
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
    for (let i = 0; i < this.medicineList.length; i++) {
      if (this.medicineList[i].entry) {
        let packageLeafletEntry = this.medicineList[i].entry.filter((entry) => entry?.item?.extension[0].valueCoding.display === "Package leaflet" && entry?.item?.extension[1].valueCoding.display === 'en')[0];
        let leafletBundleId = packageLeafletEntry?.item?.reference.split('/')[1];
        if (leafletBundleId && leafletBundleId != 'None') {
          this.fhirService.getBundle(leafletBundleId).subscribe((data) => {
            this.medicineList[i].sectionsCompareResults = this.getSectionsWithKey(data.entry[0].resource.entry[0].resource.section, [], "Pregnancy".toLowerCase());

          }, (error) => {
            console.error('Could not load bundle');
          });
        }
      }
      this.inCompareState = true;
    }
    this.compareResultsText = "Comparing " + this.medicineList.length + " products";
  }

  getSectionsWithKey(sectionData: FhirMessageSection[], resultsList: FhirMessageSection[], key: string) {
    if (!sectionData)
      return []
    for (let sectionIndex = 0; sectionIndex < sectionData?.length; sectionIndex++) {
      resultsList.concat(this.getSectionsWithKey(sectionData[sectionIndex].section, resultsList, key));
      if (sectionData[sectionIndex].title.toLowerCase().includes(key)) {
        resultsList.push(sectionData[sectionIndex]);
      }
    }
    return resultsList
  }

  getAllMedicines() {
    this.fhirService.getAllLists();
    this.fhirService.medicineData.subscribe((data) => {
      if (data) {
        this.medicineList = null;
        for (let i = 0; i < data.entry?.length; i++) {
          let resourceData = data.entry[i].resource;
          let requiredEntry: any;
          let medicine: SearchMedicine = {};
          medicine.name = data.entry[i].resource.identifier[0].value;
          medicine.listId = data.entry[i].resource.id;
          medicine.entry = resourceData.entry;
          requiredEntry = resourceData.entry.filter((entry) => entry.item.extension[0].valueCoding.display === 'SmPC' && entry.item.extension[1].valueCoding.display === 'en')[0];
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
    });
  }

  showCompareButton() {
    if (this.medicineList.length > 1) {
      this.showCompare = true;
    }
    else {
      this.showCompare = false;
    }
  }

  backToSearchView() {
    this.inCompareState = false;
  }

  searchChanged(event) {

    if (event.operation === 'add') {
      this.searchTagList = event.keyList;

      for (let listIdx = 0; listIdx < this.searchTagList.length; listIdx++) {
        if (this.searchTagList[listIdx] == '*') {
          this.medicineList = [];
          this.getAllMedicines();
          this.searchTagList = [];
          this.searchTagList.push('*');
          break;
        }
        else if (!(this.medicineList.filter((medicine) => medicine.name === this.searchTagList[listIdx]).length > 0) &&
          !(this.invalidKeys.filter((key) => key === this.searchTagList[listIdx]).length > 0)) {
          this.fhirService.getListWithIdentifier(this.searchTagList[listIdx]).subscribe(data => {
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
      this.medicineList = [];
      this.searchTagList = [];
      this.setResultCount();
      this.showCompare = false;
    }
    else if (event.operation === 'clearSelected') {
      this.searchTagList = event.keyList;

      if (event.keyToDelete == '*') {
        this.medicineList = [];
        this.showCompare = false;
      }
      else {
        for (let idx = 0; idx < this.medicineList.length; idx++) {
          if (this.medicineList[idx].name === event.keyToDelete) {
            this.medicineList.splice(idx, 1);
          }
          this.showCompareButton();
        }
      }
      this.setResultCount();
    }
  }
}
