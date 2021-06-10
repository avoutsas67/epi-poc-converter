import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TagsComponent } from './tags.component';
import { EmaIconsModule } from '../icons/ema-icons/ema-icons.module';



@NgModule({
  declarations: [TagsComponent],
  imports: [
    CommonModule,
    EmaIconsModule
  ],
  exports: [TagsComponent]
})
export class TagsModule { }
