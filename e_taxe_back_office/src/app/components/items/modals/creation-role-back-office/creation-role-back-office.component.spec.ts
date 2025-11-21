import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreationRoleBackOfficeComponent } from './creation-role-back-office.component';

describe('CreationRoleBackOfficeComponent', () => {
  let component: CreationRoleBackOfficeComponent;
  let fixture: ComponentFixture<CreationRoleBackOfficeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CreationRoleBackOfficeComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CreationRoleBackOfficeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
