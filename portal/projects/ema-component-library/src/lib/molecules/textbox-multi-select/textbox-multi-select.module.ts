import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TextboxMultiSelectComponent } from './textbox-multi-select.component';
import { TagsModule } from '../../atoms/tags/tags.module';
import { EmaIconsModule } from '../../atoms/icons/ema-icons/ema-icons.module';
import { ReactiveFormsModule } from '@angular/forms';



@NgModule({
  declarations: [TextboxMultiSelectComponent],
  imports: [
    CommonModule,
    TagsModule,
    EmaIconsModule,
    ReactiveFormsModule
  ],
  exports:[TextboxMultiSelectComponent]
})
export class TextboxMultiSelectModule { }
