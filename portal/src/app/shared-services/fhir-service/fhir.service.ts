import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { FhirMessageBundle } from 'src/app/models/fhir-message-bundle.model';

@Injectable({
  providedIn: 'root'
})
export class FhirService {
  private _medicineData = new BehaviorSubject<any>(null);
  private dataStore: { medicineData: FhirMessageBundle } = { medicineData: {} };

  get medicineData() {
    return this._medicineData.asObservable();
  }
  

   httpOptions = {

    headers: new HttpHeaders({
      'Content-Type': 'application/fhir+xml',
      "Access-Control-Allow-Origin": "*"
    })
  };

  constructor(private http: HttpClient) { }

  getBundle(id) {
    let url = 'api/Bundle/'
    return this.http.get<FhirMessageBundle>(url + id, this.httpOptions);
  }

  getList(id) {
    let url = 'api/List/';
    return this.http.get<FhirMessageBundle>(url + id,this.httpOptions);
  }

  getListWithIdentifier(identifier) {
    let url = 'api/List?identifier=';
    return this.http.get<FhirMessageBundle>(url + identifier,this.httpOptions);
  }

  getAllLists(){
    let url = 'api/List/'
     this.http.get<FhirMessageBundle>(url, this.httpOptions).subscribe((data)=>{
      this.dataStore.medicineData = data;
      this._medicineData.next(Object.assign({}, this.dataStore).medicineData)
    },
    (error)=>{
      console.error('Could not load lists');
    });
  }
}