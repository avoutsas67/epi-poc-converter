import { FhirMessageContained } from "./fhir-message-contiained.model";
import { FhirMessageEntry } from "./fhir-message-entry.model";
import { FhirMessageSection } from "./fhir-message-section.model";

export interface FhirMessageResource {
    entry?: FhirMessageEntry[];
    section?: FhirMessageSection[];
    contained?: FhirMessageContained[];
}