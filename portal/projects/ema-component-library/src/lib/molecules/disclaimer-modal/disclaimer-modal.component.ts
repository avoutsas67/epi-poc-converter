import { Component, OnInit } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { DisclaimerServiceService } from 'src/app/shared-services/disclaimer-service/disclaimer-service.service';

@Component({
  selector: 'ema-disclaimer-modal',
  templateUrl: './disclaimer-modal.component.html',
  styleUrls: ['./disclaimer-modal.component.scss']
})
export class DisclaimerModalComponent implements OnInit {

  constructor(public activeModal: NgbActiveModal,
    private readonly disclaimerServiceService: DisclaimerServiceService) { }

  ngOnInit(): void {
  }

  closeDisclaimer(){
    this.disclaimerServiceService.setDisclaimerStatus(true);
    this.activeModal.close('Close click');
  }

}
