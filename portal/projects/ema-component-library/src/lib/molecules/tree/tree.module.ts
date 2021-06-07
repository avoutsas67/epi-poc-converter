import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TreeComponent } from './tree.component';
import { BrowserModule } from '@angular/platform-browser';
import { RouterModule } from '@angular/router';
import { EmaIconsModule } from '../../atoms/icons/ema-icons/ema-icons.module';



@NgModule({
  declarations: [TreeComponent],
  imports: [
    CommonModule,
    BrowserModule,
    RouterModule,
    EmaIconsModule
  ],
  exports:[TreeComponent]
})
export class TreeModule { }
