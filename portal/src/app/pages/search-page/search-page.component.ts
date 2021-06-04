import { AfterViewInit, Component, OnDestroy, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { NgbModal, NgbModalConfig } from '@ng-bootstrap/ng-bootstrap';
import { DisclaimerModalComponent } from 'projects/ema-component-library/src/lib/molecules/disclaimer-modal/disclaimer-modal.component';
import { DisclaimerServiceService } from 'src/app/shared-services/disclaimer-service/disclaimer-service.service';
import { FhirService } from 'src/app/shared-services/fhir-service/fhir.service';

@Component({
  selector: 'ema-search-page',
  templateUrl: './search-page.component.html',
  styleUrls: ['./search-page.component.scss']
})
export class SearchPageComponent implements OnInit, AfterViewInit, OnDestroy {
  routeDocumentId = null;

  constructor( private modalService: NgbModal,
    modalConfig: NgbModalConfig,
    private readonly disclaimerServiceService: DisclaimerServiceService,
    private readonly fhirService: FhirService,
    private router: Router
    ) {
      modalConfig.backdrop = 'static';
      modalConfig.keyboard = false;
     }

  ngOnInit(): void {
    
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

  linkClicked(listId){
    this.fhirService.getList(listId).subscribe((data) => {
      
      if(data){
        data.entry.forEach(entry => {
          if (!this.routeDocumentId && entry.item.extension[0].valueCoding.display === 'SmPC' && entry.item.extension[1].valueCoding.display === 'en') {
            this.routeDocumentId = entry.item.reference;
          }
          if(this.routeDocumentId){
            this.router.navigate(['/View', listId,'en',this.routeDocumentId.split('/')[1]]);
          }
        })
      }
    });
  }
  
}
