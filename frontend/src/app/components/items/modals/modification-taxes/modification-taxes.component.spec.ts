import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ModificationTaxesComponent } from './modification-taxes.component';

describe('ModificationTaxesComponent', () => {
  let component: ModificationTaxesComponent;
  let fixture: ComponentFixture<ModificationTaxesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ModificationTaxesComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ModificationTaxesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
