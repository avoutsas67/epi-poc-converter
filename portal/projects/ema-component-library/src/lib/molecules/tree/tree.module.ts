import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TreeComponent } from './tree.component';
import { BrowserModule } from '@angular/platform-browser';
import { RouterModule } from '@angular/router';



@NgModule({
  declarations: [TreeComponent],
  imports: [
    CommonModule,
    BrowserModule,
    RouterModule
  ],
  exports:[TreeComponent]
})
export class TreeModule { }
