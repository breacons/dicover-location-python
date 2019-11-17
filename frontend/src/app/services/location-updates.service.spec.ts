import { TestBed } from '@angular/core/testing';

import { LocationUpdatesService } from './location-updates.service';

describe('LocationUpdatesService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: LocationUpdatesService = TestBed.get(LocationUpdatesService);
    expect(service).toBeTruthy();
  });
});
