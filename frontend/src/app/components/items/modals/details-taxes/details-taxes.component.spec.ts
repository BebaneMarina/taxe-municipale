import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DetailsTaxesComponent } from './details-taxes.component';

describe('DetailsTaxesComponent', () => {
  let component: DetailsTaxesComponent;
  let fixture: ComponentFixture<DetailsTaxesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DetailsTaxesComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DetailsTaxesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
