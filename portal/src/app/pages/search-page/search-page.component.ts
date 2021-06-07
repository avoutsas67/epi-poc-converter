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

  constructor( private modalService: NgbModal,
    modalConfig: NgbModalConfig,
    private readonly disclaimerServiceService: DisclaimerServiceService,
    private readonly fhirService: FhirService
    ) {
      modalConfig.backdrop = 'static';
      modalConfig.keyboard = false;
     }
  medicineList: SearchMedicine[] = null;
  resultsText = "";

  ngOnInit(): void {
    this.fhirService.medicineData.subscribe((data) => {
      if(data){
        for(let i=0; i<data.entry?.length;i++){
          let resourceData  = data.entry[i].resource;
          let requiredEntry :any;
          let medicine: SearchMedicine ={};
          medicine.name = data.entry[i].resource.identifier[0].value;
          medicine.listId = data.entry[i].resource.id;
          requiredEntry = resourceData.entry.filter((entry)=>entry.item.extension[0].valueCoding.display === 'SmPC' && entry.item.extension[1].valueCoding.display === 'en')[0];
          if(requiredEntry){
            medicine.routeReference = requiredEntry.item.reference.split('/')[1];
            medicine.routeLanguage = 'en';
          }
          else{
            medicine.routeReference = resourceData.entry[0].item.reference.split('/')[1];
            medicine.routeLanguage =resourceData.entry[0].item.extension[1].valueCoding.display;
          }
          if(!this.medicineList){
            this.medicineList = [];
          }
          this.medicineList.push(medicine);
          this.resultsText = this.medicineList?.length === 1?  this.medicineList?.length + ' result' : this.medicineList?.length + ' results'
          
        }
      }
      else if(data==null){
        this.fhirService.getAllLists();
      }
   
    });
  }

  ngAfterViewInit(){
    this.disclaimerServiceService.getDisclaimerStatus().subscribe((status)=>{
      if(!status){
        const modalRef = this.modalService.open(DisclaimerModalComponent, { scrollable: true, centered: true });
      }
    });
  }
  
  ngOnDestroy(){
    this.modalService.dismissAll();
  }
  
}
