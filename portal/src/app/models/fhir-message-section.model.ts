export interface FhirMessageSection {
    id?:string;
    title: string;
    text:any;
    section?: FhirMessageSection[];
}