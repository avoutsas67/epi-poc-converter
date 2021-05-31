import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FooterComponent } from './footer.component';
import { EmaIconsModule } from '../../atoms/icons/ema-icons/ema-icons.module';



@NgModule({
  declarations: [FooterComponent],
  imports: [
    CommonModule,
    EmaIconsModule
  ],
  exports:[FooterComponent]
})
export class FooterModule { }
