import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AccordionComponent } from './accordion.component';
import { PipesModule } from 'src/app/shared-pipes/pipes.module';
import { EmaIconsModule } from '../../atoms/icons/ema-icons/ema-icons.module';



@NgModule({
  declarations: [AccordionComponent],
  imports: [
    CommonModule,
    EmaIconsModule,
    PipesModule
  ],
  exports:[AccordionComponent]
})
export class AccordionModule { }
