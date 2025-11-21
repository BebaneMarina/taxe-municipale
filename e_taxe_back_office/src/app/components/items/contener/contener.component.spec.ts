import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ContenerComponent } from './contener.component';

describe('ContenerComponent', () => {
  let component: ContenerComponent;
  let fixture: ComponentFixture<ContenerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ContenerComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ContenerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
