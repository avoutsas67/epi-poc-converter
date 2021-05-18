import { NgModule } from '@angular/core';
import { EmaComponentLibraryComponent } from './ema-component-library.component';
import { HeaderComponent } from './layouts/header/header.component';
import { EmaIconsModule } from './atoms/icons/ema-icons/ema-icons.module';
import { FooterModule } from './layouts/footer/footer.module';




@NgModule({
  declarations: [EmaComponentLibraryComponent, HeaderComponent,],
  imports: [
    EmaIconsModule,
    FooterModule
  ],
  exports: [EmaComponentLibraryComponent,
    HeaderComponent,
    EmaIconsModule,
    FooterModule
  ]
})
export class EmaComponentLibraryModule { }
