import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HmaLogoComponent } from './hma-logo.component';

describe('HmaLogoComponent', () => {
  let component: HmaLogoComponent;
  let fixture: ComponentFixture<HmaLogoComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ HmaLogoComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(HmaLogoComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
