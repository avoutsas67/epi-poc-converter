import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ActionLinksComponent } from './action-links.component';

describe('ActionLinksComponent', () => {
  let component: ActionLinksComponent;
  let fixture: ComponentFixture<ActionLinksComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ActionLinksComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ActionLinksComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
