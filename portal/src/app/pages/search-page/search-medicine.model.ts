import { FhirMessageEntry } from "src/app/models/fhir-message-entry.model";
import { FhirMessageSection } from "src/app/models/fhir-message-section.model";

export interface SearchMedicine {
    name?: string;
    date?:string;
    desc?:string;
    listId?:string;
    routeReference?: string;
    routeLanguage?: string;
    requiredSection?: string;
    entry?:FhirMessageEntry[];
    sectionsCompareResults?: FhirMessageSection[];
    searchName?: string;
    authorizationHolder?: string;
    activeSubstances?: string;
    lastUpdated?:string;
}