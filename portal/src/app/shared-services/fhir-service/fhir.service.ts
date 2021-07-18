import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { FhirMessageBundle } from 'src/app/models/fhir-message-bundle.model';

@Injectable({
  providedIn: 'root'
})
export class FhirService {
  // This class contains methods that make calls to the server.

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
    // Function to get a bundle from server.
    let url = 'api/Bundle/'
    return this.http.get<FhirMessageBundle>(url + id, this.httpOptions);
  }

  getListWithIdentifier(identifier) {
    //Function to get the list for a particular medicine from the server.
    let url = 'api/List?identifier=';
    return this.http.get<FhirMessageBundle>(url + identifier, this.httpOptions);
  }

  getAllLists() {
    // Function to get list information of all medicines from the server.
    let url = 'api/List/'
    this.http.get<FhirMessageBundle>(url, this.httpOptions).subscribe((data) => {
      this.dataStore.medicineData = data;
      this._medicineData.next(Object.assign({}, this.dataStore).medicineData)
    },
      (error) => {
        console.error('Could not load lists');
      });
  }
}