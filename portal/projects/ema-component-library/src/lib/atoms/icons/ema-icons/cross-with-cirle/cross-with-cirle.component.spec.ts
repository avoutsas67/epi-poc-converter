import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CrossWithCirleComponent } from './cross-with-cirle.component';

describe('CrossWithCirleComponent', () => {
  let component: CrossWithCirleComponent;
  let fixture: ComponentFixture<CrossWithCirleComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CrossWithCirleComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(CrossWithCirleComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
