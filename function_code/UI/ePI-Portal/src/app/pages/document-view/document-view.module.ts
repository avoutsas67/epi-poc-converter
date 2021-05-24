import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DocumentViewComponent } from './document-view/document-view.component';
import { EmaComponentLibraryModule } from 'projects/ema-component-library/src/lib/ema-component-library.module';
import { HttpClientModule } from '@angular/common/http';
import { RouterModule } from '@angular/router';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';


@NgModule({
  declarations: [DocumentViewComponent],
  imports: [
    CommonModule,
    HttpClientModule,
    RouterModule,
    EmaComponentLibraryModule,
    NgbModule
  ],
  exports:[DocumentViewComponent]
})
export class DocumentViewModule { }
