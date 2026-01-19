import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ContenerGrayComponent } from './contener-gray.component';

describe('ContenerGrayComponent', () => {
  let component: ContenerGrayComponent;
  let fixture: ComponentFixture<ContenerGrayComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ContenerGrayComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ContenerGrayComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
