import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EuropeanCommissionComponent } from './european-commission.component';

describe('EuropeanCommissionComponent', () => {
  let component: EuropeanCommissionComponent;
  let fixture: ComponentFixture<EuropeanCommissionComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ EuropeanCommissionComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(EuropeanCommissionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
