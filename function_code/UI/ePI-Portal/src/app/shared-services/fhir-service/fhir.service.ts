import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { FhirMessageBundle } from 'src/app/models/fhir-message-bundle.model';

@Injectable({
  providedIn: 'root'
})
export class FhirService {
  url ='api/Bundle/'

  constructor(private http: HttpClient) { }

  getBundle(id){
    let bundleId = '72f82a5e-dee3-4e3e-a65e-0332e8a03691';
    const httpOptions = {
    
      headers: new HttpHeaders({
        'Content-Type':  'application/fhir+xml',
        "Access-Control-Allow-Origin": "*"
      })
    };
    return this.http.get<FhirMessageBundle>(this.url + id,httpOptions)
  }
}