import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { EuropeanCommissionComponent } from './european-commission/european-commission.component';
import { EmaLogoComponent } from './ema-logo/ema-logo.component';
import { HmaLogoComponent } from './hma-logo/hma-logo.component';
import { ShareComponent } from './share/share.component';
import { EmaHeaderLogoComponent } from './ema-header-logo/ema-header-logo.component';



@NgModule({
  declarations: [EuropeanCommissionComponent, EmaLogoComponent, HmaLogoComponent, ShareComponent, EmaHeaderLogoComponent],
  imports: [
    CommonModule,
    
  ],
  exports:[EuropeanCommissionComponent,
    EmaHeaderLogoComponent, 
    EmaLogoComponent,
    HmaLogoComponent,
    ShareComponent]
})
export class EmaIconsModule { }
