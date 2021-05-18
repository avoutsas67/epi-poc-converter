import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppComponent } from './app.component';
import { EmaComponentLibraryModule } from 'projects/ema-component-library/src/lib/ema-component-library.module';
import { DocumentViewModule } from './document-view/document-view.module';
import { RouterModule, Routes } from '@angular/router';
import { DocumentViewComponent } from './document-view/document-view/document-view.component';

const routes: Routes = [
  { path: '',   redirectTo: '/View', pathMatch: 'full' },
  { path: 'View', component: DocumentViewComponent }
];

@NgModule({
  declarations: [
    AppComponent
  ],
  imports: [
    BrowserModule,
    EmaComponentLibraryModule,
    DocumentViewModule,
    RouterModule.forRoot(routes)

    
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
