import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GestionCollecteursComponent } from './gestion-collecteurs.component';

describe('GestionCollecteursComponent', () => {
  let component: GestionCollecteursComponent;
  let fixture: ComponentFixture<GestionCollecteursComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GestionCollecteursComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GestionCollecteursComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
