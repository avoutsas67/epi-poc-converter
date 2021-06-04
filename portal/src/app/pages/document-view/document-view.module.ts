import { NgModule } from '@angular/core';
import { CommonModule, LocationStrategy, PathLocationStrategy } from '@angular/common';
import { DocumentViewComponent } from './document-view/document-view.component';
import { EmaComponentLibraryModule } from 'projects/ema-component-library/src/lib/ema-component-library.module';
import { HttpClientModule } from '@angular/common/http';
import { RouterModule } from '@angular/router';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { DocumentBodyTreeComponent } from './document-body-tree/document-body-tree.component';
import { BrowserModule } from '@angular/platform-browser';
import { PipesModule } from 'src/app/shared-pipes/pipes.module';


@NgModule({
  declarations: [DocumentViewComponent, DocumentBodyTreeComponent],
  imports: [
    CommonModule,
    HttpClientModule,
    RouterModule,
    EmaComponentLibraryModule,
    NgbModule,
    BrowserModule,
    PipesModule
  ],
  providers: [
    { provide: LocationStrategy, useClass: PathLocationStrategy }
  ],
  exports:[DocumentViewComponent,
    DocumentBodyTreeComponent]
})
export class DocumentViewModule { }
