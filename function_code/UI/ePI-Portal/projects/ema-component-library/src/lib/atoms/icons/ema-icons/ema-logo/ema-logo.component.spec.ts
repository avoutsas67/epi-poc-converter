import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EmaLogoComponent } from './ema-logo.component';

describe('EmaLogoComponent', () => {
  let component: EmaLogoComponent;
  let fixture: ComponentFixture<EmaLogoComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ EmaLogoComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(EmaLogoComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
