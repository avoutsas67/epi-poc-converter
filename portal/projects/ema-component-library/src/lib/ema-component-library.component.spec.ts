import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EmaComponentLibraryComponent } from './ema-component-library.component';

describe('EmaComponentLibraryComponent', () => {
  let component: EmaComponentLibraryComponent;
  let fixture: ComponentFixture<EmaComponentLibraryComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ EmaComponentLibraryComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(EmaComponentLibraryComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
