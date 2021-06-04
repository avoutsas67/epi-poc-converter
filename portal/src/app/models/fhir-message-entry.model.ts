import { FhirMessageResource } from "./fhir-message-resource.model";
export interface FhirEntryItemExtension {
    url?: string;
    valueCoding: {
        code?: string;
        display?: string;
        system?: string;
    }
}
export interface FhirEntryItem {
    extension?: FhirEntryItemExtension[],
    reference?:string
}
export interface FhirMessageEntry {
    fullUrl?: string;
    resource?: FhirMessageResource;
    item?:FhirEntryItem
}