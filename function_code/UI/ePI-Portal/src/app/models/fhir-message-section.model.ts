import { Guid } from "guid-typescript";

export interface FhirMessageSection {
    id?:Guid;
    title: string;
    text:any;
    section?: FhirMessageSection[];
}