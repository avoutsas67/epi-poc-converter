import { TestBed } from '@angular/core/testing';

import { EmaComponentLibraryService } from './ema-component-library.service';

describe('EmaComponentLibraryService', () => {
  let service: EmaComponentLibraryService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(EmaComponentLibraryService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
