import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdministrationsTableComponent } from './administrations-table.component';

describe('AdministrationsTableComponent', () => {
  let component: AdministrationsTableComponent;
  let fixture: ComponentFixture<AdministrationsTableComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AdministrationsTableComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AdministrationsTableComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
