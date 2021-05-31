import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SearchPageComponent } from './search-page.component';
import { EmaComponentLibraryModule } from 'projects/ema-component-library/src/lib/ema-component-library.module';
import { RouterModule } from '@angular/router';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';



@NgModule({
  declarations: [SearchPageComponent],
  imports: [
    CommonModule,
    EmaComponentLibraryModule,
    RouterModule,
    NgbModule
  ],
  exports:[SearchPageComponent]
})
export class SearchPageModule { }
