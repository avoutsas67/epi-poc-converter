import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EmaHeaderLogoComponent } from './ema-header-logo.component';

describe('EmaHeaderLogoComponent', () => {
  let component: EmaHeaderLogoComponent;
  let fixture: ComponentFixture<EmaHeaderLogoComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ EmaHeaderLogoComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(EmaHeaderLogoComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
