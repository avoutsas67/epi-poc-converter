import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class DisclaimerServiceService {
  /* Service used to keep track of whether the disclaimer modal was accepted or not*/
  
  private disclaimerStatus = new BehaviorSubject<Boolean>(false);
  
  constructor() { }

  setDisclaimerStatus(status){
    this.disclaimerStatus.next(status);
  }
  getDisclaimerStatus(){
    return this.disclaimerStatus.asObservable();
  }
}


