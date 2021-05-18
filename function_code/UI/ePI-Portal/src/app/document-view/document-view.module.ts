import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DocumentViewComponent } from './document-view/document-view.component';



@NgModule({
  declarations: [DocumentViewComponent],
  imports: [
    CommonModule
  ],
  exports:[DocumentViewComponent]
})
export class DocumentViewModule { }
