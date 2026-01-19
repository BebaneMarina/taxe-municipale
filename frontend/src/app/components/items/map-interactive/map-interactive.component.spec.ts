import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MapInteractiveComponent } from './map-interactive.component';

describe('MapInteractiveComponent', () => {
  let component: MapInteractiveComponent;
  let fixture: ComponentFixture<MapInteractiveComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MapInteractiveComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MapInteractiveComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
