import { AfterViewInit, ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { FhirCompareDocTypeEnum } from 'src/app/models/enums/fhir-compare-doctype-dropdown.enum';
import { FhirCompareSectionsMeta } from 'src/app/models/fhir-compare-sections.model';
import { CompareSectionService } from 'src/app/shared-services/compare-section-service/compare-section.service';

@Component({
  selector: 'ema-compare-modal',
  templateUrl: './compare-modal.component.html',
  styleUrls: ['./compare-modal.component.scss']
})
export class CompareModalComponent implements OnInit, AfterViewInit {
  docTypeDropdownOptions = [FhirCompareDocTypeEnum.SMPC, 
    FhirCompareDocTypeEnum.ANNEX_II,
    FhirCompareDocTypeEnum.LABELLING,
    FhirCompareDocTypeEnum.PACKAGE_LEAFLET];
  compareSectionsMetaData: FhirCompareSectionsMeta = {
    docType:null,
    searchKey:null
  };

  constructor(private readonly cd: ChangeDetectorRef, private activeModal: NgbActiveModal, 
    private readonly compareSectionService:CompareSectionService) { }

  ngOnInit(): void {
  }

  ngAfterViewInit() {

  }

  dropdownToggle(event) {
    if (event) {
      (document.getElementsByClassName('dropdown-menu')[0] as HTMLElement).style.transition = "height 0.25s ease";
      (document.getElementsByClassName('ema-compare-menu')[0] as HTMLElement).style.display = "block";
      (document.getElementsByClassName('ema-compare-menu')[0] as HTMLElement).style.transition = "height 0.5s ease";
      (document.getElementsByClassName('ema-compare-menu')[0] as HTMLElement).style.height = '150px';
      this.cd.detectChanges();
    }
    else {
      (document.getElementsByClassName('ema-compare-menu')[0] as HTMLElement).style.height = '0px';
    }
  }

  closeModal() {
    this.activeModal.dismiss();
  }
  compareClicked(){
    this.compareSectionService.storeCompareMeta(this.compareSectionsMetaData);
    this.activeModal.dismiss();
  }

  onDocTypeChange(event){
    this.compareSectionsMetaData.docType = event.data;
  }

  onSectionChange(event){
    if(event.operation === 'add'){
      this.compareSectionsMetaData.searchKey = event.keyList[0];
    }
    else if(event.operation === 'clearSelected'){
      this.compareSectionsMetaData.searchKey = null;
    }
  }  
}
