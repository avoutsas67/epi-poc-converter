import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { EuropeanCommissionComponent } from './european-commission/european-commission.component';
import { EmaLogoComponent } from './ema-logo/ema-logo.component';
import { HmaLogoComponent } from './hma-logo/hma-logo.component';
import { ShareComponent } from './share/share.component';
import { EmaHeaderLogoComponent } from './ema-header-logo/ema-header-logo.component';
import { ArrowComponent } from './arrow/arrow.component';



@NgModule({
  declarations: [EuropeanCommissionComponent, EmaLogoComponent, HmaLogoComponent, ShareComponent, EmaHeaderLogoComponent, ArrowComponent],
  imports: [
    CommonModule,
    
  ],
  exports:[EuropeanCommissionComponent,
    EmaHeaderLogoComponent, 
    EmaLogoComponent,
    HmaLogoComponent,
    ShareComponent,
    ArrowComponent]
})
export class EmaIconsModule { }
