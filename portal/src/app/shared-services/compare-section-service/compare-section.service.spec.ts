import { TestBed } from '@angular/core/testing';

import { CompareSectionService } from './compare-section.service';

describe('CompareSectionService', () => {
  let service: CompareSectionService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CompareSectionService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
