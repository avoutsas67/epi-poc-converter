import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { FhirCompareSectionsMeta } from 'src/app/models/fhir-compare-sections.model';

@Injectable({
  providedIn: 'root'
})
export class CompareSectionService {
  private compareSectionsMeta = new BehaviorSubject<FhirCompareSectionsMeta>(null);

  constructor() { }

  storeCompareMeta(meta: FhirCompareSectionsMeta){
    this.compareSectionsMeta.next(meta);
  }

  clearCompareMeta(){
    this.compareSectionsMeta.next(null);
  }

  getCompareMeta(){
    return this.compareSectionsMeta.asObservable();
  }
}
