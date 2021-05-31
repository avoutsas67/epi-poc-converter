import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DocumentBodyTreeComponent } from './document-body-tree.component';

describe('DocumentBodyTreeComponent', () => {
  let component: DocumentBodyTreeComponent;
  let fixture: ComponentFixture<DocumentBodyTreeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DocumentBodyTreeComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(DocumentBodyTreeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
