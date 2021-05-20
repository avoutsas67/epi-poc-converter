import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DocumentViewComponent } from './document-view/document-view.component';
import { EmaComponentLibraryModule } from 'projects/ema-component-library/src/lib/ema-component-library.module';
import { HttpClientModule } from '@angular/common/http';


@NgModule({
  declarations: [DocumentViewComponent],
  imports: [
    CommonModule,
    HttpClientModule,
    EmaComponentLibraryModule
  ],
  exports:[DocumentViewComponent]
})
export class DocumentViewModule { }
