import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { FhirMessageBundle } from 'src/app/models/fhir-message-bundle.model';

@Injectable({
  providedIn: 'root'
})
export class FhirService {

  constructor(private http: HttpClient) { }

  getBundle(id) {
    let url = 'api/Bundle/'
    const httpOptions = {

      headers: new HttpHeaders({
        'Content-Type': 'application/fhir+xml',
        "Access-Control-Allow-Origin": "*"
      })
    };
    
    return this.http.get<FhirMessageBundle>(url + id, httpOptions);
  }

  getList(id) {
    let url = 'api/List/'
    const httpOptions = {

      headers: new HttpHeaders({
        'Content-Type': 'application/fhir+xml',

        "Access-Control-Allow-Origin": "*"
      })
    };
    return this.http.get<FhirMessageBundle>(url + id, httpOptions);
  }
}