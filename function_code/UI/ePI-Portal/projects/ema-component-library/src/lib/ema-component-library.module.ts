import { NgModule } from '@angular/core';
import { EmaComponentLibraryComponent } from './ema-component-library.component';
import { HeaderComponent } from './layouts/header/header.component';
import { EmaIconsModule } from './atoms/icons/ema-icons/ema-icons.module';
import { FooterModule } from './layouts/footer/footer.module';
import { SidebarComponent } from './layouts/sidebar/sidebar.component';
import { TreeComponent } from './molecules/tree/tree.component';
import { BrowserModule } from '@angular/platform-browser';
import { TreeModule } from './molecules/tree/tree.module';
import { DocumentHeaderComponent } from './layouts/document-header/document-header.component';
import { DropdownComponent } from './molecules/dropdown/dropdown.component';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';




@NgModule({
  declarations: [EmaComponentLibraryComponent, HeaderComponent, SidebarComponent, DocumentHeaderComponent, DropdownComponent],
  imports: [
    EmaIconsModule,
    FooterModule,
    BrowserModule,
    TreeModule,
    NgbModule
  ],
  exports: [EmaComponentLibraryComponent,
    HeaderComponent,
    SidebarComponent,
    DocumentHeaderComponent,
    EmaIconsModule,
    FooterModule, 
    DropdownComponent
  ]
})
export class EmaComponentLibraryModule { }
