import { AfterViewInit, Component, OnInit } from '@angular/core';
import { NgbModal, NgbModalConfig } from '@ng-bootstrap/ng-bootstrap';
import { DisclaimerModalComponent } from 'projects/ema-component-library/src/lib/molecules/disclaimer-modal/disclaimer-modal.component';
import { DisclaimerServiceService } from 'src/app/shared-services/disclaimer-service/disclaimer-service.service';

@Component({
  selector: 'ema-search-page',
  templateUrl: './search-page.component.html',
  styleUrls: ['./search-page.component.scss']
})
export class SearchPageComponent implements OnInit, AfterViewInit {

  constructor( private modalService: NgbModal,
    modalConfig: NgbModalConfig,
    private readonly disclaimerServiceService: DisclaimerServiceService
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
}
