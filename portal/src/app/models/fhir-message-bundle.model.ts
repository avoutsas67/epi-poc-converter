import { FhirMessageEntry } from "./fhir-message-entry.model";

export interface FhirMessageBundle {
    resourceType?:string;
    id?:string;
    type?:string;
    entry: FhirMessageEntry[];
    meta?: {versionId: string, lastUpdated: string}
}