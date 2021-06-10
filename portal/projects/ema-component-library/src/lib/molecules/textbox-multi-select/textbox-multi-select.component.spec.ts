import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TextboxMultiSelectComponent } from './textbox-multi-select.component';

describe('TextboxMultiSelectComponent', () => {
  let component: TextboxMultiSelectComponent;
  let fixture: ComponentFixture<TextboxMultiSelectComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TextboxMultiSelectComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TextboxMultiSelectComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
