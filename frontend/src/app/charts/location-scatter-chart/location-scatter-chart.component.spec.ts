import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { LocationScatterChartComponent } from './location-scatter-chart.component';

describe('LocationScatterChartComponent', () => {
  let component: LocationScatterChartComponent;
  let fixture: ComponentFixture<LocationScatterChartComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ LocationScatterChartComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(LocationScatterChartComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
