import { TestBed } from '@angular/core/testing';

import { DisclaimerServiceService } from './disclaimer-service.service';

describe('DisclaimerServiceService', () => {
  let service: DisclaimerServiceService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(DisclaimerServiceService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
