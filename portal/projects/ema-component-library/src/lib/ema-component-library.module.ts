import { NgModule } from '@angular/core';
import { EmaComponentLibraryComponent } from './ema-component-library.component';
import { HeaderComponent } from './layouts/header/header.component';
import { EmaIconsModule } from './atoms/icons/ema-icons/ema-icons.module';
import { FooterModule } from './layouts/footer/footer.module';
import { SidebarComponent } from './layouts/sidebar/sidebar.component';
import { BrowserModule } from '@angular/platform-browser';
import { TreeModule } from './molecules/tree/tree.module';
import { DocumentHeaderComponent } from './layouts/document-header/document-header.component';
import { DropdownComponent } from './molecules/dropdown/dropdown.component';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { ActionLinksComponent } from './molecules/action-links/action-links.component';
import { DisclaimerModalComponent } from './molecules/disclaimer-modal/disclaimer-modal.component';
import { RouterModule } from '@angular/router';
import { TagsModule } from './atoms/tags/tags.module';
import { TextboxMultiSelectModule } from './molecules/textbox-multi-select/textbox-multi-select.module';




@NgModule({
  declarations: [EmaComponentLibraryComponent, HeaderComponent, SidebarComponent, DocumentHeaderComponent, DropdownComponent, ActionLinksComponent, DisclaimerModalComponent],
  imports: [
    EmaIconsModule,
    FooterModule,
    BrowserModule,
    RouterModule,
    TreeModule,
    NgbModule,
    TagsModule,
    TextboxMultiSelectModule
  ],
  exports: [EmaComponentLibraryComponent,
    HeaderComponent,
    SidebarComponent,
    DocumentHeaderComponent,
    EmaIconsModule,
    FooterModule, 
    TagsModule,
    DropdownComponent,
    ActionLinksComponent,
    DisclaimerModalComponent,
    TextboxMultiSelectModule
  ],
  entryComponents: [
    DisclaimerModalComponent
  ]
})
export class EmaComponentLibraryModule { }
