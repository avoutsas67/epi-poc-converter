import { AfterViewInit, Component, OnDestroy, OnInit } from '@angular/core';
import { NgbModal, NgbModalConfig } from '@ng-bootstrap/ng-bootstrap';
import { DisclaimerModalComponent } from 'projects/ema-component-library/src/lib/molecules/disclaimer-modal/disclaimer-modal.component';
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
  invalidKeys = [];

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

  getAllMedicines() {
    this.fhirService.getAllLists();
    this.fhirService.medicineData.subscribe((data) => {
      if (data) {
        for (let i = 0; i < data.entry?.length; i++) {
          let resourceData = data.entry[i].resource;
          let requiredEntry: any;
          let medicine: SearchMedicine = {};
          medicine.name = data.entry[i].resource.identifier[0].value;
          medicine.listId = data.entry[i].resource.id;
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
          this.resultsText = this.medicineList?.length === 1 ? this.medicineList?.length + ' result' : this.medicineList?.length + ' results';
        }
      }
    });
  }

  searchChanged(event) {

    if (event.operation === 'add') {
      let searchList = event.keyList;
      for (let listIdx = 0; listIdx < searchList.length; listIdx++) {
        if (!(this.medicineList.filter((medicine) => medicine.name === searchList[listIdx]).length > 0) && 
        !(this.invalidKeys.filter((key) => key === searchList[listIdx]).length > 0)) {
          this.fhirService.getListWithIdentifier(searchList[listIdx]).subscribe(data => {
            if (data  && data.entry) {
              this.medicineList.push(this.createSearchItem(data));
              this.setResultCount();
            }
            else if(!data.entry){
              this.invalidKeys.push(searchList[listIdx]);
            }
          });
        }
      }
    }
    else if (event.operation === 'clearAll') {
      this.medicineList = [];
      this.setResultCount();
    }
    else if (event.operation === 'clearSelected') {
      for (let idx = 0; idx < this.medicineList.length; idx++) {
        if (this.medicineList[idx].name === event.keyToDelete) {
          this.medicineList.splice(idx, 1);
        }
      }
      this.setResultCount();
    }
  }
}
