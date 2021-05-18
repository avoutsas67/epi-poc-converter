import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { EuropeanCommissionComponent } from './european-commission/european-commission.component';
import { EmaLogoComponent } from './ema-logo/ema-logo.component';
import { HmaLogoComponent } from './hma-logo/hma-logo.component';



@NgModule({
  declarations: [EuropeanCommissionComponent, EmaLogoComponent, HmaLogoComponent],
  imports: [
    CommonModule,
    
  ],
  exports:[EuropeanCommissionComponent, 
    EmaLogoComponent,
    HmaLogoComponent]
})
export class EmaIconsModule { }
