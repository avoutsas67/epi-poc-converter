import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppComponent } from './app.component';
import { EmaComponentLibraryModule } from 'projects/ema-component-library/src/lib/ema-component-library.module';
import { RouterModule, Routes } from '@angular/router';
import { HttpClientModule } from '@angular/common/http';
import { DocumentViewComponent } from './pages/document-view/document-view/document-view.component';
import { DocumentViewModule } from './pages/document-view/document-view.module';
import { SearchPageModule } from './pages/search-page/search-page.module';
import { SearchPageComponent } from './pages/search-page/search-page.component';

const routes: Routes = [
  { path: '',   redirectTo: '/Search', pathMatch: 'full' },
  {path: 'Search' , component: SearchPageComponent},
  { path: 'View/:id', component: DocumentViewComponent },
  { path: 'View',  redirectTo: '/Search', pathMatch: 'full' }
];

@NgModule({
  declarations: [
    AppComponent
  ],
  imports: [
    BrowserModule,
    RouterModule.forRoot(routes, {
      scrollPositionRestoration: 'enabled', // or 'top'
      anchorScrolling: 'enabled',
      scrollOffset: [0, 64], 
    }),
    EmaComponentLibraryModule,
    HttpClientModule,
    DocumentViewModule,
    SearchPageModule,

    
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
