import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TreeComponent } from './tree.component';
import { BrowserModule } from '@angular/platform-browser';



@NgModule({
  declarations: [TreeComponent],
  imports: [
    CommonModule,
    BrowserModule,
  ],
  exports:[TreeComponent]
})
export class TreeModule { }
