import { FhirMessageResource } from "./fhir-message-resource.model";

export interface FhirMessageEntry {
    fullUrl?: string;
    resource: FhirMessageResource;
}