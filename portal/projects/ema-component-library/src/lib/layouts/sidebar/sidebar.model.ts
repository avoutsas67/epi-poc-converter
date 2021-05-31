import { Guid } from "guid-typescript";

export interface DocumentSidebarMenuNode {
    id: Guid;
    title: string;
    showChildren?: boolean;
    section?: any[];
}