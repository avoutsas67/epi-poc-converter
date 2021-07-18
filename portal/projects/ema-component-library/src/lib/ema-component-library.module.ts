import { NgModule } from '@angular/core';
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
import { ButtonComponent } from './atoms/button/button.component';
import { PipesModule } from 'src/app/shared-pipes/pipes.module';
import { AccordionModule } from './molecules/accordion/accordion.module';
import { CompareModalComponent } from './molecules/compare-modal/compare-modal.component';

@NgModule({
  declarations: [HeaderComponent, SidebarComponent, DocumentHeaderComponent, DropdownComponent, ActionLinksComponent, DisclaimerModalComponent, ButtonComponent, CompareModalComponent],
  imports: [
    PipesModule,
    EmaIconsModule,
    FooterModule,
    BrowserModule,
    RouterModule,
    TreeModule,
    NgbModule,
    AccordionModule,
    TagsModule,
    TextboxMultiSelectModule
  ],
  exports: [
    ButtonComponent,
    HeaderComponent,
    SidebarComponent,
    DocumentHeaderComponent,
    EmaIconsModule,
    FooterModule, 
    TagsModule,
    AccordionModule,
    DropdownComponent,
    ActionLinksComponent,
    DisclaimerModalComponent,
    TextboxMultiSelectModule,
    CompareModalComponent
  ],
  entryComponents: [
    DisclaimerModalComponent,
    CompareModalComponent
  ]
})
export class EmaComponentLibraryModule { }
